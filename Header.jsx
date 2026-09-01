export default function Header({ status }) {
  const statusConfig = {
    online: {
      dot: "bg-clear",
      text: "Model service online",
    },
    checking: {
      dot: "bg-signal animate-pulse",
      text: "Connecting to model service…",
    },
    offline: {
      dot: "bg-alert",
      text: "Model service unreachable",
    },
  };

  const current = statusConfig[status] || statusConfig.checking;

  return (
    <header className="border-b border-panelLine bg-ink px-5 py-6 lg:px-8">

      <div className="mx-auto flex max-w-7xl flex-col gap-5 md:flex-row md:items-center md:justify-between">

        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-signal/30 bg-signal/10">
              <span className="font-data text-lg text-signal">
                CI
              </span>
            </div>

            <div>
              <p className="font-data text-[10px] uppercase tracking-[0.3em] text-muted">
                CASE INTAKE / FRAUD TRIAGE
              </p>

              <h1 className="font-case text-2xl font-bold tracking-tight text-paper md:text-3xl">
                Cybercrime Intelligence Console
              </h1>
            </div>
          </div>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
            Screens bank transactions for fraud risk and cross-references
            historical confirmed fraud to identify relevant withdrawal
            locations.
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-3 rounded-full border border-panelLine bg-panel px-4 py-2">
          <span className={`h-2.5 w-2.5 rounded-full ${current.dot}`} />

          <span className="font-data text-xs text-muted">
            {current.text}
          </span>
        </div>

      </div>
    </header>
  );
}