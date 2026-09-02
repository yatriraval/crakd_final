import React from "react";

function RiskResultPanel({ result }) {
  const fraudProbability =
    Number(result?.fraud_probability || 0) * 100;

  const locations =
    result?.location_intelligence?.locations || [];

  const riskLevel =
    result?.risk_level || "UNKNOWN";

  const getRiskClass = () => {
    const level = String(riskLevel).toLowerCase();

    if (level.includes("high")) return "high";
    if (level.includes("medium")) return "medium";
    if (level.includes("low")) return "low";

    return "unknown";
  };

  const riskClass = getRiskClass();

  return (
    <div className="results">
      {/* Main Risk Card */}
      <div className={`risk-card ${riskClass}`}>
        <div className="risk-card-top">
          <div>
            <span className="section-label">
              FRAUD RISK ASSESSMENT
            </span>

            <h3>
              {riskLevel}
            </h3>
          </div>

          <div className="risk-icon">
            {riskClass === "high"
              ? "!"
              : riskClass === "medium"
              ? "△"
              : "✓"}
          </div>
        </div>

        <div className="probability">
          <div className="probability-value">
            {fraudProbability.toFixed(1)}
            <span>%</span>
          </div>

          <div className="probability-label">
            FRAUD PROBABILITY
          </div>
        </div>

        <div className="probability-bar">
          <div
            style={{
              width: `${Math.min(
                fraudProbability,
                100
              )}%`,
            }}
          />
        </div>

        <div className="risk-footer">
          <span>
            MODEL ASSESSMENT
          </span>

          <strong>
            {riskClass === "high"
              ? "IMMEDIATE REVIEW"
              : riskClass === "medium"
              ? "REVIEW RECOMMENDED"
              : "LOW CONCERN"}
          </strong>
        </div>
      </div>

      {/* Location Intelligence */}
      <div className="location-section">
        <div className="location-heading">
          <div>
            <span className="section-label">
              LOCATION INTELLIGENCE
            </span>

            <h3>
              Historical Cash-Out Hotspots
            </h3>
          </div>

          <span className="location-count">
            {locations.length} LOCATIONS
          </span>
        </div>

        {locations.length === 0 ? (
          <div className="no-locations">
            No historical location intelligence
            available for this transaction.
          </div>
        ) : (
          <div className="location-list">
            {locations
              .slice(0, 3)
              .map((location, index) => {
                const score =
                  Number(
                    location.intelligence_score ??
                      location.score ??
                      0
                  );

                return (
                  <div
                    className="location-card"
                    key={`${location.location}-${index}`}
                  >
                    <div className="rank">
                      {String(
                        location.rank ?? index + 1
                      ).padStart(2, "0")}
                    </div>

                    <div className="location-main">
                      <div className="location-name">
                        {location.location ||
                          "Unknown Location"}
                      </div>

                      <div className="location-meta">
                        {location.city &&
                          `${location.city}`}

                        {location.state &&
                          `, ${location.state}`}
                      </div>

                      <div className="location-bar">
                        <div
                          style={{
                            width: `${Math.min(
                              score,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="location-score">
                      <strong>
                        {location.score_label ??
                          `${score.toFixed(0)}%`}
                      </strong>

                      <span>
                        {location.historical_fraud_cases ??
                          0}{" "}
                        CASES
                      </span>
                    </div>
                  </div>
                );
              })}
          </div>
        )}

        <div className="intelligence-disclaimer">
          <span>ⓘ</span>

          <p>
            These locations represent historical
            transaction intelligence. They should not
            be interpreted as guaranteed future
            withdrawal locations.
          </p>
        </div>
      </div>
    </div>
  );
}

export default RiskResultPanel;