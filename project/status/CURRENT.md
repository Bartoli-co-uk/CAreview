<!-- claudex-state
stage: ISSUE_REVIEW
active_issue: ISSUE-0003
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
| Active milestone | `M1` (in progress) |
| Active issue | `ISSUE-0003` (Graph client) — status `REVIEWING`, branch `ai/ISSUE-0003-graph-client`, Starting SHA `98a20bc` |
| Issue repair round | None (round 0) |
| Candidate product commit | Branch HEAD of `ai/ISSUE-0003-graph-client` (the launcher binds the exact SHA at review time) |
| Latest implementation handoff | `project/handoffs/ISSUE-0003-handoff.md` |
| Latest Codex review | Pending ISSUE-0003 review; ISSUE-0002 final was clean per DECISION-004 |
| Completed issues | `ISSUE-0001` (server shell) `23e6633`; `ISSUE-0002` (device-code auth) `3c8fb869` |
| Last human decision | `DECISION-006` (ISSUE-0002 extra round + merge); also `DECISION-005` (autonomy), `DECISION-004` (gate policy), `DECISION-003`..`001` |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (run the ISSUE-0003 Codex review) |
| Next permitted action | Run `./scripts/run-codex-review.sh issue ISSUE-0003 98a20bc… <HEAD>`; address substantive findings (≤2 repairs); if BLOCKED only on execution evidence, merge under DECISION-004/005. Live Graph fetch is a protected action; STOP before any real tenant call |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
