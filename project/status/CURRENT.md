<!-- claudex-state
stage: ISSUE_REPAIR
active_issue: ISSUE-0004
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
| Active milestone | `M1` (in progress) |
| Active issue | `ISSUE-0004` (analyzer) — status `REPAIRING`, branch `ai/ISSUE-0004-analyzer`, Starting SHA `e94ef5a` |
| Issue repair round | None |
| Candidate product commit | Branch HEAD of `ai/ISSUE-0003-graph-client` (the launcher binds the exact SHA at review time) |
| Latest implementation handoff | `project/handoffs/ISSUE-0004-handoff.md` |
| Latest Codex review | ISSUE-0003 final `ISSUE-0003-065675e53ee8-codex.json` — no product-code defect (DECISION-004/007) |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e` |
| Last human decision | `DECISION-007` (raised repair budget); also `DECISION-006`..`001` |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (implement ISSUE-0004 autonomously per DECISION-005) |
| Next permitted action | Start `ISSUE-0004` (analyzer + rules + scoring) on branch `ai/ISSUE-0004-analyzer` from `main`; implement with sanitized fixtures, run checks, Codex review + repairs (DECISION-007 budget), merge under DECISION-004/005 |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
