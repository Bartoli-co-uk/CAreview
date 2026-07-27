# Project brief: CAreview — Conditional Access policy analyzer

**Status:** `APPROVED` (v2 amendment approved by `DECISION-013`, binding this exact commit)
**Version:** `2`
**Amends:** v1, approved by `DECISION-001` at `179a023`
**Source description:** `project/intake/PROJECT_DESCRIPTION.md` at `19e5863d19f856b635df878234a37333f391b4e9`
**Prepared by:** `Claude Code requirements session (2026-07-24, v1); amended 2026-07-27`
**Prepared at:** `2026-07-24T10:29:45Z` (v1); `2026-07-27` (v2 amendment)

## v2 amendment summary

The owner has an existing Microsoft Entra enterprise application already
granted **application (app-only)** `Policy.Read.All`. v1 excluded any
app-registration or non-device-code authentication as a non-goal. This
amendment proposes lifting that exclusion to add an **opt-in second sign-in
mode** — OAuth 2.0 client-credentials with a client secret — alongside the
existing device-code flow, which remains the default. Everything else in v1
is unchanged unless marked below. This amendment does not authorize
implementation; it is a draft for approval like v1 was.

## Plain-language interpretation

The owner wants their own, locally-run version of the open-source
`Jhope188/ca-policy-analyzer`. It should let a security practitioner sign into a
Microsoft Entra ID tenant, read that tenant's Conditional Access (CA) policies
through Microsoft Graph, and get an at-a-glance security assessment: a single
0–100 score, a list of best-practice / vulnerability findings, and a simple
visual breakdown of each policy. Everything runs on the practitioner's own
machine; nothing is deployed publicly, and no tenant data leaves the machine
except the direct calls to Microsoft.

The distinguishing constraints versus the original are deliberate simplicity:
authentication must "just request authentication" with **no Azure app
registration required to get started**, and the tool must run with **no build
toolchain** — the Python standard library only. (v2: device-code sign-in with
no app registration remains the default and requires no change from the user.
An app registration is now an *optional* alternative for a user who already
has one with app-only `Policy.Read.All`, not a requirement.)

## Users and stakeholders

| User or stakeholder | Need | Expected outcome |
|---|---|---|
| Repository owner / security practitioner | Assess a tenant's CA posture quickly and locally | Signs in, sees a score, findings, and per-policy visualization for their tenant |
| Tenant administrator (consent grantor) | Grant the read-only access the tool needs | One-time admin consent to read-only Graph scopes; no standing app registration |
| Reviewers of this project (Codex, human owner) | Confidence the build is correct and safe | Each issue and milestone passes the governed review gates |
| **(v2)** Owner with an existing app registration | Use an already-consented enterprise app instead of relying on the shared first-party client | Can opt into app-only sign-in and get the same analysis, without depending on the Microsoft Graph PowerShell client being present/consented in their tenant |

## Goals

- Sign in to Entra ID via OAuth 2.0 **device-code flow** against a Microsoft
  first-party public client (click *Sign in* → enter code at
  `microsoft.com/devicelogin`). **This remains the default and requires no
  setup change.**
- **(v2, opt-in)** Offer a second sign-in mode — OAuth 2.0
  **client-credentials flow** — for a user who already has an Entra app
  registration with **application** `Policy.Read.All` granted. The user
  chooses this mode explicitly and supplies tenant ID, client ID, and client
  secret via the UI; nothing about the default path changes.
- Fetch the tenant's Conditional Access policies from Microsoft Graph
  (unchanged: the same read-only Graph call regardless of which mode obtained
  the token).
- Produce a **0–100 security score** and a **severity-sorted findings list** from
  a transparent, data-driven rule set.
- Render a **simple per-policy visualization** (Users → Conditions → Apps →
  Controls).
- Run entirely locally on `http://localhost:8765` with **Python standard
  library only**. **No app registration is required to use the default mode;**
  one is required only if the user opts into the v2 app-only mode.
- Be **offline-testable**: analyzer scoring verified against committed sanitized
  fixtures without signing in.

## Non-goals

- CIS Microsoft 365 Benchmark v7.0 control matrix.
- FOCI application database / token-sharing analysis.
- MS Learn documented-exclusion checks.
- Zero Trust persona scoring.
- Baseline comparison against external repositories.
- PowerPoint / deployment-bundle exports.
- **(v2 revision)** App registration / non-device-code authentication is **no
  longer excluded**; it is now an opt-in second mode (see Goals). What remains
  excluded:
  - **Certificate-based client assertions** (would require RSA/JWT signing —
    a third-party dependency — violating the stdlib-only constraint). Secret
    auth only.
  - **Persisting the secret to disk, config file, or logs.** It is supplied
    per-session via the UI and held in memory only, exactly like the
    device-code access token.
  - **Registering an app on the user's behalf.** CAreview never creates or
    modifies an app registration; the user brings their own, already
    consented.
  - CAreview does not become multi-tenant-hosted, and app-only mode does not
    change the read-only Graph scope.
- Multi-tenant hosting, user accounts, or any public/hosted deployment.
- Writing to or changing tenant configuration (the tool is strictly read-only).

## Confirmed facts

- Source project is `Jhope188/ca-policy-analyzer`, a client-side analyzer of
  Entra ID Conditional Access policies (source description).
- Hosting is local only; only network egress is to Microsoft (source description).
- Authentication is device-code against a first-party public client; no app
  registration, no client secret (source description).
- Implementation language/runtime is Python 3.10+ (Python 3.14 confirmed present
  locally), standard library only, no Node.js (source description; environment
  check).
- Delegated Graph scopes are limited to `Policy.Read.All`,
  `Application.Read.All`, `Directory.Read.All`; Security Reader role suffices
  (source description). **(v2 correction)** `graph.py` only ever calls
  `identity/conditionalAccess/policies`; `Application.Read.All` and
  `Directory.Read.All` are requested but unused. This amendment folds in
  trimming the delegated request to `Policy.Read.All` alone — unrelated to
  app-only mode in mechanism, but bundled here because it reduces the same
  consent-screen friction this amendment is meant to route around, and
  because `auth.py`'s `SCOPES` constant is being touched anyway.
- Tokens are held only in process memory and never persisted (source description).
- The build follows the ClaudexCodexSetUp workflow already committed in this
  repository; Codex CLI is installed and authenticated (environment check).
- **(v2)** The owner has confirmed they hold an Entra enterprise application
  already granted **application-type** (app-only) `Policy.Read.All` consent in
  at least one tenant, distinct from the delegated device-code path (owner
  statement, this session).
- **(v2)** The owner has chosen client-secret authentication for that app, not
  certificate-based; and has chosen UI form-field entry for tenant ID, client
  ID, and secret over a server-side environment variable, accepting that the
  secret transits the browser and the loopback HTTP POST body (owner decision,
  this session).

## Assumptions requiring confirmation

- **A1 — First-party public client can read CA policies via device code.** We
  assume a Microsoft first-party public client (candidate: Microsoft Graph
  PowerShell, `14d82eec-204b-4c2f-b7e8-296a70dab67e`) can obtain a delegated
  token carrying `Policy.Read.All` after admin consent. *If wrong:* device-code
  sign-in may succeed but Graph returns 403; the user can fall back to the v2
  app-only mode if they have a suitable app registration. Needs verification
  against a real tenant.
- **A2 — Default tenant value.** We assume `organizations` (work/school) is the
  right default authority; a tenant GUID may be needed in some tenants. *If
  wrong:* sign-in fails for some accounts until the tenant is entered manually.
- **A3 — Scope of policy fetch for the MVP rule set.** We assume the MVP can
  score policies primarily from the CA policy objects themselves, fetching named
  locations and directory-role assignments only if a starter rule needs them.
  *If wrong:* some findings are less precise until those objects are added.
- **A4 — Single local user.** We assume one local user on a trusted machine; the
  local server has no authentication of its own beyond binding to `localhost`.
  *If wrong:* another local process/user could reach the API while a session's
  token is in memory.
- **A5 — Browser available for the device-code approval step.** The user has a
  browser (possibly on another device) to complete `microsoft.com/devicelogin`.
- **A6 (v2) — App-only token is a drop-in bearer credential.** We assume
  `graph.py`'s Graph client needs no change to accept an app-only token: it
  already only requires a bearer access token scoped to
  `graph.microsoft.com` and attaches it the same way regardless of how it was
  obtained. *If wrong:* app-only mode would need Graph-client changes beyond
  the auth layer, widening this from the currently estimated one issue.
- **A7 (v2) — `.default` scope is sufficient.** We assume requesting
  `https://graph.microsoft.com/.default` under client-credentials returns
  exactly the app's consented application permissions (i.e. `Policy.Read.All`
  if that is all that was granted), with no way for CAreview to request a
  narrower application scope at runtime — unlike delegated scopes, app-only
  consent is fixed at the app-registration level, not negotiated per request.
  *If wrong (e.g. the app also holds broader application permissions):*
  CAreview would receive a token capable of more than it uses; this is an
  accepted risk of app-only mode, not something the client can suppress.

## Contradictions and unknowns

- The original tool is a browser-only SPA with MSAL popup auth; this project
  deliberately diverges to a local Python backend with device-code auth. This is
  an intentional re-scope, not a contradiction, but it means feature parity with
  the original is explicitly **not** promised.
- Exact starter rule weights for the 0–100 score are not yet fixed; they will be
  proposed in the roadmap/implementation and are a place where reasonable people
  differ. The score is a heuristic, not an authoritative compliance measure.
- Unknown whether the owner's target tenant(s) restrict first-party device-code
  flows (conditional access on the tooling account itself) — see A1.

## Constraints

- Technical: Python 3.10+ standard library only; no third-party packages, no
  Node.js, no build step.
- Platform: runs locally on the owner's machine (macOS confirmed; should not
  depend on OS-specific features); serves `localhost:8765`.
- Time/cost: no paid infrastructure; only cost is the owner's existing Microsoft
  tenant and the Codex/Claude review usage inherent to the workflow.
- Legal/compliance: not established; the tool reads tenant security
  configuration and must not exfiltrate it. No compliance certification claimed.
- Accessibility: basic — legible, keyboard-usable HTML UI; no formal WCAG target
  set for the MVP (candidate future work).
- Other: strictly read-only against the tenant; no write scopes.

## Integrations and external systems

| System | Purpose | Data exchanged | Authentication/permission assumption |
|---|---|---|---|
| Microsoft identity platform (`login.microsoftonline.com`) | Device-code sign-in and token issuance (default mode) | Device code, delegated access token | First-party public client; user completes device-code approval; admin consent to `Policy.Read.All` (trimmed, v2) |
| **(v2)** Microsoft identity platform (`login.microsoftonline.com`) | Client-credentials token issuance (opt-in app-only mode) | Tenant ID, client ID, client secret (submitted, not stored); app-only access token returned | User's own app registration; already-granted application `Policy.Read.All`; `.default` scope |
| Microsoft Graph (`graph.microsoft.com`) | Read Conditional Access policies | CA policy JSON returned to the local app | `Policy.Read.All` only (delegated or application, depending on mode), read-only |
| Local browser | Complete `microsoft.com/devicelogin` (default mode), or enter tenant/client/secret (v2 app-only mode); view the UI | User code entry or app credentials; rendered results | Localhost only |

## Data and security

- Data classification: **sensitive** (tenant security configuration).
- Personal or regulated data: policy objects may reference user/group/role IDs
  and named locations; no bulk personal data is intended to be fetched.
- Trust boundaries: local user ↔ local server (localhost); local server ↔
  Microsoft endpoints (TLS). The local server performs no authn of its own.
- Secrets and credentials: **default mode unchanged** — no client secret
  exists (public client); tokens live in process memory only. **(v2, app-only
  mode only)** A real, tenant-wide-capable client secret is now in scope. Per
  owner decision this session: entered via a UI form field (not an
  environment variable), transiting the loopback HTTP POST body and the
  browser's JS runtime for the session. It must still never be written to
  disk, logs, tracked files, review reports, or echoed back in any API
  response (including error bodies). It is held in server process memory only
  for the session's lifetime, cleared on logout/process exit, same as a
  token. Browser-side, the field must be `autocomplete="off"` and its value
  must not be logged to the console.
- Material abuse or failure cases: token left in memory readable by another local
  process (A4); a malicious/typo tenant value directing auth elsewhere; over-broad
  scopes; accidental logging of tokens or policy data; SSRF if any user-supplied
  value reached an outbound URL; binding beyond localhost. **(v2 addition)** A
  local process or browser extension capturing the secret from the page/POST
  body during entry has a materially larger blast radius than capturing a
  delegated user token: an application secret is typically longer-lived and
  not scoped to one person's access, so anyone holding it can mint fresh
  tokens for as long as it remains valid, independent of this tool. The
  existing RISK-002 (no local authentication beyond loopback binding) is
  widened by this mode, not newly created by it. Browser autofill/history
  caching a submitted secret is an additional new failure mode this mode
  introduces that the device-code path does not have.
- Required external isolation or expert review: none mandated for a local
  read-only tool; the milestone security review covers the threat model. The
  security review for the app-only issue must explicitly address secret
  handling end-to-end (UI field → POST body → memory → outbound token
  request → discard) as a named check, not folded into general review.

## Deployment and operation

- Intended environment: local developer/practitioner machine; run on demand.
- Availability and recovery: none required; it is a run-on-demand local tool with
  no persistence to recover.
- Observability/support: console logs for local troubleshooting, with tokens and
  policy data redacted; no telemetry or external logging.
- Migration or deletion: no datastore; closing the process discards all state and
  tokens. No provider-side deletion is claimed.

## Measurable success criteria

1. `python3 server.py` serves the app on `http://localhost:8765` with no
   third-party dependencies installed.
2. Clicking *Sign in* completes a device-code sign-in with a work/school account
   and the app lists that tenant's Conditional Access policies.
3. Each policy set yields a 0–100 score and a severity-sorted findings list.
4. `python3 -m unittest discover -s tests` passes, demonstrating the analyzer
   scoring committed sanitized fixtures fully offline.
5. Every implementation issue has a committed, passing Codex review bound to its
   exact commit, and the milestone passes its four blind reviews.
6. **(v2)** From the sign-in card, the user can choose "Use an application"
   instead of device-code, enter tenant ID, client ID, and client secret, and
   get the same score/findings/policy-card output as the device-code path,
   without changing anything for a user who does not choose that mode.
7. **(v2)** The client secret never appears in a server log, an API response
   body, a committed file, or a review report; unit tests assert this using a
   mock transport, without exercising a real tenant.
8. **(v2)** `auth.py`'s delegated `SCOPES` requests only `Policy.Read.All`.

## Questions for the human

1. **Client id / tenant default (A1, A2):** Are you content to proceed with the
   Microsoft Graph PowerShell first-party public client and an `organizations`
   default authority, accepting that a tenant which blocks first-party
   device-code will need the app-registration fallback added later? This is the
   single biggest technical risk. *(v2: resolved — the fallback is being added
   now, per this amendment.)*
2. ~~Fallback scope~~ *(v2: resolved by this amendment — pulled in as an
   opt-in mode, not folded into the default path.)*
3. **Local-server exposure (A4):** Is "trusted single-user machine, localhost
   binding, no local auth" acceptable for the MVP, or do you want a local
   loopback token/PIN gate on the API from the start? **(v2 note: this
   question now carries more weight — RISK-002 covers a delegated read-only
   token today; app-only mode puts a live client secret behind the same "no
   local auth" boundary. Re-confirm you accept RISK-002 as widened, or want a
   loopback gate added as a prerequisite to this amendment rather than after
   it.)**
4. **Score transparency:** Is a documented heuristic score (with each rule's
   weight shown) acceptable, given it is explicitly not a compliance
   certification?
5. **(v2) Tenant validation for app-only mode:** Client-credentials requires a
   real tenant ID or verified domain (`organizations`/`common` are invalid).
   Should CAreview reject those two default-style values client-side with a
   clear error when app-only mode is selected, so the failure is immediate and
   local rather than a confusing round-trip to Microsoft?
6. **(v2) Secret re-entry:** App-only access tokens expire hourly like
   delegated ones, but there is no refresh token in this design (matching
   `DECISION-004`'s no-`offline_access` stance). Re-authenticating means
   re-submitting tenant/client/secret through the UI each time, not just
   clicking one button. Acceptable for the MVP of this mode?

## Approval gate

This brief is not approved until a human decision record names this exact path,
version, and commit SHA. Approval permits roadmap drafting only; it does not
permit implementation or protected actions.

**v1 decision record:** `project/decisions/DECISION-001-brief-approval.md` (APPROVE, binds v1 at `179a02354aecbafa2c9d5aa34f9c9a5a04bbc79a`)
**v2 decision record:** `project/decisions/DECISION-013-brief-v2-approval.md` (APPROVE, binds v2 at `98feea68b840bc2c92eda1cd46af8217555daeb5`). This approval covers the brief as written; it does not itself resolve Questions 3, 5, and 6 above — those remain open and gate `ISSUE-0008` in `ROADMAP.md`.
