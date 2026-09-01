export default function Header({ status }) {
  const statusColor =
    status === "online" ? "bg-clear" : status === "checking" ? "bg-signal" : "bg-alert";
  const statusLabel =
    status === "online" ? "Model service online" : status === "checking" ? "Connecting…" : "Model service unreachable";

  return (
    <header className="border-b border-panelLine px-8 py-6 flex items-baseline justify-between">
      <div>
        <p className="font-data text-xs tracking-wide text-muted">CASE INTAKE / FRAUD TRIAGE</p>
        <h1 className="font-case text-3xl text-paper mt-1">Cybercrime Intelligence Console</h1>
        <p className="text-muted text-sm mt-1 max-w-xl">
          Screens a bank transaction for fraud risk, then cross-references it against
          historical confirmed fraud to surface where cash has previously been withdrawn
          in similar cases.
        </p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <span className={`h-2 w-2 rounded-full ${statusColor}`} />
        <span className="font-data text-xs text-muted">{statusLabel}</span>
      </div>
    </header>
  );
}
