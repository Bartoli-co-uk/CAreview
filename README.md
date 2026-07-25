# CAreview — Conditional Access policy analyzer

CAreview is a locally-hosted tool that signs into Microsoft Entra ID, reads your
Conditional Access (CA) policies through Microsoft Graph, scores them against
security best practice, and explains what to fix. Everything runs on your own
machine: one Python process, no installs, no Azure app registration, no build
step.

It is inspired by [`Jhope188/ca-policy-analyzer`](https://github.com/Jhope188/ca-policy-analyzer),
re-scoped to run entirely locally.

> **Status: MVP complete.** Sign-in, policy fetch, scoring, findings and the UI
> are all implemented and unit-tested offline.
> **One tracked gap:** the device-code sign-in and Graph fetch have only been
> exercised against mocked transports — a live sign-in against a real tenant has
> not yet been performed. See [Known limitations](#known-limitations).

---

## Contents

- [What it does](#what-it-does)
- [Quick start](#quick-start)
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
   public client. You click *Sign in*, get a code, approve it at
   `microsoft.com/devicelogin`. No app registration, no client secret.
2. **Fetch** — reads your tenant's Conditional Access policies from Microsoft
   Graph (read-only, paged) and normalizes them into a stable internal shape.
3. **Score** — runs a declarative rule set and produces a **0–100 heuristic
   score**.
4. **Explain** — a severity-sorted findings list, each with a rationale and a
   remediation step.
5. **Visualize** — one flow card per policy: Users → Conditions → Apps →
   Controls.

Nothing is persisted. Tokens and policy data live in process memory only;
closing the process discards everything.

## Quick start

Requires **Python 3.10 or newer**. Nothing to `pip install`.

On Windows, or if you have not used Git or Python before, follow
[Step-by-step setup for beginners (Windows)](#step-by-step-setup-for-beginners-windows)
instead — it covers installing both from scratch.

```sh
git clone https://github.com/Bartoli-co-uk/CAreview.git
cd CAreview
python3 server.py
```

Open <http://127.0.0.1:8765/> (`localhost` works too). Then either:

- **Try it without signing in** — click **"View a sample analysis"** on the
  Server status card. This renders the committed, sanitized
  [`web/sample-data.json`](web/sample-data.json) (fake GUIDs, no real tenant
  data) through exactly the same code path as a live analysis.
- **Analyse your own tenant** — click **Sign in**, optionally change the tenant
  (`organizations` by default), and enter the displayed code at
  `microsoft.com/devicelogin`. Once approved, the page automatically fetches
  your policies and renders the score, findings and policy cards. **Sign out**
  clears the in-memory token and the analysis.

To use a different port: `CAREVIEW_PORT=8888 python3 server.py`.

Reading Conditional Access policies requires delegated consent to
`Policy.Read.All`; a **Security Reader** directory role is sufficient.

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

6. **Run CAreview:**
   ```powershell
   python server.py
   ```
   If PowerShell says `python` isn't recognized, try:
   ```powershell
   py server.py
   ```

7. **Open it in your browser:** go to
   [http://127.0.0.1:8765](http://127.0.0.1:8765). You should see a health
   badge reading "ok". Click **Sign in** to connect to your tenant, or **View
   a sample analysis** to try it without signing in.

8. **To stop it**, go back to the PowerShell window and press `Ctrl+C`.

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

The rule set lives in [`rules.py`](rules.py) — ten data-driven rules, each with a
severity, a weight, a rationale and a remediation string. Total weight is 120.

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
| [`auth.py`](auth.py) | OAuth 2.0 device-code flow against the Microsoft Graph PowerShell first-party public client. In-memory token store, full poll state machine, opaque bounded session handle, logout. Transport- and clock-injectable so it is testable without a network. |
| [`graph.py`](graph.py) | Read-only Microsoft Graph client. Fetches `identity/conditionalAccess/policies`, follows paging, and normalizes each policy into the internal data contract the analyzer and UI consume. Refuses to attach the bearer token to any non-Graph host. |
| [`rules.py`](rules.py) | The declarative rule set: ten rules with severity, weight, rationale, remediation and required fields, plus the evaluability model. |
| [`analyzer.py`](analyzer.py) | Runs the rules over normalized policies, computes the weighted score, and returns severity-sorted findings. |
| [`web/`](web/) | The UI — `index.html`, `app.js`, `style.css`, and the sanitized `sample-data.json`. No frameworks, no external assets. Untrusted tenant strings are inserted as text, never HTML. |
| [`tests/`](tests/) | 83 unit tests plus sanitized fixtures (`strong`, `weak`, `incomplete` tenants). Fully offline — no sign-in, no network. |

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
| `POST` | `/api/auth/logout` | Clear the in-memory token and session. |
| `POST` | `/api/breakglass` | Supply break-glass account object IDs (GUIDs, memory only). Body: `{"ids": [...]}`; an empty list clears them. |

Static routes: `/`, `/index.html`, `/app.js`, `/style.css`, `/sample-data.json`.

## Verify it offline

```sh
python3 -m unittest discover -s tests            # 83 tests; no sign-in, no network
python3 -m py_compile $(git ls-files '*.py')     # compile check
python3 scripts/validate_repo.py                 # governance/docs validator
```

The analyzer is unit-tested against committed **sanitized** fixtures
(`tests/fixtures/{strong,weak,incomplete}_tenant.json` — fake GUIDs, no real
tenant data): the strong tenant scores 100 and the weak tenant scores low,
deterministically.

GitHub Actions runs exactly these three commands on every push and pull request
(plus a PowerShell syntax check of the review launcher), so the checks you run
locally are the checks that gate the repository — see
[`.github/workflows/validate.yml`](.github/workflows/validate.yml).

## Design goals and scope

- **Local only.** One Python process on `http://127.0.0.1:8765`. Your policies
  and tokens stay on your machine; the only network egress is to Microsoft.
- **Zero registration, zero build.** No Azure app registration, no client
  secret, no Node.js toolchain.
- **Standard library only.** No third-party Python dependencies.
- **Read-only, least privilege.** Delegated Graph scopes limited to
  `Policy.Read.All`, `Application.Read.All` and `Directory.Read.All`.

The MVP is deliberately focused: sign in → fetch → score → findings → per-policy
visualization. CIS-17 alignment, the FOCI database, persona scoring, baseline
comparison, and PowerPoint/deployment-bundle exports are recorded non-goals for
the MVP, not part of it. They would need a new brief and roadmap cycle.

## Security model

- **Tokens never leave memory.** Access tokens obtained by the device-code flow
  live only in the running process — never on disk, in logs, in tracked files,
  or in agent prompts. Request logging is disabled so request contents cannot
  leak to stderr.
- **No secrets in the repository.** The first-party `client_id` is public by
  design and there is no client secret. Never commit a tenant ID, a policy
  export, or any account data.
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
[`ROADMAP.md`](ROADMAP.md)) and the one open follow-up:

| ID | Limitation |
|---|---|
| **Live sign-in unverified** | Auth and Graph access have only been exercised against mocked transports. Whether the chosen first-party client can obtain `Policy.Read.All` by device code in a given real tenant is not yet confirmed. |
| **RISK-001** | A tenant may block first-party device-code sign-in or withhold `Policy.Read.All` consent. The app-registration fallback is deferred, not part of the MVP. |
| **RISK-002** | The local API has no authentication beyond loopback binding plus the Host/Origin allowlists. Another process running as the same user on the same machine could reach it while a token is in memory. Acceptable for a single-user local tool — **do not run it on a shared or multi-user host.** |
| **RISK-004** | The 0–100 score is a documented heuristic across a starter rule set. It is not a compliance certification and not a substitute for professional assessment. |
| **Browser rendering** | The UI has been verified by fetching and asserting on server responses and by static checks, not by an automated in-browser test. |

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
