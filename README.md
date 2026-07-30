# CAreview — Conditional Access policy analyzer

CAreview is a locally-hosted tool that signs into Microsoft Entra ID, reads your
Conditional Access (CA) policies through Microsoft Graph, scores them against
security best practice, and explains what to fix. Everything runs on your own
machine: one Python process, no installs, no Azure app registration to use it.
Building the UI (once, or after a UI change) does require Node.js/npm — see
[DECISION-024](project/decisions/DECISION-024-react-frontend-build-step.md).

It is inspired by [`Jhope188/ca-policy-analyzer`](https://github.com/Jhope188/ca-policy-analyzer),
re-scoped to run entirely locally.

> **Status: MVP complete, dual-mode auth complete.** Sign-in (device-code, the
> default, and an optional app-only mode), policy fetch, scoring, findings and
> the UI are all implemented and unit-tested offline.
> **One tracked gap:** in both modes, sign-in and Graph fetch have only been
> exercised against mocked transports — a live sign-in against a real tenant has
> not yet been performed. See [Known limitations](#known-limitations).

---

## Contents

- [What it does](#what-it-does)
- [The dashboard](#the-dashboard)
- [Quick start](#quick-start)
- [App-only mode (advanced)](#app-only-mode-advanced)
- [End-to-end walkthrough](#end-to-end-walkthrough)
- [Step-by-step setup for beginners (Windows)](#step-by-step-setup-for-beginners-windows)
- [What it checks](#what-it-checks)
- [How the score works](#how-the-score-works)
- [How the code fits together](#how-the-code-fits-together)
- [HTTP API](#http-api)
- [Verify it offline](#verify-it-offline)
- [Design goals and scope](#design-goals-and-scope)
- [Security model](#security-model)
- [Known limitations](#known-limitations)
- [Contributing](#contributing)
- [How this project is built](#how-this-project-is-built)
- [Licence](#licence)

---

## What it does

1. **Sign in** — OAuth 2.0 device-code flow against a Microsoft first-party
   public client (the default). You click *Sign in*, get a code, approve it at
   `microsoft.com/devicelogin`. No app registration, no client secret. An
   optional **app-only mode** is also available for a user who already owns
   an Entra app registration — see
   [App-only mode (advanced)](#app-only-mode-advanced).
2. **Fetch** — reads your tenant's Conditional Access policies from Microsoft
   Graph (read-only, paged) and normalizes them into a stable internal shape.
3. **Score** — runs a declarative rule set and produces a **0–100 heuristic
   score**.
4. **Explain** — a severity-sorted findings list, each with a rationale and a
   remediation step.
5. **Visualize** — a multi-page dashboard (see [The dashboard](#the-dashboard)
   below) with a Users → Conditions → Apps → Controls flow view per policy.

Nothing is persisted. Tokens and policy data live in process memory only;
closing the process discards everything.

## The dashboard

The UI (`frontend/`, a React + TypeScript app — see
[DECISION-024](project/decisions/DECISION-024-react-frontend-build-step.md))
is built to work for both **technicians** who need full findings/policy
detail and **senior management** who want an at-a-glance summary, in one
sidebar-navigated dashboard:

| Page | What it shows |
|---|---|
| **Overview** | The management-glance page: a security score gauge, recommendation counts by priority, a policy-status donut (enabled/report-only/disabled), the top open recommendations, a "policies at a glance" breakdown, and a recent-policies table. |
| **Recommendations** | Every finding from the current analysis, filterable by severity, with rationale, remediation, and affected policies — plus the full pass/fail rule-coverage table (not just failures). |
| **Policies** | A searchable table of every Conditional Access policy in the tenant, with drill-down into a policy's full Users → Conditions → Apps → Controls detail. |
| **Policy Explorer** | Faceted search over the same policies — filter by state, control type (MFA/block/device-compliance/session control), or admin-role targeting — for technician-depth investigation. |
| **Insights** | Extra breakdowns computed entirely in your browser from the same data shown elsewhere (severity mix, client-app-type spread, MFA/device-compliance coverage, rule pass/fail ratio) — no additional tenant data is read. |
| **Reports**, **Audit Log** | Honest "not available yet" placeholders — CAreview doesn't generate exports or keep a persisted activity log today, and the dashboard says so rather than showing fake data. |
| **Settings** | Real session info (signed-in state, tenant as entered, sign-out) and a break-glass account ID input, wired to the existing `/api/breakglass` endpoint. No preferences persist between runs, by design. |
| **About** | What the heuristic score does and doesn't mean, plus a short glossary (report-only, legacy authentication, grant/session controls, break-glass accounts) for readers who aren't Conditional Access specialists. |

A **sample data** mode (no sign-in required) exercises the entire dashboard
against the committed, sanitized `web/sample-data.json` fixture, so you can
explore every page before ever connecting to a real tenant.

## Quick start

Requires **Python 3.10 or newer** and, for building the UI, **Node.js/npm**
(see [DECISION-024](project/decisions/DECISION-024-react-frontend-build-step.md)).
Nothing to `pip install`.

On Windows, or if you have not used Git or Python before, follow
[Step-by-step setup for beginners (Windows)](#step-by-step-setup-for-beginners-windows)
instead — it covers installing both from scratch.

```sh
git clone https://github.com/Bartoli-co-uk/CAreview.git
cd CAreview
cd frontend && npm install && npm run build && cd ..
python3 server.py
```

Open <http://127.0.0.1:8765/> (`localhost` works too). Then either:

- **Try it without signing in** — click **"View a sample analysis"** on the
  sign-in screen. This renders the committed, sanitized
  [`web/sample-data.json`](web/sample-data.json) (fake GUIDs, no real tenant
  data) through exactly the same code path as a live analysis.
- **Analyse your own tenant** — click **Sign in**, optionally change the tenant
  (`organizations` by default), and enter the displayed code at
  `microsoft.com/devicelogin`. Once approved, the dashboard automatically
  fetches your policies and populates every page (see
  [The dashboard](#the-dashboard)). **Sign out** clears the in-memory token
  and the analysis.
- **App-only sign-in (advanced)** — if you'd rather authenticate with an
  Entra app registration's client credentials instead of your own account,
  click **"Use app-only sign-in (advanced)"** on the Sign in card and enter
  the tenant, client (application) ID, and client secret. The secret field
  is never written to `localStorage`, `sessionStorage`, a cookie, the URL, or
  the console, and is cleared from the page immediately after every submit,
  on switching back to standard sign-in, and on sign-out.

To use a different port: `CAREVIEW_PORT=8888 python3 server.py`.

Reading Conditional Access policies requires delegated consent to
`Policy.Read.All`; a **Security Reader** directory role is sufficient.

## App-only mode (advanced)

Device-code sign-in (above) is the default and works for most users with no
setup. App-only mode is an **opt-in alternative** for someone who already
manages an Entra app registration and would rather authenticate as that
application than as themselves.

**Prerequisite — CAreview never creates this for you.** You need an Entra
app registration you already own, with:

- the **application** (not delegated) Graph permission `Policy.Read.All`,
  already admin-consented in the target tenant;
- its **Application (client) ID**;
- a **client secret** you have generated for it (Entra portal → your app
  registration → *Certificates & secrets* → *New client secret*).

CAreview only ever reads whatever the app registration already holds — it
does not create, register, or modify an app registration, and it cannot
request a narrower set of permissions than the app already has (Microsoft's
`.default` scope returns everything the app is consented for). **Recommend
a dedicated app registration holding only application `Policy.Read.All`** so
the token CAreview receives can't do more than read policies (`RISK-006`).

**How to use it:** on the Sign in card, click **"Use app-only sign-in
(advanced)"**, then enter the tenant (a GUID or a verified domain like
`contoso.onmicrosoft.com` — the multi-tenant aliases `organizations`,
`common`, and `consumers` are rejected, since they don't identify one tenant
for a client-credentials grant), the Application (client) ID, and the
client secret.

**What happens to the secret:**

- Your browser sends it once, over the loopback POST body, to CAreview's
  own local server — never to any other page, host, or process.
- The local server then sends it on to Microsoft's tenant token endpoint
  (`login.microsoftonline.com`) to request the token, and again on every
  silent renewal — this is the client-credentials grant itself, not an
  extra exposure. It is never sent to, or returned by, any host other than
  that Microsoft endpoint, and it is never sent back to the browser.
- If sign-in succeeds, the server process **retains it in memory for the
  session** (not discarded after the first request) so it can repeat that
  renewal request silently when the current token expires, without asking
  you to re-enter it. This is a deliberate trade-off, documented as
  `RISK-002` (widened) — see [Security model](#security-model).
- It is **never written to disk, logs, or any tracked file**, in either the
  server process or the browser page (`type="password"`, `autocomplete="off"`,
  no `console`/`localStorage`/`sessionStorage`/cookie/URL writes, cleared
  from the page the instant you submit, switch modes, or sign out).
- **Sign out** clears the retained secret from server memory immediately.
  Closing the CAreview process also discards it — nothing persists between
  runs.

**To rotate or revoke access:** manage this entirely in the Entra portal,
not in CAreview. Deleting or rotating the app registration's client secret,
or removing its `Policy.Read.All` permission, takes effect the next time
CAreview would need to renew its token — sign out first so CAreview drops
the old secret, then sign in again with a new one if you rotated rather than
revoked.

**Certificate-based authentication is not supported in this release.**
Only a client secret is accepted. Certificate/JWT-based client assertions
are recorded as a **deferred future enhancement** — they would need a
third-party cryptography dependency, which breaks CAreview's
standard-library-only constraint, so adding them would need its own,
separate dependency-approval decision.

## End-to-end walkthrough

Both walkthroughs below are entirely local until the one clearly marked
**live step**. That step is a **protected action** — CAreview's own
[`AGENTS.md`](AGENTS.md) never lets an agent perform a live sign-in; it's
something you, the reader, do yourself in your own browser with your own
credentials.

**Device-code (default):**

1. `cd frontend && npm install && npm run build && cd ..` (once, or after any UI change), then `python3 server.py`, then open <http://127.0.0.1:8765/>.
2. Click **Sign in** (optionally change the tenant from `organizations`).
3. **Live step:** open the displayed `microsoft.com/devicelogin` link and
   enter the code shown on the page, using your own Microsoft account.
4. Once approved, the page automatically fetches your policies and renders
   the score, findings, and policy cards.
5. Click **Sign out** to clear the in-memory token and the analysis.

**App-only (advanced):**

1. `cd frontend && npm install && npm run build && cd ..` (once, or after any UI change), then `python3 server.py`, then open <http://127.0.0.1:8765/>.
2. Click **"Use app-only sign-in (advanced)"** and enter your tenant,
   Application (client) ID, and client secret — see
   [App-only mode (advanced)](#app-only-mode-advanced) for the prerequisite.
3. **Live step:** click **"Sign in with app-only credentials."** This sends
   your real client secret to CAreview's local server and, on success,
   CAreview requests a real token from Microsoft on the app registration's
   behalf.
4. On success, the page fetches your policies and renders the score,
   findings, and policy cards, the same as device-code mode.
5. Click **Sign out** to clear the in-memory token, session, and the
   retained client secret.

Either walkthrough can be tried without the live step: click **"View a
sample analysis"** on the sign-in screen instead of signing in, which
exercises the identical scoring/rendering path against the committed,
sanitized [`web/sample-data.json`](web/sample-data.json).

## Step-by-step setup for beginners (Windows)

Never used Git or Python before? Follow these steps in order, copy-pasting
each command into **PowerShell** (open it from the Start menu — search for
"PowerShell"). Command Prompt works too; the commands below are the same
either way unless noted.

1. **Install Git** (skip if you already have it — check with `git --version`).
   Easiest way, in PowerShell:
   ```powershell
   winget install --id Git.Git -e --source winget
   ```
   No `winget`? Download the installer from
   [git-scm.com/downloads](https://git-scm.com/downloads) and run it, keeping
   the default options.

   After installing, **close and reopen PowerShell** so it picks up the new
   command.

2. **Check whether Python is already installed:**
   ```powershell
   python --version
   ```
   If you see something like `Python 3.11.4`, you're set — skip to step 4.
   If instead you see an error, or it opens the Microsoft Store, Python isn't
   properly installed yet — continue to step 3.

3. **Install Python** (only if step 2 didn't show a version number):
   ```powershell
   winget install --id Python.Python.3.12 -e
   ```
   No `winget`? Download the installer from
   [python.org/downloads](https://python.org/downloads), run it, and make sure
   you **tick "Add python.exe to PATH"** on the first screen before clicking
   Install.

   After installing, **close and reopen PowerShell**, then confirm it worked:
   ```powershell
   python --version
   ```

4. **Download this repository.** Pick one:
   - With Git:
     ```powershell
     git clone https://github.com/Bartoli-co-uk/CAreview.git
     ```
   - Without Git: on this page, click the green **Code** button → **Download
     ZIP**, then right-click the downloaded file and choose **Extract All**.

5. **Move into the folder you just downloaded:**
   ```powershell
   cd CAreview
   ```
   (If you used "Download ZIP" and extracted it somewhere else, `cd` to that
   extracted folder instead — e.g. `cd Downloads\CAreview-main`.)

6. **Check whether Node.js is already installed** (needed once, to build the
   UI):
   ```powershell
   node --version
   ```
   If you see something like `v20.11.0`, skip to step 8. Otherwise, install
   it:
   ```powershell
   winget install --id OpenJS.NodeJS.LTS -e
   ```
   No `winget`? Download the installer from
   [nodejs.org](https://nodejs.org). After installing, **close and reopen
   PowerShell**.

7. **Build the UI** (once, or again after pulling a UI change):
   ```powershell
   cd frontend
   npm install
   npm run build
   cd ..
   ```

8. **Run CAreview:**
   ```powershell
   python server.py
   ```
   If PowerShell says `python` isn't recognized, try:
   ```powershell
   py server.py
   ```

9. **Open it in your browser:** go to
   [http://127.0.0.1:8765](http://127.0.0.1:8765). Click **Sign in** to
   connect to your tenant, or **View a sample analysis** to try it without
   signing in.

10. **To stop it**, go back to the PowerShell window and press `Ctrl+C`.

**Troubleshooting:**

- `python`/`py` "is not recognized as the name of a cmdlet..." → Python isn't
  on your PATH. Reopen PowerShell first; if that doesn't fix it, reinstall
  Python and make sure "Add python.exe to PATH" is ticked.
- `git` "is not recognized..." → same fix, but for Git: reopen PowerShell, or
  reinstall Git.
- Port `8765` already in use → run
  `$env:CAREVIEW_PORT=8888; python server.py` to use a different port, then
  open `http://127.0.0.1:8888` instead.

## What it checks

The rule set lives in [`rules.py`](rules.py) — eleven data-driven rules, each with a
severity, a weight, a rationale and a remediation string. Total weight is 130.

| Rule ID | Check | Severity | Weight |
|---|---|---|---:|
| `block-legacy-auth` | Legacy authentication is blocked | high | 20 |
| `mfa-admins` | MFA is required for administrators | high | 20 |
| `mfa-all-users` | MFA is required for all users | high | 15 |
| `not-all-report-only` | At least one policy is actually enforced | high | 10 |
| `no-overly-broad-block` | No all-users/all-apps block without exclusions | high | 10 |
| `device-compliance` | Device compliance or hybrid join is required | medium | 10 |
| `signin-risk` | A sign-in risk policy is present | medium | 10 |
| `user-risk` | A user risk policy is present | medium | 10 |
| `break-glass-excluded` | Break-glass accounts are excluded from lockout | medium | 10 |
| `location-restriction-present` | At least one policy conditions on named locations | medium | 10 |
| `session-controls` | Session controls are in use | low | 5 |

`break-glass-excluded` needs an input CAreview cannot discover on its own: which
accounts are your emergency-access accounts. Supply them locally (held in memory
only, never written anywhere) with `POST /api/breakglass`. Without them the rule
is reported **not evaluable** rather than guessed.

## How the score works

The score is a **heuristic, not a compliance certification**. It is the
weight-weighted fraction of *evaluable* rules that pass:

```text
score = round(100 × passed_weight / evaluable_weight)
```

A rule whose required evidence is missing is marked **not evaluable** and
excluded from *both* the numerator and the denominator, so missing evidence is
never silently scored as a pass or a fail. Two things make a rule not evaluable:

- a required external input is absent (currently only break-glass account IDs); or
- a policy-existence rule has no applicable policy to judge (for example, an
  empty tenant).

The implementation is in [`analyzer.py`](analyzer.py); the evaluability model is
documented at the bottom of [`rules.py`](rules.py).

## How the code fits together

| Path | What it does |
|---|---|
| [`server.py`](server.py) | Standard-library HTTP server. Binds loopback only (refuses any other bind address), serves an explicit static-file allowlist and the JSON API, enforces the Host/Origin allowlists, and sets CSP + `nosniff` headers. |
| [`auth.py`](auth.py) | Two sign-in modes: OAuth 2.0 device-code against the Microsoft Graph PowerShell first-party public client (default), and an opt-in client-credentials (app-only) flow for a user-owned app registration, with session-retained secret and silent renewal. In-memory token store only, opaque bounded session handle, logout. Transport- and clock-injectable so it is testable without a network. |
| [`graph.py`](graph.py) | Read-only Microsoft Graph client. Fetches `identity/conditionalAccess/policies`, follows paging, and normalizes each policy into the internal data contract the analyzer and UI consume. Refuses to attach the bearer token to any non-Graph host. |
| [`rules.py`](rules.py) | The declarative rule set: eleven rules with severity, weight, rationale, remediation and required fields, plus the evaluability model. |
| [`analyzer.py`](analyzer.py) | Runs the rules over normalized policies, computes the weighted score, and returns severity-sorted findings. |
| [`frontend/`](frontend/) | The UI source — a React + TypeScript app built with Vite (see [DECISION-024](project/decisions/DECISION-024-react-frontend-build-step.md) for why this needed its own approved exception to the stdlib-only/no-build-step constraint). `npm run build` compiles it into `web/` with fixed, non-hashed filenames. |
| [`web/`](web/) | Served static output — `index.html`, `index.js`, `index.css` (all generated by `frontend/`'s build, not committed) plus the hand-maintained, sanitized `sample-data.json`. Untrusted tenant strings are always rendered as text, never HTML (JSX escaping on the frontend side). |
| [`tests/`](tests/) | 188 unit tests plus sanitized fixtures (`strong`, `weak`, `incomplete` tenants), all offline — no sign-in, no network. The frontend has its own parallel test suite (`frontend/src/test/`, run via `npm test`). |

The remaining top-level directories (`docs/`, `project/`, `prompts/`,
`scripts/`, `.claude/`, `.codex/`) belong to the build process rather than the
application — see [How this project is built](#how-this-project-is-built).

## HTTP API

All endpoints are served on the loopback interface only. Every request must
carry a loopback `Host` header; every `POST` must also carry a loopback
`Origin`. Responses carrying tenant data are sent `Cache-Control: no-store`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Liveness check — `{"status": "ok"}`. |
| `GET` | `/api/policies` | Normalized Conditional Access policies. Requires a signed-in session. |
| `GET` | `/api/analysis` | Score and findings for the current tenant. Requires a signed-in session. |
| `POST` | `/api/auth/start` | Begin device-code sign-in. Body: `{"tenant": "organizations"}`. |
| `POST` | `/api/auth/poll` | Poll for completion. Body: `{"handle": "<opaque handle>"}`. |
| `POST` | `/api/auth/app` | App-only sign-in via client credentials. Body: `{"tenant": "<GUID or domain>", "client_id": "<GUID>", "client_secret": "<secret>"}`. Rejects `organizations`/`common`/`consumers` and malformed/oversized fields with 400 before any outbound request. |
| `POST` | `/api/auth/abandon` | Abandon one device-code attempt (`ISSUE-0013`). Body: `{"handle": "<opaque handle>"}`. Clears only that handle's pending session/token — an unknown or already-superseded handle is a safe no-op, and this can never clear a different, newer session. Used when the UI moves away from an in-progress sign-in (e.g. to the sample-data view) without an explicit sign-out. |
| `POST` | `/api/auth/logout` | Clear the in-memory token, session, and any retained app-only secret. |
| `POST` | `/api/breakglass` | Supply break-glass account object IDs (GUIDs, memory only). Body: `{"ids": [...]}`; an empty list clears them. |

Static routes: `/`, `/index.html`, `/index.js`, `/index.css`, `/sample-data.json`.
The first four are the React frontend's build output (see
[`frontend/`](frontend/)) — run `npm install && npm run build` inside
`frontend/` before starting the server, or these routes 404.

## Verify it offline

```sh
cd frontend && npm install && npm run build      # builds web/index.html, index.js, index.css
cd frontend && npm test                          # frontend unit/component tests
python3 -m unittest discover -s tests            # 188 tests; no sign-in, no network
python3 -m py_compile $(git ls-files '*.py')     # compile check
python3 scripts/validate_repo.py                 # governance/docs validator
```

The analyzer is unit-tested against committed **sanitized** fixtures
(`tests/fixtures/{strong,weak,incomplete}_tenant.json` — fake GUIDs, no real
tenant data): the strong tenant scores 100 and the weak tenant scores low,
deterministically.

GitHub Actions runs all five commands above — the three Python checks and the
two `frontend/` commands (`npm ci && npm run build`, `npm test`) — on every
push and pull request, plus a PowerShell syntax check of the review launcher
(`ISSUE-0014`). See [`.github/workflows/validate.yml`](.github/workflows/validate.yml).

## Design goals and scope

- **Local only.** One Python process on `http://127.0.0.1:8765`. Your policies
  and tokens stay on your machine; the only network egress is to Microsoft.
- **Zero registration by default.** The default device-code path needs no
  Azure app registration and no client secret. App-only mode is an explicit
  opt-in for a user who already has their own app registration — see
  [App-only mode (advanced)](#app-only-mode-advanced).
- **Standard library only on the backend.** `server.py`/`auth.py`/`graph.py`/
  `analyzer.py`/`rules.py` have no third-party Python dependencies. The UI is
  the one exception: building it now requires Node.js/npm (see
  [`frontend/README.md`](frontend/README.md) and
  [DECISION-024](project/decisions/DECISION-024-react-frontend-build-step.md)) — the
  *served* artifact is still a static, dependency-free bundle, but producing
  it is no longer a zero-build step.
- **Read-only, least privilege.** Delegated Graph scope limited to
  `Policy.Read.All` — the only Graph call CAreview makes is to
  `identity/conditionalAccess/policies`.

The MVP is deliberately focused: sign in → fetch → score → findings → per-policy
visualization. CIS-17 alignment, the FOCI database, persona scoring, baseline
comparison, and PowerPoint/deployment-bundle exports are recorded non-goals for
the MVP, not part of it. They would need a new brief and roadmap cycle.

## Security model

- **Tokens never leave memory, in either mode.** Access tokens — device-code
  or app-only — live only in the running process, never on disk, in logs, in
  tracked files, or in agent prompts. Request logging is disabled so request
  contents cannot leak to stderr.
- **App-only mode's client secret is session-memory-only, and widens the
  trust boundary.** Unlike device-code mode (no secret at all — the
  first-party `client_id` is public by design), a user-supplied client
  secret is retained by the server process for the whole app-only session,
  not just the one request, so it can silently renew the token on expiry.
  This is a deliberate, documented trade-off (`RISK-002`, widened) — the
  local API's existing no-authentication-beyond-loopback boundary now also
  covers a live client secret, not just a delegated user token, for as long
  as an app-only session is active. It is never written to disk, logs, or
  any tracked file. See [App-only mode (advanced)](#app-only-mode-advanced)
  for the browser-side handling and [`docs/security-boundaries.md`](docs/security-boundaries.md)
  for the full delta.
- **No secrets in the repository.** Never commit a tenant ID, a policy
  export, a real client secret, or any other account data. The only
  secret-shaped string in this repository is a synthetic, clearly-fake
  literal used in tests.
- **Loopback-bound, with DNS-rebinding defence.** The server factory refuses any
  non-loopback bind address. Every request's `Host` header must be on a loopback
  allowlist, which stops a remote page rebinding DNS to `127.0.0.1` and reading
  the API's responses. State-changing `POST`s additionally require a loopback
  `Origin`.
- **Egress is Microsoft only.** Tokens are attached only to URLs whose host is
  exactly `graph.microsoft.com`; the token endpoint is
  `login.microsoftonline.com` for the validated tenant.
- **Untrusted rendering.** Tenant-supplied strings (policy and display names)
  are inserted as text, never HTML, under a restrictive CSP delivered both as an
  HTTP header and a `<meta>` tag.

Report a suspected vulnerability privately — see [`SECURITY.md`](SECURITY.md).
Wider operating boundaries are in
[`docs/security-boundaries.md`](docs/security-boundaries.md).

## Known limitations

These are the recorded, accepted residual risks (tracked in
[`ROADMAP.md`](ROADMAP.md)) plus the currently open follow-ups:

| ID | Limitation |
|---|---|
| **Live sign-in unverified** | Auth and Graph access, in **both** modes, have only been exercised against mocked transports. Whether the chosen first-party client can obtain `Policy.Read.All` by device code, or a given app registration's client-credentials grant succeeds, in a real tenant is not yet confirmed. |
| **RISK-001** | A tenant may block first-party device-code sign-in or withhold `Policy.Read.All` consent. App-only mode is an available alternative for a user who already has a suitable app registration, not a fallback CAreview arranges for you. |
| **RISK-002** | The local API has no authentication beyond loopback binding plus the Host/Origin allowlists. Another process running as the same user on the same machine could reach it while a token — or, in an app-only session, the retained client secret — is in memory. Acceptable for a single-user local tool — **do not run it on a shared or multi-user host.** |
| **RISK-004** | The 0–100 score is a documented heuristic across a starter rule set. It is not a compliance certification and not a substitute for professional assessment. |
| **RISK-005** | The app-only client secret passes through the browser page once, at entry. Mitigated (`type="password"`, no console/storage/URL writes, cleared on submit/mode-switch/logout) but not eliminated: a compromised browser, extension, or someone reading over your shoulder while you type it remains a residual risk the device-code path doesn't have. |
| **RISK-006** | App-only mode's token carries **every** application permission the app registration holds, not just `Policy.Read.All` — Microsoft's `.default` scope can't be narrowed by the client. Use a dedicated app registration with only `Policy.Read.All` to limit this. |
| **Browser rendering** | The frontend has its own automated test suite (`frontend/src/test/`, Vitest + React Testing Library — jsdom, not a real browser engine) and has been manually verified in an actual browser, but there is no automated real-browser (e.g. Playwright) test in CI. |
| **RISK-009** | The React frontend build (`frontend/`) introduces a ~170-package npm dependency graph that the previously dependency-free backend never had. A compromised or typosquatted transitive package executes at build time and could reach the served bundle. Accepted as residual (`DECISION-028`) on a low-traffic/single-user basis; the lockfile is committed and no external asset loads at runtime, but nothing pins or audits transitive versions beyond the lockfile, and no `npm audit` runs anywhere. |
| **RISK-010** | `git clone && python3 server.py` no longer serves a working UI on its own — `cd frontend && npm install && npm run build` must run first, since the build output is generated and gitignored. A deliberate, documented regression from the original "clone and run, no installs" property (accepted, `DECISION-029`). |
| **RISK-011** (device-code abandon delivery, `ISSUE-0013`) | `POST /api/auth/abandon` retries a failed delivery for ~16 minutes, but can still "fail open" if every attempt fails before the abandoned device-code attempt's own server-side expiry. Accepted as residual (`DECISION-027`): loopback-only delivery, a ~16-minute retry window deliberately past the attempt's own expiry, and tab-closure/permanent-failure as the sole uncovered case. |

CAreview has not been independently security tested. Two AI reviews passing is
not a certification.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) — note that changes here follow the
governed workflow described below. [`SUPPORT.md`](SUPPORT.md) covers where to
ask questions, and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) applies to all
project spaces.

## How this project is built

CAreview is a working application, but it was also built as a demonstration of a
governed AI development process: **Claude** plans and writes all the code,
**Codex** independently reviews it read-only, and the **human owner** approves
every gate. The repository — not chat history — is the durable memory, so a
fresh session can reconstruct the exact state from committed files.

**If you are an AI agent picking this repository up, start at
[`START_HERE.md`](START_HERE.md)**, then follow the reading order it gives you.
Do not begin material work until you can state the current stage and the next
permitted action from the repository files alone.

| Path | Purpose |
|---|---|
| [`START_HERE.md`](START_HERE.md) | Entry point for a fresh agent or contributor: what to read, in what order. |
| [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md) | The operating rules every agent follows, plus the Claude-specific additions. |
| [`docs/`](docs/workflow.md) | The workflow itself — [workflow](docs/workflow.md), [roles](docs/roles-and-responsibilities.md), [approvals and reviews](docs/approvals-and-reviews.md), [security boundaries](docs/security-boundaries.md), [model assignment](docs/model-assignment.md). |
| [`ROADMAP.md`](ROADMAP.md) | The approved roadmap: milestones, issues, acceptance criteria, risks, definitions of done. |
| [`project/`](project/README.md) | Durable project memory: intake, approved brief, issues, handoffs, every review report, human decisions, risks, milestones, and [`project/status/CURRENT.md`](project/status/CURRENT.md) — the authoritative current-state index. |
| [`prompts/`](prompts/README.md) | Copy-paste session prompts for each workflow step. |
| [`scripts/`](scripts/) | [`validate_repo.py`](scripts/validate_repo.py) (governance validator, also run by CI) and the [Codex review launcher](scripts/run_codex_review.py) with its `.sh`/`.ps1` wrappers. |
| [`.claude/`](.claude/rules/workflow.md) / [`.codex/`](.codex/config.toml) | Agent definitions, per-role rules, and reviewer configuration. |

Everything the process produced is in the open: the
[approved brief](project/brief/PROJECT_BRIEF.md), every
[issue](project/issues/README.md), [handoff](project/handoffs/README.md),
[review report](project/reviews/README.md) and
[human decision](project/decisions/README.md), plus the
[M1 milestone record](project/milestones/M1.md).

The governance layer is project-agnostic and can be lifted into another
repository — [`START_HERE.md`](START_HERE.md) explains how.

The workflow is a set of documented conventions and manual review gates. It is
not a hard security boundary and not a certification — a local user or agent
with sufficient access can bypass it.

## Licence

Licensed under the [Apache License 2.0](LICENSE).
