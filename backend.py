from functools import lru_cache
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from predict import predict_fraud, load_model


# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="Cybercrime Predictive Analytics API",
    description=(
        "Backend API for cybercrime risk and "
        "cash-withdrawal location intelligence"
    ),
    version="2.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODEL
# ============================================================

# Load the trained fraud model once when the backend starts.
pipeline, threshold = load_model()

DATA_PATH = "Bank_Transaction_Fraud_Detection.csv"


# ============================================================
# REQUEST MODEL
# ============================================================

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


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Cybercrime predictive intelligence backend is running",
        "version": "2.0",
    }


# ============================================================
# LOAD HISTORICAL FRAUD DATA
# ============================================================

@lru_cache(maxsize=1)
def _load_fraud_history() -> pd.DataFrame:

    df = pd.read_csv(DATA_PATH)

    required = {
        "Is_Fraud",
        "Transaction_Location",
        "State",
        "City",
    }

    missing = required - set(df.columns)

    if missing:
        raise RuntimeError(
            f"Dataset is missing required columns: {sorted(missing)}"
        )

    # Keep only confirmed fraud cases.
    fraud_df = df[df["Is_Fraud"] == 1].copy()

    return fraud_df


# ============================================================
# LOCATION INTELLIGENCE
# ============================================================

def _rank_locations(
    state=None,
    city=None,
    top_n=5,
):
    """
    Rank historical fraud locations.

    IMPORTANT:
    The supplied dataset does not contain a true
    'next withdrawal location' target.

    Therefore these are historical fraud-location
    intelligence scores, NOT calibrated ML probabilities.
    """

    # Keep top_n within a reasonable range.
    top_n = max(1, min(int(top_n), 10))

    all_fraud = _load_fraud_history()

    scope = "nationwide"
    filtered = all_fraud

    # --------------------------------------------------------
    # First preference: exact city
    # --------------------------------------------------------

    if city:

        city_df = all_fraud[
            all_fraud["City"]
            .astype(str)
            .str.casefold()
            == str(city).casefold()
        ]

        if len(city_df) > 0:
            filtered = city_df
            scope = f"city: {city}"

    # --------------------------------------------------------
    # Second preference: exact state
    # --------------------------------------------------------

    if scope == "nationwide" and state:

        state_df = all_fraud[
            all_fraud["State"]
            .astype(str)
            .str.casefold()
            == str(state).casefold()
        ]

        if len(state_df) > 0:
            filtered = state_df
            scope = f"state: {state}"

    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if len(filtered) == 0:

        return {
            "scope": scope,
            "total_fraud_cases": 0,
            "locations": [],
        }

    # --------------------------------------------------------
    # Count fraud cases by location
    # --------------------------------------------------------

    counts = (
        filtered
        .groupby(
            [
                "Transaction_Location",
                "State",
                "City",
            ]
        )
        .size()
        .sort_values(ascending=False)
        .head(top_n)
    )

    total = int(counts.sum())

    locations = []

    # --------------------------------------------------------
    # Build ranked location results
    # --------------------------------------------------------

    for rank, ((location, loc_state, loc_city), count) in enumerate(
        counts.items(),
        start=1,
    ):

        share = float(count / total) if total else 0.0

        locations.append(
            {
                "rank": rank,
                "location": str(location),
                "state": str(loc_state),
                "city": str(loc_city),
                "historical_fraud_cases": int(count),

                # Historical intelligence score.
                "intelligence_score": round(
                    share * 100,
                    1,
                ),

                "score_label": f"{share * 100:.1f}%",
            }
        )

    return {
        "scope": scope,
        "total_fraud_cases": int(len(filtered)),
        "locations": locations,
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict(transaction: TransactionRequest):

    # Convert Pydantic request into a normal dictionary.
    transaction_data = transaction.model_dump()

    # --------------------------------------------------------
    # STAGE 1
    # Fraud risk prediction
    # --------------------------------------------------------

    fraud_result = predict_fraud(
        transaction_data,
        pipeline=pipeline,
        threshold=threshold,
    )

    # --------------------------------------------------------
    # STAGE 2
    # Historical location intelligence
    # --------------------------------------------------------

    location_result = _rank_locations(
        state=transaction.State,
        city=transaction.City,
        top_n=5,
    )

    # --------------------------------------------------------
    # Determine risk priority
    # --------------------------------------------------------

    if fraud_result["is_fraud"]:

        priority = "HIGH"

    elif fraud_result["fraud_probability"] >= max(
        0.25,
        threshold * 0.70,
    ):

        priority = "MEDIUM"

    else:

        priority = "LOW"

    # --------------------------------------------------------
    # Send result to frontend
    # --------------------------------------------------------

    return {
        **fraud_result,

        "risk_level": priority,

        "location_intelligence": location_result,

        "message": (
            "Top historical fraud locations associated "
            "with the submitted area are shown as "
            "cash-out intelligence candidates."
        ),
    }


# ============================================================
# HOTSPOTS ENDPOINT
# ============================================================

@app.get("/hotspots")
def hotspots(
    state: str | None = None,
    city: str | None = None,
    top_n: int = 5,
):

    """
    Return historical fraud-location intelligence
    for the dashboard.
    """

    return _rank_locations(
        state=state,
        city=city,
        top_n=top_n,
    )