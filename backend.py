from functools import lru_cache

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from predict import predict_fraud, load_model


app = FastAPI(
    title="Cybercrime Predictive Analytics API",
    description="Backend API for the cybercrime analysis system",
    version="1.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Load model ONCE when backend starts
# ---------------------------------------------------------

pipeline, threshold = load_model()

# Path to the training data used to compute historical fraud
# hotspots. Point this at wherever the CSV lives in your deployment.
DATA_PATH = "Bank_Transaction_Fraud_Detection.csv"


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------

class TransactionRequest(BaseModel):

    Gender: str
    Age: int
    State: str
    City: str
    Bank_Branch: str
    Account_Type: str

    Transaction_Date: str
    Transaction_Time: str

    Transaction_Amount: float

    Transaction_Type: str
    Merchant_Category: str

    Account_Balance: float

    Transaction_Device: str
    Transaction_Location: str
    Device_Type: str


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "status": "online",
        "message": "Cybercrime ML backend is running",
    }


# ---------------------------------------------------------
# Prediction endpoint
# ---------------------------------------------------------

@app.post("/predict")
def predict(transaction: TransactionRequest):

    transaction_data = transaction.model_dump()

    result = predict_fraud(
        transaction_data,
        pipeline=pipeline,
        threshold=threshold,
    )

    return result


# ---------------------------------------------------------
# Location intelligence endpoint
# ---------------------------------------------------------
#
# NOTE: the XGBoost model above predicts whether a *given* transaction
# is fraudulent. It does not predict *where* the cash will be
# withdrawn - that would require a genuinely different model, trained
# with a location column (e.g. Transaction_Location) as the target
# instead of Is_Fraud, and would need to be trained on complaints
# where the withdrawal location is known only after the fact.
#
# As a practical stand-in that you can ship today, this endpoint
# surfaces the "actionable intelligence" the problem statement asks
# for in a defensible way: it ranks the locations that have
# historically had the most confirmed fraud, optionally filtered to
# the same state/city as the transaction just submitted. That turns
# "here's a transaction that looks fraudulent" into "here's where
# similar fraud has historically been cashed out" - useful to an
# investigator today, without pretending a classifier is doing
# geolocation forecasting it wasn't trained for.


@lru_cache(maxsize=1)
def _load_fraud_history() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df[df["Is_Fraud"] == 1]


@app.get("/hotspots")
def hotspots(state: str | None = None, city: str | None = None, top_n: int = 5):
    """
    Returns the top-N historical fraud locations, each with a fraud
    count and share of all confirmed fraud in the dataset. If `state`
    or `city` is supplied, results are filtered to that scope first -
    e.g. call with the State/City from a flagged transaction to get
    "likely cash-out points near this transaction" instead of a
    nationwide ranking.
    """
    fraud_df = _load_fraud_history()

    if state:
        fraud_df = fraud_df[fraud_df["State"].str.lower() == state.lower()]
    if city:
        fraud_df = fraud_df[fraud_df["City"].str.lower() == city.lower()]

    total = len(fraud_df)
    if total == 0:
        return {"scope": {"state": state, "city": city}, "total_fraud_cases": 0, "locations": []}

    counts = (
        fraud_df.groupby(["Transaction_Location", "State", "City"])
        .size()
        .sort_values(ascending=False)
        .head(top_n)
    )

    locations = [
        {
            "location": location,
            "state": loc_state,
            "city": loc_city,
            "fraud_count": int(count),
            "share_of_fraud": round(count / total, 4),
        }
        for (location, loc_state, loc_city), count in counts.items()
    ]

    return {
        "scope": {"state": state, "city": city},
        "total_fraud_cases": total,
        "locations": locations,
    }
