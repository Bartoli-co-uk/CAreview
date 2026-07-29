# Project roadmap — CAreview

This is the canonical project roadmap for CAreview, a locally-hosted Conditional
Access policy analyzer.

**Current status:** `APPROVED` (roadmap **v5**, approved `DECISION-029` directly from the round-2 review record — see below. v4 remains separately approved and continues to govern the completed M1 and M2 content below; nothing in v5 changes it).
**Roadmap version:** `5`
**Approved brief:** `project/brief/PROJECT_BRIEF.md` v1 at `179a02354aecbafa2c9d5aa34f9c9a5a04bbc79a` (DECISION-001) — governs M1
**Amending brief:** `project/brief/PROJECT_BRIEF.md` v2 at `9ccf835`, approved by `DECISION-013`; open questions resolved by `DECISION-014` — governs M2 below
**Governing decision for M3:** `project/decisions/DECISION-024-react-frontend-build-step.md`. **(v5)** M3 has **no** governing brief section. It was delivered under a direct human override rather than a brief/roadmap cycle, and this roadmap version records that fact rather than papering over it — see the M3 issue sequence preamble.
**Codex plan review:** v3 rounds recorded in Planning reconciliation below. v4: four rounds recorded below (`ROADMAP-71f7ba60b045-*`, `ROADMAP-605c282c5c81-*`, `ROADMAP-76a09c46a57d-*`, `ROADMAP-faf5ec70bf00-*`); the review/repair loop's absolute five-iteration cap (`AGENTS.md`) was reached, and the human approved directly from that record. **(v5) Round 1: `CHANGES_REQUIRED`** — `project/reviews/plans/ROADMAP-441b4da0d3ba-codex.json`, reviewed candidate `441b4da0d3ba0d9d13dcf0d710bdae5a1c0685ab`. F-001 (high): `ISSUE-0014` had no work-item record — fixed, `project/issues/ISSUE-0014.md` added. F-002 (medium): `project/status/CURRENT.md` named a stale candidate SHA — fixed. F-003 (medium): `ISSUE-0014`'s negative-CI acceptance criterion depended on an unspecified protected external action — fixed, a local-verification procedure is now specified in that issue record. F-004 (question): `RISK-009` needed an exact human treatment decision before v5 could be approved — **resolved**, accepted as residual per `DECISION-028`. **Round 2: `CHANGES_REQUIRED`** — `project/reviews/plans/ROADMAP-9bd2c0f8f6fb-codex.json`, reviewed candidate `9bd2c0f8f6fb5f4153be0cf5661f63929449ce85`. F-001 (medium): `ISSUE-0014`'s negative-CI fallback proof doesn't verify workflow-level failure propagation, only that Vitest itself can fail. F-002 (medium): `RISK-010` was described inconsistently (accepted vs. undecided) across this file and `CURRENT.md`. This was the second and final permitted planning-repair round (`AGENTS.md`); per `DECISION-029`, the human approved v5 directly from this record, accepting both round-2 findings as documented residuals rather than authorizing a third repair round — the same disposition `DECISION-015` used for v4 at its own iteration cap.
**Human approval record:** `project/decisions/DECISION-003-roadmap-approval.md` (APPROVE, binds v3 at `125d74f6d4bfe85f1a727293064d0887f2d121c7`); `project/decisions/DECISION-015-roadmap-v4-approval.md` (APPROVE, binds **v4** at `9e5ba6d`). **(v5)** `project/decisions/DECISION-029-roadmap-v5-approval.md` (APPROVE, binds **v5** at `8ea41ee`).
**Delivery status:** `M1` COMPLETE and accepted (`DECISION-012`); all six issues merged. `M2` is `COMPLETE` and accepted (`DECISION-023`); `ISSUE-0007` COMPLETE and merged (`DECISION-016`); `ISSUE-0008` COMPLETE and merged (`DECISION-017`); `ISSUE-0009` COMPLETE and merged (`DECISION-019`); `ISSUE-0010` COMPLETE and merged (`DECISION-020`); `ISSUE-0011` COMPLETE and merged (`DECISION-022`) — all five planned M2 issues are merged and the M2 milestone acceptance gate has passed. **(v5)** `M3` (React/TypeScript dashboard UI) has all three of its planned issues merged — `ISSUE-0012` (`DECISION-025`), `ISSUE-0013` (`DECISION-027`), and `ISSUE-0014` (`DECISION-031`) — but the milestone itself is **not** complete: **none of the four blind milestone reviews has been run**. Current state: `project/status/CURRENT.md`.

No implementation may begin until a human records approval of the exact roadmap
version and commit. Roadmap v4 remains a separately approved artifact governing
M1 and M2, both of which are delivered. **(v5)** This version is now approved
(`DECISION-029`, binding `8ea41ee`): it adds `M3`, three issues, and three
risks. Approval of the roadmap does not by itself start an issue — that
still needs its own separate human decision, as `ISSUE-0014`'s own start
(`DECISION-030`) did. All three of v5's issues (`ISSUE-0012`, `ISSUE-0013`,
`ISSUE-0014`) are now `COMPLETE` and merged.

## Project outcome

When complete, running `python3 server.py` starts a local, standard-library-only
web app on `http://localhost:8765`. The user clicks *Sign in*, completes an OAuth
2.0 device-code sign-in against a Microsoft first-party public client, and the app
fetches the tenant's Conditional Access policies from Microsoft Graph. It shows a
0–100 security score, a severity-sorted list of best-practice / vulnerability
findings, and a simple per-policy visualization (Users → Conditions → Apps →
Controls). The analyzer is unit-tested offline against committed sanitized
fixtures. No Azure app registration, no client secret, and no third-party
Python packages are required **to use the default (M1) path**. **(DECISION-024)**
Node.js/npm is required once, to build the UI (`cd frontend && npm install &&
npm run build`); the running app itself still needs nothing beyond Python.
**(v4)** A user who already holds an Entra app registration with application
`Policy.Read.All` may instead opt into a second sign-in mode — client-credentials
with a secret they supply — for the same policies/score/findings output,
without changing anything for a user who does not opt in. Certificate-based
auth is not supported and is documented as a deferred future enhancement.

**(v5)** The "simple per-policy visualization" above describes the M1-era
vanilla-JS UI, which no longer exists. What ships now is a multi-page React +
TypeScript dashboard (`frontend/src/pages/`) serving two audiences from the
same data: an at-a-glance Overview for a non-specialist reader, and Policies /
Policy Explorer / Insights / Recommendations / Reports / Audit Log / Settings /
About for a practitioner. It consumes the unchanged `/api/policies` and
`/api/analysis` contract — M3 added no analyzer capability and no new backend
data source; the Insights page derives its figures client-side
(`frontend/src/lib/deriveInsights.ts`) precisely so that no new endpoint was
needed. The served artifact is still a static bundle under the same
`default-src 'self'` CSP and the same loopback-only binding.

## Users and success measures

| User or stakeholder | Need | Measurable success criterion |
|---|---|---|
| Security practitioner (owner) | Assess a tenant's CA posture locally | Product goal: signs in and sees policies, a 0–100 score, and findings for their tenant. M1 acceptance is proven on mocked/fixture evidence; the live sign-in against a real tenant is a separately approved protected step (a residual evidence gap the human accepts), not an M1 gate (F-003) |
| Tenant admin (consent) | Grant least-privilege read access | One-time consent to read-only Graph scopes for the default mode; no standing app registration required for that mode. **(v4)** A user opting into app-only mode instead brings their own already-consented app registration — CAreview never creates or requests one |
| Project reviewers | Correct, safe build | Each issue has a committed passing Codex review; milestone passes four blind reviews |

## Constraints and non-goals

### Constraints

- Python 3.10+ standard library only; no third-party packages, no build step —
  **for the backend** (`server.py`, `auth.py`, `graph.py`, `analyzer.py`,
  `rules.py`). **(DECISION-024)** The UI is a documented exception: it is now
  a React/TypeScript app built with Vite (`frontend/`, requiring Node.js/npm
  to build), replacing the earlier hand-written vanilla-JS/HTML/CSS `web/`
  UI. The served artifact remains a static bundle with the same CSP and
  loopback-only posture; only *producing* it now requires a build step. See
  `project/decisions/DECISION-024-react-frontend-build-step.md`.
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
- **(v5) The exact bounds of the `DECISION-024` build-step exception.** Stated
  once, as a constraint in its own right rather than as an aside, because it is
  the only place this project permits a dependency toolchain at all:
  - **Permitted:** a Node.js/npm toolchain whose sole job is compiling
    `frontend/` into `web/index.html`, `web/index.css`, and `web/index.js`.
  - **Not permitted by it:** any third-party *runtime* dependency in the Python
    backend, which stays stdlib-only; any CSP relaxation; any persistence; any
    binding beyond loopback; any new Graph scope; any external/CDN asset
    fetched by the served page. The build's output is plain static files —
    nothing is fetched at runtime.
  - **Consequence, not a side note:** the build introduces a transitive
    dependency graph (`frontend/package-lock.json`) that the backend
    deliberately does not have. That is a real trust boundary and is tracked
    as `RISK-009`, not treated as covered by the exception itself.
  - **Consequence for onboarding:** `web/index.html`/`index.js`/`index.css` are
    generated and gitignored, so a fresh clone will **not** serve a UI until
    `npm install && npm run build` has run. Tracked as `RISK-010`.

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
  new sign-in (either mode), and on process exit, same as a token.
  **Provider-supplied error text (from the identity endpoint) is never
  returned to the client or written to a log at all** — literal-only
  secret scrubbing cannot be trusted to catch every transformed
  representation (URL-encoded, JSON-escaped, partially reflected) of an
  untrusted error body, so the safer rule is to map every provider failure
  to one of a small set of stable, locally-defined error labels (e.g.
  `invalid_tenant`, `provider_error`, `network_error`) and discard the raw
  provider text entirely, rather than attempt to sanitize and forward it.
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
| `M2` | Least-privilege delegated scope, plus an **opt-in** app-only (client-credentials, secret-only) sign-in mode beside the unchanged device-code default | `M1` COMPLETE; brief v2 APPROVED (`DECISION-013`); secret-retention/RISK-002/tenant-validation decided (`DECISION-014`) | All five M2 issues COMPLETE; `python3 -m unittest discover -s tests`, `python3 -m py_compile $(git ls-files '*.py')`, and `python3 scripts/validate_repo.py` pass at one frozen candidate; every pre-existing device-code test still passes unmodified in behaviour; mock-transport tests prove **the real submitted secret** appears in **no** API response body, **no** log record, and **no** tracked file (the committed synthetic test-sentinel literal used to exercise these tests is expected in `tests/` and is not itself a violation); `auth.py` requests only `Policy.Read.All` delegated; README and `docs/security-boundaries.md` describe both modes, the app-only prerequisites, the secret's lifetime, and certificate support as a deferred future enhancement; four blind milestone reviews against that one SHA, with the **security** pair required to treat the end-to-end secret lifecycle — field → POST body → server memory, **retained for the app-only session and reused to silently renew the token on expiry**, then **cleared on logout, on supersession by a new sign-in, and on process exit** (never discarded after a single use) — as a **named, separately reported check** (brief v2 requirement), not folded into general review. Live app-only sign-in against a real tenant is **not** an exit criterion — it stays a protected action and a declared evidence gap | `COMPLETE` (`DECISION-023`) |
| `M3` **(v5)** | React/TypeScript dashboard UI (`frontend/`, built with Vite) replacing the vanilla-JS `web/` UI, against the unchanged `/api/policies` + `/api/analysis` contract | `M2` COMPLETE; `DECISION-024` (build-step exception) | `ISSUE-0012`, `ISSUE-0013`, and `ISSUE-0014` all COMPLETE and merged — **all three satisfied**; `python3 -m unittest discover -s tests`, `python3 -m py_compile $(git ls-files '*.py')`, `python3 scripts/validate_repo.py`, and `cd frontend && npm test` all pass at one frozen candidate, and CI now runs the frontend build/tests too (`ISSUE-0014`); the served bundle keeps `default-src 'self'` with no external asset and no new endpoint; untrusted tenant strings still render as text (JSX escaping, asserted by both `frontend/src/test/hostileMarkup.test.tsx` and `tests/test_ui_safety.py`); four blind milestone reviews against that one SHA — **none has been run** | `ISSUES DELIVERED — milestone gate not run` |

**(v5) Why `M3` is not marked `COMPLETE`.** Its two delivered issues each
passed the per-issue Codex gate and carry a human merge decision, so the
*code* is as reviewed as M1's and M2's was. The milestone gate is a different,
additional gate: four blind reviews against one frozen candidate. For M3 that
gate has not run at all. `M1` and `M2` earned `COMPLETE` through it
(`DECISION-012`, `DECISION-023`), and M3 has not, so it does not carry the
same word. Whether to run that gate — and whether to do it before or after
`ISSUE-0014` — is a human decision this roadmap does not presume.

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

### M2 issue sequence (COMPLETE — accepted `DECISION-023`)

Prerequisite gate, before `ISSUE-0007` may start: a decision record approving
brief v2 at its exact commit (satisfied — `DECISION-013` binds `9ccf835`).
Before `ISSUE-0008` specifically: `DECISION-014` resolves secret retention
(session-lifetime, silent renewal), `RISK-002` (accepted as widened, on that
basis), and tenant-value validation (client-side, mirroring the server) — all
satisfied.

| Order | Issue | Objective | Depends on | Acceptance and checks | Risk | Status |
|---:|---|---|---|---|---|---|
| 7 | `ISSUE-0007` | Trim delegated `SCOPES` to `Policy.Read.All` only | Brief v2 approved | `auth.py` `SCOPES` contains exactly `https://graph.microsoft.com/Policy.Read.All`; a unit test asserts the constant and that the device-code request body carries only that scope; every existing test in `tests/test_auth.py` still passes with no behavioural change to the flow; README and `docs/security-boundaries.md` no longer claim three delegated scopes; `unittest`, `py_compile`, `validate_repo.py` all pass | Low | `COMPLETE` (`b314d82`, merged `0c35851`, `DECISION-016`) |
| 8 | `ISSUE-0008` | App-only token acquisition inside `auth.py` only — no HTTP endpoint, no UI | `ISSUE-0007`; `DECISION-014` (retention model, RISK-002 acceptance) | Pure auth-layer change: a `build_client_credentials_request()` and an `AuthManager` method that installs an app-only token in the existing token slot **and retains the secret in the manager instance for the session** (per `DECISION-014` — not discarded after the first request); a renewal path uses the retained secret to silently request a fresh token on expiry with no caller-supplied secret needed; tenant validation rejects `organizations`/`common`/`consumers` and anything that is not a GUID or DNS-style domain, **before** any outbound request; mock-transport unit tests cover success, invalid tenant, wrong client id, provider error, transient/network error, silent renewal after simulated expiry, supersession by a device-code start, and `logout()` clearing the retained secret; using a blocking/controllable mock transport, tests also cover **in-flight stale-response races**: a `logout()` or a new `start()`/app-only call issued while an initial client-credentials request or a silent-renewal request is still outstanding must not let that stale response install a token, retain, or recreate secret state once it completes — mirroring the existing device-code `AuthManager`'s generation-counter guard; a test asserts the fake secret literal appears in no return value, no exception message, no `repr()` of the manager, and no captured `logging`/stderr output; **raw provider error text is never returned by any public method or stored** — a failed request maps to one of a small, fixed set of local error labels regardless of the provider's response body, and a test asserts this holds even when the mock provider's error body contains the secret literally, URL-encoded, JSON-escaped, or split across surrounding text; `graph.py` and `server.py` are untouched (proving brief A6); `unittest`, `py_compile`, `validate_repo.py` pass | **Medium–high** (first live-secret handling; retained for the session per `DECISION-014`) | `COMPLETE` (`2051254`, merged `04e68ee`, `DECISION-017`) |
| 9 | `ISSUE-0009` | `POST /api/auth/app` endpoint wiring the app-only mode to the existing server | `ISSUE-0008` | Endpoint reuses the existing Host allowlist, Origin check, and body-size limit; validates `tenant`/`client_id`/`client_secret` presence, type, **and bounded format** before any value is retained or transported outbound — `tenant` must be a GUID or a DNS-style domain label under a documented maximum length (rejecting `organizations`/`common`/`consumers` per `DECISION-014`); `client_id` must match the GUID shape Entra app IDs use; `client_secret` must be a non-empty string under a documented maximum length (generous enough for a real Entra secret, e.g. 512 characters) — oversized or malformed values on any of the three fields are rejected with 400 **before** an identity request is made and without being retained in `AuthManager` state; boundary tests cover minimum, maximum, one-over-maximum, and malformed values for each field, asserting no outbound call and no retained state on rejection; returns `{"state":"success"}` on success and a stable machine-label error otherwise; maps invalid input → 400, provider rejection → 502 with a stable local error label only (never the raw provider response body or text), never 5xx with a stack; `/api/policies` and `/api/analysis` work unchanged after an app-only sign-in (mock Graph transport); with mocked identity and Graph transports and a simulated expired app-only token, a test verifies silent renewal succeeds transparently and both `/api/policies` and `/api/analysis` complete against the newly renewed token, and a separate test verifies a renewal failure (provider/network error) surfaces a stable, non-secret, non-5xx error from those endpoints rather than a stale or missing token; `/api/auth/logout` clears app-only state; a test scans **every** response body across success, each failure path, and the malformed-body path for the fake secret literal — including its URL-encoded and JSON-escaped forms — and fails if found; a test asserts nothing is written to the access log; `no-store` on any response reflecting auth state; `unittest`, `py_compile`, `validate_repo.py` pass | **Medium–high** | `COMPLETE` (`7b0600f0831f68f8933b68ca0bba34f58a00b0cc`, merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`) |
| 10 | `ISSUE-0010` | Sign-in card mode toggle and app-only form in `web/index.html` + `web/app.js` | `ISSUE-0009` | Default view is unchanged device-code; an explicit toggle reveals tenant ID / client ID / client secret fields; secret input is `type="password"` with `autocomplete="off"`; the value is never written to `console`, `localStorage`, `sessionStorage`, a cookie, a URL, or a query string; the field is cleared after submit, on mode switch, and on logout; a short in-page caution names what the secret grants; client-side rejection of `organizations`/`common`/`consumers` mirrors the server; existing CSP and text-only rendering rules unchanged; extended `tests/test_ui_safety.py` static assertions cover each of the above against the committed `web/` sources; **because no JavaScript test toolchain exists (stdlib-only constraint), the runtime clearing behavior itself — not just the presence of the clearing code — is additionally verified by a documented manual browser walkthrough** (synthetic tenant/client/fake-secret values, browser dev tools inspecting the field/DOM/console after each of: successful submit, mode switch, and logout) with its observed results recorded in the issue handoff as evidence, alongside the static assertions; `unittest`, `py_compile`, `validate_repo.py` pass | Medium | `COMPLETE` (`2a2d0b73e94d2635a645728e5b78f7f500c0a6b2`, merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`) |
| 11 | `ISSUE-0011` | M2 documentation finalization and dual-mode walkthrough | `ISSUE-0007..0010` | README documents both modes, the exact app-only prerequisite (a user-owned app registration with **application** `Policy.Read.All` already consented), that CAreview never creates one, that certificates are unsupported **in this release and recorded as a deferred future enhancement** (would need its own dependency-approval decision, e.g. `cryptography`), that the secret is session-only with silent renewal, and how to rotate/revoke it; `docs/security-boundaries.md` records the trust-boundary delta and the widened `RISK-002`; a documented end-to-end walkthrough exists for each mode, with the live steps marked as protected actions the reader performs themselves; no live run is required to complete this issue; `unittest`, `py_compile`, `validate_repo.py` pass from a clean checkout | Low | `COMPLETE` (`e878cdcd979b7be87ff20cc986cb16d0d457dfe0`, merged `b50cbc2fb67e8066f22ab06a03f61425dbf1a9d1`, `DECISION-022`) |

#### Per-issue boundaries

| Issue | Allowed paths | Explicitly out of scope | Documentation in the same change |
|---|---|---|---|
| `ISSUE-0007` | `auth.py`, `tests/test_auth.py`, `README.md`, `docs/security-boundaries.md` | Any app-only code; `graph.py`; `server.py`; UI | Scope list corrections in README and security-boundaries |
| `ISSUE-0008` | `auth.py`, `tests/test_auth.py` | `server.py`, `web/`, `graph.py`, any persistence, any certificate path, any env-var input | Module docstring stating the secret lifecycle and retention decision |
| `ISSUE-0009` | `server.py`, `tests/test_server.py`, `README.md` | `web/`, `graph.py`, changes to `auth.py` beyond calling it, any new dependency | README API section entry for the new endpoint (in this issue's own change, since `README.md` is in its allowed paths) |
| `ISSUE-0010` | `web/index.html`, `web/app.js`, `web/style.css`, `tests/test_ui_safety.py`, `README.md` | Server or auth logic; new external assets; CSP relaxation | In-page caution text; README screenshot-free description of the toggle (in this issue's own change, since `README.md` is in its allowed paths) |
| `ISSUE-0011` | `README.md`, `docs/security-boundaries.md`, `project/` records | Any product source change (a source change here reopens the issue as an implementation issue) | This issue *is* the documentation change |

### M3 issue sequence **(v5)** (delivered out-of-band; milestone gate not run)

**Read this preamble before the table.** `ISSUE-0012` and `ISSUE-0013` were
implemented, reviewed, and merged **before** any roadmap entry for them
existed. The human explicitly chose that path (`DECISION-024`): asked how to
reconcile a dashboard rebuild with `AGENTS.md`'s requirement that
implementation wait on an approved brief and roadmap, they selected "Direct
override — build it now, record the decision after," relying on `AGENTS.md`'s
own instruction-order rule, which places the human's current explicit
instructions above this roadmap.

Recording those issues here does **not** retroactively supply the brief and
roadmap cycle they skipped, and does not convert the direct override into a
planning gate that was met. Both statements stay true after this edit:

- The per-issue Codex review gate **was** applied to both, retroactively and
  in full — three rounds each, every round a fresh ephemeral read-only
  process, each ending in a recorded human decision (`DECISION-025`,
  `DECISION-027`). Neither issue's residual was accepted by an agent.
- The pre-implementation planning gate was **not** applied and cannot now be.

What this section changes is narrower and worth doing anyway: the two issues
stop being orphans. Before it, `project/issues/ISSUE-0012.md` and
`ISSUE-0013.md` both read `Milestone: None` / `Approved roadmap: N/A`, so the
largest single change to the product had no parent in the roadmap, and
`ISSUE-0014` had nowhere to attach.

| Order | Issue | Objective | Depends on | Acceptance and checks | Risk | Status |
|---:|---|---|---|---|---|---|
| 12 | `ISSUE-0012` | Replace the vanilla-JS `web/` UI with a React + TypeScript dashboard built by Vite, against the unchanged API contract | `DECISION-024`; M2 delivered | Retroactive record of work already done. The dashboard builds via `npm run build` into `web/`'s fixed, non-hashed filenames (`server.py` serves an explicit `STATIC_FILES` allowlist, not a directory); `server.py` changes limited to that allowlist; untrusted tenant strings render as text, asserted from both sides (`hostileMarkup.test.tsx`, `tests/test_ui_safety.py`); a `noDangerousSinks.test.ts` scan rejects dangerous DOM/code sinks across `src/`; `unittest`, `py_compile`, `validate_repo.py`, and `npm test` all pass | Medium — largest single product change; no pre-implementation review | `COMPLETE` (`195bd8e746884c23b4774162667ee5905f2680e1`, merged `5189959392ec2331c799199f5d70457ff361a3ba`, `DECISION-025`) — merged with a **tracked residual**, remediated by `ISSUE-0013` |
| 13 | `ISSUE-0013` | Scoped, server-side device-code session abandonment (`POST /api/auth/abandon`) | `ISSUE-0012` | `AuthManager.abandon(handle)` clears only the pending session or installed token produced by that exact handle, under the same lock as every other lifecycle transition, touching neither `_generation` nor app-only state — so a late abandon can never clear a different, newer, legitimately-current session; an unknown handle is a safe no-op; tests in both `tests/test_auth.py` and `tests/test_server.py` directly exercise that race | Medium — auth-lifecycle change | `COMPLETE` (`8858858a2090aa72d8d0b14a6de64a17a447c120`, fast-forwarded to `main` at `80156d32feb6f4b85debc44897d04563bb35998a`, `DECISION-027`) — merged with an **accepted residual** (see `RISK-011`) |
| 14 | `ISSUE-0014` | Wire the frontend build and test suite into CI | `ISSUE-0012` | `.github/workflows/validate.yml` gained a Node step (SHA-pinned `actions/setup-node`, Node 22) running `npm ci`, `npm run build`, and `npm test` in `frontend/`, after the three existing Python steps; negative-CI verification used the documented local fallback (`act` unavailable in the implementing environment) rather than a live push, per `project/issues/ISSUE-0014.md`'s acceptance criterion 2; `README.md`/`CONTRIBUTING.md` updated to say CI now covers the frontend | Low | `COMPLETE` (`f63a0dadae917f35b328b60b1a562aa535d97d10`, merged, `DECISION-031`) — merged with an **accepted sandbox execution-evidence residual** (round-2 Codex review `BLOCKED` with zero content findings, same pattern as `ISSUE-0011`) |

**Why `ISSUE-0014` is worth its own issue.** The frontend's test suite — 91
Vitest tests, including the hostile-markup and dangerous-sink checks that are
part of how this project argues the UI is XSS-safe — has never run in CI. It
runs only when someone runs it locally. `DECISION-024` recorded this as
untracked follow-up with no owner and no date; nothing has tracked it since.
Until it lands, "the frontend tests pass" is a claim about somebody's laptop.

#### Per-issue boundaries **(v5)**

| Issue | Allowed paths | Explicitly out of scope | Documentation in the same change |
|---|---|---|---|
| `ISSUE-0012` | `frontend/`, `web/` (build output + removal of superseded sources), `server.py` (`STATIC_FILES` only), `tests/test_ui_safety.py`, `.gitignore`, `scripts/validate_repo.py` (node_modules exclusion, JSONC tolerance), `README.md`, `AGENTS.md`, `ROADMAP.md`, `project/` records | Any auth/analyzer/Graph logic change; any new endpoint; any CSP relaxation; any backend dependency | `frontend/README.md`; README build step and dashboard description |
| `ISSUE-0013` | `auth.py`, `server.py`, `frontend/src/state/appState.tsx`, `tests/test_auth.py`, `tests/test_server.py`, `frontend/src/test/`, `docs/security-boundaries.md` | Any analyzer/Graph change; any change to app-only state; widening `logout()` semantics | `docs/security-boundaries.md` abandonment + residual entry |
| `ISSUE-0014` | `.github/workflows/validate.yml`, `CONTRIBUTING.md`, `README.md` (CI status wording) | Any product source change; any change to the frontend's test content to make CI pass; loosening a check to get green | README/CONTRIBUTING note that CI now covers the frontend |

## Verification strategy

- Unit checks: `python3 -m unittest discover -s tests` (auth handling for **both**
  modes, Graph paging/normalization, analyzer scoring on fixtures, health, UI
  static-safety assertions).
- **(v4) UI runtime-behavior check:** `ISSUE-0010`'s secret-clearing criteria
  (submit, mode switch, logout) are additionally verified by a documented
  manual browser walkthrough with synthetic credentials, since no JavaScript
  test toolchain exists to assert runtime behavior automatically; static
  source assertions alone cannot prove the clearing code executes.
- **(v4) Secret-leak checks:** every M2 auth/server test uses a mock transport and
  a synthetic secret literal, and asserts that literal is absent from every
  response body, exception message, `repr()`, and captured log stream across
  success and every failure path. These are ordinary `unittest` assertions and
  require no tenant, no network, and no credential.
- **(v4) Tracked-file check:** `scripts/validate_repo.py` checks repository
  governance and cleanliness (required files, structure, workflow-state
  consistency); it does **not** scan file contents for secrets or entropy, and
  this roadmap does not claim it does. Real-secret hygiene in tracked files is
  enforced by process (`AGENTS.md`'s prohibition on committing credentials)
  plus explicit reviewer inspection of every M2 diff — a manual control, not an
  automated one. The synthetic literal is the only secret-shaped string
  expected to appear in the repository, in `tests/` only.
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
- ~~Clean-environment / onboarding check: fresh clone → `python3 server.py` with
  no installs.~~ **(v5) No longer true, corrected here rather than quietly
  dropped.** Since `DECISION-024`, `web/index.html`/`index.js`/`index.css` are
  generated and gitignored, so a fresh clone serves no UI until
  `cd frontend && npm install && npm run build` has run. The onboarding check is
  now: fresh clone → `npm install && npm run build` → `python3 server.py` →
  the dashboard loads. The *backend* still installs nothing, which is the part
  of the original constraint that survives.
- **(v5) Frontend checks:** `cd frontend && npm test` (Vitest — 91 tests at the
  `ISSUE-0013` candidate: severity/score logic, the typed API client's error
  branches, the SVG gauge, the device-code cancellation race, hostile-markup
  rendering, and a dangerous-sink scan across `src/`) and
  `cd frontend && npm run build`. **CI now runs both on every push and pull
  request** (`ISSUE-0014`, merged `DECISION-031`), alongside the three
  Python checks — see `.github/workflows/validate.yml`.
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
- **(v5)** `M3`: `README.md`'s dashboard description, Quick Start build step,
  and known-limitations table (done in `ISSUE-0012`/`ISSUE-0013`);
  `frontend/README.md` covering install, build, dev-server caveat, tests, and
  source layout (done in `ISSUE-0012`); `docs/security-boundaries.md` entries
  for scoped abandonment (done in `ISSUE-0013`) and for the build-time
  dependency boundary plus the frontend's rendering-safety model (done in this
  roadmap change, alongside `RISK-009`); `CONTRIBUTING.md` frontend commands
  (done in this roadmap change — its command list was Python-only, which would
  have left a new contributor unable to build the UI at all).

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

| `RISK-009` | **(v5, new; accepted `DECISION-028`)** Build-time supply chain. `DECISION-024` introduced a transitive npm dependency graph (`frontend/package-lock.json`) that the stdlib-only backend deliberately does not have. A compromised or typosquatted transitive package executes with the developer's privileges at install/build time and can write arbitrary content into `web/index.js`, which the server then serves. This is a genuinely new trust boundary for this project, not a variation on an existing one | Medium — build-time code execution; would reach the served bundle | Jay (@Jay-cli) | **Accepted as residual per `DECISION-028`**, on the same low-traffic/single-user reasoning already applied to `RISK-002`: the lockfile is committed, so builds are reproducible and a dependency change is visible in a diff; the served page keeps `default-src 'self'` and loads no external asset, so a compromise must arrive through the build rather than at runtime; no dependency reaches the backend, which still handles every token and secret. Gaps not closed by this acceptance: nothing pins or audits transitive versions beyond the lockfile, and `npm audit` runs nowhere. **CI now runs `npm ci`/`npm run build`/`npm test` on every push and pull request** (`ISSUE-0014`, merged `DECISION-031`), so a broken build or failing test is caught automatically — but this does not audit *what* the build pulled in. Recommended future treatment is `npm audit` in CI, without needing to reopen `DECISION-028` | At `ISSUE-0014`; then at any M3 milestone security review |
| `RISK-010` | **(v5, new; accepted `DECISION-029`)** Onboarding regression. `git clone && python3 server.py` no longer produces a working app — the UI's build output is gitignored, so the server starts and its static routes 404 until `npm install && npm run build` has run. The project's original "clone and run, no installs" property is gone for the UI | Low — documentation-shaped, no security impact | Jay (@Jay-cli) | **Accepted per `DECISION-029`** (resolving round-2 plan-review F-002's inconsistency between this row and the reconciliation text below): a consequence of `DECISION-024`, mitigated by documentation only — `README.md` Quick Start, `frontend/README.md`, and `CONTRIBUTING.md` all state the build step. Not otherwise mitigated — the alternative (committing build output) was rejected as making generated code look like reviewable source | On any change to the build/serve arrangement |
| `RISK-011` | **(v5, records an already-accepted risk)** `ISSUE-0013`'s device-code abandonment "fails open": if every delivery attempt of `POST /api/auth/abandon` fails, or the tab closes mid-retry, cleanup is never acknowledged and nothing observable records that. The abandoned attempt's own ~15-minute server-side expiry is then the only backstop | Low–medium — a token the user believes abandoned can remain installed until natural expiry | Jay (@Jay-cli) | **Accepted by the human at `DECISION-027`**, exactly as documented: loopback-only delivery, ~16-minute retry window (deliberately past the attempt's own expiry), tab-closure/permanent-failure as the sole uncovered case. Listed here because it was accepted in an issue record while no roadmap entry existed to carry it — a roadmap-level risk register that omits it is incomplete. `ISSUE-0013`'s option 2 (an observable cleanup-pending state) remains available as future work | If the abandon mechanism is revisited |

Critical or high security findings cannot use the default risk-acceptance path.
`RISK-002` as widened, `RISK-005`, `RISK-006`, and `RISK-007` were each decided
by the human (`DECISION-014`) rather than accepted or inferred by an agent.
**(v5)** `RISK-011` was likewise decided by the human (`DECISION-027`) and is
recorded here, not accepted here. `RISK-009` is now decided too: accepted as
residual per `DECISION-028`. `RISK-010` is likewise **accepted per
`DECISION-029`**, resolving round-2 plan-review F-002's inconsistency between
this text and the risk table above — both now say "accepted."

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

- Every approved milestone complete (`M1`; **(v4)** `M2` once approved and
  delivered is an **extension** of the completed M1 MVP, not a redefinition
  of it — M1 alone already satisfied "the whole MVP" for the original scope,
  and M2 is a separately approved, opt-in increment on top of it).
- Fresh full-project Claude and Codex general and security reviews against one final commit.
- Installation, onboarding, rollback, support, security, and known limitations accurate.
- The human records final approval.

## Planning reconciliation

| Round | Codex review | Claude response | Remaining decision |
|---:|---|---|---|
| 1 | `ROADMAP-691b1427de57-codex.json` (BLOCKED, 5 findings) | `ROADMAP-691b1427de57-claude-response.md` (F-002..F-005 accepted; F-001 via prompt convention) | Resolved in v2 |
| 2 | `ROADMAP-4daf03ca5be5-codex.json` (BLOCKED, 4 findings) | `ROADMAP-4daf03ca5be5-claude-response.md` (F-001..F-003 accepted → v3; F-004 is a review-sandbox limitation with out-of-band validator evidence) | Presented to human: approved as v3 (`DECISION-003`) |
| 3 (v4, round 1) | `ROADMAP-71f7ba60b045-codex.json` (BLOCKED, 5 findings) | `ROADMAP-71f7ba60b045-claude-response.md` (F-002..F-005 accepted; F-001 is a review-sandbox limitation, out-of-band validator evidence recorded) | First of two permitted revision rounds |
| 4 (v4, round 2) | `ROADMAP-605c282c5c81-codex.json` (BLOCKED, 2 findings + 1 advisory) | `ROADMAP-605c282c5c81-claude-response.md` (F-002, F-003 accepted; F-001 is the same review-sandbox limitation, out-of-band evidence recorded) | Second and final permitted revision round used |
| 5 (v4, confirmatory) | `ROADMAP-76a09c46a57d-codex.json` (`CHANGES_REQUIRED`, 2 findings) | `ROADMAP-76a09c46a57d-claude-response.md` — findings presented to the human before any edit (revision cap already used); human directed both be fixed | Fixed: brief/roadmap secret-lifecycle wording contradiction, and ISSUE-0010's static-only UI verification gap |
| 6 (v4, confirmatory) | `ROADMAP-faf5ec70bf00-codex.json` (BLOCKED, 3 findings + 1 advisory) | This response — the repository's absolute five-iteration cap (`AGENTS.md`) is exhausted at this point, so no further automated Codex re-review is run; the human decided to have these findings fixed and then approve directly from this record | Fixed at the current commit: bounded input-validation criteria for `ISSUE-0009`'s tenant/client-id/secret fields; dropped provider-supplied error text entirely (stable local labels only) instead of relying on literal-only secret scrubbing; refreshed the stale top-level project outcome/stakeholder/definition-of-done narrative for the dual-mode M2 scope. F-001 (governance validator unavailable in the sandbox) is, again, the same structural limitation — out-of-band validator evidence: `python3 scripts/validate_repo.py` passes (67 required files checked) outside the review sandbox. **No further Codex plan review will be run for v4; the human approves directly from this reconciliation record and the response files above.** |

### v4 reconciliation note (closed)

Recorded so no later reader has to reconstruct the v4 approval path from
scratch:

- Four Codex plan-review rounds were run against successive v4 candidates
  (rows 3–6 above): one initial `BLOCKED` review, the two revision rounds
  `AGENTS.md` permits, and two further confirmatory rounds run at the human's
  explicit direction after the repository's absolute five-iteration cap was
  reached. Every actionable finding across all four rounds was fixed; the
  recurring blocker was the review sandbox's inability to run real checks
  (governance validator, full unit suite, compile cache), addressed each time
  with out-of-band evidence that those checks pass against the exact reviewed
  commit — the same class of limitation recorded for the v3 roadmap's own
  round-2 review.
- `DECISION-003` binds roadmap **v3** at `125d74f` and still governs M1; it
  never extended to v4. `DECISION-015` binds roadmap **v4** at `9e5ba6d` and
  is the approval that authorizes M2. Both decisions stand; neither
  invalidates the other.
- Unlike the reverted `origin/claude/graph-auth-without-cli-8om0zw` draft this
  roadmap's M2 content was independently re-derived from (brief v2 and
  `DECISION-013`/`DECISION-014` were approved fresh in this cycle, not
  resurrected), brief v2 Questions 3/5/6 were already resolved before this v4
  candidate was first drafted, so no open brief question blocked `ISSUE-0008`
  beyond the plan-review and roadmap-approval steps themselves.
- Permitted next action: `ISSUE-0007` starts in a new top-level Claude issue
  task, under the same governed per-issue workflow used for all six M1
  issues.

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

**(v5)** This version was also such a change and is now **approved**
(`DECISION-029`, binding `8ea41ee`). It adds `M3`, three issues (`ISSUE-0012`,
`ISSUE-0013`, `ISSUE-0014`), three risks (`RISK-009`, `RISK-010`, `RISK-011`),
a first-class statement of the `DECISION-024` build-step exception's bounds,
and a correction to a verification-strategy claim that had become false. It
required its own fresh Codex plan review and its own human decision record;
`DECISION-003` and `DECISION-015` do not cover it, `DECISION-029` does. The
approved-and-executed M1 and M2 content is unchanged by v5 except where
explicitly marked `(v5)`.

Two things about v5 are unusual and are stated plainly rather than smoothed
over:

1. **It is partly retroactive.** `ISSUE-0012` and `ISSUE-0013` are already
   implemented, reviewed, and merged. Approving v5 does not approve them —
   they were already merged under `DECISION-025` and `DECISION-027`. It binds
   them to a milestone so they are no longer orphaned, and so `ISSUE-0014` has
   a parent. `ISSUE-0014` is the only genuinely forward-looking item, and it is
   `PLANNED`, not started.
2. **Its required Codex plan review ran twice, both `CHANGES_REQUIRED`.**
   `codex` was not available in the environment where v5 was drafted, so the
   launcher could not be invoked there; it was invoked here, retroactively.
   Round 1 (`441b4da`, `project/reviews/plans/ROADMAP-441b4da0d3ba-codex.json`):
   F-001 (missing `ISSUE-0014` record), F-002 (stale candidate SHA in
   `CURRENT.md`), and F-003 (unspecified negative-CI verification) were fixed;
   F-004 (`RISK-009` needs an exact human treatment decision) was resolved by
   the human accepting it as residual (`DECISION-028`). Round 2 (`9bd2c0f`,
   `project/reviews/plans/ROADMAP-9bd2c0f8f6fb-codex.json`): F-001
   (`ISSUE-0014`'s negative-CI fallback doesn't verify workflow-level failure
   propagation) and F-002 (`RISK-010`'s treatment was described
   inconsistently) were **not** repaired further — `AGENTS.md`'s two-round
   planning-repair limit was reached, so per `DECISION-029` the human approved
   v5 directly from the round-2 record, accepting both findings as documented
   residuals rather than authorizing a third repair round. This mirrors
   `DECISION-015`'s handling of v4 at its own iteration cap.
