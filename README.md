# SIH Location Intelligence Update

This update changes the application from a UI that primarily shows
"FLAGGED" fraud results into a two-stage predictive-intelligence flow:

1. Fraud-risk screening using the existing XGBoost model.
2. Historical fraud-location ranking to provide candidate cash-out locations.

## Important dataset limitation

The supplied CSV has `Is_Fraud` and `Transaction_Location`, but it does not
contain a labelled "next cash withdrawal location" target. Therefore the
location output is intentionally called **location intelligence** / an
**intelligence score**, not a calibrated probability or a claim that the
model knows the next ATM.

## Files to replace

- backend.py
- predict.py
- api.js
- App.jsx
- components/RiskResultPanel.jsx

Keep your existing:
- model.joblib
- Bank_Transaction_Fraud_Detection.csv
- feature_engineering.py
- TransactionForm.jsx
- Header.jsx

## Run backend

From the folder containing backend.py:

    uvicorn backend:app --reload

Expected:

    Application startup complete.

## Run frontend

Use your existing frontend command, usually:

    npm run dev

Then submit a transaction.

The result should show:

- HIGH / MEDIUM / LOW risk
- fraud risk score
- Likely Cash Withdrawal Locations
- ranked locations
- historical intelligence score
- number of historical fraud cases
- an investigator-facing intelligence note

## Recommended presentation wording

"Once a suspicious transaction is identified, the system ranks historical
fraud/cash-out hotspots associated with the complaint area to help investigators
prioritize locations for monitoring."

Do NOT claim that this dataset trains an ML model to predict the exact next ATM.
That would require complaint sequences with a known subsequent withdrawal
location.
