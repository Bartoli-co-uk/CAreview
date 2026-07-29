# Project-level final review: CAreview

**Status:** `REVIEWING`
**Approved roadmap:** `ROADMAP.md` version `5`, `APPROVED` (`DECISION-029`, binds `8ea41ee`)
**Frozen candidate SHA:** round 1 was `5ce510871a17677fe862e3098972d9a85a6727a9` (the freeze commit itself — both round-1 general reviewers correctly blocked because this field then named `802ea4d`, the product-identical parent, instead of the actual reviewed commit). Round 2 (this repair) is this commit — the launcher records the full HEAD SHA. Product/backend/frontend content has been unchanged since `861f401`/`802ea4d`; only `project/`-tree and `README.md` files differ across all three commits.
**Tree identity:** working tree clean; 188 backend tests, `py_compile` clean, `validate_repo.py` clean, `cd frontend && npm run build && npm test` clean (91 passed), CI green on `main` (confirmed via `gh run watch`)

## What this record is, and is not

`ROADMAP.md`'s "Definitions of done" → "Project" section requires, beyond
every approved milestone being complete: "Fresh full-project Claude and
Codex general and security reviews against one final commit" and
"Installation, onboarding, rollback, support, security, and known
limitations accurate," before "the human records final approval."

No dedicated launcher mode or milestone-ID convention exists in this
repository for a project-level (as opposed to per-milestone) review — the
`run-codex-review.sh` launcher only has `plan`, `issue`,
`milestone-general`, and `milestone-security` modes, each bound to a
named milestone or issue record. `project/templates/security-review.md`'s
own header ("`[Claude/Codex] security review: [milestone/project]`")
anticipates project-scope use, so this record reuses the milestone-review
machinery — `milestone-general`/`milestone-security` launcher modes, this
file standing in for a `project/milestones/<ID>.md` target with ID
`PROJECT` — rather than inventing new untested process. The review rigor,
findings taxonomy, and repair-round limits are identical to `M1`/`M2`/`M3`'s
own milestone gates; the *scope* is the whole project as of one frozen
commit, not one milestone's issues.

This file is **not** itself the final human approval `ROADMAP.md` requires
— read "Human decision" before treating any part of this as one.

## Outcome and traceability

CAreview is, as of this candidate, a locally-hosted Conditional Access
policy analyzer with two completed authorization milestones (device-code
sign-in as the default, opt-in app-only client-credentials sign-in) and a
third completed milestone replacing the UI with a React/TypeScript
dashboard, whose build and test suite CI now exercises on every push.

| Milestone | Status | Evidence |
|---|---|---|
| `M1` — working MVP (device-code sign-in, score, findings, offline-testable) | `COMPLETE`, accepted `DECISION-012` | `project/milestones/M1.md` |
| `M2` — least-privilege scope + opt-in app-only auth | `COMPLETE`, accepted `DECISION-023` | `project/milestones/M2.md` |
| `M3` — React/TypeScript dashboard UI, scoped device-code abandonment, CI wiring | `COMPLETE`, accepted `DECISION-032` | `project/milestones/M3.md` |

No milestone, issue, or roadmap version is currently open. Roadmap v5 is
the approved artifact (`DECISION-029`); v4 remains separately approved and
still governs the M1/M2 content it delivered.

## Verification evidence

Independently re-executed against the frozen **round-1** candidate
`5ce510871a17677fe862e3098972d9a85a6727a9`. Round 1's Codex general and
Codex security reviews both independently found this table, at the time,
still bound to the product-identical parent commit (`802ea4d…`) rather
than the actual reviewed candidate — real finding, fixed here. This
repair commit changes `README.md` (two governance/`RISK` rows) and this
file only — no product/backend/frontend/CI-config file — so the round-1
results below remain the accurate, current state of the tree.

| Check | Command/method | Candidate SHA | Result | Evidence gap |
|---|---|---|---|---|
| Backend tests | `python3 -m unittest discover -s tests` | `5ce510871a17…` | 188 passed, exit 0 | none |
| Frontend tests | `cd frontend && npm test` | `5ce510871a17…` | 91 passed, 7 test files, exit 0 | none |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | `5ce510871a17…` | exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | `5ce510871a17…` | passed (67 required files) | none |
| Frontend build | `cd frontend && npm run build` | `5ce510871a17…` | produced `web/index.html`/`index.css`/`index.js` | no build-provenance/lockfile-audit check (`RISK-009`, accepted `DECISION-028`) |
| Fresh-clone onboarding | `git clone` to a scratch directory, then `cd frontend && npm install && npm run build && cd .. && python3 server.py` | `5ce510871a17…` | exit 0 throughout; `GET /api/health` → 200; `GET /` → 200 with CSP header present; no Python dependency manifest exists | none — independently reproduced from a genuinely fresh clone, not asserted from memory |
| CI (GitHub Actions) | `.github/workflows/validate.yml`, `validate` job | `861f401` (product/CI-config identical to `5ce510871a17…`) | green — all 10 steps succeeded (confirmed via `gh run watch`) | reviewer sandboxes have no network access to independently query the Actions API |
| Repository/branch hygiene | `git ls-remote --heads origin`; `gh api repos/.../branches` | — | exactly one branch, `main`, on `origin`; local `main` identical to `origin/main`; all four historical PRs merged/closed | none |
| Browser verification | Manual walkthrough in a real browser | per `ISSUE-0012` handoff | as expected | jsdom-based tests are not a real browser engine; no automated real-browser test exists in CI |
| Live E2E | Sign-in + fetch against a real tenant, either mode | — | **not performed** | protected action requiring separate human approval; unchanged since M1 |

## Four mandatory reviews

**Round 1** (candidate `5ce510871a17677fe862e3098972d9a85a6727a9`):

| Order | Fresh review | Report path | Reviewed SHA | Outcome |
|---:|---|---|---|---|
| 1 | Claude general | `project/reviews/milestones/PROJECT-5ce510871a17-claude-general.md` | `5ce510871a17…` | `CHANGES_REQUIRED` |
| 2 | Codex general | `project/reviews/milestones/PROJECT-5ce510871a17-codex-general.json` | `5ce510871a17…` | `BLOCKED` |
| 3 | Claude security | `project/reviews/milestones/PROJECT-5ce510871a17-claude-security.md` | `5ce510871a17…` | `BLOCKED` |
| 4 | Codex security | `project/reviews/milestones/PROJECT-5ce510871a17-codex-security.json` | `5ce510871a17…` | `BLOCKED` |

Initial peer conclusions were withheld: **yes.** Both Codex reviews were
launched as background processes before either Claude report was
written, and both Claude reports were written without reading
`project/reviews/milestones/PROJECT-*` first.

**Round 2 (this repair) has not yet run** — see "Findings, remediation,
and invalidation" below. A fresh set of all four reviews against this
commit is the next required action.

## Findings, remediation, and invalidation

**Round-1 general findings (both against `5ce510871a17…`):**

- **Claude general — `CHANGES_REQUIRED`, two findings:** F-001 (high):
  this file's own "Frozen candidate SHA" and verification table named
  `802ea4d` (the product-identical parent) rather than the actual
  reviewed commit `5ce5108` — the same class of record-binding defect
  every milestone gate in this project has hit at least once. F-002
  (medium): `README.md`'s "Known limitations" table had a stale
  `ISSUE-0013`/abandon row (said "blocked pending a human decision" when
  it was actually accepted, `DECISION-027`) and was missing `RISK-009`
  and `RISK-010` entirely, despite the table's own preamble claiming to
  list every accepted residual risk. No product-code defect found;
  onboarding independently reproduced from a genuinely fresh clone and
  confirmed accurate.
- **Codex general — `BLOCKED`, one finding (F-001, high):** independently
  found the same candidate-binding defect as Claude general's F-001 —
  the launcher target (`5ce5108`) didn't match this file's claimed frozen
  candidate (`802ea4d`), and required checks couldn't be reproduced in
  the review sandbox as a result (compounded by the sandbox's own
  recurring execution-evidence limitations: no writable temp dir, no
  loopback sockets, no frontend dependencies).

**Round-1 security findings (both against `5ce510871a17…`):**

- **Claude security — `BLOCKED`, two findings:** SEC-001 (high) — the
  same candidate-binding defect, security-framed: per `AGENTS.md`,
  wrong-commit-bound evidence must block a security review regardless of
  how clean the underlying code is, even though this reviewer
  independently re-verified every cited check against the *correct* SHA
  directly. SEC-002 (medium) — the same `README.md` risk-disclosure
  staleness as Claude general's F-002, security-framed (a reader relying
  on the table would under-count the project's actual accepted risk
  surface). No new product security defect found across a full-coverage
  pass (trust boundaries, auth/authz, secrets/logs, injection,
  dependencies/CI, network, config defaults, privacy/retention,
  governance integrity) — every property re-checked matches M1/M2/M3's
  own already-accepted state.
- **Codex security — `BLOCKED`, two findings:** `SEC-001` (high,
  `PROJECT-SEC-TARGET-IDENTITY-MISMATCH`) — same candidate-binding
  defect, independently converged with both Claude reports and Codex
  general. `SEC-002` (medium) — the review sandbox's own recurring
  inability to complete required checks (loopback sockets, temp dir,
  frontend dependencies), the same class of limitation this project has
  accepted repeatedly (not a new finding about this candidate's actual
  security posture).

**All four reviewers converged on the same root cause for the blocking
findings**: this record's candidate-binding fields and verification
table were written against the wrong commit before the freeze was
finalized. **This repair (round 2) fixes it** by rebinding the header and
verification table to the actual round-1 candidate `5ce5108` (with fresh,
real command output, including an independently reproduced fresh-clone
onboarding check), and separately fixes `README.md`'s two disclosed
staleness/omission defects (both general reviews' F-002 / both security
reviews' SEC-002). No product, backend, frontend, or CI-config file
changed in this repair.

- General-remediation cycles used: **`1` (maximum 1) — exhausted**, this
  round.
- Security-remediation cycles used: `1` (maximum 2).
- Highest iteration count for any loop: `2` (round 1 + round 2; absolute
  maximum 5).
- Reviews invalidated and rerun: this repair creates a new candidate per
  `AGENTS.md` — round 1's four reports above remain on record but are
  superseded; all four reviews must run fresh against the new candidate
  (this commit) before any human decision.
- Critical/high findings remaining: **none on product code.** Every
  finding across all four round-1 reviews was either the shared
  candidate-binding defect or the `README.md` disclosure staleness — no
  reviewer identified a product-code correctness or security defect
  anywhere in the project.

## Documentation and release readiness

- Documentation audit: to be assessed by the general reviews — `README.md`,
  `frontend/README.md`, `CONTRIBUTING.md`, `docs/security-boundaries.md`,
  `AGENTS.md`, `docs/workflow.md`, `docs/roles-and-responsibilities.md`,
  `docs/approvals-and-reviews.md` all exist and were each touched by at
  least one of M1/M2/M3's own documentation obligations.
- Migration/rollback: `N/A` — the app persists no data in any mode; the
  vanilla `web/` UI (pre-`ISSUE-0012`) remains in Git history if
  `DECISION-024` is ever revoked.
- Onboarding/operations: `git clone` → `cd frontend && npm install && npm
  run build` → `python3 server.py` (documented in `README.md` Quick Start;
  the frontend build step is a deliberate, documented regression from the
  original "clone and run" property, `RISK-010`, accepted `DECISION-029`).
- Known limitations: as named in `README.md`'s "Known limitations" table
  and `docs/security-boundaries.md` — to be independently checked for
  accuracy by the general reviews rather than asserted here.

## Residual risks (project-wide, as of this candidate)

| Risk | Severity | Treatment | Owner/review date |
|---|---|---|---|
| `RISK-001` (device-code may be blocked by tenant policy) | Medium | Accepted `DECISION-001`; partially mitigated by app-only mode | Jay |
| `RISK-002` (no local auth beyond loopback binding; widened for app-only) | Medium–high in app-only mode | Accepted as widened `DECISION-014` | Jay |
| `RISK-004` (heuristic score, not compliance certification) | Low | Documented, `DECISION-001`/M1 | Jay |
| `RISK-005` (client secret exposed browser-side during entry) | Medium–high | Accepted, roadmap v4 | Jay |
| `RISK-006` (app-only token can't be scoped narrower than app registration) | Medium | Documentation + UI caution only | Jay |
| `RISK-009` (npm build-time supply chain) | Medium | Accepted `DECISION-028` | Jay / if scope or user base grows |
| `RISK-010` (onboarding regression — build step required) | Low | Accepted `DECISION-029` | Jay / on build-arrangement change |
| `RISK-011` (device-code abandon-retry fails open after ~16 min) | Low–medium | Accepted `DECISION-027` | Jay / if abandon is revisited |
| SEC-001 (M2, silent-renewal-after-revocation replay) | Low | Tracked, non-blocking, `DECISION-023` | Jay |
| SEC-003 (M2, unauthenticated credential-validation oracle) | Low | Tracked, non-blocking, `DECISION-023` | Jay |

None of these is newly identified by this record — all were already
accepted or tracked at their respective milestone gates. Listed here so
the full project-wide picture is visible in one place, as `ROADMAP.md`'s
project-level definition of done requires ("security... accurate").

## Human decision

- Decision record: **none yet.**
- Exact package/candidate approved: `N/A` — pending the four reviews above.
- Result: `N/A`.

Reviews passing means only that they passed for the documented scope, SHA,
and evidence. It is not a security certification.
