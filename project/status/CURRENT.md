<!-- claudex-state
stage: ROADMAP_REVIEW
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
| Stage | `ROADMAP_REVIEW` |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v1; APPROVED (DECISION-001) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (binds `179a023`) |
| Roadmap | `ROADMAP.md` v3; Codex rounds 1–2 done (both BLOCKED), findings addressed; awaiting human approval |
| Roadmap approval | Not recorded |
| Active milestone | None |
| Active issue | None |
| Issue repair round | None |
| Candidate product commit | None |
| Latest implementation handoff | None |
| Latest Codex review | round 2 `project/reviews/plans/ROADMAP-4daf03ca5be5-codex.json` (BLOCKED) + response `…-4daf03ca5be5-claude-response.md` |
| Last human decision | `DECISION-001` (brief), `DECISION-002` (launcher fix) |
| Open blockers | Codex F-004: review sandbox cannot run `validate_repo.py` (no writable temp); out-of-band validator evidence recorded in the round-2 response. Structural — recurs every plan review |
| Next required actor | Human (roadmap approval decision) |
| Next permitted action | Human reviews `ROADMAP.md` v3 (+ the two Codex reports and responses) and either approves the exact v3 commit or requests a third confirmatory Codex review. No implementation until roadmap approval is recorded |
| Actions not yet permitted | Roadmap approval, implementation, review of product code, merge, publication, deployment, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
