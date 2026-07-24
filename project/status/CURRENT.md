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
| Active issue | None — ISSUE-0005 COMPLETE and merged |
| Issue repair round | None |
| Candidate product commit | `main` at the ISSUE-0005 merge; reviewed product SHA `3dc059f` |
| Latest implementation handoff | `project/handoffs/ISSUE-0005-handoff.md` |
| Latest Codex review | ISSUE-0005 final `ISSUE-0005-3dc059f2b16c-codex.json` — no substantive defect (DECISION-004/007) |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f` |
| Last human decision | `DECISION-009` (ISSUE-0004 final round); also `DECISION-008` (evaluability model), `DECISION-007`..`001` |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (implement ISSUE-0006 autonomously per DECISION-005) |
| Next permitted action | Start `ISSUE-0006` (docs finalization + E2E verification) on branch `ai/ISSUE-0006-docs-verification` from `main`; verify README from a clean-checkout perspective, run full checks, Codex review, merge under DECISION-004/005/007 — then present M1 for the milestone gate |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
