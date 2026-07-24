<!-- claudex-state
stage: ISSUE_REPAIR
active_issue: ISSUE-0002
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
| Active issue | `ISSUE-0002` (device-code auth) — status `REPAIRING`, branch `ai/ISSUE-0002-device-code-auth`, Starting SHA `eb0490c` |
| Issue repair round | Repair round 1 (fixing Codex F-001 concurrency race, F-002 error normalization) |
| Candidate product commit | Branch HEAD of `ai/ISSUE-0002-device-code-auth` (the launcher binds the exact SHA at review time) |
| Latest implementation handoff | `project/handoffs/ISSUE-0002-handoff.md` |
| Latest Codex review | ISSUE-0002 round 0 `project/reviews/issues/ISSUE-0002-536f11cb7a9f-codex.json` (CHANGES_REQUIRED: F-001/F-002) + response `…-536f11cb7a9f-claude-response.md`; repaired candidate pending re-review |
| Completed issues | `ISSUE-0001` (server shell) — merged `23e6633` |
| Last human decision | `DECISION-005` (merge ISSUE-0001 + autonomous cadence to M1); also `DECISION-004` (gate policy), `DECISION-003` (roadmap), `DECISION-002` (launcher fix), `DECISION-001` (brief) |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (run the ISSUE-0002 Codex review) |
| Next permitted action | Run `./scripts/run-codex-review.sh issue ISSUE-0002 eb0490c… <HEAD>`; address substantive findings (≤2 repairs); if BLOCKED only on execution evidence, merge under DECISION-004/005. Live sign-in remains a protected action; STOP before any real tenant auth |
| Actions not yet permitted | Merge, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
