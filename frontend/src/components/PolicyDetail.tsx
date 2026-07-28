import type { Policy } from "../api/types";
import { StatusBadge } from "./StatusBadge";

function joinOrNone(values: string[]): string {
  return values.length ? values.join(", ") : "(none)";
}

// Componentized version of the "Users → Conditions → Apps → Controls" flow
// card the previous vanilla UI rendered in web/app.js's renderPolicyCard.
export function PolicyDetail({ policy, onBack }: { policy: Policy; onBack?: () => void }) {
  const c = policy.conditions;
  const users = [...c.includeUsers, ...c.includeRoles.map((r) => `role:${r}`)];
  const excluded = [...c.excludeUsers, ...c.excludeGroups, ...c.excludeRoles];
  const conditionParts: string[] = [];
  if (c.clientAppTypes.length) conditionParts.push(`client apps: ${c.clientAppTypes.join(", ")}`);
  if (c.includeLocations.length) conditionParts.push(`locations: ${c.includeLocations.join(", ")}`);
  if (c.signInRiskLevels.length) conditionParts.push(`sign-in risk: ${c.signInRiskLevels.join(", ")}`);
  if (c.userRiskLevels.length) conditionParts.push(`user risk: ${c.userRiskLevels.join(", ")}`);
  if (excluded.length) conditionParts.push(`excludes ${excluded.length} principal(s)`);

  return (
    <div className="card">
      {onBack && (
        <button type="button" className="link-plain" onClick={onBack} style={{ marginBottom: 12 }}>
          ← Back
        </button>
      )}
      <div className="card-header">
        <h3 style={{ margin: 0 }}>{policy.displayName || policy.id}</h3>
        <StatusBadge state={policy.state} />
      </div>

      <div className="detail-section">
        <h4>Users</h4>
        <div className="tag-list">
          {users.length ? users.map((u) => <span className="tag" key={u}>{u}</span>) : <span className="tag">(none)</span>}
        </div>
      </div>

      <div className="detail-section">
        <h4>Conditions</h4>
        <p style={{ margin: 0, fontSize: 13 }}>{conditionParts.length ? conditionParts.join("; ") : "(none)"}</p>
      </div>

      <div className="detail-section">
        <h4>Applications</h4>
        <div className="tag-list">
          {c.includeApplications.length ? (
            c.includeApplications.map((a) => <span className="tag" key={a}>{a}</span>)
          ) : (
            <span className="tag">(none)</span>
          )}
        </div>
      </div>

      <div className="detail-section">
        <h4>Grant controls</h4>
        <p style={{ margin: 0, fontSize: 13 }}>
          {policy.grantControls.operator} of: {joinOrNone(policy.grantControls.builtInControls)}
        </p>
      </div>

      <div className="detail-section">
        <h4>Session controls</h4>
        <div className="tag-list">
          {policy.sessionControls.length ? (
            policy.sessionControls.map((s) => <span className="tag" key={s}>{s}</span>)
          ) : (
            <span className="tag">(none)</span>
          )}
        </div>
      </div>
    </div>
  );
}
