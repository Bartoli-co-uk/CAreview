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
| Active issue | None — ISSUE-0001 COMPLETE and merged |
| Issue repair round | None |
| Candidate product commit | `main` at the ISSUE-0001 merge (`23e6633`); reviewed product SHA `39cff76` |
| Latest implementation handoff | `project/handoffs/ISSUE-0001-handoff.md` |
| Latest Codex review | ISSUE-0001 final `project/reviews/issues/ISSUE-0001-39cff76bef15-codex.json` — clean (zero substantive findings) per DECISION-004 |
| Completed issues | `ISSUE-0001` (server shell) — merged `23e6633` |
| Last human decision | `DECISION-005` (merge ISSUE-0001 + autonomous cadence to M1); also `DECISION-004` (gate policy), `DECISION-003` (roadmap), `DECISION-002` (launcher fix), `DECISION-001` (brief) |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (implement ISSUE-0002 autonomously per DECISION-005) |
| Next permitted action | Start `ISSUE-0002` (device-code auth) on branch `ai/ISSUE-0002-device-code-auth` from `main`; implement, run checks, Codex review + bounded repair, then merge under DECISION-004/005. Live sign-in remains a protected action; STOP for the human before any real tenant auth |
| Actions not yet permitted | Merge, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
