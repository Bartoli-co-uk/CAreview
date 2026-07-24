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
| Active issue | None — ISSUE-0002 COMPLETE and merged |
| Issue repair round | None |
| Candidate product commit | `main` at the ISSUE-0002 merge; reviewed product SHA `3c8fb869` |
| Latest implementation handoff | `project/handoffs/ISSUE-0002-handoff.md` |
| Latest Codex review | ISSUE-0002 final `ISSUE-0002-3c8fb869b01f-codex.json` — no product-code defect; execution-evidence only (DECISION-004) |
| Completed issues | `ISSUE-0001` (server shell) `23e6633`; `ISSUE-0002` (device-code auth) `3c8fb869` |
| Last human decision | `DECISION-006` (ISSUE-0002 extra round + merge); also `DECISION-005` (autonomy), `DECISION-004` (gate policy), `DECISION-003`..`001` |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (implement ISSUE-0003 autonomously per DECISION-005) |
| Next permitted action | Start `ISSUE-0003` (Graph client) on branch `ai/ISSUE-0003-graph-client` from `main`. First resolve A3 + the normalized data contract; implement mocked-only, run checks, Codex review, merge under DECISION-004/005. Live Graph fetch is a protected action; STOP before any real tenant call |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
