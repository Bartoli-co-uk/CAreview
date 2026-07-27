<!-- claudex-state
stage: ISSUE_REVIEW
active_issue: ISSUE-0010
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

**Resume point:** `ISSUE-0009` (`POST /api/auth/app` endpoint) is
**COMPLETE**, merged into `main` at `8253c1d7a754a3a967c2687c5ccc45e71794391a`
(`DECISION-019`).

**`ISSUE-0010` (sign-in card mode toggle and app-only form in `web/`) is
implemented and in review.** No deferral was recorded against it, so it
started directly in a new top-level task, base
`f3b5414a4f2d3104d11bbb1ce6d5669a58123e79`. Round 0's candidate implements
the toggle, the app-only form, client-side tenant-alias rejection, and
secret-field clearing on submit/mode-switch/logout, with 10 new static
`tests/test_ui_safety.py` assertions. Because no JavaScript test toolchain
exists, the runtime clearing behavior was additionally verified by a
human-performed, Claude-guided manual browser walkthrough (synthetic
values; dev tools inspection of the field/DOM/console after submit, mode
switch, and logout) — the human reported the field was empty at every
checkpoint and nothing appeared in console or storage. Full evidence is in
`project/handoffs/ISSUE-0010-handoff.md`.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). `ISSUE-0007`, `ISSUE-0008`,
and `ISSUE-0009` are complete and merged; `ISSUE-0010` is implemented and
awaiting its fresh Codex review; `ISSUE-0011` has not started.

| Field | Current value |
|---|---|
| Stage | `ISSUE_REVIEW` — `ISSUE-0010` round-0 candidate submitted for Codex review |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007`, `ISSUE-0008`, `ISSUE-0009` of 5 complete; `ISSUE-0010` in review) |
| Active issue | `ISSUE-0010` (sign-in card mode toggle and app-only form), branch `ai/ISSUE-0010-app-only-ui`, base `f3b5414a4f2d3104d11bbb1ce6d5669a58123e79` |
| Issue repair round | None open (round 0 awaiting first review) |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. `ISSUE-0009`'s candidate `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` merged at `8253c1d7a754a3a967c2687c5ccc45e71794391a`. `ISSUE-0010`'s round-0 candidate not yet reviewed |
| Latest implementation handoff | `project/handoffs/ISSUE-0010-handoff.md` (M2, round 0) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone (3 of 5 issues complete, 1 in review) |
| Latest Codex issue review | `ISSUE-0009` round 1 (final): `project/reviews/issues/ISSUE-0009-7b0600f0831f-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual. `ISSUE-0010` round 0: not yet run |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`) |
| Last human decision | `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None. `ISSUE-0010`'s round-0 candidate is implemented, checked, and awaiting its first Codex review |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once `ISSUE-0010` is merged. Neither is a completion gate for any issue. `ISSUE-0010`'s runtime browser evidence was human-performed/Claude-guided, not Claude-automated — no browser-automation tool was available; disclosed in the issue's Stop conditions and the handoff |
| Next required actor | Claude — invoke the fresh Codex review for `ISSUE-0010` round 0 |
| Next permitted action | Invoke `./scripts/run-codex-review.sh issue ISSUE-0010 f3b5414a4f2d3104d11bbb1ce6d5669a58123e79 <round-0-candidate-sha>` |
| Actions not yet permitted | Any `ISSUE-0011`+ work; merging `ISSUE-0010` before a clean or human-accepted review outcome; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate, and `project/handoffs/ISSUE-0010-handoff.md`
for `ISSUE-0010`'s verification evidence (including the manual browser
walkthrough).

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 172 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
