<!-- claudex-state
stage: MILESTONE_REVIEW
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

| Field | Current value |
|---|---|
| Stage | `MILESTONE_REVIEW` |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v1; APPROVED (DECISION-001) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (binds `179a023`) |
| Roadmap | `ROADMAP.md` v3; APPROVED (DECISION-003, binds `125d74f`) |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` |
| Active milestone | `M1` — frozen for the four-review gate, status `REVIEWING` |
| Active issue | None — ISSUE-0006 COMPLETE and merged; all six M1 issues done |
| Issue repair round | Closed per DECISION-010 (4 rounds; no product finding in last 3) |
| Candidate product commit | M1 remediation candidate (this commit; the launcher binds the exact SHA) — round 2, superseding `61210b4` |
| Latest implementation handoff | `project/handoffs/ISSUE-0006-handoff.md` |
| Latest Codex review | ISSUE-0006 final `ISSUE-0006-d15f47c5fb15-codex.json` — no product finding; closed per DECISION-010. M1 round-1 Codex general `M1-61210b436bd1-codex-general.json` (BLOCKED, GEN-001) — superseded, remediated (DECISION-011) |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c` |
| Last human decision | `DECISION-011` (M1 validator fix, general-remediation cycle); also `DECISION-010`, `DECISION-009`..`001` |
| Open blockers | None. M1 round 1 found a real blocking finding (validator self-test bug) which is now fixed; round 2's four fresh reviews are in progress |
| Next required actor | Human (milestone acceptance decision) |
| Next permitted action | Human reviews the M1 package (`project/milestones/M1.md` round 2, all four fresh reports) and records `APPROVE`/`REJECT`/`REMEDIATION_REQUIRED` in a decision file naming the exact package/SHAs. On approval, project completion may be pursued next |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
