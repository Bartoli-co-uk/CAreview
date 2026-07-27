<!-- claudex-state
stage: IMPLEMENTATION
active_issue: none
active_milestone: M1
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

M1 was the entire approved MVP scope and remains complete and accepted
(`DECISION-012`). Brief v2 (opt-in app-only client-credentials auth, secret
only) is approved (`DECISION-013`), with its open questions resolved
(`DECISION-014`). Roadmap v4, adding milestone `M2` (five issues,
`ISSUE-0007`..`ISSUE-0011`), is now **approved** (`DECISION-015`) after four
Codex plan-review rounds and full remediation. No M2 issue has started yet.
Stage is `IMPLEMENTATION`, mirroring the same resting state used after the v3
roadmap approval and before `ISSUE-0001` began.

| Field | Current value |
|---|---|
| Stage | `IMPLEMENTATION` — M2 approved; no M2 issue started yet |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, not started |
| Active issue | None. `ISSUE-0007` is the next permitted M2 issue |
| Issue repair round | None open |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. No M2 product code exists yet; only planning documents have changed |
| Latest implementation handoff | `project/handoffs/ISSUE-0006-handoff.md` (M1; no M2 handoff exists yet) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only) |
| Latest Codex issue review | ISSUE-0006 final `ISSUE-0006-d15f47c5fb15-codex.json` — no product finding; closed per DECISION-010. Latest **plan** review: `ROADMAP-faf5ec70bf00-codex.json` (BLOCKED on the review-sandbox limitation only; all actionable findings fixed — see `ROADMAP-faf5ec70bf00-claude-response.md`) |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c` |
| Last human decision | `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None gating `ISSUE-0007`. Accepted residual (per `DECISION-015`): the Codex review sandbox cannot run `validate_repo.py`/the full unit suite/compile cache — run these out-of-band per issue, as for every M1 issue |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once M2 exists. Neither is a completion gate for any issue |
| Next required actor | Claude (implement `ISSUE-0007` in a fresh issue task) |
| Next permitted action | Start `ISSUE-0007` on branch `ai/ISSUE-0007-trim-scopes`: trim `auth.py`'s delegated `SCOPES` to `Policy.Read.All` only, update tests/docs, run checks, commit, set stage `ISSUE_REVIEW` with `active_issue: ISSUE-0007`, then run `./scripts/run-codex-review.sh issue ISSUE-0007 <BASE> <HEAD>` |
| Actions not yet permitted | Merge without a clean review; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 83 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
