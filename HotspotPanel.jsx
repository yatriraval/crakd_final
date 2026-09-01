export default function HotspotPanel({ hotspots, loading, error, scope }) {
  return (
    <div className="border border-panelLine rounded-sm p-5 bg-panel">
      <p className="font-data text-xs text-signal">LOCATION INTELLIGENCE</p>
      <p className="font-case text-xl text-paper mt-1">Likely cash-out points</p>
      <p className="text-xs text-muted mt-1">
        {scope?.state || scope?.city
          ? `Ranked by historical confirmed fraud in ${[scope.city, scope.state].filter(Boolean).join(", ")}.`
          : "Ranked by confirmed fraud across all historical cases."}
      </p>

      <div className="mt-4 space-y-2">
        {loading && <p className="text-sm text-muted">Loading historical fraud locations…</p>}
        {error && <p className="text-sm text-alert">Couldn't load hotspot data: {error}</p>}
        {!loading && !error && hotspots?.locations?.length === 0 && (
          <p className="text-sm text-muted">No historical fraud recorded for this scope.</p>
        )}
        {!loading &&
          !error &&
          hotspots?.locations?.map((loc, i) => (
            <div key={loc.location} className="flex items-center justify-between border-b border-panelLine/60 py-2 last:border-0">
              <div className="flex items-center gap-3">
                <span className="font-data text-xs text-muted w-4">{i + 1}</span>
                <span className="text-sm text-paper">{loc.location}</span>
              </div>
              <div className="text-right">
                <p className="font-data text-sm text-signal">{loc.fraud_count}</p>
                <p className="text-[10px] text-muted">{Math.round(loc.share_of_fraud * 1000) / 10}% of cases</p>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
