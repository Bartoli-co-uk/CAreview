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
| Stage | `ISSUE_REPAIR` |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v1; APPROVED (DECISION-001) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (binds `179a023`) |
| Roadmap | `ROADMAP.md` v3; APPROVED (DECISION-003, binds `125d74f`) |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` |
| Active milestone | None |
| Active issue | `ISSUE-0001` (server shell) — status `REPAIRING`, branch `ai/ISSUE-0001-server-shell`, Starting SHA `840b8ff` |
| Issue repair round | Repair round 2 (final; addressing Codex round-2 findings F-002 status, F-003 handoff, F-004 whitespace; F-001 execution is dispositioned by DECISION-004) |
| Candidate product commit | Branch HEAD of `ai/ISSUE-0001-server-shell` (repair-round-2 candidate; the launcher binds the exact SHA at review time) |
| Latest implementation handoff | `project/handoffs/ISSUE-0001-handoff.md` (repair round 2; plan `ISSUE-0001-plan.md`) |
| Latest Codex review | issue round 2 `project/reviews/issues/ISSUE-0001-f1a9db0be692-codex.json` (BLOCKED; no code defect found; F-001 execution evidence + record-hygiene findings) + response `…-5a239c3225b6-claude-response.md` |
| Last human decision | `DECISION-004` (execution-evidence gate policy); also `DECISION-003` (roadmap), `DECISION-002` (launcher fix), `DECISION-001` (brief) |
| Open blockers | Structural, dispositioned by DECISION-004: the Codex review sandbox is read-only with no sockets/temp, so it cannot execute checks; issue reviews stay `BLOCKED` on execution evidence. Out-of-band checks pass; the human decides the merge |
| Next required actor | Claude (final re-review of the repaired candidate), then Human (ISSUE-0001 merge decision) |
| Next permitted action | Commit the repair-round-2 candidate, run the final `./scripts/run-codex-review.sh issue ISSUE-0001 <BASE> <HEAD>`; if it is `BLOCKED` only on execution evidence with no substantive finding, present the report + out-of-band evidence to the human for the merge decision (per DECISION-004) |
| Actions not yet permitted | Merge, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
