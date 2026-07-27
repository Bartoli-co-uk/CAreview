<!-- claudex-state
stage: ISSUE_REVIEW
active_issue: ISSUE-0011
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
no product source) is implemented and in review.** No deferral was recorded
against it, so it started directly in a new top-level task, base
`4f35275d004265ee152348e7e3d1f7b9f6a62cc6`. Round 0's candidate documents
both auth modes in `README.md` (a new "App-only mode (advanced)" section
covering the exact prerequisite, secret lifecycle, rotation/revocation,
and the certificate-deferral note; a new "End-to-end walkthrough" section
for both modes with live steps marked as the reader's own protected
action) and extends `docs/security-boundaries.md`'s application-boundaries
section with the app-only trust-boundary delta, widened `RISK-002`, and
the `RISK-006` residual. No product source changed. Full evidence is in
`project/handoffs/ISSUE-0011-handoff.md`.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). `ISSUE-0007` through
`ISSUE-0010` are complete and merged; `ISSUE-0011` is implemented and
awaiting its fresh Codex review — the final M2 issue.

| Field | Current value |
|---|---|
| Stage | `ISSUE_REVIEW` — `ISSUE-0011` round-0 candidate submitted for Codex review |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007`, `ISSUE-0008`, `ISSUE-0009`, `ISSUE-0010` of 5 complete; `ISSUE-0011` in review) |
| Active issue | `ISSUE-0011` (M2 documentation finalization), branch `ai/ISSUE-0011-m2-docs`, base `4f35275d004265ee152348e7e3d1f7b9f6a62cc6` |
| Issue repair round | None open (round 0 awaiting first review) |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. `ISSUE-0009`'s candidate `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` merged at `8253c1d7a754a3a967c2687c5ccc45e71794391a`. `ISSUE-0010`'s candidate `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` merged at `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`. `ISSUE-0011` is documentation-only; its round-0 candidate not yet reviewed |
| Latest implementation handoff | `project/handoffs/ISSUE-0011-handoff.md` (M2, round 0) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone (4 of 5 issues complete, 1 in review) |
| Latest Codex issue review | `ISSUE-0010` round 2 (final): `project/reviews/issues/ISSUE-0010-2a2d0b73e94d-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual. `ISSUE-0011` round 0: not yet run |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`); `ISSUE-0010` `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` (merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`) |
| Last human decision | `DECISION-020` (ISSUE-0010 advance and merge); `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None. `ISSUE-0011`'s round-0 candidate is implemented, checked, and awaiting its first Codex review |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once dual-mode auth is fully accepted. Neither is a completion gate for any issue |
| Next required actor | Claude — invoke the fresh Codex review for `ISSUE-0011` round 0 |
| Next permitted action | Invoke `./scripts/run-codex-review.sh issue ISSUE-0011 4f35275d004265ee152348e7e3d1f7b9f6a62cc6 <round-0-candidate-sha>` |
| Actions not yet permitted | Merging `ISSUE-0011` before a clean or human-accepted review outcome; any M3+/post-roadmap work; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate, and `project/handoffs/ISSUE-0011-handoff.md`
for `ISSUE-0011`'s verification evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
