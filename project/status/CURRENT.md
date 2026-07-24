<!-- claudex-state
stage: ISSUE_REPAIR
active_issue: ISSUE-0001
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
| Stage | `ISSUE_REVIEW` |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v1; APPROVED (DECISION-001) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (binds `179a023`) |
| Roadmap | `ROADMAP.md` v3; APPROVED (DECISION-003, binds `125d74f`) |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` |
| Active milestone | None |
| Active issue | `ISSUE-0001` (server shell) — status REVIEWING, branch `ai/ISSUE-0001-server-shell`, Starting SHA `840b8ff` |
| Issue repair round | Repair round 1 (addressing Codex round-1 findings F-001..F-003) |
| Candidate product commit | Branch HEAD of `ai/ISSUE-0001-server-shell` (repaired candidate; launcher records the full SHA) |
| Latest implementation handoff | `project/handoffs/ISSUE-0001-handoff.md` (plan: `ISSUE-0001-plan.md`) |
| Latest Codex review | issue round 1 `project/reviews/issues/ISSUE-0001-5a239c3225b6-codex.json` (BLOCKED: F-001 README, F-002 status, F-003 advisory bind, plus execution-evidence limitations) |
| Last human decision | `DECISION-003` (roadmap v3 approval); also `DECISION-001` (brief), `DECISION-002` (launcher fix) |
| Open blockers | Structural: the Codex review sandbox is read-only with no sockets/temp, so it cannot execute this project's checks; issue reviews BLOCK on missing execution evidence even when code is correct. Out-of-band checks pass. Gate policy is a human decision |
| Next required actor | Claude (finish repair round 1), then Human (execution-evidence gate policy + merge) |
| Next permitted action | Commit the repaired ISSUE-0001 candidate (F-001..F-003 fixed) with real out-of-band check evidence, then present the structural execution-evidence limitation to the human for a gate-policy decision before re-review/merge |
| Actions not yet permitted | Merge, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
