import { useMemo, useState } from "react";
import { useAppState } from "../state/appState";
import { StatusBadge } from "../components/StatusBadge";
import { PolicyDetail } from "../components/PolicyDetail";
import { derivedPolicyType } from "../lib/deriveInsights";

export function Policies() {
  const { policies, status, message } = useAppState();
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const filtered = useSearch(policies, search);

  if (status === "loading" || status === "idle") return <div className="empty-state">Loading policies…</div>;
  if (status === "unauthenticated") return <div className="empty-state">Sign in to see your tenant's policies.</div>;
  if (status === "consent_required") return <div className="empty-state">Admin consent to Policy.Read.All is required.</div>;
  if (status === "error") return <div className="empty-state">{message ?? "Could not load policies."}</div>;

  const selected = selectedId ? policies.find((p) => p.id === selectedId) : null;
  if (selected) {
    return <PolicyDetail policy={selected} onBack={() => setSelectedId(null)} />;
  }

  return (
    <div className="card">
      <input
        type="text"
        className="search-input"
        placeholder="Search policies by name…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {filtered.length === 0 ? (
        <p style={{ color: "#667085", fontSize: 13 }}>No policies match your search.</p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Policy Name</th>
                <th>Status</th>
                <th>Type</th>
                <th>Users/Groups</th>
                <th>Applications</th>
                <th>Controls</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((policy) => {
                const userCount =
                  policy.conditions.includeUsers.length + policy.conditions.includeGroups.length + policy.conditions.includeRoles.length;
                const apps = policy.conditions.includeApplications;
                return (
                  <tr key={policy.id} className="clickable" onClick={() => setSelectedId(policy.id)}>
                    <td>{policy.displayName || policy.id}</td>
                    <td>
                      <StatusBadge state={policy.state} />
                    </td>
                    <td>{derivedPolicyType(policy)}</td>
                    <td>{userCount || "—"}</td>
                    <td>{apps.length ? (apps.includes("All") ? "All cloud apps" : `${apps.length} app(s)`) : "—"}</td>
                    <td>{policy.grantControls.builtInControls.join(", ") || "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function useSearch<T extends { displayName: string; id: string }>(items: T[], search: string): T[] {
  return useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return items;
    return items.filter((item) => item.displayName.toLowerCase().includes(term) || item.id.toLowerCase().includes(term));
  }, [items, search]);
}
