<!-- claudex-state
stage: IMPLEMENTATION
active_issue: none
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

| Field | Current value |
|---|---|
| Stage | `IMPLEMENTATION` |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v1; APPROVED (DECISION-001) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (binds `179a023`) |
| Roadmap | `ROADMAP.md` v3; APPROVED (DECISION-003, binds `125d74f`) |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` |
| Active milestone | `M1` (in progress) |
| Active issue | None — ISSUE-0006 COMPLETE and merged; all six M1 issues done |
| Issue repair round | Closed per DECISION-010 (4 rounds; no product finding in last 3) |
| Candidate product commit | `main` at the ISSUE-0006 merge; reviewed product SHA `d15f47c` |
| Latest implementation handoff | `project/handoffs/ISSUE-0006-handoff.md` |
| Latest Codex review | ISSUE-0006 final `ISSUE-0006-d15f47c5fb15-codex.json` — no product finding; closed per DECISION-010 |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c` |
| Last human decision | `DECISION-010` (ISSUE-0006 closeout); also `DECISION-009`, `DECISION-008`, `DECISION-007`..`001` |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (freeze M1 candidate and prepare the four milestone reviews) |
| Next permitted action | Freeze one candidate commit on `main` as the M1 milestone candidate; run the four blind reviews (Claude general, Codex general, Claude security, Codex security) per `docs/workflow.md`; present all four to the human for milestone acceptance |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
