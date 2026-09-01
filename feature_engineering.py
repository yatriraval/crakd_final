"""
feature_engineering.py
-----------------------
Defines which raw columns are safe to use, and turns raw
Transaction_Date / Transaction_Time strings into numeric/categorical
features for the XGBoost model.

CHANGED FROM THE SVM VERSION:
  - City, Bank_Branch, and Transaction_Location are no longer dropped.
    They were dropped previously because one-hot encoding + an
    RBF-kernel SVM does not handle high-cardinality columns well.
    XGBoost (with enable_categorical=True) splits directly on
    categorical columns without one-hot encoding, so these
    higher-cardinality location fields are now kept as useful
    features.
  - build_preprocessor() no longer does OneHotEncoder / StandardScaler.
    XGBoost's tree splits don't need scaled numeric features, and
    enable_categorical=True needs categorical columns to arrive as
    pandas 'category' dtype rather than one-hot columns. The
    preprocessor now just: imputes numeric columns (median) and casts
    categorical columns to 'category' dtype (imputing missing values
    with a literal "missing" category first, since XGBoost's
    categorical split handling expects no NaNs from an imputer step
    here - NaNs are still fine to leave as native missing values if
    you'd rather let XGBoost handle them itself, but we impute
    explicitly for consistency with the numeric side).
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------
# Column configuration
# ---------------------------------------------------------------

# The label we are trying to predict.
TARGET_COLUMN = "Is_Fraud"

# Columns we deliberately EXCLUDE from the model, and why:
#
#   Identifiers / PII (no genuine predictive value, and risky to use):
#     - Customer_ID, Customer_Name, Transaction_ID, Merchant_ID,
#       Customer_Contact, Customer_Email, Transaction_Description
#
#   Constant / zero-signal columns:
#     - Transaction_Currency (only 1 unique value in this dataset)
#
# NOTE: City, Bank_Branch, and Transaction_Location are NOT dropped
# here (unlike the old SVM version) - XGBoost handles high-cardinality
# categoricals natively via enable_categorical=True, so they're kept
# as features below.
DROPPED_COLUMNS = [
    "Customer_ID",
    "Customer_Name",
    "Transaction_ID",
    "Merchant_ID",
    "Customer_Contact",
    "Customer_Email",
    "Transaction_Description",
    "Transaction_Currency",
]

# Raw columns read from the CSV that we keep as model inputs
# (everything else, including TARGET_COLUMN and DROPPED_COLUMNS, is
# excluded before training).
RAW_INPUT_COLUMNS = [
    "Gender",
    "Age",
    "State",
    "City",
    "Bank_Branch",
    "Account_Type",
    "Transaction_Date",
    "Transaction_Time",
    "Transaction_Amount",
    "Transaction_Type",
    "Merchant_Category",
    "Account_Balance",
    "Transaction_Device",
    "Transaction_Location",
    "Device_Type",
]

# After feature engineering (see extract_features below), these are
# the final numeric and categorical columns fed into the pipeline.
NUMERIC_FEATURES = [
    "Age",
    "Transaction_Amount",
    "Account_Balance",
    "transaction_hour",
    "transaction_day_of_week",
    "transaction_day",
    "transaction_month",
    "is_weekend",
    "is_night",
    "amount_to_balance_ratio",
]

CATEGORICAL_FEATURES = [
    "Gender",
    "State",
    "City",
    "Bank_Branch",
    "Account_Type",
    "Transaction_Type",
    "Merchant_Category",
    "Transaction_Device",
    "Transaction_Location",
    "Device_Type",
]


def extract_features(X_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the raw input columns and engineers extra features from
    Transaction_Date and Transaction_Time, plus a couple of simple
    derived ratios. Returns a DataFrame containing exactly
    NUMERIC_FEATURES + CATEGORICAL_FEATURES.
    """
    X = X_raw.copy()

    # Transaction_Date is like "23-01-2025" (DD-MM-YYYY)
    dates = pd.to_datetime(X["Transaction_Date"], format="%d-%m-%Y", errors="coerce")
    # Transaction_Time is like "16:04:07" (HH:MM:SS)
    times = pd.to_timedelta(X["Transaction_Time"], errors="coerce")

    X["transaction_hour"] = (times.dt.components["hours"]).fillna(-1).astype(int)
    X["transaction_day_of_week"] = dates.dt.dayofweek.fillna(-1).astype(int)  # 0=Mon
    X["transaction_day"] = dates.dt.day.fillna(-1).astype(int)
    X["transaction_month"] = dates.dt.month.fillna(-1).astype(int)
    X["is_weekend"] = (X["transaction_day_of_week"] >= 5).astype(int)
    X["is_night"] = X["transaction_hour"].apply(
        lambda h: 1 if (h != -1 and (h >= 22 or h < 6)) else 0
    )

    # Simple derived ratio: how large is this transaction relative to
    # the account's balance? Guard against divide-by-zero.
    X["amount_to_balance_ratio"] = X["Transaction_Amount"] / X["Account_Balance"].replace(
        0, np.nan
    )
    X["amount_to_balance_ratio"] = X["amount_to_balance_ratio"].fillna(0)

    return X[NUMERIC_FEATURES + CATEGORICAL_FEATURES]


class _CategoricalCaster:
    """
    Simple transformer that:
      - imputes numeric columns with the median,
      - imputes categorical columns with a literal "missing" category,
      - casts categorical columns to pandas 'category' dtype so
        XGBoost's enable_categorical=True can split on them directly.

    Implemented as a small custom transformer (instead of
    ColumnTransformer + OneHotEncoder/StandardScaler, as in the SVM
    version) because scikit-learn's ColumnTransformer normally returns
    a plain numpy array, which would lose the 'category' dtype
    XGBoost needs. Keeping everything as a DataFrame preserves dtypes
    end-to-end.
    """

    def __init__(self):
        self.numeric_medians_ = None

    def fit(self, X: pd.DataFrame, y=None):
        self.numeric_medians_ = X[NUMERIC_FEATURES].median()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()

        X[NUMERIC_FEATURES] = X[NUMERIC_FEATURES].fillna(self.numeric_medians_)

        for col in CATEGORICAL_FEATURES:
            X[col] = X[col].astype("object").fillna("missing").astype("category")

        return X[NUMERIC_FEATURES + CATEGORICAL_FEATURES]

    def fit_transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

    # get_params/set_params so this plays nicely inside an sklearn
    # Pipeline (e.g. with RandomizedSearchCV / cloning) even though it
    # doesn't take any hyperparameters.
    def get_params(self, deep=True):
        return {}

    def set_params(self, **params):
        return self


def build_preprocessor():
    """
    Builds the preprocessing step used as the first stage of the
    sklearn Pipeline, ahead of the XGBoost classifier.

    Unlike the old SVM version, this does NOT one-hot encode
    categoricals or scale numeric features:
      - Tree-based models like XGBoost split on raw thresholds, so
        feature scaling has no effect on model quality.
      - enable_categorical=True lets XGBoost split directly on
        categorical columns, provided they arrive as pandas 'category'
        dtype - which is exactly what _CategoricalCaster produces.
    """
    return _CategoricalCaster()