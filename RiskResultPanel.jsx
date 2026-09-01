export default function RiskResultPanel({ result, error }) {
  if (error) {
    return (
      <section className="rounded-xl border border-alert/30 bg-alert/5 p-6">

        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-alert/10">
            <span className="text-alert">!</span>
          </div>

          <div>
            <p className="font-data text-[10px] uppercase tracking-[0.2em] text-alert">
              Analysis failed
            </p>

            <h2 className="mt-1 text-lg font-semibold text-paper">
              Unable to complete screening
            </h2>
          </div>
        </div>

        <p className="rounded-lg border border-alert/20 bg-ink/50 p-4 text-sm leading-6 text-muted">
          {error}
        </p>

      </section>
    );
  }

  if (!result) {
    return (
      <section className="rounded-xl border border-panelLine bg-panel/40 p-6">

        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-signal/20 bg-signal/10">
            <span className="font-data text-sm text-signal">
              AI
            </span>
          </div>

          <div>
            <p className="font-data text-[10px] uppercase tracking-[0.2em] text-signal">
              Predictive Intelligence
            </p>

            <h2 className="mt-1 text-lg font-semibold text-paper">
              Awaiting transaction
            </h2>
          </div>
        </div>

        <div className="rounded-lg border border-dashed border-panelLine p-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-panelLine">
            <span className="text-xl text-muted">
              ⌁
            </span>
          </div>

          <p className="text-sm text-muted">
            Submit a transaction to generate fraud-risk and
            withdrawal-location intelligence.
          </p>
        </div>

      </section>
    );
  }

  const locations =
    result.location_intelligence?.locations || [];

  const probability =
    result.fraud_probability != null
      ? result.fraud_probability * 100
      : null;

  const riskLevel =
    result.risk_level || "UNKNOWN";

  const riskClass =
    riskLevel === "HIGH"
      ? "border-alert/40 bg-alert/10 text-alert"
      : riskLevel === "MEDIUM"
      ? "border-signal/40 bg-signal/10 text-signal"
      : "border-clear/40 bg-clear/10 text-clear";

  const scoreBar =
    riskLevel === "HIGH"
      ? "bg-alert"
      : riskLevel === "MEDIUM"
      ? "bg-signal"
      : "bg-clear";

  return (
    <section className="space-y-5">

      {/* RISK CARD */}
      <div className="rounded-xl border border-panelLine bg-panel/50 p-6">

        <div className="flex items-start justify-between gap-4">

          <div>
            <p className="font-data text-[10px] uppercase tracking-[0.2em] text-muted">
              Predictive Intelligence
            </p>

            <h2 className="mt-1 text-lg font-semibold text-paper">
              Fraud Risk Assessment
            </h2>
          </div>

          <span
            className={`rounded-full border px-3 py-1 font-data text-xs font-bold tracking-wider ${riskClass}`}
          >
            {riskLevel} RISK
          </span>

        </div>

        <div className="mt-8">

          <div className="flex items-end justify-between">
            <span className="text-sm text-muted">
              Fraud risk score
            </span>

            <span className="font-data text-3xl font-bold text-paper">
              {probability != null
                ? `${probability.toFixed(1)}%`
                : "N/A"}
            </span>
          </div>

          <div className="mt-3 h-2 overflow-hidden rounded-full bg-ink">
            <div
              className={`h-full rounded-full transition-all duration-700 ${scoreBar}`}
              style={{
                width: `${Math.min(probability || 0, 100)}%`,
              }}
            />
          </div>

          <div className="mt-2 flex justify-between text-[10px] text-muted">
            <span>LOW</span>
            <span>MEDIUM</span>
            <span>HIGH</span>
          </div>

        </div>
      </div>

      {/* LOCATION INTELLIGENCE */}
      <div className="rounded-xl border border-panelLine bg-panel/50 p-6">

        <div className="mb-5">
          <p className="font-data text-[10px] uppercase tracking-[0.2em] text-signal">
            Historical Intelligence
          </p>

          <h2 className="mt-1 text-lg font-semibold text-paper">
            Likely Cash Withdrawal Locations
          </h2>

          <p className="mt-2 text-xs text-muted">
            Scope:{" "}
            <span className="text-paper">
              {result.location_intelligence?.scope || "historical"}
            </span>
          </p>
        </div>

        {locations.length === 0 ? (
          <div className="rounded-lg border border-dashed border-panelLine p-6 text-center">
            <p className="text-sm text-muted">
              No historical fraud locations were found.
            </p>
          </div>
        ) : (
          <div className="space-y-3">

            {locations.map((item, index) => (
              <div
                key={index}
                className="rounded-lg border border-panelLine bg-ink/50 p-4 transition hover:border-signal/30"
              >

                <div className="flex items-start justify-between gap-3">

                  <div className="flex gap-3">

                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-signal/10 font-data text-xs font-bold text-signal">
                      {item.rank || index + 1}
                    </div>

                    <div>
                      <h3 className="font-semibold text-paper">
                        {item.location || "Unknown location"}
                      </h3>

                      <p className="mt-1 text-xs text-muted">
                        {item.city || ""}, {item.state || ""}
                      </p>
                    </div>

                  </div>

                  <span className="font-data text-sm font-bold text-signal">
                    {item.score_label ||
                      `${((item.intelligence_score || item.score || 0)).toFixed(1)}%`}
                  </span>

                </div>

                <div className="mt-4 flex items-center justify-between border-t border-panelLine pt-3 text-xs">
                  <span className="text-muted">
                    Historical fraud cases
                  </span>

                  <span className="font-data font-semibold text-paper">
                    {item.historical_fraud_cases || 0}
                  </span>
                </div>

              </div>
            ))}

          </div>
        )}

        <p className="mt-5 text-[10px] leading-5 text-muted">
          These locations represent historical fraud-location intelligence
          candidates. They are not guaranteed future withdrawal locations.
        </p>

      </div>

    </section>
  );
}