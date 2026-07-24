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
| Issue repair round | Repair round 5 (over the DECISION-007 budget); ⛔ human decision requested before further rounds |
| Candidate product commit | Branch HEAD of `ai/ISSUE-0004-analyzer` at commit fixing F-002 nested-path validation (the launcher binds the exact SHA at review time) |
| Latest implementation handoff | `project/handoffs/ISSUE-0004-handoff.md` |
| Latest Codex review | ISSUE-0004 repair-4 `ISSUE-0004-a7ec63010bd5-codex.json` (BLOCKED; F-001 repair-limit exceeded, F-002 nested-path validation now fixed, F-003 stale records, F-004 execution) |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e` |
| Last human decision | `DECISION-007` (raised repair budget); also `DECISION-006`..`001` |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (implement ISSUE-0004 autonomously per DECISION-005) |
| Next permitted action | ISSUE-0004 has used 5 repair rounds, exceeding the DECISION-007 budget (~4). All substantive code findings are now fixed (F-002/F-003 from round 4 addressed). ⛔ Human decides: authorize one final confirming review + merge, or accept current state as a residual and merge without a further round |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
