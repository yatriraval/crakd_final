console.log("MY APP JSX IS LOADING");
import { useEffect, useState } from "react";

import Header from "./Header.jsx";
import TransactionForm from "./TransactionForm.jsx";
import RiskResultPanel from "./RiskResultPanel.jsx";
import { predictTransaction, checkHealth } from "./api.js";

export default function App() {
  const [status, setStatus] = useState("checking");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [predictError, setPredictError] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(() => {
        setStatus("online");
      })
      .catch(() => {
        setStatus("offline");
      });
  }, []);

  async function handleSubmit(transaction) {
    setSubmitting(true);
    setPredictError(null);

    try {
      const data = await predictTransaction(transaction);
      setResult(data);
    } catch (err) {
      console.error("Prediction error:", err);
      setPredictError(err.message);
      setResult(null);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink font-body">
      <Header status={status} />

      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-8 px-8 py-8 lg:grid-cols-5">

        <section className="lg:col-span-3">
          <TransactionForm
            onSubmit={handleSubmit}
            submitting={submitting}
          />
        </section>

        <section className="lg:col-span-2">
          <RiskResultPanel
            result={result}
            error={predictError}
          />
        </section>

      </main>
    </div>
  );
}