<!-- claudex-state
stage: ISSUE_REPAIR
active_issue: ISSUE-0006
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
| Active issue | `ISSUE-0006` (docs + E2E) — status `REPAIRING`, branch `ai/ISSUE-0006-docs-verification`, Starting SHA `4e8e999` |
| Issue repair round | Repair round 3 (over the default 2-round limit; authorized by DECISION-007) — CURRENT.md staleness only |
| Candidate product commit | `ai/ISSUE-0006-docs-verification` at `e95edf2b4cb5b3e420846e10cd340eeaa9158bec` (repair-2 candidate; already committed, awaiting a fresh review of this exact SHA) |
| Latest implementation handoff | `project/handoffs/ISSUE-0006-handoff.md` |
| Latest Codex review | ISSUE-0006 repair-2 `ISSUE-0006-e95edf2b4cb5-codex.json` (BLOCKED; F-002 this record was stale) + response; metadata-only fix pending final review |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f` |
| Last human decision | `DECISION-009` (ISSUE-0004 final round); also `DECISION-008` (evaluability model), `DECISION-007`..`001` |
| Open blockers | None. Standing: Codex issue reviews stay `BLOCKED` on execution evidence (DECISION-004); author runs checks out-of-band |
| Next required actor | Claude (run one more fresh Codex review of the current, already-committed candidate) |
| Next permitted action | Run `./scripts/run-codex-review.sh issue ISSUE-0006 4e8e999… <HEAD>` against the exact current HEAD; if BLOCKED only on execution evidence with no substantive finding, merge under DECISION-004/005/007 — then present M1 for the four-review milestone gate |
| Actions not yet permitted | Merge without a clean review, publication, deployment, live tenant auth/fetch, or any protected action |

When this repository is adopted for a project, replace the values above and add
links to the exact brief, approval decision, roadmap, issue, and review files.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
