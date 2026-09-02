import React, { useEffect, useState } from "react";
import TransactionForm from "./TransactionForm.jsx";
import RiskResultPanel from "./RiskResultPanel.jsx";
import { predictTransaction, checkHealth } from "./api.js";
import "./index.css";

function App() {
  const [status, setStatus] = useState("checking");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkHealth()
      .then(() => setStatus("online"))
      .catch(() => setStatus("offline"));
  }, []);

  const analyze = async (transaction) => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await predictTransaction(transaction);
      setResult(data);
    } catch (err) {
      setError(err.message || "Backend connection failed");
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>CRAKD</h1>
          <p>CYBERCRIME PREDICTIVE INTELLIGENCE</p>
        </div>

        <div className="status">
          <span className={status === "online" ? "green" : "red"}>
            ●
          </span>
          {status === "online" ? " SYSTEM ONLINE" : " SYSTEM OFFLINE"}
        </div>
      </header>

      <main>
        <section className="hero">
          <p className="tag">SMART INDIA HACKATHON 2026</p>
          <h2>Predictive Intelligence Console</h2>
          <p>
            Analyze suspicious transactions and identify historical
            cash-out locations to support proactive cybercrime intervention.
          </p>
        </section>

        <div className="stats">
          <div>
            <small>SCREENINGS</small>
            <strong>1,284</strong>
          </div>

          <div>
            <small>HIGH RISK CASES</small>
            <strong>146</strong>
          </div>

          <div>
            <small>HOTSPOTS</small>
            <strong>37</strong>
          </div>

          <div>
            <small>AVG RESPONSE</small>
            <strong>1.8s</strong>
          </div>
        </div>

        <div className="grid">
          <section className="card">
            <h3>Transaction Analysis</h3>
            <p className="muted">
              Enter transaction information for ML-based risk screening.
            </p>

            <TransactionForm
              onSubmit={analyze}
              submitting={loading}
            />
          </section>

          <section className="card">
            <h3>Risk Intelligence</h3>

            {loading && (
              <div className="waiting">
                <div className="loader"></div>
                <h4>ANALYZING TRANSACTION</h4>
                <p>Running predictive model...</p>
              </div>
            )}

            {!loading && error && (
              <div className="error">
                <h4>Backend Error</h4>
                <p>{error}</p>
                <p>Make sure uvicorn is running.</p>
              </div>
            )}

            {!loading && !error && !result && (
              <div className="waiting">
                <div className="big-icon">⌁</div>
                <h4>AWAITING ANALYSIS</h4>
                <p>
                  Submit transaction details to generate
                  fraud probability and location intelligence.
                </p>
              </div>
            )}

            {!loading && result && (
              <RiskResultPanel result={result} />
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;