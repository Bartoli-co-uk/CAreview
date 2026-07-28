import { useState } from "react";
import { useAppState } from "../state/appState";
import { SeverityBadge } from "../components/SeverityBadge";
import { sortBySeverity } from "../lib/severity";
import type { Severity } from "../api/types";

const FILTERS: (Severity | "all")[] = ["all", "critical", "high", "medium", "low", "info"];

const RULE_STATUS_LABEL: Record<string, { label: string; color: string }> = {
  pass: { label: "Pass", color: "#079455" },
  fail: { label: "Fail", color: "#d92d20" },
  not_evaluable: { label: "Not evaluable", color: "#98a2b3" },
};

export function Recommendations() {
  const { analysis, status, message } = useAppState();
  const [filter, setFilter] = useState<Severity | "all">("all");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  if (status === "loading" || status === "idle") return <div className="empty-state">Loading recommendations…</div>;
  if (status === "unauthenticated") return <div className="empty-state">Sign in to see recommendations for your tenant.</div>;
  if (status === "consent_required") return <div className="empty-state">Admin consent to Policy.Read.All is required.</div>;
  if (status === "error" || !analysis) return <div className="empty-state">{message ?? "Could not load recommendations."}</div>;

  const findings = sortBySeverity(analysis.findings).filter((f) => filter === "all" || f.severity === filter);

  function toggle(id: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="card-header-title" style={{ marginBottom: 12 }}>
          Findings ({analysis.findings.length})
        </div>
        <div className="severity-filter">
          {FILTERS.map((sev) => (
            <button key={sev} type="button" className={filter === sev ? "active" : undefined} onClick={() => setFilter(sev)}>
              {sev === "all" ? "All" : sev.charAt(0).toUpperCase() + sev.slice(1)}
            </button>
          ))}
        </div>
        {findings.length === 0 ? (
          <p style={{ color: "#667085", fontSize: 13 }}>No findings match this filter.</p>
        ) : (
          findings.map((finding) => {
            const isOpen = expanded.has(finding.id);
            return (
              <div key={finding.id} className="list-row" style={{ flexDirection: "column", alignItems: "stretch" }}>
                <button
                  type="button"
                  onClick={() => toggle(finding.id)}
                  style={{ background: "none", border: "none", padding: 0, textAlign: "left", cursor: "pointer" }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
                    <div className="list-row-main">
                      <p className="list-row-title">{finding.title}</p>
                      <p className="list-row-desc">{finding.rationale}</p>
                    </div>
                    <SeverityBadge severity={finding.severity} />
                  </div>
                </button>
                {isOpen && (
                  <div style={{ marginTop: 8, paddingLeft: 4, fontSize: 13 }}>
                    <p>
                      <strong>Remediation:</strong> {finding.remediation}
                    </p>
                    {finding.affectedPolicies.length > 0 && (
                      <p>
                        <strong>Affected policies:</strong> {finding.affectedPolicies.join(", ")}
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      <div className="card">
        <div className="card-header-title" style={{ marginBottom: 12 }}>
          Full rule coverage
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Rule</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {analysis.evaluated.map((rule) => {
              const info = RULE_STATUS_LABEL[rule.status] ?? { label: rule.status, color: "#98a2b3" };
              return (
                <tr key={rule.id}>
                  <td>{rule.title}</td>
                  <td>
                    <span className="badge" style={{ background: `${info.color}1a`, color: info.color }}>
                      {info.label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {analysis.notEvaluable.length > 0 && (
          <p style={{ fontSize: 12, color: "#667085", marginTop: 10 }}>
            Not evaluable in this tenant: {analysis.notEvaluable.join(", ")}
          </p>
        )}
      </div>
    </div>
  );
}
