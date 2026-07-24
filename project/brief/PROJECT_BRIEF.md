# Project brief: CAreview — Conditional Access policy analyzer

**Status:** `DRAFT`
**Version:** `1`
**Source description:** `project/intake/PROJECT_DESCRIPTION.md` at `19e5863d19f856b635df878234a37333f391b4e9`
**Prepared by:** `Claude Code requirements session (2026-07-24)`
**Prepared at:** `2026-07-24T10:29:45Z`

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
registration to set up**, and the tool must run with **no build toolchain** — the
Python standard library only.

## Users and stakeholders

| User or stakeholder | Need | Expected outcome |
|---|---|---|
| Repository owner / security practitioner | Assess a tenant's CA posture quickly and locally | Signs in, sees a score, findings, and per-policy visualization for their tenant |
| Tenant administrator (consent grantor) | Grant the read-only access the tool needs | One-time admin consent to read-only Graph scopes; no standing app registration |
| Reviewers of this project (Codex, human owner) | Confidence the build is correct and safe | Each issue and milestone passes the governed review gates |

## Goals

- Sign in to Entra ID via OAuth 2.0 **device-code flow** against a Microsoft
  first-party public client (click *Sign in* → enter code at
  `microsoft.com/devicelogin`).
- Fetch the tenant's Conditional Access policies from Microsoft Graph.
- Produce a **0–100 security score** and a **severity-sorted findings list** from
  a transparent, data-driven rule set.
- Render a **simple per-policy visualization** (Users → Conditions → Apps →
  Controls).
- Run entirely locally on `http://localhost:8765` with **Python standard library
  only** and **no Azure app registration**.
- Be **offline-testable**: analyzer scoring verified against committed sanitized
  fixtures without signing in.

## Non-goals

- CIS Microsoft 365 Benchmark v7.0 control matrix.
- FOCI application database / token-sharing analysis.
- MS Learn documented-exclusion checks.
- Zero Trust persona scoring.
- Baseline comparison against external repositories.
- PowerPoint / deployment-bundle exports.
- Any Azure app registration flow or non-device-code authentication.
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
  (source description).
- Tokens are held only in process memory and never persisted (source description).
- The build follows the ClaudexCodexSetUp workflow already committed in this
  repository; Codex CLI is installed and authenticated (environment check).

## Assumptions requiring confirmation

- **A1 — First-party public client can read CA policies via device code.** We
  assume a Microsoft first-party public client (candidate: Microsoft Graph
  PowerShell, `14d82eec-204b-4c2f-b7e8-296a70dab67e`) can obtain a delegated
  token carrying `Policy.Read.All` after admin consent. *If wrong:* device-code
  sign-in may succeed but Graph returns 403, forcing the app-registration
  fallback (currently a non-goal). Needs verification against a real tenant.
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
| Microsoft identity platform (`login.microsoftonline.com`) | Device-code sign-in and token issuance | Device code, delegated access/refresh tokens | First-party public client; user completes device-code approval; admin consent to read scopes |
| Microsoft Graph (`graph.microsoft.com`) | Read Conditional Access policies (and, if needed, named locations, directory roles) | CA policy JSON returned to the local app | Delegated `Policy.Read.All`, `Application.Read.All`, `Directory.Read.All`, read-only |
| Local browser | Complete `microsoft.com/devicelogin` and view the UI | User code entry; rendered results | Localhost only |

## Data and security

- Data classification: **sensitive** (tenant security configuration).
- Personal or regulated data: policy objects may reference user/group/role IDs
  and named locations; no bulk personal data is intended to be fetched.
- Trust boundaries: local user ↔ local server (localhost); local server ↔
  Microsoft endpoints (TLS). The local server performs no authn of its own.
- Secrets and credentials: no client secret exists (public client). Tokens live
  in process memory only; never written to disk, logs, tracked files, or review
  reports. The public `client_id` and tenant hint are not secrets.
- Material abuse or failure cases: token left in memory readable by another local
  process (A4); a malicious/typo tenant value directing auth elsewhere; over-broad
  scopes; accidental logging of tokens or policy data; SSRF if any user-supplied
  value reached an outbound URL; binding beyond localhost.
- Required external isolation or expert review: none mandated for a local
  read-only tool; the milestone security review covers the threat model.

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

## Questions for the human

1. **Client id / tenant default (A1, A2):** Are you content to proceed with the
   Microsoft Graph PowerShell first-party public client and an `organizations`
   default authority, accepting that a tenant which blocks first-party
   device-code will need the app-registration fallback added later? This is the
   single biggest technical risk.
2. **Fallback scope:** If A1 fails in your tenant, do you want the app
   registration fallback pulled into the MVP, or kept as a separate later issue?
3. **Local-server exposure (A4):** Is "trusted single-user machine, localhost
   binding, no local auth" acceptable for the MVP, or do you want a local
   loopback token/PIN gate on the API from the start?
4. **Score transparency:** Is a documented heuristic score (with each rule's
   weight shown) acceptable, given it is explicitly not a compliance
   certification?

## Approval gate

This brief is not approved until a human decision record names this exact path,
version, and commit SHA. Approval permits roadmap drafting only; it does not
permit implementation or protected actions.

**Decision record:** `Not yet recorded`
