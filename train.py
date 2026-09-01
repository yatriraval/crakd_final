"""
train.py
--------
Trains an XGBoost classifier to predict `Is_Fraud` (0 = legitimate,
1 = fraud) for a bank transaction, using only information that would
be known at transaction time.

Run with:
    python train.py

CHANGED FROM THE PREVIOUS SVM VERSION:
  - Model: SVC (SVM) -> XGBClassifier (gradient-boosted trees).
    XGBoost trains in roughly seconds-to-a-couple-minutes on 200,000
    rows (tree_method="hist"), vs. an SVM's O(n^2)-O(n^3) blowup, and
    it also tends to be more accurate on this kind of tabular,
    mixed numeric/categorical data.
  - Categorical columns (Gender, State, City, Bank_Branch, ...) are
    now passed to XGBoost natively as pandas 'category' dtype
    (enable_categorical=True) instead of being one-hot encoded. This
    is why City / Bank_Branch / Transaction_Location - previously
    dropped for being too high-cardinality for one-hot + SVM - are
    now kept as features (see feature_engineering.py).
  - Class imbalance (~5% fraud) is handled with scale_pos_weight
    instead of SVM's class_weight="balanced".
  - Added: a small randomized hyperparameter search (cross-validated
    on ROC-AUC), early stopping on a validation split to pick the
    best number of trees, and decision-threshold tuning (instead of
    the default 0.5) to maximize F1 on the fraud class - all of this
    is aimed at squeezing out extra accuracy on an imbalanced dataset.

Steps:
  1. Load the dataset from DATA_PATH.
  2. Split it into X (input features) and y (target = Is_Fraud).
  3. Engineer extra features from Transaction_Date / Transaction_Time.
  4. Split into train/val/test sets (stratified, since fraud is rare).
  5. (Optional) Randomized hyperparameter search on the training set.
  6. Fit final XGBoost model with early stopping on the validation set.
  7. Tune the decision threshold on the validation set.
  8. Evaluate on the held-out test set (accuracy, balanced accuracy,
     ROC-AUC, PR-AUC, classification report, confusion matrix).
  9. Save the fitted pipeline + chosen threshold to model.joblib.
"""

import time

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    f1_score,
)
from xgboost import XGBClassifier

from feature_engineering import (
    extract_features,
    build_preprocessor,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    RAW_INPUT_COLUMNS,
    TARGET_COLUMN,
)

DATA_PATH = "Bank_Transaction_Fraud_Detection.csv"
MODEL_PATH = "model.joblib"
RANDOM_STATE = 42

# Set to an integer (e.g. 20000) to subsample while testing the
# pipeline quickly. Set to None to train on the full dataset.
SAMPLE_SIZE = None

# Set to True to run RandomizedSearchCV (slower, usually more accurate).
# Set to False to skip tuning and use the hand-picked DEFAULT_PARAMS
# below (much faster - useful while iterating).
RUN_HYPERPARAMETER_SEARCH = True
N_SEARCH_ITER = 25
CV_FOLDS = 3

# Reasonable defaults if RUN_HYPERPARAMETER_SEARCH is False, or as a
# fallback starting point for the search.
DEFAULT_PARAMS = dict(
    n_estimators=600,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=1,
    gamma=0.0,
    reg_alpha=0.0,
    reg_lambda=1.0,
)


def load_data(path: str) -> pd.DataFrame:
    print(f"[1/9] Loading data from {path} ...")
    df = pd.read_csv(path)
    print(f"      Loaded {len(df)} rows, {len(df.columns)} columns.")

    if SAMPLE_SIZE is not None and SAMPLE_SIZE < len(df):
        print(f"      SAMPLE_SIZE is set - subsampling to {SAMPLE_SIZE} rows "
              f"(stratified by {TARGET_COLUMN}) for a faster run ...")
        df, _ = train_test_split(
            df,
            train_size=SAMPLE_SIZE,
            stratify=df[TARGET_COLUMN],
            random_state=RANDOM_STATE,
        )
    return df


def prepare_features_and_target(df: pd.DataFrame):
    """
    Separates the raw input columns (X) from the target column (y),
    then applies feature engineering to X.

    Columns that must NEVER be used as features (leakage / identifiers /
    PII / zero-signal - see feature_engineering.DROPPED_COLUMNS for the
    full list and reasons):
      - Customer_ID, Customer_Name, Transaction_ID, Merchant_ID,
        Customer_Contact, Customer_Email, Transaction_Description
      - Transaction_Currency (constant - only 1 unique value)
    """
    print("[2/9] Separating input features (X) from target (y) ...")

    y = df[TARGET_COLUMN].copy()

    # Keep ONLY the raw columns that are legitimately safe to use.
    # This line is also our main defence against accidentally leaking
    # identifiers into the model.
    X_raw = df[RAW_INPUT_COLUMNS].copy()

    print("      Engineering features from Transaction_Date / Transaction_Time ...")
    X = extract_features(X_raw)

    return X, y


def build_pipeline(params: dict, scale_pos_weight: float) -> Pipeline:
    """
    Builds the full Pipeline: preprocessing + XGBoost classifier.

    Why XGBoost here:
      - Gradient-boosted decision trees are a strong, fast default for
        tabular data with a mix of numeric and categorical columns -
        this is exactly what fraud-detection data looks like.
      - tree_method="hist" makes training on 200,000 rows fast.
      - enable_categorical=True lets XGBoost split directly on
        categorical columns (Gender, State, City, ...) without one-hot
        encoding, so high-cardinality columns like City / Bank_Branch /
        Transaction_Location can be used without exploding the feature
        space.
      - scale_pos_weight compensates for fraud being rare (~5% of
        rows), similar in spirit to SVM's class_weight="balanced".
      - eval_metric="aucpr" (area under precision-recall curve) is a
        better fit than plain accuracy/logloss for a rare-class
        problem like fraud.
    """
    preprocessor = build_preprocessor()

    xgb_classifier = XGBClassifier(
        objective="binary:logistic",
        eval_metric="aucpr",
        tree_method="hist",
        enable_categorical=True,
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        **params,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("xgb", xgb_classifier),
        ]
    )
    return pipeline


def search_hyperparameters(X_train, y_train, scale_pos_weight):
    """
    Randomized search over a modest hyperparameter grid, cross-validated
    on ROC-AUC. This searches CV_FOLDS folds x N_SEARCH_ITER
    combinations - increase N_SEARCH_ITER for a more thorough (but
    slower) search.
    """
    print(f"[4/9] Running RandomizedSearchCV "
          f"({N_SEARCH_ITER} candidates x {CV_FOLDS} folds) ...")
    t0 = time.time()

    base_pipeline = build_pipeline(DEFAULT_PARAMS, scale_pos_weight)

    param_distributions = {
        "xgb__n_estimators": [200, 300, 400, 600, 800],
        "xgb__max_depth": [3, 4, 5, 6, 8],
        "xgb__learning_rate": [0.01, 0.03, 0.05, 0.08, 0.1],
        "xgb__subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
        "xgb__colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
        "xgb__min_child_weight": [1, 3, 5, 7],
        "xgb__gamma": [0, 0.1, 0.3, 0.5],
        "xgb__reg_alpha": [0, 0.01, 0.1, 1.0],
        "xgb__reg_lambda": [0.5, 1.0, 1.5, 2.0],
    }

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    search = RandomizedSearchCV(
        base_pipeline,
        param_distributions=param_distributions,
        n_iter=N_SEARCH_ITER,
        scoring="roc_auc",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=1,  # XGBoost already parallelizes internally (n_jobs=-1)
        verbose=1,
    )
    search.fit(X_train, y_train)

    print(f"      Done in {time.time() - t0:.1f}s. "
          f"Best CV ROC-AUC: {search.best_score_:.4f}")
    print(f"      Best params: {search.best_params_}")

    best_params = {k.replace("xgb__", ""): v for k, v in search.best_params_.items()}
    return best_params


def fit_final_model(X_train, y_train, X_val, y_val, params, scale_pos_weight):
    """
    Fits the final pipeline using early stopping: XGBoost keeps adding
    trees as long as performance on the validation set keeps improving,
    and stops (rolling back to the best round) once it doesn't, which
    both saves time and helps avoid overfitting.
    """
    print("[5/9] Fitting final model with early stopping ...")

    # Give early stopping room to work with by allowing a large
    # n_estimators ceiling; the model will stop early if val AUCPR
    # stops improving.
    final_params = dict(params)
    final_params["n_estimators"] = max(final_params.get("n_estimators", 600), 2000)

    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_val_processed = preprocessor.transform(X_val)

    xgb_classifier = XGBClassifier(
        objective="binary:logistic",
        eval_metric="aucpr",
        tree_method="hist",
        enable_categorical=True,
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        early_stopping_rounds=50,
        **final_params,
    )
    xgb_classifier.fit(
        X_train_processed,
        y_train,
        eval_set=[(X_val_processed, y_val)],
        verbose=False,
    )
    print(f"      Best iteration: {xgb_classifier.best_iteration} "
          f"(stopped early out of {final_params['n_estimators']} max trees)")

    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("xgb", xgb_classifier)])
    return pipeline


def tune_threshold(pipeline: Pipeline, X_val, y_val) -> float:
    """
    The default 0.5 probability cutoff is rarely optimal for a rare
    positive class like fraud (~5% of rows). This scans candidate
    thresholds on the validation set and picks the one that maximizes
    F1 on the fraud class.
    """
    print("[6/9] Tuning decision threshold on the validation set ...")
    val_proba = pipeline.predict_proba(X_val)[:, 1]

    thresholds = np.arange(0.05, 0.96, 0.01)
    f1_scores = [f1_score(y_val, (val_proba >= t).astype(int), zero_division=0) for t in thresholds]
    best_idx = int(np.argmax(f1_scores))
    best_threshold = float(thresholds[best_idx])

    print(f"      Best threshold: {best_threshold:.2f} "
          f"(validation F1 for fraud class: {f1_scores[best_idx]:.4f}, "
          f"vs. {f1_score(y_val, (val_proba >= 0.5).astype(int), zero_division=0):.4f} at 0.50)")
    return best_threshold


def evaluate_model(pipeline: Pipeline, X_test, y_test, threshold: float):
    print("\n[8/9] Evaluating model on the held-out test set ...")

    y_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    accuracy = accuracy_score(y_test, y_pred)
    balanced_acc = balanced_accuracy_score(y_test, y_pred)

    print(f"      Decision threshold used: {threshold:.2f}")
    print(f"      Accuracy:          {accuracy:.4f}")
    print(f"      Balanced accuracy: {balanced_acc:.4f}")

    # ROC-AUC and PR-AUC matter a lot here because fraud is rare
    # (~5% of rows): accuracy alone can look great by just predicting
    # "not fraud" every time.
    try:
        roc_auc = roc_auc_score(y_test, y_proba)
        pr_auc = average_precision_score(y_test, y_proba)
        print(f"      ROC-AUC:           {roc_auc:.4f}")
        print(f"      PR-AUC:            {pr_auc:.4f}")
    except ValueError as e:
        print(f"      Could not compute ROC-AUC/PR-AUC: {e}")

    print("\n      Classification report (precision/recall/F1 for each class):")
    print(classification_report(y_test, y_pred, zero_division=0, target_names=["Not Fraud (0)", "Fraud (1)"]))

    print("      Confusion matrix (rows = true label, columns = predicted label):")
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    cm_df = pd.DataFrame(cm, index=["Actual: Not Fraud", "Actual: Fraud"],
                          columns=["Predicted: Not Fraud", "Predicted: Fraud"])
    print(cm_df)

    # Feature importance - useful sanity check that the model is
    # learning something reasonable rather than noise.
    print("\n      Top 10 feature importances:")
    xgb_model = pipeline.named_steps["xgb"]
    feature_names = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    importances = pd.Series(xgb_model.feature_importances_, index=feature_names)
    print(importances.sort_values(ascending=False).head(10).to_string())

    print(
        "\n      NOTE: Fraud detection datasets are typically highly imbalanced.\n"
        "      Focus on balanced accuracy, ROC-AUC/PR-AUC, and the Fraud-class\n"
        "      recall/precision above rather than raw accuracy alone - a model\n"
        "      that just predicts 'not fraud' every time would still score\n"
        "      ~95% accuracy on this data while being useless."
    )


def main():
    df = load_data(DATA_PATH)
    X, y = prepare_features_and_target(df)

    print("[3/9] Splitting into train/val/test sets "
          "(64%/16%/20%, stratified by target) ...")
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y,
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=0.20, random_state=RANDOM_STATE, stratify=y_trainval,
    )
    print(f"      Train size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")

    scale_pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    print(f"      scale_pos_weight (neg/pos ratio in train): {scale_pos_weight:.2f}")

    if RUN_HYPERPARAMETER_SEARCH:
        best_params = search_hyperparameters(X_train, y_train, scale_pos_weight)
    else:
        print("[4/9] Skipping hyperparameter search (RUN_HYPERPARAMETER_SEARCH=False), "
              "using DEFAULT_PARAMS ...")
        best_params = dict(DEFAULT_PARAMS)

    pipeline = fit_final_model(X_train, y_train, X_val, y_val, best_params, scale_pos_weight)

    threshold = tune_threshold(pipeline, X_val, y_val)

    evaluate_model(pipeline, X_test, y_test, threshold)

    print(f"\n[9/9] Saving trained pipeline + threshold to {MODEL_PATH} ...")
    joblib.dump({"pipeline": pipeline, "threshold": threshold}, MODEL_PATH)
    print("      Done. Load model.joblib (a dict with 'pipeline' and 'threshold') "
          "to make predictions on new transactions:\n"
          "          bundle = joblib.load('model.joblib')\n"
          "          proba = bundle['pipeline'].predict_proba(new_X)[:, 1]\n"
          "          pred = (proba >= bundle['threshold']).astype(int)")


if __name__ == "__main__":
    main()
    