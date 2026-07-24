<!-- claudex-state
stage: ISSUE_REVIEW
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
| Stage | `IMPLEMENTATION` |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v1; APPROVED (DECISION-001) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (binds `179a023`) |
| Roadmap | `ROADMAP.md` v3; APPROVED (DECISION-003, binds `125d74f`) |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` |
| Active milestone | None |
| Active issue | None |
| Issue repair round | None |
| Candidate product commit | None |
| Latest implementation handoff | None |
| Latest Codex review | round 2 `project/reviews/plans/ROADMAP-4daf03ca5be5-codex.json` (BLOCKED) + response `…-4daf03ca5be5-claude-response.md` |
| Last human decision | `DECISION-003` (roadmap v3 approval); also `DECISION-001` (brief), `DECISION-002` (launcher fix) |
| Open blockers | None gating implementation. Accepted residual: Codex review sandbox cannot run `validate_repo.py` (F-004) — run it out-of-band per issue |
| Next required actor | Claude (implement ISSUE-0001 in a fresh issue task) |
| Next permitted action | Start `ISSUE-0001` on branch `ai/ISSUE-0001-server-shell`: write implementation plan, implement server + UI shell + `/api/health` + Host-allowlist, run checks, commit, set stage `ISSUE_REVIEW` with `active_issue: ISSUE-0001`, then run `./scripts/run-codex-review.sh issue ISSUE-0001 <BASE> <HEAD>` |
| Actions not yet permitted | Roadmap approval, implementation, review of product code, merge, publication, deployment, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
