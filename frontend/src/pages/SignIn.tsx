import { useState } from "react";
import { useAppState } from "../state/appState";
import { ShieldIcon } from "../components/icons";

// Mirrors the client-side tenant-alias rejection in the previous vanilla UI
// (web/app.js, DECISION-014): these aliases are meaningless for a specific
// app registration's client-credentials grant, matching the server-side
// check in server.py/auth.py.
const APP_ONLY_DISALLOWED_TENANTS = new Set(["organizations", "common", "consumers"]);

function isDisallowedAppOnlyTenant(tenant: string): boolean {
  return APP_ONLY_DISALLOWED_TENANTS.has(tenant.trim().toLowerCase());
}

export function SignIn() {
  const { deviceCode, startDeviceCodeSignIn, submitAppOnlySignIn, viewSampleData } = useAppState();

  const [tenant, setTenant] = useState("organizations");
  const [showAppOnly, setShowAppOnly] = useState(false);
  const [appOnlyTenant, setAppOnlyTenant] = useState("");
  const [appOnlyClientId, setAppOnlyClientId] = useState("");
  const [appOnlySecret, setAppOnlySecret] = useState("");
  const [appOnlySubmitting, setAppOnlySubmitting] = useState(false);
  const [appOnlyError, setAppOnlyError] = useState<string | null>(null);

  function clearAppOnlySecretField() {
    setAppOnlySecret("");
  }

  function switchToAppOnly() {
    setShowAppOnly(true);
    clearAppOnlySecretField();
    setAppOnlyError(null);
  }

  function switchToDeviceCode() {
    setShowAppOnly(false);
    // Cleared on every mode switch, in both directions, so the secret never
    // lingers in state once the form is no longer in view.
    clearAppOnlySecretField();
  }

  async function submitAppOnly() {
    const tenantValue = appOnlyTenant.trim();
    const clientIdValue = appOnlyClientId.trim();
    const secretValue = appOnlySecret;

    if (!tenantValue || !clientIdValue || !secretValue) {
      clearAppOnlySecretField();
      setAppOnlyError("Tenant, client ID, and client secret are all required.");
      return;
    }
    if (isDisallowedAppOnlyTenant(tenantValue)) {
      clearAppOnlySecretField();
      setAppOnlyError("Tenant must be a specific tenant GUID or domain, not organizations/common/consumers.");
      return;
    }

    setAppOnlySubmitting(true);
    setAppOnlyError(null);
    try {
      const result = await submitAppOnlySignIn(tenantValue, clientIdValue, secretValue);
      if (!result.ok) {
        setAppOnlyError(result.message ?? "App-only sign-in failed.");
      }
    } finally {
      // Cleared the instant the request settles — resolved or rejected —
      // so the secret is never retained in component state past this point.
      clearAppOnlySecretField();
      setAppOnlySubmitting(false);
    }
  }

  return (
    <div className="signin-page">
      <div className="card signin-card">
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
          <ShieldIcon width={28} height={28} color="#1f4287" />
          <div>
            <h3 style={{ margin: 0 }}>CAreview</h3>
            <p style={{ margin: 0, color: "#667085", fontSize: 13 }}>Local Conditional Access policy analyzer</p>
          </div>
        </div>

        {!showAppOnly && (
          <div>
            <p style={{ fontSize: 14 }}>Sign in to your Microsoft Entra tenant to read Conditional Access policies.</p>
            <label className="form-field">
              Tenant
              <input
                type="text"
                value={tenant}
                onChange={(e) => setTenant(e.target.value)}
                autoComplete="off"
                spellCheck={false}
              />
            </label>
            {deviceCode.phase !== "pending" && (
              <button type="button" className="btn" onClick={() => void startDeviceCodeSignIn(tenant)}>
                Sign in
              </button>
            )}
            {deviceCode.phase === "pending" && (
              <div className="device-code-box">
                <p style={{ margin: 0, fontSize: 13 }}>
                  Open{" "}
                  <a href={deviceCode.verificationUri} target="_blank" rel="noopener noreferrer">
                    the Microsoft sign-in page
                  </a>{" "}
                  and enter the code:
                </p>
                <p className="device-code-value">{deviceCode.userCode}</p>
                <p className="status-text">Waiting for approval…</p>
              </div>
            )}
            {deviceCode.phase === "error" && <p className="status-text error">{deviceCode.message}</p>}
            <p style={{ marginTop: 12 }}>
              <button type="button" className="link-plain" onClick={switchToAppOnly}>
                Use app-only sign-in (advanced)
              </button>
            </p>
          </div>
        )}

        {showAppOnly && (
          <div>
            <p className="caution-text">
              Advanced: sign in using an Entra app registration's client credentials instead of your own account. The
              client secret you enter below grants whatever Microsoft Graph application permissions that app
              registration already holds in this tenant — treat it like a password.
            </p>
            <label className="form-field">
              Tenant ID or domain
              <input
                type="text"
                value={appOnlyTenant}
                onChange={(e) => setAppOnlyTenant(e.target.value)}
                autoComplete="off"
                spellCheck={false}
                placeholder="contoso.onmicrosoft.com or a GUID"
              />
            </label>
            <label className="form-field">
              Client (application) ID
              <input
                type="text"
                value={appOnlyClientId}
                onChange={(e) => setAppOnlyClientId(e.target.value)}
                autoComplete="off"
                spellCheck={false}
              />
            </label>
            <label className="form-field">
              Client secret
              <input
                type="password"
                value={appOnlySecret}
                onChange={(e) => setAppOnlySecret(e.target.value)}
                autoComplete="off"
                spellCheck={false}
              />
            </label>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" className="btn" disabled={appOnlySubmitting} onClick={() => void submitAppOnly()}>
                {appOnlySubmitting ? "Signing in…" : "Sign in with app-only credentials"}
              </button>
              <button type="button" className="link-plain" onClick={switchToDeviceCode}>
                Back to standard sign-in
              </button>
            </div>
            {appOnlyError && <p className="status-text error">{appOnlyError}</p>}
          </div>
        )}

        <hr style={{ margin: "20px 0", border: "none", borderTop: "1px solid var(--border)" }} />
        <button type="button" className="btn btn-secondary" onClick={() => void viewSampleData()}>
          View a sample analysis
        </button>
        <p style={{ fontSize: 12, color: "#667085", marginTop: 8 }}>
          No sign-in required — explores the dashboard with committed sample data.
        </p>
      </div>
    </div>
  );
}
