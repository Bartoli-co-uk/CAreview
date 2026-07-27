<!-- claudex-state
stage: ISSUE_REPAIR
active_issue: ISSUE-0009
active_milestone: M2
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

**Resume point:** `ISSUE-0008` (app-only client-credentials token
acquisition inside `auth.py` only) is **COMPLETE**, merged into `main` at
`04e68ee930c44a6c6dc438dfab39c381b6105e6d` (`DECISION-017`).

**`ISSUE-0009` is authorized and in progress.** The human explicitly
authorized starting it (`DECISION-018`), superseding `DECISION-017`'s prior
deferral. Round 0's candidate `c029199c5671069917c13c268a6c4a32ac73881f`
was reviewed `BLOCKED` with three findings:

- **F-001 (high):** the candidate lacked a durable repository record of the
  human's authorization to start, and the candidate's base SHA
  (`04e68ee`, the `ISSUE-0008` merge commit) was stale — `main`'s actual
  tip at branch-creation time was the later closeout commit `4fdfa9f`, so
  the reviewed diff spuriously included that intervening non-issue commit's
  changes to `ROADMAP.md`/`ISSUE-0008.md`/`CURRENT.md`. Fixed by
  `DECISION-018` (this record) and correcting `ISSUE-0009.md`'s Starting
  SHA to `4fdfa9f65b1e32bc0992dc3b7bd7d2357c3a8339`.
- **F-002 (medium):** the silent-renewal tests did not prove both
  `/api/policies` and `/api/analysis` complete against the *renewed* token
  specifically (the mock Graph client ignored its token argument), and the
  renewal-failure test exercised only `/api/policies`. Repair round 1
  addresses this.
- **F-003 (medium):** the secret-leak response scan did not cover every
  distinct response path (missing/type/boundary errors, all disallowed
  tenant aliases, network/invalid-response/superseded provider errors), and
  the dedicated provider-error test checked only the literal secret form,
  not its URL-encoded/JSON-escaped forms. Repair round 1 addresses this.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). `ISSUE-0007` and `ISSUE-0008`
are both complete and merged; `ISSUE-0009` is in repair round 1 of at most
2 permitted; `ISSUE-0010..0011` have not started.

| Field | Current value |
|---|---|
| Stage | `ISSUE_REPAIR` — `ISSUE-0009` round-0 candidate `BLOCKED` (3 findings); repair round 1 in progress |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007`, `ISSUE-0008` of 5 complete; `ISSUE-0009` in repair) |
| Active issue | `ISSUE-0009` (`POST /api/auth/app` endpoint), branch `ai/ISSUE-0009-app-only-endpoint`, base `4fdfa9f65b1e32bc0992dc3b7bd7d2357c3a8339` |
| Issue repair round | Round 1 of at most 2 permitted (round 0 candidate `c029199c5671069917c13c268a6c4a32ac73881f` `BLOCKED`, 3 findings) |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. `ISSUE-0009`'s round-0 candidate `c029199` reviewed `BLOCKED`; no `ISSUE-0009` candidate has been approved or merged |
| Latest implementation handoff | `project/handoffs/ISSUE-0009-handoff.md` (M2, round 0) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone (2 of 5 issues complete) |
| Latest Codex issue review | `ISSUE-0009` round 0: `project/reviews/issues/ISSUE-0009-c029199c5671-codex.json` — `BLOCKED` (F-001 missing start authorization + stale base SHA; F-002 renewal tests incomplete; F-003 secret-scan coverage incomplete). Prior issue: `ISSUE-0008` round 1 (final) — `BLOCKED`, zero findings, sandbox execution-evidence residual only |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`) |
| Last human decision | `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None process-related — `ISSUE-0009` is authorized (`DECISION-018`). Product blocker: repair round 1 must resolve F-001/F-002/F-003 before the next Codex re-review |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once `ISSUE-0009..0010` land. Neither is a completion gate for any issue |
| Next required actor | Claude — complete `ISSUE-0009` repair round 1, then invoke a fresh Codex re-review |
| Next permitted action | Fix F-001 (recorded as `DECISION-018` plus corrected Starting SHA), F-002, and F-003 on `ai/ISSUE-0009-app-only-endpoint`; rerun required checks; commit the round-1 candidate; invoke `./scripts/run-codex-review.sh issue ISSUE-0009 4fdfa9f65b1e32bc0992dc3b7bd7d2357c3a8339 <round-1-candidate-sha>` |
| Actions not yet permitted | Any `ISSUE-0010`+ work; publication, deployment, live tenant auth/fetch (either mode), or any other protected action; merging `ISSUE-0009` before a clean or human-accepted review outcome |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate, and `project/handoffs/ISSUE-0008-handoff.md`
for `ISSUE-0008`'s verification evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 116 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
