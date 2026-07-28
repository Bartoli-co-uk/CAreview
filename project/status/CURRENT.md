<!-- claudex-state
stage: ISSUE_REPAIR
active_issue: ISSUE-0012
active_milestone: none
-->

# Current workflow status

Update this file whenever a human approval, issue completion, milestone gate, or
material blocker changes what may happen next. Commit the update with its
supporting artifact; do not use chat as the only status record.

Keep the `claudex-state` block above synchronized with the table. The review
launcher reads that small committed block to reject a review for the wrong
workflow stage, issue, or milestone; it does not replace the human approval
records described below.

## Summary

**M2 (dual-mode authentication) is COMPLETE and accepted.** All four
mandatory milestone reviews ran against frozen candidate
`9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` (product-identical to
`98be0bc562de8f7cf52e3019715bc4cff571ad91`): Claude general
`CHANGES_REQUIRED`, Codex general `BLOCKED`, Claude security
`PASS_WITH_NOTES`, Codex security `BLOCKED`. **No reviewer found a
product-code security or correctness defect** — every blocking finding was
either a governance-record accuracy issue or the review sandbox's
already-accepted execution-evidence limitation. The human approved M2
(`DECISION-023`), treating the record-hygiene findings (this file's prior
staleness, `ROADMAP.md`'s leftover pre-approval language) as ordinary
follow-up rather than grounds for another milestone candidate — the same
disposition `DECISION-012` gave M1. `ROADMAP.md`'s stale "PLANNED
(unapproved)" language is corrected in this same commit.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). No milestone is currently
active; no roadmap work is in progress under the M1/M2 roadmap.

**Out-of-band work, now entering a retroactive per-issue review:** the human
directly instructed a rebuild of the UI as a React/TypeScript dashboard
(`frontend/`, built with Vite), and explicitly chose to proceed without the
normal pre-implementation brief/roadmap cycle (`DECISION-024`), since
`AGENTS.md`'s own instruction-order rule puts the human's current explicit
instructions above that requirement. It replaces the vanilla-JS `web/` UI
and introduces a Node.js/npm build-step exception scoped to the frontend
only (backend remains stdlib-only). No M3 milestone has been opened for
this work; whether to formalize it into one remains a decision for the
human. See `project/decisions/DECISION-024-react-frontend-build-step.md`.

The human then asked for the mandatory per-issue Codex review to be run
retroactively before this work is committed to `main`, to close that gap
rather than leave it permanently skipped. This is recorded as
**`ISSUE-0012`** (`project/issues/ISSUE-0012.md`), `Starting SHA`
`8648f2ba11907ac32016c724d8ae49a08bdb6b2d` (the `main` tip before this
work), on branch `ai/react-dashboard-frontend`. This issue is **not**
governed by `ROADMAP.md` v4 (no roadmap version covers it) — it is a
retroactive application of the per-issue review gate only, not a claim
that the missing brief/roadmap cycle has been supplied. CI
(`.github/workflows/validate.yml`) still does not run the new `npm`
commands as of this record.

**Round 0 result: `BLOCKED`.** The fresh Codex issue review against
candidate `4cb61161be32b43506bb0e2c1b6921635561054d`
(`project/reviews/issues/ISSUE-0012-4cb61161be32-codex.json`) found one
real, high-severity defect — **F-001**: `pollOnce()` had no cancellation
check, so a device-code poll still in flight when the user moved to sample
mode, app-only mode, or signed out could later settle and overwrite that
state (flip `mode` back to `"live"`, load stale tenant data, or reschedule
itself). It also raised **F-002** (medium): no durable, commit-bound
record of the required checks' real output existed in the repository, and
Codex's own sandbox could not independently run them (no
`frontend/node_modules`, no loopback socket binding, no writable temp
directory). Round 1 fixes F-001 (a real `authAttempt` cancellation token in
`frontend/src/state/appState.tsx`, with two new regression tests) and
addresses F-002 with a handoff document
(`project/handoffs/ISSUE-0012-handoff.md`) recording real command output
for every required check, bound to the round-1 candidate SHA. A fresh
Codex review of round 1 is pending as of this record.

| Field | Current value |
|---|---|
| Stage | `ISSUE_REPAIR` — `ISSUE-0012` round 1 (retroactive React/Vite frontend review, out-of-band per `DECISION-024`), repairing round 0's `BLOCKED` outcome; M1 and M2 remain complete and accepted with no milestone in progress |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) governed the completed M1; v4 has now fully delivered M2 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `COMPLETE`, accepted (`DECISION-023`). Neither milestone is currently in progress; no M3 exists yet |
| Active issue | `ISSUE-0012` — React/Vite frontend, `REPAIRING`, out-of-band (not under the M1/M2 roadmap; see `DECISION-024`). No further issues are planned under the current roadmap |
| Issue repair round | Round 1 of at most 2, repairing round 0's `BLOCKED` outcome (F-001 device-code polling race, F-002 missing check evidence) |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `M2`'s frozen product commit is `98be0bc562de8f7cf52e3019715bc4cff571ad91`; its milestone-review candidate `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` was accepted by `DECISION-023` |
| Latest implementation handoff | `project/handoffs/ISSUE-0011-handoff.md` (M2, rounds 0-1, complete) |
| Latest milestone reviews | `M2` round 1 (accepted): Claude general `CHANGES_REQUIRED` (`project/reviews/milestones/M2-9c01749b221d-claude-general.md`); Codex general `BLOCKED` (`project/reviews/milestones/M2-9c01749b221d-codex-general.json`); Claude security `PASS_WITH_NOTES` (`project/reviews/milestones/M2-9c01749b221d-claude-security.md`); Codex security `BLOCKED`, sandbox residual only (`project/reviews/milestones/M2-9c01749b221d-codex-security.json`). Round 0 (superseded, candidate `b55bf97`) retained for the record. M1 round 2 remains accepted (`DECISION-012`) |
| Latest Codex issue review | `ISSUE-0012` round 0: `project/reviews/issues/ISSUE-0012-4cb61161be32-codex.json` — `BLOCKED`, F-001 (high, device-code polling race, fixed round 1) and F-002 (medium, missing check evidence, addressed round 1 via handoff). Round 1 review pending. `ISSUE-0011` round 1 (final, unrelated M2 work): `project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`); `ISSUE-0010` `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` (merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`); `ISSUE-0011` `e878cdcd979b7be87ff20cc986cb16d0d457dfe0` (merged `b50cbc2fb67e8066f22ab06a03f61425dbf1a9d1`, `DECISION-022`) |
| Last human decision | `DECISION-024` (React/Vite frontend, direct-override, out-of-band); `DECISION-023` (M2 milestone acceptance); `DECISION-022` (ISSUE-0011 advance and merge); `DECISION-021` (ISSUE-0011 start authorization); `DECISION-020` (ISSUE-0010 advance and merge); `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None. M2 is accepted; no roadmap work is currently authorized or in progress |
| Tracked follow-up | Live-tenant sign-in verification (M1 and M2, both auth modes) — deferred pending the human's access restrictions (`DECISION-012`), remains a protected action, not a completion gate for either milestone. `DECISION-023`'s SEC-001 (silent-renewal-after-revocation replay) and SEC-003 (unauthenticated credential-validation oracle, undocumented in `RISK-002`) are tracked, non-blocking follow-ups — see `project/milestones/M2.md` and `DECISION-023`. `ISSUE-0012`: CI not yet updated for `npm` commands, and whether to open an M3 for this frontend work is undecided |
| Next required actor | Claude (this task) — run the fresh Codex issue review for `ISSUE-0012` round 1 against the round-1 candidate SHA once committed. If it passes, the human then decides whether to merge `ai/react-dashboard-frontend` to `main` and whether to open an M3 |
| Next permitted action | Invoke `./scripts/run-codex-review.sh issue ISSUE-0012 8648f2ba11907ac32016c724d8ae49a08bdb6b2d <round-1-candidate-SHA>` against the round-1 commit. A new task should read this file, `AGENTS.md`, and `ROADMAP.md` fresh before proposing any other next step |
| Actions not yet permitted | Any new issue or milestone work without an explicit human decision to start it; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M2.md` for the
full milestone record and the four review reports for complete evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed, exit 0, at the M2 milestone candidate. `174 passed` after the `DECISION-024` frontend change (`tests/test_ui_safety.py` rewritten for the React source) |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |
| Frontend tests (new, `DECISION-024`) | `cd frontend && npm test` | 88 passed, exit 0 (86 at round 0 + 2 new `deviceCodeRace.test.tsx` regression tests added in round 1) |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
