<!-- claudex-state
stage: ISSUE_REVIEW
active_issue: ISSUE-0007
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

**Resume point:** `ISSUE-0007` is implemented and committed on branch
`ai/ISSUE-0007-trim-scopes` (checked out; not merged to `main`). Three Codex
issue reviews have now run, all `BLOCKED`: round 0 against
`54e207a04b1c5f86cc18c3f4860977e4d8dd6f0d` (F001 — stale 83-test count in
README), round 1 against `79f28638411dd82e04cf3d836baef86ad664cb44` (a
second stale 83-test count, plus F002 — workflow records not synced with the
review history), and round 2 against `b314d82087f36b5fadae3119410e838ec2255997`
with **zero findings** — the sole remaining blocker across all three rounds
is the review sandbox's known execution-evidence limitation (accepted
residual, `DECISION-015`), never a product defect. All local checks pass at
the round-2 candidate (85 unit tests, clean compile, clean governance
validation). Both permitted issue repair rounds are now used; no further
Claude-initiated repair may occur. Per `AGENTS.md`'s completion standard and
the `DECISION-010` precedent (the analogous ISSUE-0006 closeout, which also
required an explicit human decision despite no product findings), this
Claude task cannot mark `ISSUE-0007` complete on its own — it is presenting
the clean round-2 result to the human for an advance/merge decision. See
"Next permitted action" below.

M1 was the entire approved MVP scope and remains complete and accepted
(`DECISION-012`). Brief v2 (opt-in app-only client-credentials auth, secret
only) is approved (`DECISION-013`), with its open questions resolved
(`DECISION-014`). Roadmap v4, adding milestone `M2` (five issues,
`ISSUE-0007`..`ISSUE-0011`), is approved (`DECISION-015`). `ISSUE-0007` (trim
delegated `SCOPES` to `Policy.Read.All`) is implemented on branch
`ai/ISSUE-0007-trim-scopes` and awaiting its fresh Codex issue review.

| Field | Current value |
|---|---|
| Stage | `ISSUE_REVIEW` — `ISSUE-0007` implemented, Codex issue review pending |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress |
| Active issue | `ISSUE-0007` — implemented on `ai/ISSUE-0007-trim-scopes`, `REVIEWING` |
| Issue repair round | 2 of 2 permitted, both used and both reviewed (round 0 `BLOCKED`; round 1 `BLOCKED`; round 2 `BLOCKED` with zero findings — sole blocker is the accepted sandbox residual). No further Claude-initiated repair is permitted; a human decision is required next |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s round-2 candidate `b314d82087f36b5fadae3119410e838ec2255997` on `ai/ISSUE-0007-trim-scopes` is reviewed and clean of findings, awaiting a human advance/merge decision |
| Latest implementation handoff | `project/handoffs/ISSUE-0007-handoff.md` (M2, round 0) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only) |
| Latest Codex issue review | `ISSUE-0007` round 2 (final): `project/reviews/issues/ISSUE-0007-b314d82087f3-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual. Round 1: `project/reviews/issues/ISSUE-0007-79f28638411d-codex.json` — `BLOCKED` (F001: second stale 83-test count; F002: workflow records not synced; sandbox limitation), fixed in round 2. Round 0: `project/reviews/issues/ISSUE-0007-54e207a04b1c-codex.json` — `BLOCKED` (F001: first stale 83-test count; sandbox limitation), fixed in round 1. Prior completed-issue review: `ISSUE-0006-d15f47c5fb15-codex.json` — no product finding; closed per DECISION-010. Latest **plan** review: `ROADMAP-faf5ec70bf00-codex.json` (BLOCKED on the review-sandbox limitation only; all actionable findings fixed — see `ROADMAP-faf5ec70bf00-claude-response.md`) |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c` |
| Last human decision | `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None gating `ISSUE-0007`. Accepted residual (per `DECISION-015`): the Codex review sandbox cannot run `validate_repo.py`/the full unit suite/compile cache — run these out-of-band per issue, as for every M1 issue |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once M2 exists. Neither is a completion gate for any issue |
| Next required actor | **The human.** Both permitted issue repair rounds are used; the round-2 candidate `b314d82087f36b5fadae3119410e838ec2255997` is reviewed and clean of findings. Decide whether to accept it (per the `DECISION-010` precedent for the identical sandbox-only-blocker pattern) and approve advancing/merging `ISSUE-0007` |
| Next permitted action | Awaiting the human's advance/merge decision for `ISSUE-0007`'s round-2 candidate `b314d82087f36b5fadae3119410e838ec2255997`. If approved: record a `DECISION-0xx` (see `project/templates/`), merge `ai/ISSUE-0007-trim-scopes` into `main`, mark `ISSUE-0007` `COMPLETE` in `ROADMAP.md`'s M2 table and `project/issues/ISSUE-0007.md`, then start `ISSUE-0008` in a **new** top-level Claude task per `AGENTS.md` (this task must not continue into it). No further Claude-initiated repair or review is permitted for `ISSUE-0007` — the two-round limit is exhausted |
| Actions not yet permitted | Merge `ai/ISSUE-0007-trim-scopes` without a clean Codex review; any `ISSUE-0008`+ work before `ISSUE-0007` completes; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

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
