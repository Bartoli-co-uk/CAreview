import { useMemo, useState } from "react";
import { useAppState } from "../state/appState";
import { StatusBadge } from "../components/StatusBadge";
import { PolicyDetail } from "../components/PolicyDetail";
import { ADMIN_ROLE_TEMPLATE_IDS, derivedPolicyType } from "../lib/deriveInsights";
import type { Policy, PolicyState } from "../api/types";

type ControlFilter = "any" | "mfa" | "block" | "device-compliance" | "session-control";
type StateFilter = "any" | PolicyState;

function matchesControl(policy: Policy, filter: ControlFilter): boolean {
  const controls = policy.grantControls.builtInControls;
  switch (filter) {
    case "mfa":
      return controls.includes("mfa");
    case "block":
      return controls.includes("block");
    case "device-compliance":
      return controls.includes("compliantDevice") || controls.includes("domainJoinedDevice");
    case "session-control":
      return policy.sessionControls.length > 0;
    default:
      return true;
  }
}

export function PolicyExplorer() {
  const { policies, status, message } = useAppState();
  const [search, setSearch] = useState("");
  const [stateFilter, setStateFilter] = useState<StateFilter>("any");
  const [controlFilter, setControlFilter] = useState<ControlFilter>("any");
  const [adminOnly, setAdminOnly] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return policies.filter((policy) => {
      if (term && !policy.displayName.toLowerCase().includes(term) && !policy.id.toLowerCase().includes(term)) return false;
      if (stateFilter !== "any" && policy.state !== stateFilter) return false;
      if (!matchesControl(policy, controlFilter)) return false;
      if (adminOnly && !policy.conditions.includeRoles.some((r) => ADMIN_ROLE_TEMPLATE_IDS.has(r))) return false;
      return true;
    });
  }, [policies, search, stateFilter, controlFilter, adminOnly]);

  if (status === "loading" || status === "idle") return <div className="empty-state">Loading policies…</div>;
  if (status === "unauthenticated") return <div className="empty-state">Sign in to explore your tenant's policies.</div>;
  if (status === "consent_required") return <div className="empty-state">Admin consent to Policy.Read.All is required.</div>;
  if (status === "error") return <div className="empty-state">{message ?? "Could not load policies."}</div>;

  const selected = selectedId ? policies.find((p) => p.id === selectedId) : null;
  if (selected) {
    return <PolicyDetail policy={selected} onBack={() => setSelectedId(null)} />;
  }

  return (
    <div className="stack">
      <div className="card">
        <input
          type="text"
          className="search-input"
          placeholder="Search by name or ID…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", fontSize: 13 }}>
          <label>
            State:{" "}
            <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value as StateFilter)}>
              <option value="any">Any</option>
              <option value="enabled">Enabled</option>
              <option value="enabledForReportingButNotEnforced">Report-only</option>
              <option value="disabled">Disabled</option>
            </select>
          </label>
          <label>
            Control:{" "}
            <select value={controlFilter} onChange={(e) => setControlFilter(e.target.value as ControlFilter)}>
              <option value="any">Any</option>
              <option value="mfa">Requires MFA</option>
              <option value="block">Blocks access</option>
              <option value="device-compliance">Requires compliant device</option>
              <option value="session-control">Has session controls</option>
            </select>
          </label>
          <label>
            <input type="checkbox" checked={adminOnly} onChange={(e) => setAdminOnly(e.target.checked)} /> Targets admin roles only
          </label>
        </div>
      </div>

      <div className="card">
        <p style={{ margin: "0 0 12px", fontSize: 13, color: "#667085" }}>
          {filtered.length} of {policies.length} policies match
        </p>
        {filtered.map((policy) => (
          <div key={policy.id} className="list-row" style={{ cursor: "pointer" }} onClick={() => setSelectedId(policy.id)}>
            <div className="list-row-main">
              <p className="list-row-title">{policy.displayName || policy.id}</p>
              <p className="list-row-desc">{derivedPolicyType(policy)}</p>
            </div>
            <StatusBadge state={policy.state} />
          </div>
        ))}
      </div>
    </div>
  );
}
