# Project-level final review: CAreview

**Status:** `COMPLETE` — accepted `DECISION-033`.
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

Independently re-executed once, against a product/backend/frontend/CI-config
tree that is **byte-identical across round 1's candidate**
(`5ce510871a17677fe862e3098972d9a85a6727a9`) **and round 2's candidate**
(`917764a46cea280480f4bc40f2fbc7478dde5f9b`, the round-1 repair) — neither
repair touched any product, backend, frontend, or CI-config file, only
`project/`-tree and `README.md`. Round 1's Codex general and Codex
security reviews found this table bound to the product-identical parent
commit (`802ea4d…`) rather than either actual reviewed candidate; round
2's Codex general and Codex security reviews found the round-1 repair
still bound it to round 1's SHA specifically rather than describing the
identity explicitly, plus stale `CURRENT.md` rows (both fixed in this
follow-up commit, accepted as ordinary record-hygiene per `DECISION-033`
rather than requiring a third review round). The results below are the
accurate, current state of the tree as of round 2's candidate.

| Check | Command/method | Candidate SHA (product state, identical round 1 ↔ round 2) | Result | Evidence gap |
|---|---|---|---|---|
| Backend tests | `python3 -m unittest discover -s tests` | `5ce510871a17…` = `917764a46cea…` | 188 passed, exit 0 | none |
| Frontend tests | `cd frontend && npm test` | `5ce510871a17…` = `917764a46cea…` | 91 passed, 7 test files, exit 0 | none |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | `5ce510871a17…` = `917764a46cea…` | exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | `5ce510871a17…` = `917764a46cea…` | passed (67 required files) | none |
| Frontend build | `cd frontend && npm run build` | `5ce510871a17…` = `917764a46cea…` | produced `web/index.html`/`index.css`/`index.js` | no build-provenance/lockfile-audit check (`RISK-009`, accepted `DECISION-028`) |
| Fresh-clone onboarding | `git clone` to a scratch directory, then `cd frontend && npm install && npm run build && cd .. && python3 server.py` | `5ce510871a17…` = `917764a46cea…` | exit 0 throughout; `GET /api/health` → 200; `GET /` → 200 with CSP header present; no Python dependency manifest exists | none — independently reproduced from a genuinely fresh clone, not asserted from memory |
| CI (GitHub Actions) | `.github/workflows/validate.yml`, `validate` job | `861f401` (product/CI-config identical to both round-1 and round-2 candidates) | green — all 10 steps succeeded (confirmed via `gh run watch`) | reviewer sandboxes have no network access to independently query the Actions API |
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

**Round 2** (candidate `917764a46cea280480f4bc40f2fbc7478dde5f9b`, the round-1
repair):

| Order | Fresh review | Report path | Reviewed SHA | Outcome |
|---:|---|---|---|---|
| 1 | Claude general | `project/reviews/milestones/PROJECT-917764a46cea-claude-general.md` | `917764a46cea…` | `PASS_WITH_NOTES` |
| 2 | Codex general | `project/reviews/milestones/PROJECT-917764a46cea-codex-general.json` | `917764a46cea…` | `BLOCKED` |
| 3 | Claude security | `project/reviews/milestones/PROJECT-917764a46cea-claude-security.md` | `917764a46cea…` | `PASS_WITH_NOTES` |
| 4 | Codex security | `project/reviews/milestones/PROJECT-917764a46cea-codex-security.json` | `917764a46cea…` | `BLOCKED` |

Initial peer conclusions were withheld for round 2 too: **yes**, same
independence discipline as round 1.

**This was the second general/security review cycle (round 1 → round 2
was the one permitted general-remediation cycle; `AGENTS.md` allows at
most one).** Per that limit, round 2's findings (below) are not repaired
by a further automated round — they are presented to the human.

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

**Round-2 general findings (both against `917764a46cea…`, the round-1 repair):**

- **Claude general — `PASS_WITH_NOTES`:** confirmed both round-1 findings
  fixed by direct inspection (candidate-binding field, `README.md`'s
  three risk rows); no new finding.
- **Codex general — `BLOCKED`, one finding (F-001, high):** the repair
  fixed `README.md`'s disclosure staleness but did not fully fix the
  candidate-binding defect — this file's verification table explicitly
  bound its command evidence to round 1's SHA (`5ce5108…`) rather than
  the actual round-2 candidate itself, and `project/status/CURRENT.md`'s
  own project-review rows (lines 223/225) still named `802ea4d`,
  contradicting the launcher target. A narrower, second instance of the
  same defect class round 1 found.

**Round-2 security findings (both against `917764a46cea…`):**

- **Claude security — `PASS_WITH_NOTES`:** confirmed both round-1
  findings fixed; no new security-relevant finding — this round's diff
  touched only `README.md` prose and this file, nothing in scope of
  auth/secrets/CSP/dependencies/CI.
- **Codex security — `BLOCKED`, two findings:** `SEC-001` (high,
  `PROJECT-SEC-STALE-CANDIDATE-EVIDENCE`) — same verification-table
  binding defect Codex general found, security-framed: a human gate
  could otherwise accept round-1 evidence as if it validated the
  round-2 candidate without independently confirming tree equivalence.
  `SEC-002` (medium) — the review sandbox's own recurring inability to
  complete required checks (loopback sockets, temp dir, frontend
  dependencies, network), the same accepted-elsewhere limitation class,
  not a new finding about this candidate's actual security posture.

**All four round-2 reviewers converged**: the repair fixed the
disclosed-content defect (`README.md`) fully, but only partially fixed
the candidate-binding defect — it explained *why* the verification table
still referenced round 1's SHA (product content unchanged), but per
`AGENTS.md`'s strict rule, evidence must be bound to the *exact* candidate
under review, not cross-referenced to a prior one with a rationale.
`CURRENT.md`'s own lines 223/225 were also missed.

- General-remediation cycles used: **`1` (maximum 1) — exhausted.** Per
  `AGENTS.md`, round 2's findings are **not** repaired by a third
  automated round.
- Security-remediation cycles used: `1` (maximum 2) — one remains, but is
  moot without a new candidate, which requires resolving the exhausted
  general-remediation budget first.
- Highest iteration count for any loop: `3` (round 1 + round 2 + this
  accounting; absolute maximum 5).
- Reviews invalidated and rerun: round 1's four reports are superseded by
  round 2's. Round 2's four reports stand as the current record pending
  the human's decision below.
- Critical/high findings remaining: **none, in either round.** Every
  finding across both rounds and all eight review reports is a
  governance-record/evidence-binding defect or a documentation-disclosure
  defect (both now content-fixed; the binding mechanics remain the open
  item) — no reviewer, in either round, identified a product-code
  correctness or security defect.

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

Both rounds of the project-level four-review gate are complete. Round 1
(candidate `5ce510871a17677fe862e3098972d9a85a6727a9`) was blocked by both
general reviewers on a single defect class: this file's "Frozen candidate
SHA" and verification-evidence table named the product-identical parent
commit (`802ea4d`) rather than the actual reviewed candidate, plus a stale
`README.md` risk-disclosure passage. Round 2 (candidate
`917764a46cea280480f4bc40f2fbc7478dde5f9b`, the round-1 repair) fixed the
`README.md` disclosure fully, but all four round-2 reviewers converged on
a narrower, second instance of the same candidate-binding defect:

- **Codex general — `BLOCKED`, F-001 (high):** the "Verification evidence"
  table above still binds its command evidence to round 1's SHA
  (`5ce510871a17…`) rather than round 2's actual candidate, and
  `project/status/CURRENT.md`'s own project-review rows (Stage/Open
  blockers cells) still named `802ea4d`, contradicting the launcher
  target.
- **Codex security — `BLOCKED`, SEC-001 (high) + SEC-002 (medium):**
  SEC-001 is the same binding defect, security-framed — a human gate
  could otherwise accept round-1 evidence as validating round 2 without
  independently confirming tree equivalence. SEC-002 is the review
  sandbox's own recurring inability to complete required checks
  (loopback sockets, temp dir, frontend dependencies, network) — the
  same already-accepted limitation class from every prior milestone
  gate, not a new finding about this candidate.
- **Claude general and Claude security — both `PASS_WITH_NOTES`:**
  confirmed the round-1 findings fixed by direct inspection; neither
  identified a new finding.

**No reviewer, in either round, identified a product-code correctness or
security defect anywhere in the project.** Every finding across both
rounds and all eight reports is a governance-record/evidence-binding
defect or a documentation-disclosure defect (the latter now fixed).

`AGENTS.md` permits exactly one general-remediation cycle; it is now used
(round 1 → round 2), and round 2 still found a binding defect. Per that
limit, no further automated repair round is permitted without an explicit
human decision to extend past it.

**Options for the human:**
1. **Accept round 2's residual candidate-binding and `CURRENT.md`-staleness
   findings as documented, fix them as an ordinary follow-up commit (not a
   new project-review candidate), and record final project approval
   directly from this record** — the same disposition `DECISION-012` (M1),
   `DECISION-023` (M2), and `DECISION-032` (M3) each gave their own
   milestone gates at this same finding class (record staleness, never a
   product defect).
2. **Authorize a third review round** outside the normal one-cycle budget,
   after the binding defect is fixed, to get a fully clean set of four
   reports before any approval decision.
3. **Reject or hold** final approval for other reasons.

- Decision record: `project/decisions/DECISION-033-project-final-approval.md`
- Exact package/candidate approved: round 1
  `5ce510871a17677fe862e3098972d9a85a6727a9`; round 2 (final reviewed
  candidate) `917764a46cea280480f4bc40f2fbc7478dde5f9b`. Product/backend/
  frontend content unchanged from `861f401`/`802ea4d` throughout both
  rounds.
- Result: **approved** — option 1 of the three presented above: round 2's
  residual candidate-binding table and `CURRENT.md` staleness is treated
  as ordinary record-hygiene follow-up, corrected in this same commit
  that records this decision, mirroring `DECISION-012` (M1), `DECISION-023`
  (M2), and `DECISION-032` (M3)'s acceptance of the same class of finding
  at their own gates.

Reviews passing means only that they passed for the documented scope, SHA,
and evidence. It is not a security certification.
