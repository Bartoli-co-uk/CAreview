<!-- claudex-state
stage: BRIEF_REVIEW
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
| Stage | `BRIEF_REVIEW` |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v1; DRAFT, awaiting human approval |
| Brief approval | Not recorded |
| Roadmap | Template only; not approved |
| Roadmap approval | Not recorded |
| Active milestone | None |
| Active issue | None |
| Issue repair round | None |
| Candidate product commit | None |
| Latest implementation handoff | None |
| Latest Codex review | None |
| Last human decision | None |
| Open blockers | None |
| Next required actor | Human (brief approval) |
| Next permitted action | Human reviews `project/brief/PROJECT_BRIEF.md` v1 and records approval or rejection of this exact commit (answering the four questions in the brief). On approval, a fresh Claude planning task drafts the roadmap. No roadmap or implementation work until approval is recorded |
| Actions not yet permitted | Roadmap approval, implementation, review of product code, merge, publication, deployment, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
