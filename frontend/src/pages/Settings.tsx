import { useState } from "react";
import { useAppState } from "../state/appState";
import { setBreakGlassIds } from "../api/client";

// A GUID per the same pattern server.py/graph.py validate against.
const GUID_RE = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

export function Settings() {
  const { mode, tenant, signOut } = useAppState();
  const [breakGlassInput, setBreakGlassInput] = useState("");
  const [breakGlassStatus, setBreakGlassStatus] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const signedIn = mode === "live";

  async function submitBreakGlass() {
    const ids = breakGlassInput
      .split(/[\s,]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    const invalid = ids.filter((id) => !GUID_RE.test(id));
    if (invalid.length) {
      setBreakGlassStatus(`Not a valid GUID: ${invalid[0]}`);
      return;
    }
    setSubmitting(true);
    setBreakGlassStatus(null);
    try {
      const result = await setBreakGlassIds(ids);
      setBreakGlassStatus(result.ok ? `Saved ${result.count} break-glass account ID(s) for this session.` : "Could not save break-glass account IDs.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="card-header-title" style={{ marginBottom: 12 }}>
          Session
        </div>
        <div className="glance-row">
          <span className="glance-row-label">Status</span>
          <span className="glance-row-value">
            {mode === "live" ? "Signed in" : mode === "sample" ? "Viewing sample data" : "Signed out"}
          </span>
        </div>
        {tenant && (
          <div className="glance-row">
            <span className="glance-row-label">Tenant (as entered)</span>
            <span className="glance-row-value">{tenant}</span>
          </div>
        )}
        <p style={{ fontSize: 12, color: "#667085", marginTop: 8 }}>
          CAreview has no dedicated "am I signed in" endpoint, so this reflects whatever the last policy/analysis fetch
          returned, and the tenant shown is what you typed at sign-in — not a verified directory name.
        </p>
        {signedIn && (
          <button type="button" className="btn btn-danger" onClick={() => void signOut()} style={{ marginTop: 8 }}>
            Sign out
          </button>
        )}
      </div>

      <div className="card">
        <div className="card-header-title" style={{ marginBottom: 4 }}>
          Break-glass accounts
        </div>
        <p style={{ fontSize: 13, color: "#667085", marginTop: 0 }}>
          Object IDs of your tenant's break-glass/emergency-access accounts, used by the "break-glass accounts are
          excluded from lockout" recommendation. Held in server memory only for this session — never written to disk,
          and cleared on restart.
        </p>
        <textarea
          value={breakGlassInput}
          onChange={(e) => setBreakGlassInput(e.target.value)}
          placeholder="One GUID per line or comma-separated"
          rows={3}
          style={{ width: "100%", padding: 8, border: "1px solid var(--border)", borderRadius: 6, fontSize: 13 }}
        />
        <button type="button" className="btn" disabled={submitting} onClick={() => void submitBreakGlass()} style={{ marginTop: 8 }}>
          {submitting ? "Saving…" : "Save break-glass accounts"}
        </button>
        {breakGlassStatus && <p className="status-text" style={{ marginTop: 8 }}>{breakGlassStatus}</p>}
      </div>

      <div className="card placeholder-card">
        <h3>Persisted preferences — not available</h3>
        <p>CAreview keeps no on-disk state by design; nothing here (or elsewhere in the app) survives a restart.</p>
      </div>
    </div>
  );
}
