import type { PolicyState } from "../api/types";

const STATE_INFO: Record<PolicyState, { label: string; color: string }> = {
  enabled: { label: "Enabled", color: "#079455" },
  enabledForReportingButNotEnforced: { label: "Report-only", color: "#1570ef" },
  disabled: { label: "Disabled", color: "#98a2b3" },
};

export function StatusBadge({ state }: { state: string }) {
  const info = STATE_INFO[state as PolicyState] ?? { label: state, color: "#98a2b3" };
  return (
    <span className="badge" style={{ background: `${info.color}1a`, color: info.color }}>
      <span className="badge-dot" style={{ background: info.color }} aria-hidden="true" />
      {info.label}
    </span>
  );
}
