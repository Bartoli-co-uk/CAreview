<!-- claudex-state
stage: ISSUE_REPAIR
active_issue: ISSUE-0013
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

## Summary

**M2 (dual-mode authentication) is COMPLETE and accepted.** All four
mandatory milestone reviews ran against frozen candidate
`9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` (product-identical to
`98be0bc562de8f7cf52e3019715bc4cff571ad91`): Claude general
`CHANGES_REQUIRED`, Codex general `BLOCKED`, Claude security
`PASS_WITH_NOTES`, Codex security `BLOCKED`. **No reviewer found a
product-code security or correctness defect** — every blocking finding was
either a governance-record accuracy issue or the review sandbox's
already-accepted execution-evidence limitation. The human approved M2
(`DECISION-023`), treating the record-hygiene findings (this file's prior
staleness, `ROADMAP.md`'s leftover pre-approval language) as ordinary
follow-up rather than grounds for another milestone candidate — the same
disposition `DECISION-012` gave M1. `ROADMAP.md`'s stale "PLANNED
(unapproved)" language is corrected in this same commit.

M1 remains complete and accepted (`DECISION-012`). Brief v2 and roadmap v4
remain approved (`DECISION-013`/`014`/`015`). No milestone is currently
active; no roadmap work is in progress under the M1/M2 roadmap.

**Out-of-band work, now entering a retroactive per-issue review:** the human
directly instructed a rebuild of the UI as a React/TypeScript dashboard
(`frontend/`, built with Vite), and explicitly chose to proceed without the
normal pre-implementation brief/roadmap cycle (`DECISION-024`), since
`AGENTS.md`'s own instruction-order rule puts the human's current explicit
instructions above that requirement. It replaces the vanilla-JS `web/` UI
and introduces a Node.js/npm build-step exception scoped to the frontend
only (backend remains stdlib-only). No M3 milestone has been opened for
this work; whether to formalize it into one remains a decision for the
human. See `project/decisions/DECISION-024-react-frontend-build-step.md`.

The human then asked for the mandatory per-issue Codex review to be run
retroactively before this work is committed to `main`, to close that gap
rather than leave it permanently skipped. This is recorded as
**`ISSUE-0012`** (`project/issues/ISSUE-0012.md`), `Starting SHA`
`8648f2ba11907ac32016c724d8ae49a08bdb6b2d` (the `main` tip before this
work), on branch `ai/react-dashboard-frontend`. This issue is **not**
governed by `ROADMAP.md` v4 (no roadmap version covers it) — it is a
retroactive application of the per-issue review gate only, not a claim
that the missing brief/roadmap cycle has been supplied. CI
(`.github/workflows/validate.yml`) still does not run the new `npm`
commands as of this record.

**Round 0 result: `BLOCKED`.** The fresh Codex issue review against
candidate `4cb61161be32b43506bb0e2c1b6921635561054d`
(`project/reviews/issues/ISSUE-0012-4cb61161be32-codex.json`) found one
real, high-severity defect — **F-001**: `pollOnce()` had no cancellation
check, so a device-code poll still in flight when the user moved to sample
mode, app-only mode, or signed out could later settle and overwrite that
state (flip `mode` back to `"live"`, load stale tenant data, or reschedule
itself). It also raised **F-002** (medium): no durable, commit-bound
record of the required checks' real output existed in the repository.
Round 1 added an `authAttempt` cancellation token (`frontend/src/state/
appState.tsx`) so a stale poll can no longer mutate client state, plus a
handoff document (`project/handoffs/ISSUE-0012-handoff.md`) with real
command output for every required check.

**Round 1 result: `BLOCKED` again**, same F-001 id, deeper form. The fresh
review against candidate `3748ff13318241e8cbe2bc38debc55e3d3042ecb`
(`project/reviews/issues/ISSUE-0012-3748ff133182-codex.json`) confirmed the
client-side race was fixed, but found that blocking the client mutation
wasn't sufficient: a stale **successful** poll means the *server* has
already installed a live token in `AuthManager` for an attempt the user
believes they abandoned, and the UI has no reachable "Sign out" control for
a session it never considers itself signed into (`Settings` only shows one
while `mode === "live"`) — that orphaned server-side session could only
ever be cleared by restarting the whole process. Round 2 fixed this by
making the stale-success branch of `pollOnce()` call `authLogout()` as a
compensating cleanup, with a regression test asserting that call happens
exactly once.

**Round 2 result: `CHANGES_REQUIRED`** — no longer `BLOCKED`, but still a
real, narrower finding, same F-001 id. The fresh review against candidate
`195bd8e746884c23b4774162667ee5905f2680e1`
(`project/reviews/issues/ISSUE-0012-195bd8e74688-codex.json`) found the
round-2 compensating `authLogout()` call is fire-and-forget (a failed
logout request silently leaves the orphaned token installed) and
unconditional/unscoped (server-side `AuthManager.logout()` clears *all*
current auth state, so a delayed logout racing a newer, legitimately
completed sign-in could sign that newer session out too).

**This was the second and final repair round `AGENTS.md` permits for an
issue.** Per that bounded-repair rule, this Claude task stopped there
rather than attempting a third fix, and presented the finding to the
human.

**Human decision (`DECISION-025`): merge now, open `ISSUE-0013` to fix it
properly.** The human reviewed the three options in
`project/issues/ISSUE-0012.md`'s "Human decision required" section and
chose a combination of options 1 and 2: accept the round-2 F-001 residual
as tracked risk (in the spirit of `DECISION-023`'s SEC-001/SEC-003), merge
`ai/react-dashboard-frontend` to `main` now to save the work, and
immediately open `ISSUE-0013` with its own fresh repair budget to build a
proper server-side scoped-abandon mechanism. `ISSUE-0012` is now
`COMPLETE (merged, with tracked residual)`.

**`ISSUE-0013` implemented (round 0), start-authorized by `DECISION-026`.**
`auth.py`'s `AuthManager` gained a `_token_handle`-tracked, exactly-scoped
`abandon(handle)` method — under the same lock as every other lifecycle
transition, it clears only the pending session or installed token
produced by the named handle, touching neither `_generation` nor app-only
state, so it can never clear a different, newer session regardless of
network timing. A new `POST /api/auth/abandon` endpoint exposes it.
`frontend/src/state/appState.tsx` now calls it at the moment a device-code
attempt is cancelled (sample mode, app-only mode, sign-out, or a fresh
attempt), and `pollOnce()`'s round-2 reactive `authLogout()` call is
removed entirely — superseded and unnecessary. New tests directly exercise
the round-2 race (a late `abandon()` for an old handle must not clear a
newer, currently-installed session) in both `tests/test_auth.py` and
`tests/test_server.py`.

**Round 0 result: `BLOCKED`.** The fresh Codex issue review
(`project/reviews/issues/ISSUE-0013-d3866851c7d6-codex.json`) confirmed
`AuthManager.abandon()` itself is sound, but found F-001 (high): the
frontend's `authAbandon` call was fire-and-forget with no retry, so a
single failed delivery could silently leave the abandoned token installed.

**Round 1 result: `BLOCKED` again**, same F-001 id, narrower form, plus a
new **F-002** (medium). The fresh review
(`project/reviews/issues/ISSUE-0013-8c273e194622-codex.json`) found that
round 1's fix (`authAbandon()` returns a success boolean; a new
`abandonWithRetry()` retries up to 3 times over ~6 seconds) still gives up
too quickly — persistent failures, or the tab navigating away, could still
leave cleanup unacknowledged. F-002 was this file (`CURRENT.md`) itself:
stale round-0 references (table still said round 0/89 frontend tests)
after the round-1 commit landed.

**Round 2: fixes both, but review result was `BLOCKED` again.**
`abandonWithRetry()` now retries every 3 seconds for up to ~16 minutes —
safely past a device-code attempt's own ~15-minute server-side expiry —
rather than giving up after 3 attempts, and this file was fully
resynchronized (F-002). The fresh Codex review
(`project/reviews/issues/ISSUE-0013-8858858a2090-codex.json`) confirmed
the server-side `abandon()` primitive is sound and this file is now
synchronized, but kept **F-001** (high) open in a narrower, procedural
form: `abandonWithRetry()` still "fails open" silently if every retry
fails (no observable unresolved-cleanup state exists), and — independent
of the code — the review correctly noted that a Claude task cannot itself
write the tab-closure/exhaustion residual into the record as "accepted";
per `AGENTS.md` only the human can accept a residual risk.

**This was the second and final repair round `AGENTS.md` permits for an
issue.** Per that bounded-repair rule, this Claude task stopped there
rather than attempting a third fix, and presented the finding to the
human, the same way `ISSUE-0012` did. `ISSUE-0013`'s status is `BLOCKED`
pending a human decision (see `project/issues/ISSUE-0013.md`'s "Human
decision required" section: accept the documented residual and merge;
open a new issue to build an observable cleanup-pending state; or drop
the abandon mechanism and rely on the device-code session's existing
~15-minute natural expiry instead).

| Field | Current value |
|---|---|
| Stage | `ISSUE_REPAIR` — `ISSUE-0012` merged (`DECISION-025`); `ISSUE-0013` `BLOCKED` after its repair budget was exhausted (2 of 2 rounds used) with an unresolved finding; awaiting a human decision. M1 and M2 remain complete and accepted with no milestone in progress |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` v4; APPROVED (DECISION-015, binds `9e5ba6d`). v3 (`DECISION-003`, `125d74f`) governed the completed M1; v4 has now fully delivered M2 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `COMPLETE`, accepted (`DECISION-023`). Neither milestone is currently in progress; no M3 exists yet |
| Active issue | `ISSUE-0013` — scoped device-code abandonment, `BLOCKED` (repair budget exhausted, human decision required), out-of-band per `DECISION-026`. `ISSUE-0012` is `COMPLETE` (merged) |
| Issue repair round | `ISSUE-0013`: exhausted at 2 of 2 — round 0 `BLOCKED` (F-001 fire-and-forget abandon), round 1 `BLOCKED` (F-001 narrower: retry window too short; F-002: stale `CURRENT.md`), round 2 `BLOCKED` (F-001 narrower still: fails open after retry exhaustion; residual lacks human acceptance). No further repair by this task; see "Human decision required" in `project/issues/ISSUE-0013.md`. `ISSUE-0012`: exhausted at 2 of 2, final outcome `CHANGES_REQUIRED`, accepted as tracked residual by `DECISION-025` |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `M2`'s frozen product commit is `98be0bc562de8f7cf52e3019715bc4cff571ad91`; its milestone-review candidate `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` was accepted by `DECISION-023` |
| Latest implementation handoff | `project/handoffs/ISSUE-0013-handoff.md` (rounds 0-2, real check output for 188 Python + 91 Vitest tests at round 2). `project/handoffs/ISSUE-0012-handoff.md` (rounds 1-2, complete, merged with tracked residual). `project/handoffs/ISSUE-0011-handoff.md` (M2, rounds 0-1, complete) |
| Latest milestone reviews | `M2` round 1 (accepted): Claude general `CHANGES_REQUIRED` (`project/reviews/milestones/M2-9c01749b221d-claude-general.md`); Codex general `BLOCKED` (`project/reviews/milestones/M2-9c01749b221d-codex-general.json`); Claude security `PASS_WITH_NOTES` (`project/reviews/milestones/M2-9c01749b221d-claude-security.md`); Codex security `BLOCKED`, sandbox residual only (`project/reviews/milestones/M2-9c01749b221d-codex-security.json`). Round 0 (superseded, candidate `b55bf97`) retained for the record. M1 round 2 remains accepted (`DECISION-012`) |
| Latest Codex issue review | `ISSUE-0013` round 2 (final, repair budget exhausted): `project/reviews/issues/ISSUE-0013-8858858a2090-codex.json` — `BLOCKED`, F-001 (high: fails open after retry exhaustion; residual lacks human acceptance). Round 1: `project/reviews/issues/ISSUE-0013-8c273e194622-codex.json` — `BLOCKED`, F-001 (retry window too short) + F-002 (stale `CURRENT.md`). Round 0: `project/reviews/issues/ISSUE-0013-d3866851c7d6-codex.json` — `BLOCKED`, F-001 (fire-and-forget abandon). `ISSUE-0012` round 2 (final, repair budget exhausted): `project/reviews/issues/ISSUE-0012-195bd8e74688-codex.json` — `CHANGES_REQUIRED`, F-001 (high: unawaited/unscoped compensating logout). `ISSUE-0011` round 1 (final, unrelated M2 work): `project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`); `ISSUE-0010` `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` (merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`); `ISSUE-0011` `e878cdcd979b7be87ff20cc986cb16d0d457dfe0` (merged `b50cbc2fb67e8066f22ab06a03f61425dbf1a9d1`, `DECISION-022`); `ISSUE-0012` `195bd8e746884c23b4774162667ee5905f2680e1` (merged `5189959392ec2331c799199f5d70457ff361a3ba`, `DECISION-025`, out-of-band, tracked residual → `ISSUE-0013`) |
| Last human decision | `DECISION-026` (ISSUE-0013 start authorization); `DECISION-025` (ISSUE-0012 advance and merge, tracked residual); `DECISION-024` (React/Vite frontend, direct-override, out-of-band); `DECISION-023` (M2 milestone acceptance); `DECISION-022` (ISSUE-0011 advance and merge); `DECISION-021` (ISSUE-0011 start authorization); `DECISION-020` (ISSUE-0010 advance and merge); `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None. M2 is accepted; no roadmap work is currently authorized or in progress |
| Tracked follow-up | Live-tenant sign-in verification (M1 and M2, both auth modes) — deferred pending the human's access restrictions (`DECISION-012`), remains a protected action, not a completion gate for either milestone. `DECISION-023`'s SEC-001 (silent-renewal-after-revocation replay) and SEC-003 (unauthenticated credential-validation oracle, undocumented in `RISK-002`) are tracked, non-blocking follow-ups — see `project/milestones/M2.md` and `DECISION-023`. CI not yet updated for `npm` commands; whether to open an M3 for this frontend work is undecided |
| Next required actor | **The human** — `ISSUE-0013`'s repair budget is exhausted with an unresolved finding. Choose one of the three options in `project/issues/ISSUE-0013.md`'s "Human decision required" section (accept the documented residual and merge; open a new issue to build an observable cleanup-pending state; or drop the abandon mechanism and rely on natural device-code expiry) |
| Next permitted action | **Wait** for the human's decision on `ISSUE-0013`. A new task should read this file, `AGENTS.md`, and `ROADMAP.md` fresh before proposing any other next step — do not attempt a third repair round for this issue without a fresh human authorization to do so |
| Actions not yet permitted | Any further repair of `ISSUE-0013` without a new human authorization; merging `ai/ISSUE-0013-scoped-device-code-abandon` to `main` without a human decision; any new issue or milestone work without an explicit human decision to start it; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M2.md` for the
full milestone record and the four review reports for complete evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed at the M2 milestone candidate; 174 after `DECISION-024`'s frontend change; **188 passed** at `ISSUE-0013` (new `AbandonTests` + server abandon-endpoint tests), unchanged rounds 0-2 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |
| Frontend tests | `cd frontend && npm test` | **91 passed**, exit 0, at `ISSUE-0013` round 2 (88 at round 0; +1 round-1 retry test; +1 round-2 retry-window test) |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
