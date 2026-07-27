<!-- claudex-state
stage: ISSUE_REVIEW
active_issue: ISSUE-0008
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
acquisition inside `auth.py` only — no endpoint, no UI) is implemented and
committed on branch `ai/ISSUE-0008-app-only-token` (checked out; not merged
to `main`). Round 0's Codex review (`88a4a6d`) returned `BLOCKED` with two
required findings (F-001: scope-override was possible; F-002: missing
device-code-supersedes-app-only race tests), both fixed in repair round 1.
Round 1's re-review (`2051254`) returned `BLOCKED` with **zero findings** —
the sole blocker is the accepted sandbox execution-evidence residual
(`DECISION-015`). Only 1 of 2 permitted repair rounds was needed. All local
checks pass at the round-1 candidate (116 unit tests, clean compile, clean
governance validation). Per `AGENTS.md`'s completion standard and the
`DECISION-010`/`DECISION-016` precedent, this Claude task cannot mark
`ISSUE-0008` complete on its own — it is presenting the clean result to the
human for an advance/merge decision. See "Next permitted action" below.

`ISSUE-0007` (trim delegated scope) is complete and merged (`0c35851`,
`DECISION-016`). M1 remains complete and accepted (`DECISION-012`). Brief v2
and roadmap v4 remain approved (`DECISION-013`/`014`/`015`).

| Field | Current value |
|---|---|
| Stage | `ISSUE_REVIEW` — `ISSUE-0008` implemented, Codex issue review pending |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007` of 5 complete; `ISSUE-0008` implemented, in review) |
| Active issue | `ISSUE-0008` — implemented on `ai/ISSUE-0008-app-only-token`, `REVIEWING` |
| Issue repair round | 1 of 2 permitted, used and reviewed clean (round 0 `BLOCKED` with F-001/F-002, both fixed; round 1 `BLOCKED` with zero findings — sole blocker the accepted sandbox residual). No further Claude-initiated repair is needed or permitted; a human decision is required next |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s reviewed candidate `b314d82087f36b5fadae3119410e838ec2255997` is merged into `main` at `0c35851cc06ed87c5dda453c4c1b1b39b87dbde3`. `ISSUE-0008`'s round-1 candidate `205125474389932f02e7c484dd59ad612892ac4b` on `ai/ISSUE-0008-app-only-token` is reviewed and clean of findings, awaiting a human advance/merge decision |
| Latest implementation handoff | `project/handoffs/ISSUE-0008-handoff.md` (M2, round 0) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone |
| Latest Codex issue review | `ISSUE-0008` round 1 (final): `project/reviews/issues/ISSUE-0008-205125474389-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual. Round 0: `project/reviews/issues/ISSUE-0008-88a4a6d355eb-codex.json` — `BLOCKED` (F-001: scope-override possible; F-002: missing device-code-supersedes-app-only race tests; sandbox limitation), both fixed in round 1. Prior issue: `ISSUE-0007` round 2 (final): `project/reviews/issues/ISSUE-0007-b314d82087f3-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`) |
| Last human decision | `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None gating `ISSUE-0008`. Accepted residual (per `DECISION-015`): the Codex review sandbox cannot run `validate_repo.py`/the full unit suite/compile cache — run these out-of-band per issue, as for every issue so far |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once `ISSUE-0009..0010` land. Neither is a completion gate for any issue |
| Next required actor | **The human.** The round-1 candidate `205125474389932f02e7c484dd59ad612892ac4b` is reviewed and clean of findings (only 1 of 2 repair rounds was needed). Decide whether to accept it (per the `DECISION-010`/`DECISION-016` precedent for the identical sandbox-only-blocker pattern) and approve advancing/merging `ISSUE-0008` |
| Next permitted action | Awaiting the human's advance/merge decision for `ISSUE-0008`'s round-1 candidate `205125474389932f02e7c484dd59ad612892ac4b`. If approved: record a `DECISION-0xx`, merge `ai/ISSUE-0008-app-only-token` into `main`, mark `ISSUE-0008` `COMPLETE` in `ROADMAP.md`'s M2 table and `project/issues/ISSUE-0008.md`, then start `ISSUE-0009` in a **new** top-level Claude task per `AGENTS.md` |
| Actions not yet permitted | Merge `ai/ISSUE-0008-app-only-token` without a human advance/merge decision; any `ISSUE-0009`+ work before `ISSUE-0008` completes; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

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
