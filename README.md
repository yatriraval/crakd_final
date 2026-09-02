# CRAKD — Predictive Cybercrime Location Intelligence

**Development of a Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance, Enabling Generation of Actionable Intelligence for Timely and Proactive Cybercrime Intervention.**

Built for Smart India Hackathon (SIH).

## Problem Statement

Cybercrime complaints (UPI fraud, phishing, card fraud, etc.) are usually investigated *after* the money has already been withdrawn, by which point the trail has gone cold. Investigators need a way to act **while there's still a window to intervene** — flagging suspicious transactions early and pointing them toward the locations most likely to be used for cash-out, based on historical fraud patterns in the area.

CRAKD is a two-stage predictive-intelligence tool that helps close this gap:

1. **Fraud-risk screening** — an XGBoost model scores an incoming transaction as HIGH / MEDIUM / LOW risk.
2. **Location intelligence** — for flagged transactions, the system ranks nearby locations by historical fraud/cash-out activity, giving investigators a prioritized list of places to monitor.

> **Note on scope:** The dataset used contains fraud labels and transaction locations, but does not contain labelled "next withdrawal location" sequences. Because of this, location output is presented as an **intelligence score** derived from historical hotspot ranking — not a calibrated prediction of the exact next ATM/location. This is intentional and reflects an honest reading of what the data can support.

## How It Works

1. A transaction is submitted through the frontend form.
2. The backend engineers features from the transaction and runs them through a trained XGBoost classifier to produce a fraud risk score (HIGH / MEDIUM / LOW).
3. If the transaction is flagged, the backend cross-references historical fraud records in the same area and ranks candidate cash-out locations by:
   - Historical intelligence score
   - Number of past fraud cases at that location
4. The frontend displays the risk verdict alongside a ranked list of likely locations and an investigator-facing note, so the output is something an analyst can act on immediately.

## Tech Stack

**Backend / ML**
- Python
- FastAPI + Uvicorn (API server)
- XGBoost (fraud classification model)
- scikit-learn (metrics, preprocessing)
- pandas / NumPy (data handling)
- joblib (model serialization)
- Matplotlib (evaluation plots — ROC curve, confusion matrix)

**Frontend**
- React (Vite)
- Tailwind CSS

## Project Structure

```
├── backend.py                    # FastAPI server — risk scoring + location intelligence endpoint
├── predict.py                    # Model inference logic
├── train.py                      # Model training script
├── feature_engineering.py        # Feature extraction/transforms used by both training and inference
├── verify.py                     # Model verification/sanity checks
├── generate_plots.py             # Generates ROC curve & confusion matrix
├── model.joblib                  # Trained XGBoost model
├── Bank_Transaction_Fraud_Detection.csv   # Training/reference dataset
├── confusion_matrix.png
├── roc_curve.png
│
├── App.jsx                       # Root React component
├── main.jsx                      # React entry point
├── Header.jsx
├── TransactionForm.jsx           # Transaction input form
├── RiskResultPanel.jsx           # Displays risk verdict + score
├── HotspotPanel.jsx              # Displays ranked likely cash-out locations
├── api.js                        # Frontend → backend API calls
├── frontend_field_config.js
├── index.html / index.css
├── vite.config.js / tailwind.config.js / postcss.config.js
│
├── requirements.txt              # Python dependencies
└── package.json                  # Frontend dependencies
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup

```bash
pip install -r requirements.txt
uvicorn backend:app --reload
```

You should see:
```
Application startup complete.
```

The API will be running at `http://127.0.0.1:8000` by default.

### 2. Frontend Setup

In a separate terminal:

```bash
npm install
npm run dev
```

Open the local dev URL shown in the terminal, submit a transaction through the form, and the app will return:

- HIGH / MEDIUM / LOW fraud risk verdict
- Fraud risk score
- **Likely Cash Withdrawal Locations**
- Ranked historical hotspots
- Historical intelligence score
- Number of historical fraud cases at each location
- An investigator-facing intelligence note

### (Optional) Retrain the model

```bash
python train.py
python generate_plots.py   # regenerates confusion_matrix.png and roc_curve.png
python verify.py           # sanity-check the trained model
```

## Team

| Name | Role |
|---|---|
| Yatri Raval | Team Lead |
| Dhruven Mistry | ML & Data |
| Mana Patel | Frontend |
| Love Parekh | Frontend |
| Pratham Soni | Presentation |
| Vardhan Seth | Presentation |

## Disclaimer

This project is a hackathon prototype built for demonstration purposes. The fraud model and location intelligence scores are based on a limited, synthetic/sample dataset and are **not** validated for real-world law enforcement deployment.
