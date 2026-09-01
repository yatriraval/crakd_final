"""
generate_plots.py
------------------
Regenerates the confusion matrix and ROC curve from the CURRENT
trained model (model.joblib, produced by train.py's XGBoost pipeline
on Bank_Transaction_Fraud_Detection.csv) and the CURRENT held-out
test set.

Use this to replace any old confusion_matrix.png that was produced by
a previous SVM/Random-Forest run on a different dataset - that plot
no longer reflects this project and will look inconsistent (or plain
wrong) next to the rest of your slides.

Run with:
    python generate_plots.py
"""

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score

from feature_engineering import extract_features, RAW_INPUT_COLUMNS, TARGET_COLUMN

DATA_PATH = "Bank_Transaction_Fraud_Detection.csv"
MODEL_PATH = "model.joblib"
RANDOM_STATE = 42


def rebuild_test_split(df: pd.DataFrame):
    """
    Reproduces the exact same train/val/test split used in train.py
    (same random_state, same split ratios), so the test set here
    matches the one the saved model was actually evaluated on.
    """
    y = df[TARGET_COLUMN].copy()
    X = extract_features(df[RAW_INPUT_COLUMNS].copy())

    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y,
    )
    return X_test, y_test


def main():
    print("Loading model + threshold ...")
    bundle = joblib.load(MODEL_PATH)
    pipeline = bundle["pipeline"]

    # NOTE: bundle["threshold"] was chosen by maximizing F1 on the
    # validation set. Because this dataset has essentially no learnable
    # signal (see README), that F1-maximizing threshold degenerates to
    # an extreme value that predicts almost everything as one class
    # (not useful to look at on a slide). We use the standard 0.5
    # cutoff here instead, purely for a readable, presentable plot.
    threshold = 0.5

    print("Loading data and rebuilding the same held-out test split used in training ...")
    df = pd.read_csv(DATA_PATH)
    X_test, y_test = rebuild_test_split(df)

    print("Scoring test set ...")
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    # --- Confusion matrix ---
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Not Fraud", "Fraud"])
    ax.set_yticklabels(["Not Fraud", "Fraud"])
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(f"XGBoost Confusion Matrix (threshold={threshold:.2f})")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig("confusion_matrix.png", dpi=150)
    print("Saved confusion_matrix.png")

    # --- ROC curve ---
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)
    fig2, ax2 = plt.subplots(figsize=(5, 4.5))
    ax2.plot(fpr, tpr, label=f"XGBoost (AUC = {auc:.3f})", color="#1f6feb")
    ax2.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random guess (AUC = 0.50)")
    ax2.set_xlabel("False Positive Rate")
    ax2.set_ylabel("True Positive Rate")
    ax2.set_title("ROC Curve - XGBoost Fraud Classifier")
    ax2.legend(loc="lower right")
    fig2.tight_layout()
    fig2.savefig("roc_curve.png", dpi=150)
    print("Saved roc_curve.png")

    print(f"\nTest ROC-AUC: {auc:.4f}")


if __name__ == "__main__":
    main()
