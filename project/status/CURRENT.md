<!-- claudex-state
stage: ROADMAP_REVIEW
active_issue: none
active_milestone: M1
-->

# Current workflow status

Update this file whenever a human approval, issue completion, milestone gate, or
material blocker changes what may happen next. Commit the update with its
supporting artifact; do not use chat as the only status record.

Keep the `claudex-state` block above synchronized with the table. The review
launcher reads that small committed block to reject a review for the wrong
workflow stage, issue, or milestone; it does not replace the human approval
records described below.

## Summary

M1 was the entire approved MVP scope and remains complete and accepted
(`DECISION-012`). A brief v2 amendment (opt-in app-only client-credentials
auth, secret only) is now approved (`DECISION-013`), with its open questions
resolved (`DECISION-014`). A roadmap v4 candidate adding milestone `M2` (five
issues, `ISSUE-0007`..`ISSUE-0011`) has been drafted but **not yet reviewed or
approved** — stage is `ROADMAP_REVIEW`, awaiting a fresh Codex plan review of
the v4 candidate and then the human's exact approval. No M2 issue may start
until both complete.

| Field | Current value |
|---|---|
| Stage | `ROADMAP_REVIEW` — roadmap v4 candidate drafted, Codex plan review not yet run, not yet human-approved |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v3 remains the **approved** artifact (DECISION-003, binds `125d74f`). v4 is a **draft candidate** adding M2 — not yet reviewed or approved |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3 only; v4 not yet recorded) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, unapproved |
| Active issue | None. M2 issues (`ISSUE-0007`..`ISSUE-0011`) are `PENDING`, blocked on roadmap v4's Codex plan review and human approval |
| Issue repair round | None open |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. No M2 product code exists yet; only planning documents have changed |
| Latest implementation handoff | `project/handoffs/ISSUE-0006-handoff.md` (M1; no M2 handoff exists yet) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only) |
| Latest Codex issue review | ISSUE-0006 final `ISSUE-0006-d15f47c5fb15-codex.json` — no product finding; closed per DECISION-010. **No Codex plan review of roadmap v4 has been run yet** |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c` |
| Last human decision | `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | Roadmap v4 requires a fresh `./scripts/run-codex-review.sh plan <V4-HEAD-SHA>` and, after Claude responds to every finding, the human's exact approval of the final v4 commit, before `ISSUE-0007` may start |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once M2 exists. Neither is a completion gate for any issue |
| Next required actor | Claude (run the Codex plan review of roadmap v4 and respond to findings), then the human (approve the exact v4 roadmap) |
| Next permitted action | Run `./scripts/run-codex-review.sh plan <FULL-V4-HEAD-SHA>` against the committed v4 candidate; respond to every finding (max two revision rounds); then present the final v4 for the human's exact approval. No M2 issue may begin before that approval is recorded |
| Actions not yet permitted | Any M2 issue implementation; merge without a clean review; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 83 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
