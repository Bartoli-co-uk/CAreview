<!-- claudex-state
stage: ISSUE_REVIEW
active_issue: ISSUE-0009
active_milestone: M2
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

**Resume point:** `ISSUE-0008` (app-only client-credentials token
acquisition inside `auth.py` only) is **COMPLETE**. Its round-1 candidate
`205125474389932f02e7c484dd59ad612892ac4b` was reviewed clean of every
actionable finding (`BLOCKED` only on the accepted sandbox
execution-evidence residual, `DECISION-015`; only 1 of 2 permitted repair
rounds was needed), and the human approved advancing and merging it
(`DECISION-017`). Merged into `main` at `04e68ee930c44a6c6dc438dfab39c381b6105e6d`.

**`ISSUE-0009` has explicitly NOT been started.** The human approved the
`ISSUE-0008` merge but directed that `ISSUE-0009` wait — do not begin it
without a further explicit go-ahead, even though it is the next roadmap
item in sequence.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). `ISSUE-0007` and `ISSUE-0008`
are both complete and merged; `ISSUE-0009..0011` have not started.

| Field | Current value |
|---|---|
| Stage | `IMPLEMENTATION` — `ISSUE-0007` and `ISSUE-0008` complete; `ISSUE-0009` intentionally not started (human deferred it) |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007`, `ISSUE-0008` of 5 complete) |
| Active issue | None. `ISSUE-0009` is the next roadmap item but is **explicitly not started** — wait for the human |
| Issue repair round | None open |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. No `ISSUE-0009` product code exists |
| Latest implementation handoff | `project/handoffs/ISSUE-0008-handoff.md` (M2, rounds 0-1, complete) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone (2 of 5 issues complete) |
| Latest Codex issue review | `ISSUE-0008` round 1 (final): `project/reviews/issues/ISSUE-0008-205125474389-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual. Round 0: `project/reviews/issues/ISSUE-0008-88a4a6d355eb-codex.json` — `BLOCKED` (F-001 scope-override; F-002 missing race tests), both fixed in round 1. Prior issue: `ISSUE-0007` round 2 (final) — `BLOCKED`, zero findings, same sandbox residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`) |
| Last human decision | `DECISION-017` (ISSUE-0008 advance and merge; explicitly deferred starting ISSUE-0009); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None product-related. **Process blocker:** `ISSUE-0009` must not start until the human gives an explicit go-ahead — this is a human-imposed pause, not a technical or review blocker |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once `ISSUE-0009..0010` land. Neither is a completion gate for any issue |
| Next required actor | The human — decide when `ISSUE-0009` may begin |
| Next permitted action | **Wait.** When the human gives the go-ahead: start `ISSUE-0009` (`POST /api/auth/app` endpoint wiring app-only mode to the server) on a new branch (e.g. `ai/ISSUE-0009-app-only-endpoint`) in a **new top-level Claude task** per `AGENTS.md`, base = this merge commit `04e68ee930c44a6c6dc438dfab39c381b6105e6d`. Until then, no `ISSUE-0009+` implementation work is permitted |
| Actions not yet permitted | Starting `ISSUE-0009` without the human's explicit go-ahead; any `ISSUE-0010`+ work; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate, and `project/handoffs/ISSUE-0008-handoff.md`
for `ISSUE-0008`'s verification evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 116 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
