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

**Resume point:** `ISSUE-0010` (sign-in card mode toggle and app-only form)
is **COMPLETE**, merged into `main` at `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`
(`DECISION-020`).

**`ISSUE-0011` (M2 documentation finalization — README + `docs/security-boundaries.md`,
no product source) is implemented and reviewed clean, awaiting a human
advance/merge decision.** Round 0's candidate was reviewed `BLOCKED` with
two findings (F-001 inaccurate secret-transmission wording; F-002 missing
durable start-authorization record) — both fixed in repair round 1:
`DECISION-021` records the human's exact "begin ISSUE-0011" instruction,
and the README's secret-lifecycle wording now precisely describes both
transmission hops (browser → local server, once; local server →
Microsoft's token endpoint, on acquisition and every renewal). The round-1
candidate, `e878cdcd979b7be87ff20cc986cb16d0d457dfe0`, was reviewed
(`project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json`) `BLOCKED`
with **zero findings**; the sole blocker is the same sandbox
execution-evidence limitation accepted for every prior M2 issue
(`DECISION-010`/`DECISION-015`/`DECISION-016`/`DECISION-017`/`DECISION-019`/
`DECISION-020` precedent). Only 1 of 2 permitted repair rounds was needed.
This Claude task stops here per the completion standard and does not merge
`ISSUE-0011` itself. Full evidence is in
`project/handoffs/ISSUE-0011-handoff.md`.

`ISSUE-0011` is the final planned M2 issue — merging it completes M2's
issue set, though M2 acceptance itself is a separate milestone gate (four
fresh reviews against one frozen candidate) not initiated by this task.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). `ISSUE-0007` through
`ISSUE-0010` are complete and merged; `ISSUE-0011` is implemented and
cleanly reviewed, awaiting the human's advance/merge decision.

| Field | Current value |
|---|---|
| Stage | `IMPLEMENTATION` — `ISSUE-0007` through `ISSUE-0010` complete; `ISSUE-0011` reviewed clean (round 1, final), awaiting human advance/merge decision |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007`, `ISSUE-0008`, `ISSUE-0009`, `ISSUE-0010` complete; `ISSUE-0011` reviewed clean, awaiting human decision) |
| Active issue | None (this Claude task has stopped). `ISSUE-0011`'s round-1 candidate `e878cdcd979b7be87ff20cc986cb16d0d457dfe0` on `ai/ISSUE-0011-m2-docs` awaits the human's advance/merge decision |
| Issue repair round | `ISSUE-0011`: 1 of 2 permitted repair rounds was used and is final (clean, zero findings) |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. `ISSUE-0009`'s candidate `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` merged at `8253c1d7a754a3a967c2687c5ccc45e71794391a`. `ISSUE-0010`'s candidate `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` merged at `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`. `ISSUE-0011`'s round-1 candidate `e878cdcd979b7be87ff20cc986cb16d0d457dfe0` reviewed `BLOCKED` with zero findings (sandbox residual only); not yet merged |
| Latest implementation handoff | `project/handoffs/ISSUE-0011-handoff.md` (M2, rounds 0-1, awaiting human decision) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone (4 of 5 issues complete, 1 awaiting merge decision) |
| Latest Codex issue review | `ISSUE-0011` round 1 (final): `project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual. Round 0: `project/reviews/issues/ISSUE-0011-b0b91742ec6c-codex.json` — `BLOCKED` (F-001 inaccurate secret-transmission wording; F-002 missing start authorization), fixed in round 1. Prior issue: `ISSUE-0010` round 2 (final) — `BLOCKED`, zero findings, same sandbox residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`); `ISSUE-0010` `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` (merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`) |
| Last human decision | `DECISION-021` (ISSUE-0011 start authorization); `DECISION-020` (ISSUE-0010 advance and merge); `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None product-related — `ISSUE-0011`'s round-1 candidate is clean of every actionable finding. **Process blocker:** `ISSUE-0011` cannot merge without an explicit human advance/merge decision (same pattern as every prior issue) |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once dual-mode auth is fully accepted. Neither is a completion gate for any issue. Once `ISSUE-0011` merges, M2's five planned issues are all complete and the M2 milestone gate (four fresh reviews against one frozen candidate) becomes the next available step — not automatic, and not something this task initiates |
| Next required actor | The human — decide whether to advance and merge `ISSUE-0011`'s round-1 candidate |
| Next permitted action | **Wait for the human's advance/merge decision on `ISSUE-0011`.** If approved: merge `ai/ISSUE-0011-m2-docs` (`e878cdcd979b7be87ff20cc986cb16d0d457dfe0`) into `main`, mark `ISSUE-0011` `COMPLETE`, update this file. M2's milestone gate is a separate, later human-initiated step |
| Actions not yet permitted | Merging `ISSUE-0011` without the human's decision; any M2 milestone-gate or M3+ work; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate, `project/handoffs/ISSUE-0010-handoff.md`
for `ISSUE-0010`'s (merged) verification evidence, and
`project/handoffs/ISSUE-0011-handoff.md` for `ISSUE-0011`'s round-1
candidate (`e878cdcd979b7be87ff20cc986cb16d0d457dfe0`, not yet merged).

| Check | Command | Result at `ISSUE-0011` round-1 candidate |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
