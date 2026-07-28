<!-- claudex-state
stage: MILESTONE_REVIEW
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

**All five planned M2 issues (`ISSUE-0007..0011`) are merged, and the M2
milestone gate's four mandatory reviews have all now run against frozen
candidate `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d`** (product-identical
to `98be0bc562de8f7cf52e3019715bc4cff571ad91`). Results: Claude general
`CHANGES_REQUIRED`, Codex general `BLOCKED`, Claude security
`PASS_WITH_NOTES`, Codex security `BLOCKED`. **No reviewer found a
product-code security or correctness defect.** All blocking findings are
either governance-record accuracy issues (this file was stale before this
update; `ROADMAP.md` retains pre-`DECISION-015` "PLANNED (unapproved)"
language) or the review sandbox's already-accepted execution-evidence
limitation (no loopback sockets, no writable temp dir — the same class of
`BLOCKED` seen throughout M1 and every M2 issue).

An earlier candidate, `b55bf97ff4a4f850a21390443581e26e22f3179a`, was
reviewed first; a round-0 Codex general review found this record's
evidence was bound to the wrong SHA, which was fixed to produce `9c01749`.
Both Codex general (round 1) and Claude general (round 1) then
independently concluded that fix consumed the **one permitted
general-remediation cycle** — it is now exhausted. Per `AGENTS.md`,
exhausting a remediation limit blocks for an exact human decision; it does
not license Claude to create another candidate to chase a clean review.
**No further candidate has been created.** Full findings, options, and
report paths are in `project/milestones/M2.md` (`Status:
AWAITING_HUMAN_APPROVAL`).

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`).

| Field | Current value |
|---|---|
| Stage | `MILESTONE_REVIEW` — all four M2 round-1 reviews complete; awaiting the human's M2 acceptance decision |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) still governs the completed M1. **Note:** `ROADMAP.md` itself still contains stale pre-approval "PLANNED (unapproved)" language in the M2 issue-table heading and a milestone-table cell — flagged by the M2 milestone review (Claude general F-001), not yet corrected (see `project/milestones/M2.md`) |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, approved; all 5 issues complete; milestone review complete, `Status: AWAITING_HUMAN_APPROVAL` in `project/milestones/M2.md` |
| Active issue | None. No further M2 issues are planned |
| Issue repair round | None open |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `ISSUE-0007`'s candidate `b314d82` merged at `0c35851`. `ISSUE-0008`'s candidate `2051254` merged at `04e68ee`. `ISSUE-0009`'s candidate `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` merged at `8253c1d7a754a3a967c2687c5ccc45e71794391a`. `ISSUE-0010`'s candidate `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` merged at `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`. `ISSUE-0011`'s candidate `e878cdcd979b7be87ff20cc986cb16d0d457dfe0` merged at `b50cbc2fb67e8066f22ab06a03f61425dbf1a9d1`. `M2` milestone candidate frozen at `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` (product-identical to `98be0bc562de8f7cf52e3019715bc4cff571ad91`) |
| Latest implementation handoff | `project/handoffs/ISSUE-0011-handoff.md` (M2, rounds 0-1, complete) |
| Latest milestone reviews | `M2` round 1 (current, all four against `9c01749b221d…`): Claude general `CHANGES_REQUIRED` (`project/reviews/milestones/M2-9c01749b221d-claude-general.md`); Codex general `BLOCKED` (`project/reviews/milestones/M2-9c01749b221d-codex-general.json`); Claude security `PASS_WITH_NOTES` (`project/reviews/milestones/M2-9c01749b221d-claude-security.md`); Codex security `BLOCKED`, sandbox residual only (`project/reviews/milestones/M2-9c01749b221d-codex-security.json`). Round 0 (superseded, candidate `b55bf97`): Codex general and Claude general reports retained for the record but do not count toward the four required reviews. M1 round 2 remains accepted (`DECISION-012`) |
| Latest Codex issue review | `ISSUE-0011` round 1 (final): `project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`); `ISSUE-0010` `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` (merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`); `ISSUE-0011` `e878cdcd979b7be87ff20cc986cb16d0d457dfe0` (merged `b50cbc2fb67e8066f22ab06a03f61425dbf1a9d1`, `DECISION-022`) |
| Last human decision | `DECISION-022` (ISSUE-0011 advance and merge); `DECISION-021` (ISSUE-0011 start authorization); `DECISION-020` (ISSUE-0010 advance and merge); `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | **Process blocker:** the M2 milestone cannot be accepted without an explicit human decision — the general-remediation budget is exhausted per both round-1 general reviewers, and two required (non-product) findings remain: stale `ROADMAP.md` language and (as of this commit) a now-corrected `CURRENT.md`. No product-code blocker exists |
| Tracked follow-up | Live-tenant sign-in verification (M1 and M2, both auth modes) — deferred pending the human's access restrictions (`DECISION-012`) and remains a protected action, not a completion gate for the milestone. Claude security's SEC-001 (silent-renewal-after-revocation replay) and SEC-003 (unauthenticated credential-validation oracle, undocumented in `RISK-002`) are candidate follow-ups the human may choose to act on — see `project/milestones/M2.md` |
| Next required actor | The human — decide how to resolve the exhausted general-remediation cycle and the two open governance-record findings, and whether to accept M2 |
| Next permitted action | **Wait for the human's M2 decision.** See `project/milestones/M2.md`'s "Human decision" section for the three options presented (accept now treating the findings as ordinary follow-up; decline and direct a specific next step; or another explicit disposition) |
| Actions not yet permitted | Claude accepting or approving the M2 milestone itself (human-only decision); creating another M2 candidate/review round without an explicit human decision authorizing it; any M3+/new-roadmap work; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M2.md` for the
full milestone record and the four review reports for complete evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
