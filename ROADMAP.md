# Project roadmap — CAreview

This is the canonical project roadmap for CAreview, a locally-hosted Conditional
Access policy analyzer.

**Current status:** `DRAFT` (roadmap v4 candidate — supersedes approved v3 pending a new Codex plan review and a new exact human approval; **not** implementation-authorizing)
**Roadmap version:** `4`
**Approved brief:** `project/brief/PROJECT_BRIEF.md` v1 at `179a02354aecbafa2c9d5aa34f9c9a5a04bbc79a` (DECISION-001) — governs M1
**Amending brief:** `project/brief/PROJECT_BRIEF.md` v2 at `9ccf835`, approved by `DECISION-013`; open questions resolved by `DECISION-014` — governs M2 below
**Codex plan review:** v3 rounds recorded in Planning reconciliation below. **v4: not yet reviewed** — a fresh `./scripts/run-codex-review.sh plan <V4-HEAD-SHA>` is required before this version may be put to the human
**Human approval record:** `project/decisions/DECISION-003-roadmap-approval.md` (APPROVE, binds **v3** at `125d74f6d4bfe85f1a727293064d0887f2d121c7`). **v4: not yet recorded**
**Delivery status:** `M1` COMPLETE and accepted (`DECISION-012`); all six issues merged. `M2` is `PLANNED` and unapproved. Current state: `project/status/CURRENT.md`.

No implementation may begin until a human records approval of the exact roadmap
version and commit. Roadmap v3 remains the approved artifact until a decision
record binds v4; no M2 issue may start on the strength of this draft alone.

## Project outcome

When complete, running `python3 server.py` starts a local, standard-library-only
web app on `http://localhost:8765`. The user clicks *Sign in*, completes an OAuth
2.0 device-code sign-in against a Microsoft first-party public client, and the app
fetches the tenant's Conditional Access policies from Microsoft Graph. It shows a
0–100 security score, a severity-sorted list of best-practice / vulnerability
findings, and a simple per-policy visualization (Users → Conditions → Apps →
Controls). The analyzer is unit-tested offline against committed sanitized
fixtures. No Azure app registration, no client secret, no Node.js, and no
third-party Python packages are required.

## Users and success measures

| User or stakeholder | Need | Measurable success criterion |
|---|---|---|
| Security practitioner (owner) | Assess a tenant's CA posture locally | Product goal: signs in and sees policies, a 0–100 score, and findings for their tenant. M1 acceptance is proven on mocked/fixture evidence; the live sign-in against a real tenant is a separately approved protected step (a residual evidence gap the human accepts), not an M1 gate (F-003) |
| Tenant admin (consent) | Grant least-privilege read access | One-time consent to read-only Graph scopes; no standing app registration |
| Project reviewers | Correct, safe build | Each issue has a committed passing Codex review; milestone passes four blind reviews |

## Constraints and non-goals

### Constraints

- Python 3.10+ standard library only; no third-party packages, no Node.js, no build step.
- Serve on `127.0.0.1:8765` only; no local authentication beyond loopback binding (DECISION-001, re-examined by `RISK-002` below for app-only mode).
- **(v4)** Delegated Graph scopes limited to `Policy.Read.All`; read-only.
  `Application.Read.All` and `Directory.Read.All` are removed — `graph.py` calls
  only `identity/conditionalAccess/policies`, so they were requested and never
  used (brief v2 correction).
- **(v4)** App-only mode requests `https://graph.microsoft.com/.default` and
  receives whatever application permissions the user's own app already holds.
  CAreview cannot narrow an app-only grant at runtime (brief A7); it never
  requests, creates, or modifies a consent grant.
- Tokens held in process memory only; never persisted to disk, logs, or the repo.
  **(v4)** The same rule binds the app-only **client secret**, retained for the
  session per `DECISION-014` (see Architecture) but never written to disk.
- Analyzer must be verifiable offline against committed sanitized fixtures.
- **(v4)** No live-tenant authentication or fetch is a completion criterion for
  any issue, in either mode. That remains a protected action.

### Non-goals

- CIS v7.0 matrix, FOCI database, MS Learn exclusion checks, persona scoring, baseline comparison, PowerPoint/deployment exports.
- **(v4 revision — narrowed)** App registration / non-device-code authentication
  is no longer categorically excluded. Device-code remains the default and
  unchanged path; client-credentials is an **opt-in** second mode for a user who
  already holds an app registration with application-type `Policy.Read.All`.
  Still excluded from this roadmap, without exception:
  - **Certificate-based client assertions.** RSA/JWT signing would require a
    third-party dependency and break the stdlib-only constraint. Recorded as a
    **deferred future enhancement** (see documentation plan for ISSUE-0011),
    not implemented in M2. Secret only.
  - **Any persistence of the client secret** — no disk, config file, env file,
    keychain, browser storage, cookie, log, tracked file, handoff, or review
    report.
  - **Creating or modifying an app registration on the user's behalf.** The user
    brings their own, already consented.
  - App-only mode does not widen the Graph surface CAreview calls, and does not
    make CAreview multi-tenant or hosted.
- Multi-tenant hosting, user accounts, public/hosted deployment, or any write to tenant configuration.

## Architecture and security assumptions

- **Auth:** device-code flow against the Microsoft Graph PowerShell first-party
  public client (`14d82eec-204b-4c2f-b7e8-296a70dab67e`) with `organizations`
  authority (brief A1/A2, DECISION-001).
- **Protected-action gate (per Codex F-002):** performing a real device-code
  sign-in or a live Graph fetch against a named tenant is a protected action
  under `AGENTS.md` and requires separate, explicit human approval naming the
  tenant/test identity. Issue completion is gated on the **mocked** checks; live
  evidence is recorded only after such approval and is otherwise a documented
  evidence gap. No issue may perform live authentication as a precondition of
  completion.
- **Analyzer data contract (per Codex F-003):** the A3 uncertainty (whether named
  locations / directory roles are needed) is resolved **before ISSUE-0003
  implementation**. ISSUE-0003 defines the normalized policy data contract the
  analyzer consumes; ISSUE-0004 defines, per rule, the required source fields and
  the behaviour when evidence is unknown or not applicable (a rule with missing
  required evidence is marked *not evaluable* and excluded from scoring rather
  than counted as pass or fail).
- **Data classification:** sensitive tenant configuration; rendered locally only,
  never transmitted anywhere except Microsoft; trust boundary is local-user ↔
  localhost server ↔ Microsoft over TLS (brief Data and security). Tenant-supplied
  strings (policy/display names) are untrusted input and must be rendered safely
  (per Codex F-005).
- **Loopback hardening (per Codex F-001):** the server rejects any request whose
  `Host` header is not on an explicit loopback allowlist (`127.0.0.1:<port>`,
  `[::1]:<port>`, `localhost:<port>`) to defend against DNS-rebinding by a remote
  site, and applies an Origin/`Sec-Fetch` check on state-changing endpoints
  (`/api/auth/*`). Implemented and tested in ISSUE-0001. This closes the gap
  DECISION-001/RISK-002 did not cover (a remote website reading loopback
  responses).
- **Deployment:** run-on-demand local tool; no persistence, no telemetry; closing
  the process discards all state and tokens.
- **(v4) Second sign-in mode — app-only client credentials (brief v2 Goals):**
  an opt-in mode alongside the default device-code flow. The server POSTs
  `grant_type=client_credentials`, `client_id`, `client_secret`, and
  `scope=https://graph.microsoft.com/.default` to
  `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token`, and installs
  the returned access token in the **same** in-memory slot the device-code flow
  uses. `graph.py` is unchanged: it already requires only a bearer token for
  `graph.microsoft.com` (brief A6 — verified by keeping `graph.py` out of scope
  in ISSUE-0008/0009, not by assertion).
- **(v4) Mode exclusivity and single concurrency:** the two modes share one token
  slot and one generation counter. Starting either mode supersedes any pending
  session and clears any existing token, exactly as `AuthManager.start()` does
  today. `logout()` clears token, session, and secret material.
- **(v4) Tenant validation for app-only mode (`DECISION-014`):** client-credentials
  has no user context, so `organizations`, `common`, and `consumers` are invalid
  authorities. The **server** rejects them, and requires a GUID or a DNS-style
  domain label, before any secret leaves the process. The UI performs the same
  check for fast feedback; the server check is the authoritative one.
- **(v4, `DECISION-014`) Secret lifecycle (the named security boundary of M2):**
  UI form field (`type="password"`, `autocomplete="off"`, never logged to
  console) → loopback POST body over `127.0.0.1` → server process memory,
  **retained for the app-only session's lifetime** (not discarded after the
  first token request — the human's explicit choice, trading a wider retention
  window for no hourly re-entry). The retained secret is used to **silently
  mint a fresh app-only token on expiry**, with no UI resubmission required — a
  real usability improvement over the device-code path, which has no refresh
  token at all (`DECISION-004`). The secret is never assigned to a module
  global outside the `AuthManager` instance, never included in any response
  body (success *or* error), never written to a log record, and never
  rendered back to the page; it is cleared on logout, on supersession by a
  new sign-in (either mode), and on process exit, same as a token. Provider
  error text is truncated and scrubbed of any occurrence of the submitted
  secret before it is returned or logged.
- **(v4) Blast-radius statement (brief v2 Data and security):** an application
  secret is materially more dangerous than the delegated user token M1 handled.
  It is typically longer-lived, is not bound to one person's access, and lets any
  holder mint fresh tenant-wide-capable tokens independently of this tool. It sits
  behind the same "loopback binding, no local authentication" boundary that
  `DECISION-001` accepted for a read-only delegated token. This widens `RISK-002`;
  it does not create a new boundary. `DECISION-014` re-accepts `RISK-002` as
  widened, on this exact basis.
- **(v4) Protected-action gate is unchanged and reaffirmed:** an app-only sign-in
  against a real tenant, with a real secret, is a protected action requiring
  separate explicit human approval naming the tenant. It is not a completion
  criterion for any M2 issue. All M2 acceptance runs on mock transports with a
  synthetic secret literal.
- **(v4) Test-credential hygiene:** tests use an obviously fake secret literal
  (for example `TEST-CLIENT-SECRET-NOT-REAL`). A real secret must never appear in
  a test, fixture, handoff, issue record, log, or review report.

## Milestones

Each milestone has a single frozen candidate commit and four fresh reviews:
Claude general, Codex general, Claude security, and Codex security. At most one
general-remediation cycle and two security-remediation cycles; every remediation
creates a new candidate and reruns all four reviews. Exhaustion blocks for the
human, who makes the milestone decision after seeing all four reports.

| ID | Outcome | Dependencies | Exit criteria | Status |
|---|---|---|---|---|
| `M1` | Working MVP: device-code sign-in → fetch CA policies → 0–100 score + findings → per-policy visualization, offline-testable | `None` | All six issues COMPLETE; `python3 server.py` runs; `python3 -m unittest discover -s tests` passes; the UI renders score/findings/cards against the offline fixture path; four blind milestone reviews pass. Live-tenant sign-in/fetch is **not** an M1 completion criterion (Codex F-003): it is a separate protected step, recorded as an explicit residual evidence gap that the human may accept at the milestone | `COMPLETE` — accepted `DECISION-012` |
| `M2` | Least-privilege delegated scope, plus an **opt-in** app-only (client-credentials, secret-only) sign-in mode beside the unchanged device-code default | `M1` COMPLETE; brief v2 APPROVED (`DECISION-013`); secret-retention/RISK-002/tenant-validation decided (`DECISION-014`) | All five M2 issues COMPLETE; `python3 -m unittest discover -s tests`, `python3 -m py_compile $(git ls-files '*.py')`, and `python3 scripts/validate_repo.py` pass at one frozen candidate; every pre-existing device-code test still passes unmodified in behaviour; mock-transport tests prove **the real submitted secret** appears in **no** API response body, **no** log record, and **no** tracked file (the committed synthetic test-sentinel literal used to exercise these tests is expected in `tests/` and is not itself a violation); `auth.py` requests only `Policy.Read.All` delegated; README and `docs/security-boundaries.md` describe both modes, the app-only prerequisites, the secret's lifetime, and certificate support as a deferred future enhancement; four blind milestone reviews against that one SHA, with the **security** pair required to treat the end-to-end secret lifecycle — field → POST body → server memory, **retained for the app-only session and reused to silently renew the token on expiry**, then **cleared on logout, on supersession by a new sign-in, and on process exit** (never discarded after a single use) — as a **named, separately reported check** (brief v2 requirement), not folded into general review. Live app-only sign-in against a real tenant is **not** an exit criterion — it stays a protected action and a declared evidence gap | `PLANNED` (unapproved) |

## Issue sequence

Issues run sequentially. Each is small enough for one fresh Claude issue task
(up to two in-task repair rounds) and an independent fresh Codex review.

| Order | Issue | Objective | Depends on | Acceptance and checks | Risk | Status |
|---:|---|---|---|---|---|---|
| 1 | `ISSUE-0001` | Local HTTP server + static UI shell + `/api/health`; run/verify scaffolding | `None` | `python3 server.py` serves `index.html` and `/api/health` returns `{"status":"ok"}`; `python3 -m py_compile` clean; `python3 -m unittest discover -s tests` runs (health test) | Low | `COMPLETE` (`23e6633`) |
| 2 | `ISSUE-0002` | Device-code auth: `/api/auth/start` + `/api/auth/poll`, in-memory token store with a full lifecycle; Sign-in UI shows code + link and reflects success | `ISSUE-0001` | Completion gated on mocked checks: unit tests cover the poll state machine, device-code expiry, server-controlled polling cadence, opaque bounded handle, logout/cancel + memory clear, access-token-expiry behaviour, the refresh-token decision, and single-concurrency; no token on disk/logs. Live sign-in is a protected action (F-002) recorded only after human approval | Medium (brief A1) | `COMPLETE` (`3c8fb869`) |
| 3 | `ISSUE-0003` | Graph client: `/api/policies` fetches and normalizes CA policies (paged), read-only bearer calls, against a defined data contract | `ISSUE-0002`, A3 resolved | Completion gated on mocked checks: unit tests cover paging, normalization to the documented data contract, and 403→consent message. Live fetch is a protected action (F-002) recorded only after human approval | Medium | `COMPLETE` (`065675e`) |
| 4 | `ISSUE-0004` | Analyzer engine + data-driven rule set + 0–100 scoring; per-rule required-field + not-evaluable behaviour; unit tests + sanitized fixtures | `ISSUE-0003` | `python3 -m unittest discover -s tests` passes; fixtures produce documented, deterministic scores and severity-sorted findings across strong/weak/incomplete samples; a rule with missing required evidence is marked *not evaluable*, not pass/fail | Medium | `COMPLETE` (`9f3885b`) |
| 5 | `ISSUE-0005` | UI rendering: score gauge, findings list, per-policy flow cards; wire `/api/policies` + analysis; XSS-safe rendering of untrusted policy content | `ISSUE-0003`, `ISSUE-0004` | Renders offline against a fixture endpoint for review; tenant/finding strings inserted as text (not HTML); restrictive CSP; `no-store` on sensitive API responses; no external assets; no console errors | Low | `COMPLETE` (`3dc059f`) |
| 6 | `ISSUE-0006` | Documentation finalization + end-to-end verification notes + lint/test polish | `ISSUE-0001..0005` | README run/verify steps accurate from a clean checkout; `py_compile` and `unittest` clean; a documented end-to-end walkthrough exists | Low | `COMPLETE` (`d15f47c`) |

### M2 issue sequence (PLANNED — not approved)

Prerequisite gate, before `ISSUE-0007` may start: a decision record approving
brief v2 at its exact commit (satisfied — `DECISION-013` binds `9ccf835`).
Before `ISSUE-0008` specifically: `DECISION-014` resolves secret retention
(session-lifetime, silent renewal), `RISK-002` (accepted as widened, on that
basis), and tenant-value validation (client-side, mirroring the server) — all
satisfied.

| Order | Issue | Objective | Depends on | Acceptance and checks | Risk | Status |
|---:|---|---|---|---|---|---|
| 7 | `ISSUE-0007` | Trim delegated `SCOPES` to `Policy.Read.All` only | Brief v2 approved | `auth.py` `SCOPES` contains exactly `https://graph.microsoft.com/Policy.Read.All`; a unit test asserts the constant and that the device-code request body carries only that scope; every existing test in `tests/test_auth.py` still passes with no behavioural change to the flow; README and `docs/security-boundaries.md` no longer claim three delegated scopes; `unittest`, `py_compile`, `validate_repo.py` all pass | Low | `PENDING` |
| 8 | `ISSUE-0008` | App-only token acquisition inside `auth.py` only — no HTTP endpoint, no UI | `ISSUE-0007`; `DECISION-014` (retention model, RISK-002 acceptance) | Pure auth-layer change: a `build_client_credentials_request()` and an `AuthManager` method that installs an app-only token in the existing token slot **and retains the secret in the manager instance for the session** (per `DECISION-014` — not discarded after the first request); a renewal path uses the retained secret to silently request a fresh token on expiry with no caller-supplied secret needed; tenant validation rejects `organizations`/`common`/`consumers` and anything that is not a GUID or DNS-style domain, **before** any outbound request; mock-transport unit tests cover success, invalid tenant, wrong client id, provider error, transient/network error, silent renewal after simulated expiry, supersession by a device-code start, and `logout()` clearing the retained secret; using a blocking/controllable mock transport, tests also cover **in-flight stale-response races**: a `logout()` or a new `start()`/app-only call issued while an initial client-credentials request or a silent-renewal request is still outstanding must not let that stale response install a token, retain, or recreate secret state once it completes — mirroring the existing device-code `AuthManager`'s generation-counter guard; a test asserts the fake secret literal appears in no return value, no exception message, no `repr()` of the manager, and no captured `logging`/stderr output; a test asserts provider error text containing the secret is scrubbed; `graph.py` and `server.py` are untouched (proving brief A6); `unittest`, `py_compile`, `validate_repo.py` pass | **Medium–high** (first live-secret handling; retained for the session per `DECISION-014`) | `PENDING` |
| 9 | `ISSUE-0009` | `POST /api/auth/app` endpoint wiring the app-only mode to the existing server | `ISSUE-0008` | Endpoint reuses the existing Host allowlist, Origin check, and body-size limit; validates `tenant`/`client_id`/`client_secret` presence and type; returns `{"state":"success"}` on success and a stable machine-label error otherwise; maps invalid input → 400, provider rejection → 502, never 5xx with a stack; `/api/policies` and `/api/analysis` work unchanged after an app-only sign-in (mock Graph transport); `/api/auth/logout` clears app-only state; a test scans **every** response body across success, each failure path, and the malformed-body path for the fake secret literal and fails if found; a test asserts nothing is written to the access log; `no-store` on any response reflecting auth state; `unittest`, `py_compile`, `validate_repo.py` pass | **Medium–high** | `PENDING` |
| 10 | `ISSUE-0010` | Sign-in card mode toggle and app-only form in `web/index.html` + `web/app.js` | `ISSUE-0009` | Default view is unchanged device-code; an explicit toggle reveals tenant ID / client ID / client secret fields; secret input is `type="password"` with `autocomplete="off"`; the value is never written to `console`, `localStorage`, `sessionStorage`, a cookie, a URL, or a query string; the field is cleared after submit, on mode switch, and on logout; a short in-page caution names what the secret grants; client-side rejection of `organizations`/`common`/`consumers` mirrors the server; existing CSP and text-only rendering rules unchanged; extended `tests/test_ui_safety.py` static assertions cover each of the above against the committed `web/` sources; `unittest`, `py_compile`, `validate_repo.py` pass | Medium | `PENDING` |
| 11 | `ISSUE-0011` | M2 documentation finalization and dual-mode walkthrough | `ISSUE-0007..0010` | README documents both modes, the exact app-only prerequisite (a user-owned app registration with **application** `Policy.Read.All` already consented), that CAreview never creates one, that certificates are unsupported **in this release and recorded as a deferred future enhancement** (would need its own dependency-approval decision, e.g. `cryptography`), that the secret is session-only with silent renewal, and how to rotate/revoke it; `docs/security-boundaries.md` records the trust-boundary delta and the widened `RISK-002`; a documented end-to-end walkthrough exists for each mode, with the live steps marked as protected actions the reader performs themselves; no live run is required to complete this issue; `unittest`, `py_compile`, `validate_repo.py` pass from a clean checkout | Low | `PENDING` |

#### Per-issue boundaries

| Issue | Allowed paths | Explicitly out of scope | Documentation in the same change |
|---|---|---|---|
| `ISSUE-0007` | `auth.py`, `tests/test_auth.py`, `README.md`, `docs/security-boundaries.md` | Any app-only code; `graph.py`; `server.py`; UI | Scope list corrections in README and security-boundaries |
| `ISSUE-0008` | `auth.py`, `tests/test_auth.py` | `server.py`, `web/`, `graph.py`, any persistence, any certificate path, any env-var input | Module docstring stating the secret lifecycle and retention decision |
| `ISSUE-0009` | `server.py`, `tests/test_server.py`, `README.md` | `web/`, `graph.py`, changes to `auth.py` beyond calling it, any new dependency | README API section entry for the new endpoint (in this issue's own change, since `README.md` is in its allowed paths) |
| `ISSUE-0010` | `web/index.html`, `web/app.js`, `web/style.css`, `tests/test_ui_safety.py`, `README.md` | Server or auth logic; new external assets; CSP relaxation | In-page caution text; README screenshot-free description of the toggle (in this issue's own change, since `README.md` is in its allowed paths) |
| `ISSUE-0011` | `README.md`, `docs/security-boundaries.md`, `project/` records | Any product source change (a source change here reopens the issue as an implementation issue) | This issue *is* the documentation change |

## Verification strategy

- Unit checks: `python3 -m unittest discover -s tests` (auth handling for **both**
  modes, Graph paging/normalization, analyzer scoring on fixtures, health, UI
  static-safety assertions).
- **(v4) Secret-leak checks:** every M2 auth/server test uses a mock transport and
  a synthetic secret literal, and asserts that literal is absent from every
  response body, exception message, `repr()`, and captured log stream across
  success and every failure path. These are ordinary `unittest` assertions and
  require no tenant, no network, and no credential.
- **(v4) Tracked-file check:** the synthetic literal is the only secret-shaped
  string permitted in the repository; `python3 scripts/validate_repo.py` plus
  reviewer inspection covers tracked-file hygiene.
- Integration checks: manual, human-run live sign-in and policy fetch — in either
  mode — is a **protected action** requiring separate human approval naming the
  tenant (Codex F-002); it is never a completion precondition. **(v4)** A live
  app-only run additionally involves a real client secret and must not be
  performed by an agent under any circumstances.
- Security checks: `python3 -m py_compile $(git ls-files '*.py')`; manual review
  that tokens, secrets, and policy data never reach disk, logs, or the repo;
  milestone security review, which for M2 must report the secret lifecycle as a
  named check.
- Documentation checks: run README steps for both modes from a clean checkout in
  ISSUE-0011, stopping short of the protected live steps.
- Clean-environment / onboarding check: fresh clone → `python3 server.py` with no
  installs.
- Evidence gaps requiring human judgement: live-tenant behaviour in both modes
  (A1/A2/A6/A7); whether first-party device-code is permitted in the target
  tenant; whether the user's app registration holds application permissions
  beyond `Policy.Read.All` (unknowable to CAreview — see `RISK-006`).

Agent-reported claims are not test evidence. Record actual commands, commit SHA,
exit status, and limitations in each handoff.

## Documentation plan

- `M1`: README run/verify instructions (kept accurate as issues land), an
  end-to-end walkthrough, and per-issue handoffs. Security boundaries already
  documented in `docs/security-boundaries.md`; update if the threat model shifts.
- **(v4)** `M2`: README dual-mode setup and run instructions, including the exact
  prerequisite for app-only mode, the explicit statements that CAreview never
  creates an app registration and does not store the secret, and a clearly
  labeled **"planned future enhancement"** note that certificate-based auth is
  not yet supported and would require a separate dependency-approval decision;
  a rotation/revocation pointer; `docs/security-boundaries.md` threat-model
  delta for the widened trust boundary; per-issue handoffs.

## Risks and decisions

| ID | Risk or decision | Impact | Owner | Treatment or decision record | Review date |
|---|---|---|---|---|---|
| `RISK-001` | Tenant blocks first-party device-code or withholds `Policy.Read.All`, so live fetch fails | Medium — MVP can't read live policies until fallback | Jay (@Jay-cli) | Accepted for MVP per `DECISION-001`. **(v4)** Partially mitigated by M2: a user who already has an app registration with application `Policy.Read.All` can use app-only mode instead. Not mitigated for a user without one. Offline fixtures keep the analyzer verifiable regardless | On M2 acceptance |
| `RISK-002` | **(v4 — materially widened; re-accepted `DECISION-014`)** Local loopback API reachable by another local process, browser extension, or local user while credential material is in memory. M1 exposed a scoped, delegated, read-only user token. M2 additionally exposes a **client secret** in transit through the browser page and the loopback POST body, behind the same "no local authentication" boundary — and, per `DECISION-014`, retained for the **whole app-only session**, not just one token request | **Medium–high** in app-only mode (was low–medium) | Jay (@Jay-cli) | **Accepted as widened per `DECISION-014`**, on the basis that the tool is single-user and local, trading a longer retention window for no hourly re-entry. `DECISION-001`'s original acceptance did not itself cover this; this is the fresh acceptance. Mitigations unchanged: no persistence, no echo, no logging, Host/Origin checks retained | Re-checked at M2 security review |
| `RISK-003` | Accidental logging of tokens or policy JSON | Medium (sensitive data exposure) | Claude (impl), reviewed by Codex | Redact by construction; unit/security review checks that tokens and policy data are never logged or persisted. **(v4)** Extended to the client secret with explicit per-path assertions | Per issue |
| `RISK-004` | Score is a heuristic, mistaken for compliance certification | Low (reputational/interpretation) | Jay (@Jay-cli) | Document each rule's weight and label the score non-authoritative in the UI and README | ISSUE-0004 (closed); revisit at M2 acceptance |
| `RISK-005` | **(v4, new)** Client secret exposed browser-side: extension, devtools, screen capture, shoulder-surfing, browser autofill or form history caching a submitted secret, or the value lingering in page memory. The device-code path has no equivalent failure mode | Medium–high (credential disclosure) | Jay (@Jay-cli) | The owner has explicitly chosen UI form-field entry over an environment variable, accepting browser transit (brief v2, Confirmed facts). Mitigations: `type="password"`, `autocomplete="off"`, no console/storage/URL writes, field cleared on submit/mode-switch/logout, in-page caution. This covers the one-time entry only; the entered value's server-side retention for the session is governed separately by `RISK-002`/`DECISION-014` | Before `ISSUE-0010`; re-checked at M2 security review |
| `RISK-006` | **(v4, new)** Over-broad app-only token. `.default` returns every application permission the user's app already holds; CAreview cannot request a narrower app-only scope (brief A7). If the app also holds, say, write permissions, CAreview receives a token capable of far more than it uses | Medium (excess privilege in memory) | Jay (@Jay-cli) | Not technically suppressible by the client. Treatment is documentation plus UI caution: recommend a dedicated app registration holding only application `Policy.Read.All`. Must be recorded as an accepted residual, not presented as mitigated | `ISSUE-0011`; M2 security review |
| `RISK-007` | **(v4, resolved `DECISION-014`)** Originally: hourly re-authentication burden with no refresh token. **Superseded:** per `DECISION-014`, the secret is retained for the session and used to silently renew the app-only token on expiry, so no re-entry is required. The traded-off cost is `RISK-002`'s widened retention window, not user friction | Low (was low–medium; friction removed, retention cost moved to RISK-002) | Jay (@Jay-cli) | `ISSUE-0008` must implement silent renewal from the retained secret, per `DECISION-014`; document that persistence to disk remains a hard non-goal regardless | `ISSUE-0008` |
| `RISK-008` | **(v4, new)** A real client secret is pasted into a test, fixture, issue record, handoff, log, or review report during development or triage | High if it occurs (credential in Git history) | Claude (impl), reviewed by Codex | Prohibited by `AGENTS.md`. Enforced here by requiring a synthetic literal in all tests, by never performing a live app-only run in an agent task, and by an explicit reviewer check on every M2 diff | Every M2 issue |

Critical or high security findings cannot use the default risk-acceptance path.
`RISK-002` as widened, `RISK-005`, `RISK-006`, and `RISK-007` were each decided
by the human (`DECISION-014`) rather than accepted or inferred by an agent.

## Definitions of done

### Issue

- Approved scope and acceptance criteria satisfied.
- Required checks ran against the candidate commit with real results recorded.
- Tests and documentation updated in the same change.
- `scripts/run-codex-review.sh issue ...` launched a fresh read-only Codex review of the exact base/head, and its committed report has no unresolved blocker.
- Repair rounds did not exceed two.
- Residual risks and the human advance decision recorded.
- Handoff, review, decision, issue state, and `project/status/CURRENT.md` committed; the Claude issue task ended before the next issue begins.

### Milestone

- All planned issues and dependencies complete.
- Claude and Codex general reviews pass against the frozen candidate.
- Claude and Codex security reviews pass against that same candidate.
- Critical and high findings closed.
- Other material risks repaired or explicitly accepted by the human where permitted.
- General remediation ≤ one cycle, security remediation ≤ two cycles, no loop > five iterations.
- Documentation, integration, and release-readiness evidence complete.
- The human approves the exact milestone package.

### Project

- Every milestone approved (here, M1 = the whole MVP).
- Fresh full-project Claude and Codex general and security reviews against one final commit.
- Installation, onboarding, rollback, support, security, and known limitations accurate.
- The human records final approval.

## Planning reconciliation

| Round | Codex review | Claude response | Remaining decision |
|---:|---|---|---|
| 1 | `ROADMAP-691b1427de57-codex.json` (BLOCKED, 5 findings) | `ROADMAP-691b1427de57-claude-response.md` (F-002..F-005 accepted; F-001 via prompt convention) | Resolved in v2 |
| 2 | `ROADMAP-4daf03ca5be5-codex.json` (BLOCKED, 4 findings) | `ROADMAP-4daf03ca5be5-claude-response.md` (F-001..F-003 accepted → v3; F-004 is a review-sandbox limitation with out-of-band validator evidence) | Presented to human: approved as v3 (`DECISION-003`) |
| 3 (v4) | **Not yet run.** Required: commit this v4 candidate, set the `claudex-state` stage to `ROADMAP_REVIEW` with both active IDs `none`, then run `./scripts/run-codex-review.sh plan <FULL-V4-HEAD-SHA>` (PowerShell: `.\scripts\run-codex-review.ps1 plan <FULL-V4-HEAD-SHA>`) | Not yet written | **Open.** No Codex plan review of v4 exists; no human approval of v4 exists |

### v4 reconciliation note

This v4 delta has had no independent review yet. Specifically, and stated so no
later reader infers otherwise:

- No Codex plan review has been run against roadmap v4. The v3 reviews
  (`ROADMAP-691b1427de57`, `ROADMAP-4daf03ca5be5`) reviewed a roadmap that
  contained no M2, no app-only mode, and no client secret; they say nothing
  about this content and cannot be carried forward to it.
- `DECISION-003` binds roadmap **v3** at `125d74f`. It does not extend to v4.
  Until a new decision record names v4 at its exact commit, v3 is the approved
  roadmap and no M2 issue may begin.
- The expected sequence is: commit v4 → fresh Codex plan review at that SHA →
  Claude responds to every finding (at most two revision rounds) → human
  approves the exact final v4 → `ISSUE-0007` starts in a new top-level Claude
  task.
- Unlike the reverted `origin/claude/graph-auth-without-cli-8om0zw` draft this
  supersedes, brief v2 Questions 3/5/6 are already resolved (`DECISION-014`)
  before this v4 candidate was written, so no open question blocks
  `ISSUE-0008` beyond the plan review and roadmap approval themselves.

Maximum two repair rounds. Any remaining material disagreement is shown to the
human before exact roadmap approval. No workflow loop may exceed five total
iterations.

## Change control

After approval, do not silently edit this roadmap. A proposed change must state
the approved version/commit, the exact diff, its effect on scope/sequence/risk,
which approvals become stale, and the new human decision. A changed roadmap
requires a new version and exact approval.

**Status columns are the one exception.** The `Status` cells in the milestone and
issue tables, and the `Delivery status` line at the top, are live delivery
tracking. Updating them to match the committed evidence in
`project/status/CURRENT.md` and `project/milestones/M1.md` changes no scope,
sequence, acceptance criterion, or risk, and does not make `DECISION-003` stale:
the approved artifact remains roadmap **v3** as bound at
`125d74f6d4bfe85f1a727293064d0887f2d121c7`. Any edit beyond a status cell is a
roadmap change and needs a new version and a new exact approval.

**(v4)** This version is itself such a change. It adds a milestone, five issues,
five new/modified risks, a materially widened `RISK-002`, and a narrowed
non-goal. It therefore requires its own Codex plan review and its own human
decision record; `DECISION-003` does not cover it. The approved-and-executed M1
content above is unchanged by v4 except where explicitly marked `(v4)`.
