# Project roadmap — CAreview

This is the canonical project roadmap for CAreview, a locally-hosted Conditional
Access policy analyzer.

**Current status:** `ROADMAP_REVIEW` (revised to v2 after Codex round 1; awaiting fresh Codex re-review, then human approval)
**Roadmap version:** `2`
**Approved brief:** `project/brief/PROJECT_BRIEF.md` v1 at `179a02354aecbafa2c9d5aa34f9c9a5a04bbc79a` (DECISION-001)
**Codex plan review:** `project/reviews/plans/ROADMAP-691b1427de57-codex.json` (round 1, BLOCKED) + response `project/reviews/plans/ROADMAP-691b1427de57-claude-response.md`
**Human approval record:** `Not recorded`

No implementation may begin until a human records approval of the exact roadmap
version and commit.

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
| Security practitioner (owner) | Assess a tenant's CA posture locally | Signs in and sees policies, a 0–100 score, and findings for their tenant |
| Tenant admin (consent) | Grant least-privilege read access | One-time consent to read-only Graph scopes; no standing app registration |
| Project reviewers | Correct, safe build | Each issue has a committed passing Codex review; milestone passes four blind reviews |

## Constraints and non-goals

### Constraints

- Python 3.10+ standard library only; no third-party packages, no Node.js, no build step.
- Serve on `127.0.0.1:8765` only; no local authentication beyond loopback binding (DECISION-001).
- Delegated Graph scopes limited to `Policy.Read.All`, `Application.Read.All`, `Directory.Read.All`; read-only.
- Tokens held in process memory only; never persisted to disk, logs, or the repo.
- Analyzer must be verifiable offline against committed sanitized fixtures.

### Non-goals

- CIS v7.0 matrix, FOCI database, MS Learn exclusion checks, persona scoring, baseline comparison, PowerPoint/deployment exports.
- Any Azure app registration flow or non-device-code auth in the MVP (app-registration fallback is deferred; see RISK-001).
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
- **Deployment:** run-on-demand local tool; no persistence, no telemetry; closing
  the process discards all state and tokens.

## Milestones

Each milestone has a single frozen candidate commit and four fresh reviews:
Claude general, Codex general, Claude security, and Codex security. At most one
general-remediation cycle and two security-remediation cycles; every remediation
creates a new candidate and reruns all four reviews. Exhaustion blocks for the
human, who makes the milestone decision after seeing all four reports.

| ID | Outcome | Dependencies | Exit criteria | Status |
|---|---|---|---|---|
| `M1` | Working MVP: device-code sign-in → fetch CA policies → 0–100 score + findings → per-policy visualization, offline-testable | `None` | All six issues COMPLETE; `python3 server.py` runs; `python3 -m unittest discover -s tests` passes; live sign-in lists a tenant's policies with score and findings; four blind milestone reviews pass | `PLANNED` |

## Issue sequence

Issues run sequentially. Each is small enough for one fresh Claude issue task
(up to two in-task repair rounds) and an independent fresh Codex review.

| Order | Issue | Objective | Depends on | Acceptance and checks | Risk | Status |
|---:|---|---|---|---|---|---|
| 1 | `ISSUE-0001` | Local HTTP server + static UI shell + `/api/health`; run/verify scaffolding | `None` | `python3 server.py` serves `index.html` and `/api/health` returns `{"status":"ok"}`; `python3 -m py_compile` clean; `python3 -m unittest discover -s tests` runs (health test) | Low | `PLANNED` |
| 2 | `ISSUE-0002` | Device-code auth: `/api/auth/start` + `/api/auth/poll`, in-memory token store with a full lifecycle; Sign-in UI shows code + link and reflects success | `ISSUE-0001` | Completion gated on mocked checks: unit tests cover the poll state machine, device-code expiry, server-controlled polling cadence, opaque bounded handle, logout/cancel + memory clear, access-token-expiry behaviour, the refresh-token decision, and single-concurrency; no token on disk/logs. Live sign-in is a protected action (F-002) recorded only after human approval | Medium (brief A1) | `PLANNED` |
| 3 | `ISSUE-0003` | Graph client: `/api/policies` fetches and normalizes CA policies (paged), read-only bearer calls, against a defined data contract | `ISSUE-0002`, A3 resolved | Completion gated on mocked checks: unit tests cover paging, normalization to the documented data contract, and 403→consent message. Live fetch is a protected action (F-002) recorded only after human approval | Medium | `PLANNED` |
| 4 | `ISSUE-0004` | Analyzer engine + data-driven rule set + 0–100 scoring; per-rule required-field + not-evaluable behaviour; unit tests + sanitized fixtures | `ISSUE-0003` | `python3 -m unittest discover -s tests` passes; fixtures produce documented, deterministic scores and severity-sorted findings across strong/weak/incomplete samples; a rule with missing required evidence is marked *not evaluable*, not pass/fail | Medium | `PLANNED` |
| 5 | `ISSUE-0005` | UI rendering: score gauge, findings list, per-policy flow cards; wire `/api/policies` + analysis; XSS-safe rendering of untrusted policy content | `ISSUE-0003`, `ISSUE-0004` | Renders offline against a fixture endpoint for review; tenant/finding strings inserted as text (not HTML); restrictive CSP; `no-store` on sensitive API responses; no external assets; no console errors | Low | `PLANNED` |
| 6 | `ISSUE-0006` | Documentation finalization + end-to-end verification notes + lint/test polish | `ISSUE-0001..0005` | README run/verify steps accurate from a clean checkout; `py_compile` and `unittest` clean; a documented end-to-end walkthrough exists | Low | `PLANNED` |

## Verification strategy

- Unit checks: `python3 -m unittest discover -s tests` (auth handling, Graph paging/normalization, analyzer scoring on fixtures, health).
- Integration checks: manual, human-run live sign-in + policy fetch against a real tenant is a **protected action** requiring separate human approval naming the tenant (Codex F-002); it is never a completion precondition. Issue completion relies on mocked checks; live evidence is recorded per issue only after approval, otherwise noted as an evidence gap.
- Security checks: `python3 -m py_compile $(git ls-files '*.py')`; manual review that tokens/policy data never reach disk, logs, or the repo; milestone security review.
- Documentation checks: run README steps from a clean checkout in ISSUE-0006.
- Clean-environment / onboarding check: fresh clone → `python3 server.py` with no installs.
- Evidence gaps requiring human judgement: live-tenant behaviour (A1/A2), and whether first-party device-code is permitted in the target tenant.

Agent-reported claims are not test evidence. Record actual commands, commit SHA,
exit status, and limitations in each handoff.

## Documentation plan

- `M1`: README run/verify instructions (kept accurate as issues land), an
  end-to-end walkthrough, and per-issue handoffs. Security boundaries already
  documented in `docs/security-boundaries.md`; update if the threat model shifts.

## Risks and decisions

| ID | Risk or decision | Impact | Owner | Treatment or decision record | Review date |
|---|---|---|---|---|---|
| `RISK-001` | Tenant blocks first-party device-code or withholds `Policy.Read.All`, so live fetch fails | Medium — MVP can't read live policies until fallback | Jay (@Jay-cli) | Accepted for MVP per `DECISION-001`; app-registration fallback deferred to a post-MVP issue if it occurs. Offline fixtures keep the analyzer verifiable regardless | 2026-08-31 |
| `RISK-002` | Local loopback API reachable by another local process while a token is in memory | Low–medium on a trusted single-user machine | Jay (@Jay-cli) | Accepted for MVP per `DECISION-001` (localhost-only, no local auth); revisit if the tool is shared or run on a multi-user host | 2026-08-31 |
| `RISK-003` | Accidental logging of tokens or policy JSON | Medium (sensitive data exposure) | Claude (impl), reviewed by Codex | Redact by construction; unit/security review checks that tokens and policy data are never logged or persisted | Per issue |
| `RISK-004` | Score is a heuristic, mistaken for compliance certification | Low (reputational/interpretation) | Jay (@Jay-cli) | Document each rule's weight and label the score non-authoritative in the UI and README | ISSUE-0004 |

Critical or high security findings cannot use the default risk-acceptance path.

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
| 1 | `project/reviews/plans/ROADMAP-691b1427de57-codex.json` (BLOCKED, 5 findings) | `project/reviews/plans/ROADMAP-691b1427de57-claude-response.md` (F-002..F-005 accepted; F-001 addressed via prompt convention) | Re-review pending against roadmap v2 |

Maximum two repair rounds. Any remaining material disagreement is shown to the
human before exact roadmap approval. No workflow loop may exceed five total
iterations.

## Change control

After approval, do not silently edit this roadmap. A proposed change must state
the approved version/commit, the exact diff, its effect on scope/sequence/risk,
which approvals become stale, and the new human decision. A changed roadmap
requires a new version and exact approval.
