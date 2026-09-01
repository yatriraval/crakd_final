import pandas as pd
import joblib

from feature_engineering import extract_features

MODEL_PATH = "model.joblib"


def load_model(model_path=MODEL_PATH):
    """Load the trained pipeline and fraud threshold."""
    bundle = joblib.load(model_path)

    pipeline = bundle["pipeline"]
    threshold = bundle["threshold"]

    return pipeline, threshold


def predict_fraud(transaction, pipeline=None, threshold=None):
    """
    Predict whether a bank transaction is fraudulent.
    transaction should contain the same raw fields used during training.
    """

    if pipeline is None or threshold is None:
        pipeline, threshold = load_model()

    # Convert one transaction dictionary into a one-row DataFrame
    input_df = pd.DataFrame([transaction])

    # Apply the SAME feature engineering used during training
    input_features = extract_features(input_df)

    # Get fraud probability
    fraud_probability = pipeline.predict_proba(input_features)[0, 1]

    prediction = int(fraud_probability >= threshold)

    return {
        "prediction": prediction,
        "is_fraud": bool(prediction),
        "fraud_probability": round(float(fraud_probability), 4),
        "threshold": round(float(threshold), 4),
    }


if __name__ == "__main__":

    # Take one real transaction from the dataset for testing
    DATA_PATH = "Bank_Transaction_Fraud_Detection.csv"

    df = pd.read_csv(DATA_PATH)

    sample_transaction = df.iloc[0][[
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
    ]].to_dict()

    print("Loading trained model...")

    pipeline, threshold = load_model()

    result = predict_fraud(
        sample_transaction,
        pipeline=pipeline,
        threshold=threshold
    )

    print("\nPrediction:")
    print("Fraud:", result["is_fraud"])
    print("Fraud probability:", result["fraud_probability"])
    print("Decision threshold:", result["threshold"])
    print("Fraud probability:", result["fraud_probability"])
    print("Decision threshold:", result["threshold"])