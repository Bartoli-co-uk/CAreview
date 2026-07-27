<!-- claudex-state
stage: ISSUE_REPAIR
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

**`ISSUE-0010` (sign-in card mode toggle and app-only form in `web/`) is in
repair round 2 of at most 2 permitted (final).** No deferral was recorded
against it, so it started directly in a new top-level task, base
`f3b5414a4f2d3104d11bbb1ce6d5669a58123e79`. Round 0's candidate
(`1d557b3840f716ad0d25a0f6d4be407cdeeb221b`) was reviewed `BLOCKED` with
two product findings: F-001 (the secret field wasn't cleared when the
app-only `fetch()` itself rejected, only when it resolved) and F-002 (the
manual browser walkthrough only exercised the failure-submit path, not the
required successful-submit checkpoint). Both were fixed in round 1
(`451dbe236769760c2384ab3f198c1f5b11f7c1ae`): the secret field now clears
inside a `try/catch/finally` around the request, and the human re-ran the
walkthrough's submit step against a local-only mock-success server
(`AUTH`/`GRAPH` replaced with in-process mocks, no live network or
credentials) confirming the field also clears on a successful submit with
nothing leaked to console/storage. Round 1 was itself reviewed `BLOCKED`
with one finding: F-001 (this file, `CURRENT.md`, still described the
obsolete round-0 state instead of round 1's). Fixed in round 2 — this is a
metadata-only fix; no product/test source changed since round 1. Full
evidence, including all five walkthrough checkpoints, is in
`project/handoffs/ISSUE-0010-handoff.md`.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). `ISSUE-0007`, `ISSUE-0008`,
and `ISSUE-0009` are complete and merged; `ISSUE-0010` is in its final
permitted repair round; `ISSUE-0011` has not started.

| Field | Current value |
|---|---|
| Stage | `ISSUE_REPAIR` — `ISSUE-0010` round-1 candidate `BLOCKED` (1 metadata finding); repair round 2 (final, metadata-only) candidate submitted for re-review |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved, in progress (`ISSUE-0007`, `ISSUE-0008`, `ISSUE-0009` of 5 complete; `ISSUE-0010` in repair) |
| Active issue | `ISSUE-0010` (sign-in card mode toggle and app-only form), branch `ai/ISSUE-0010-app-only-ui`, base `f3b5414a4f2d3104d11bbb1ce6d5669a58123e79` |
| Issue repair round | Round 2 of at most 2 permitted, final (round 0 candidate `1d557b3840f716ad0d25a0f6d4be407cdeeb221b` `BLOCKED` 2 findings; round 1 candidate `451dbe236769760c2384ab3f198c1f5b11f7c1ae` `BLOCKED` 1 metadata finding) |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. `ISSUE-0009`'s candidate `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` merged at `8253c1d7a754a3a967c2687c5ccc45e71794391a`. `ISSUE-0010`'s round-2 candidate (this commit) submitted for re-review; not yet merged |
| Latest implementation handoff | `project/handoffs/ISSUE-0010-handoff.md` (M2, rounds 0-2) |
| Latest milestone reviews | M1 round 2, all four bound to the `6311a11a` product tree: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone gate yet — M2 is mid-milestone (3 of 5 issues complete, 1 in repair) |
| Latest Codex issue review | `ISSUE-0010` round 1: `project/reviews/issues/ISSUE-0010-451dbe236769-codex.json` — `BLOCKED` (F-001 `CURRENT.md` described the obsolete round-0 state), fixed in round 2. Round 0: `project/reviews/issues/ISSUE-0010-1d557b3840f7-codex.json` — `BLOCKED` (F-001 secret not cleared on rejected fetch; F-002 missing successful-submit browser evidence), both fixed in round 1. Round 2 re-review: pending. Prior issue: `ISSUE-0009` round 1 (final) — `BLOCKED`, zero findings, sandbox execution-evidence residual only |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`) |
| Last human decision | `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None process-related. Product: this final repair round (metadata-only) is committed and checked; awaiting its Codex re-review. This is the last permitted repair round — a further `BLOCKED` with actionable findings must stop for the human rather than attempt a third repair |
| Tracked follow-up | Live-tenant sign-in verification (M1) — deferred pending the human's access restrictions (`DECISION-012`); a live app-only run (M2) will be a separate protected action once `ISSUE-0010` is merged. Neither is a completion gate for any issue. `ISSUE-0010`'s runtime browser evidence was human-performed/Claude-guided (including via a local-only mock-success helper for the successful-submit checkpoint), not Claude-automated — no browser-automation tool was available; disclosed in the issue's Stop conditions and the handoff |
| Next required actor | Claude — invoke the fresh Codex re-review for `ISSUE-0010` round 2 (this commit) |
| Next permitted action | Invoke `./scripts/run-codex-review.sh issue ISSUE-0010 f3b5414a4f2d3104d11bbb1ce6d5669a58123e79 <this-commit-sha>` |
| Actions not yet permitted | Any `ISSUE-0011`+ work; merging `ISSUE-0010` before a clean or human-accepted review outcome; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate, and `project/handoffs/ISSUE-0010-handoff.md`
for `ISSUE-0010`'s verification evidence (including the manual browser
walkthrough).

| Check | Command | Result at round-2 candidate (this commit) |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
