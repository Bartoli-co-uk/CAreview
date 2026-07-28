import { severityInfo } from "../lib/severity";

export function SeverityBadge({ severity }: { severity: string }) {
  const info = severityInfo(severity);
  return (
    <span className="badge" style={{ background: `${info.color}1a`, color: info.color }}>
      <span className="badge-dot" style={{ background: info.color }} aria-hidden="true" />
      {info.label}
    </span>
  );
}
