import { useAppState } from "../state/appState";
import { Donut } from "../components/charts/Donut";
import { severityInfo } from "../lib/severity";
import { clientAppTypeTally, coveragePercent, countByState } from "../lib/deriveInsights";

export function Insights() {
  const { policies, analysis, status, message } = useAppState();

  if (status === "loading" || status === "idle") return <div className="empty-state">Loading insights…</div>;
  if (status === "unauthenticated") return <div className="empty-state">Sign in to see insights for your tenant.</div>;
  if (status === "consent_required") return <div className="empty-state">Admin consent to Policy.Read.All is required.</div>;
  if (status === "error" || !analysis) return <div className="empty-state">{message ?? "Could not load insights."}</div>;

  const severityTally: Record<string, number> = {};
  for (const finding of analysis.findings) severityTally[finding.severity] = (severityTally[finding.severity] ?? 0) + 1;
  const severityColors = ["critical", "high", "medium", "low", "info"] as const;

  const ruleTally = { pass: 0, fail: 0, not_evaluable: 0 } as Record<string, number>;
  for (const rule of analysis.evaluated) ruleTally[rule.status] = (ruleTally[rule.status] ?? 0) + 1;

  const appTypeTally = clientAppTypeTally(policies);
  const coverage = coveragePercent(policies);
  const stateCounts = countByState(policies);

  return (
    <div className="stack">
      <p style={{ color: "#667085", fontSize: 13, margin: 0 }}>
        Everything on this page is derived in your browser from the same policy and analysis data shown elsewhere — no
        additional tenant data is read.
      </p>

      <div className="two-col-grid">
        <div className="card">
          <div className="card-header-title" style={{ marginBottom: 12 }}>
            Findings by severity
          </div>
          <Donut
            size={110}
            slices={severityColors.map((sev) => ({
              label: severityInfo(sev).label,
              value: severityTally[sev] ?? 0,
              color: severityInfo(sev).color,
            }))}
          />
        </div>

        <div className="card">
          <div className="card-header-title" style={{ marginBottom: 12 }}>
            Rule coverage
          </div>
          <Donut
            size={110}
            slices={[
              { label: "Pass", value: ruleTally.pass ?? 0, color: "#079455" },
              { label: "Fail", value: ruleTally.fail ?? 0, color: "#d92d20" },
              { label: "Not evaluable", value: ruleTally.not_evaluable ?? 0, color: "#98a2b3" },
            ]}
          />
        </div>
      </div>

      <div className="two-col-grid">
        <div className="card">
          <div className="card-header-title" style={{ marginBottom: 12 }}>
            Coverage
          </div>
          <div className="glance-row">
            <span className="glance-row-label">MFA coverage (enabled policies)</span>
            <span className="glance-row-value">{coverage.mfaCoveragePct}%</span>
          </div>
          <div className="glance-row">
            <span className="glance-row-label">Device compliance coverage</span>
            <span className="glance-row-value">{coverage.deviceComplianceCoveragePct}%</span>
          </div>
          <div className="glance-row">
            <span className="glance-row-label">Enforced vs. report-only</span>
            <span className="glance-row-value">
              {stateCounts.enabled} / {stateCounts.reportOnly}
            </span>
          </div>
        </div>

        <div className="card">
          <div className="card-header-title" style={{ marginBottom: 12 }}>
            Policies by client app type
          </div>
          {Object.keys(appTypeTally).length === 0 ? (
            <p style={{ color: "#667085", fontSize: 13 }}>No policies restrict client app type.</p>
          ) : (
            Object.entries(appTypeTally).map(([type, count]) => (
              <div className="glance-row" key={type}>
                <span className="glance-row-label">{type}</span>
                <span className="glance-row-value">{count}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
