# Project-level final review: CAreview

**Status:** `REVIEWING`
**Approved roadmap:** `ROADMAP.md` version `5`, `APPROVED` (`DECISION-029`, binds `8ea41ee`)
**Frozen candidate SHA:** `802ea4d5d9cb92a6c5dd26ce7022ebe65bb8b589` (the `M3` acceptance commit — `main`'s tip)
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

Independently re-executed against the frozen candidate
`802ea4d5d9cb92a6c5dd26ce7022ebe65bb8b589`.

| Check | Command/method | Result | Evidence gap |
|---|---|---|---|
| Backend tests | `python3 -m unittest discover -s tests` | 188 passed, exit 0 | none |
| Frontend tests | `cd frontend && npm test` | 91 passed, 7 test files, exit 0 | none |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files) | none |
| Frontend build | `cd frontend && npm run build` | produced `web/index.html`/`index.css`/`index.js` | no build-provenance/lockfile-audit check (`RISK-009`, accepted `DECISION-028`) |
| CI (GitHub Actions) | `.github/workflows/validate.yml`, `validate` job | green — all 10 steps succeeded (confirmed via `gh run watch`) | reviewer sandboxes have no network access to independently query the Actions API |
| Repository/branch hygiene | `git ls-remote --heads origin`; `gh api repos/.../branches` | exactly one branch, `main`, on `origin`; local `main` identical to `origin/main` | none |
| Browser verification | Manual walkthrough in a real browser | as expected, per `ISSUE-0012` handoff | jsdom-based tests are not a real browser engine; no automated real-browser test exists in CI |
| Live E2E | Sign-in + fetch against a real tenant, either mode | **not performed** | protected action requiring separate human approval; unchanged since M1 |

## Four mandatory reviews

To be recorded once run — see `project/reviews/milestones/PROJECT-<sha>-*`.

| Order | Fresh review | Report path | Reviewed SHA | Outcome |
|---:|---|---|---|---|
| 1 | Claude general | *pending* | — | — |
| 2 | Codex general | *pending* | — | — |
| 3 | Claude security | *pending* | — | — |
| 4 | Codex security | *pending* | — | — |

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
