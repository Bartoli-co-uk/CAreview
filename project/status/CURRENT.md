<!-- claudex-state
stage: IMPLEMENTATION
active_issue: none
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

**Resume point:** `ISSUE-0010` (sign-in card mode toggle and app-only form
in `web/`) is **COMPLETE**. Its round-2 (final) candidate
`2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` was reviewed clean of every
actionable finding (`BLOCKED` only on the accepted sandbox
execution-evidence residual, `DECISION-015`; both of 2 permitted repair
rounds were used — round 0 found 2 product issues, since fixed: the secret
field wasn't cleared on a rejected `fetch()`, and the manual walkthrough
was missing successful-submit evidence; round 1 found a stale `CURRENT.md`,
fixed in round 2), and the human approved advancing and merging it
(`DECISION-020`). Merged into `main` at
`9d346f64422bf9bd5f89b43837a5f62f3e64d09b`. Required checks re-run on the
merged tree: 173 tests passed, `py_compile` clean, `validate_repo.py`
clean.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). `ISSUE-0007` through
`ISSUE-0010` are all complete and merged; `ISSUE-0011` has not started.

| Field | Current value |
|---|---|
| Stage | `IMPLEMENTATION` — `ISSUE-0007` through `ISSUE-0010` complete; `ISSUE-0011` not yet started |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007`, `ISSUE-0008`, `ISSUE-0009`, `ISSUE-0010` of 5 complete) |
| Active issue | None. `ISSUE-0011` is the next/final M2 roadmap item; start it in a new top-level Claude task per `AGENTS.md` |
| Issue repair round | None open |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. `ISSUE-0009`'s candidate `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` merged at `8253c1d7a754a3a967c2687c5ccc45e71794391a`. `ISSUE-0010`'s candidate `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` merged at `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`. No `ISSUE-0011` product code exists |
| Latest implementation handoff | `project/handoffs/ISSUE-0010-handoff.md` (M2, rounds 0-2, complete) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone (4 of 5 issues complete) |
| Latest Codex issue review | `ISSUE-0010` round 2 (final): `project/reviews/issues/ISSUE-0010-2a2d0b73e94d-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual. Round 1: `project/reviews/issues/ISSUE-0010-451dbe236769-codex.json` — `BLOCKED` (F-001 stale `CURRENT.md`), fixed in round 2. Round 0: `project/reviews/issues/ISSUE-0010-1d557b3840f7-codex.json` — `BLOCKED` (F-001 secret not cleared on rejected fetch; F-002 missing successful-submit browser evidence), fixed in round 1. Prior issue: `ISSUE-0009` round 1 (final) — `BLOCKED`, zero findings, same sandbox residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`); `ISSUE-0010` `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` (merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`) |
| Last human decision | `DECISION-020` (ISSUE-0010 advance and merge); `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None product-related. None process-related — `ISSUE-0011` has no recorded deferral, but per `AGENTS.md` still requires a new top-level Claude task and the standing per-issue review/repair gate before it may merge |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once dual-mode auth is fully landed. Neither is a completion gate for any issue |
| Next required actor | Whoever starts the next top-level task — `ISSUE-0011` is the final M2 roadmap item (see `ROADMAP.md` for its exact scope) |
| Next permitted action | Start `ISSUE-0011` on a new branch in a **new top-level Claude task** per `AGENTS.md`, base = this merge commit `9d346f64422bf9bd5f89b43837a5f62f3e64d09b` |
| Actions not yet permitted | Publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate, and `project/handoffs/ISSUE-0010-handoff.md`
for `ISSUE-0010`'s verification evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
