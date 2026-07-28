import { useAppState } from "../state/appState";
import type { Page } from "../state/navigation";
import { Gauge } from "../components/charts/Gauge";
import { Donut } from "../components/charts/Donut";
import { SeverityBadge } from "../components/SeverityBadge";
import { StatusBadge } from "../components/StatusBadge";
import { SummaryCard } from "../components/SummaryCard";
import { InfoTooltip } from "../components/InfoTooltip";
import { ShieldIcon, LightbulbIcon, DocumentIcon, ChartIcon, AlertTriangleIcon, ChevronRightIcon } from "../components/icons";
import { scoreBand, sortBySeverity } from "../lib/severity";
import { countByState, glanceCounts, derivedPolicyType } from "../lib/deriveInsights";

interface OverviewProps {
  onNavigate: (page: Page) => void;
}

export function Overview({ onNavigate }: OverviewProps) {
  const { policies, analysis, status, message, lastRefreshed } = useAppState();

  if (status === "loading" || status === "idle") {
    return <div className="empty-state">Loading analysis…</div>;
  }
  if (status === "unauthenticated") {
    return <div className="empty-state">Sign in to see your tenant's analysis.</div>;
  }
  if (status === "consent_required") {
    return <div className="empty-state">Admin consent to Policy.Read.All is required for this tenant.{message ? ` ${message}` : ""}</div>;
  }
  if (status === "error" || !analysis) {
    return <div className="empty-state">{message ?? "Could not load analysis."}</div>;
  }
  if (!policies.length) {
    return <div className="empty-state">No Conditional Access policies were found in this tenant.</div>;
  }

  const counts = countByState(policies);
  const glance = glanceCounts(policies);
  const severityTally: Record<string, number> = {};
  for (const finding of analysis.findings) {
    severityTally[finding.severity] = (severityTally[finding.severity] ?? 0) + 1;
  }
  const highPriority = (severityTally.critical ?? 0) + (severityTally.high ?? 0);
  const mediumPriority = severityTally.medium ?? 0;
  const topFindings = sortBySeverity(analysis.findings).slice(0, 5);
  const band = scoreBand(analysis.score);

  return (
    <div>
      <div className="summary-grid">
        <SummaryCard icon={<ShieldIcon color="#1f4287" />} title="Overall Security Score">
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <Gauge score={analysis.score} size={88} />
            <div>
              <p style={{ margin: 0, fontWeight: 600, color: band.color }}>{band.label}</p>
              <p style={{ margin: "4px 0 0", fontSize: 13, color: "#667085" }}>
                {analysis.scoreIsHeuristic ? "Heuristic score — not a compliance certification." : ""}
              </p>
            </div>
          </div>
        </SummaryCard>

        <SummaryCard icon={<LightbulbIcon color="#dc6803" />} title="Recommendations">
          <p style={{ margin: "0 0 4px", fontSize: 24, fontWeight: 700, color: "#d92d20" }}>
            {highPriority} <span style={{ fontSize: 13, fontWeight: 400, color: "#667085" }}>High priority</span>
          </p>
          <p style={{ margin: 0, fontSize: 24, fontWeight: 700, color: "#dc6803" }}>
            {mediumPriority} <span style={{ fontSize: 13, fontWeight: 400, color: "#667085" }}>Medium priority</span>
          </p>
          <button type="button" className="link-plain" style={{ marginTop: 10 }} onClick={() => onNavigate("recommendations")}>
            View recommendations <ChevronRightIcon width={14} height={14} />
          </button>
        </SummaryCard>

        <SummaryCard icon={<DocumentIcon color="#1f4287" />} title="Conditional Access Policies">
          <p style={{ margin: "0 0 4px", fontSize: 24, fontWeight: 700 }}>
            {counts.total} <span style={{ fontSize: 13, fontWeight: 400, color: "#667085" }}>Total policies</span>
          </p>
          <div style={{ display: "flex", gap: 16, fontSize: 13, color: "#667085", marginTop: 6 }}>
            <span>{counts.enabled} Enabled</span>
            <span>{counts.reportOnly} Report-only</span>
          </div>
          <button type="button" className="link-plain" style={{ marginTop: 10 }} onClick={() => onNavigate("policies")}>
            View all policies <ChevronRightIcon width={14} height={14} />
          </button>
        </SummaryCard>

        <SummaryCard icon={<ChartIcon color="#1f4287" />} title="Policies by Status">
          <Donut
            size={88}
            slices={[
              { label: "Enabled", value: counts.enabled, color: "#079455" },
              { label: "Report-only", value: counts.reportOnly, color: "#1570ef" },
              { label: "Disabled", value: counts.disabled, color: "#98a2b3" },
            ]}
          />
        </SummaryCard>
      </div>

      <div className="two-col-grid">
        <div className="card">
          <div className="card-header">
            <div className="card-header-title">
              <AlertTriangleIcon color="#dc6803" />
              Top Recommendations
            </div>
            <button type="button" className="link-plain" onClick={() => onNavigate("recommendations")}>
              View all <ChevronRightIcon width={14} height={14} />
            </button>
          </div>
          {topFindings.length === 0 ? (
            <p style={{ color: "#667085", fontSize: 13 }}>No open recommendations — nice work.</p>
          ) : (
            topFindings.map((finding) => (
              <div className="list-row" key={finding.id}>
                <div className="list-row-main">
                  <p className="list-row-title">{finding.title}</p>
                  <p className="list-row-desc">{finding.rationale}</p>
                </div>
                <SeverityBadge severity={finding.severity} />
              </div>
            ))
          )}
        </div>

        <div className="card">
          <div className="card-header-title" style={{ marginBottom: 4 }}>
            Policies at a Glance
          </div>
          <div className="glance-row">
            <span className="glance-row-label">User-based policies</span>
            <span className="glance-row-value">{glance.userBased}</span>
          </div>
          <div className="glance-row">
            <span className="glance-row-label">Group-based policies</span>
            <span className="glance-row-value">{glance.groupBased}</span>
          </div>
          <div className="glance-row">
            <span className="glance-row-label">Cloud app policies</span>
            <span className="glance-row-value">{glance.cloudAppPolicies}</span>
          </div>
          <div className="glance-row">
            <span className="glance-row-label">
              Authentication strength (MFA)
              <InfoTooltip text="Policies whose grant controls require multi-factor authentication." />
            </span>
            <span className="glance-row-value">{glance.authStrength}</span>
          </div>
          <div className="glance-row">
            <span className="glance-row-label">
              Device compliance policies
              <InfoTooltip text="Policies requiring a compliant or hybrid Azure AD-joined device." />
            </span>
            <span className="glance-row-value">{glance.deviceCompliance}</span>
          </div>
          <button type="button" className="link-plain" style={{ marginTop: 10 }} onClick={() => onNavigate("explorer")}>
            Explore all policies <ChevronRightIcon width={14} height={14} />
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-header-title">Recent Policies</div>
          <button type="button" className="link-plain" onClick={() => onNavigate("policies")}>
            View all policies <ChevronRightIcon width={14} height={14} />
          </button>
        </div>
        <div style={{ overflowX: "auto" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Policy Name</th>
                <th>Status</th>
                <th>Type</th>
                <th>Users/Groups</th>
                <th>Applications</th>
              </tr>
            </thead>
            <tbody>
              {policies.slice(0, 5).map((policy) => {
                const userCount = policy.conditions.includeUsers.length + policy.conditions.includeGroups.length + policy.conditions.includeRoles.length;
                const apps = policy.conditions.includeApplications;
                return (
                  <tr key={policy.id}>
                    <td>{policy.displayName || policy.id}</td>
                    <td>
                      <StatusBadge state={policy.state} />
                    </td>
                    <td>{derivedPolicyType(policy)}</td>
                    <td>{userCount || "—"}</td>
                    <td>{apps.length ? (apps.includes("All") ? "All cloud apps" : `${apps.length} app(s)`) : "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <p className="footnote">
        Data is from Microsoft Entra ID.
        {lastRefreshed ? ` Last refreshed on this machine at ${lastRefreshed.toLocaleString()}.` : ""}
        {analysis.scoreIsHeuristic ? " Score is heuristic, not a compliance certification." : ""}
      </p>
    </div>
  );
}
