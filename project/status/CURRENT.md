<!-- claudex-state
stage: IMPLEMENTATION
active_issue: none
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
human, the same way `ISSUE-0012` did.

**Human decision (`DECISION-027`): accept the residual and merge.** The
human reviewed the three options in `project/issues/ISSUE-0013.md`'s
"Human decision required" section and chose option 1 — accept the round-2
F-001 residual exactly as documented (loopback-only delivery, ~16-minute
retry window, tab-closure/permanent-failure as the sole uncovered case)
and merge `ai/ISSUE-0013-scoped-device-code-abandon` to `main`. `ISSUE-0013`
is now `COMPLETE (merged, with accepted residual)`.

## Roadmap v5 — the frontend work is now recorded in the roadmap (DRAFT)

At the human's direct request, the out-of-band frontend work has been given
a proper roadmap binding. It had been documented thoroughly *everywhere
else* — `DECISION-024`–`027`, both issue records, two handoffs, six Codex
reports, `README.md`, `frontend/README.md` — but `ROADMAP.md` mentioned it
only as four parenthetical asides inside M1/M2 constraint text. The result
was that the single largest change to the product had no parent: both issue
files read `Milestone: None` / `Approved roadmap: N/A`.

**Roadmap v5 (now `APPROVED`, `DECISION-029`)** adds `M3` (React/TypeScript
dashboard UI, status `ISSUES DELIVERED — MILESTONE GATE NOT RUN`), an M3
issue sequence carrying `ISSUE-0012` and `ISSUE-0013` retroactively plus
`ISSUE-0014` (originally `PLANNED`, now `COMPLETE` and merged, `DECISION-031`)
for the CI gap, a first-class statement of `DECISION-024`'s exact bounds,
three risks (`RISK-009` npm build-time supply chain — **accepted as residual,
`DECISION-028`**; `RISK-010` onboarding regression; `RISK-011` recording `DECISION-027`'s
already-accepted abandon residual at roadmap level), and a correction to a
verification-strategy claim that had silently become false ("fresh clone →
`python3 server.py` with no installs" has not been true since
`DECISION-024`). `project/milestones/M3.md`, `docs/security-boundaries.md`,
and `CONTRIBUTING.md` were updated alongside it.

**Three things this deliberately does not do**, since each would be an
agent claiming a gate it cannot satisfy: it does not retroactively supply
the brief/roadmap cycle `ISSUE-0012`/`ISSUE-0013` skipped (v5 says so in
those words); it does not mark M3 `COMPLETE`, because its four blind
milestone reviews have never run and no per-issue review substitutes for
them; and it does not write its own approval — v5 is `DRAFT` with no
decision record, and its own required Codex plan review could not run
because `codex` was unavailable in the drafting environment, which blocks
rather than passes.

| Field | Current value |
|---|---|
| Stage | `IMPLEMENTATION` — roadmap v5 is `APPROVED` (`DECISION-029`, binding `8ea41ee`) and all three of its planned M3 issues are now merged. `ISSUE-0014` (wire the frontend build/tests into CI) went through two `BLOCKED` governance-record repair rounds (stale `CURRENT.md` rows, fixed) and a final round-2 `BLOCKED` with zero content findings (sole blocker the review sandbox's own execution-evidence limitations — no writable temp dir, no loopback sockets, no network — the same class `ISSUE-0011` round 1 hit). The human accepted that sandbox residual and approved the merge (`DECISION-031`). CI now runs the frontend build and tests on every push/PR. No active issue or milestone |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `9ccf835`); open questions resolved (DECISION-014) |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `9ccf835`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md` |
| Roadmap | `ROADMAP.md` is now at **v5, `APPROVED`** (`DECISION-029`, binds `8ea41ee`). **v4 remains separately approved** (DECISION-015, binds `9e5ba6d`) and still governs the completed M1/M2 content, which v5 does not change. v3 (`DECISION-003`, `125d74f`) governed the completed M1 |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3); `project/decisions/DECISION-015-roadmap-v4-approval.md` (v4); `project/decisions/DECISION-029-roadmap-v5-approval.md` (v5, approved directly from the round-2 review record, two round-2 findings accepted as residuals) |
| Active milestone | `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `COMPLETE`, accepted (`DECISION-023`). **`M3` (React/TypeScript dashboard UI) exists** (`project/milestones/M3.md`) under approved roadmap v5, with status `ISSUES DELIVERED — MILESTONE GATE NOT RUN`: `ISSUE-0012`, `ISSUE-0013`, and `ISSUE-0014` are all merged, and **none of the four blind milestone reviews has been run**. Whether to run that gate at all remains an open question. No milestone is actively in progress |
| Active issue | None. `ISSUE-0014` (wire the frontend build/tests into CI) is `COMPLETE` (merged, accepted sandbox execution-evidence residual, `DECISION-031`), branch `ai/ISSUE-0014-frontend-ci` merged to `main`. `ISSUE-0013` — scoped device-code abandonment — is `COMPLETE` (merged, accepted residual, `DECISION-027`), out-of-band per `DECISION-026`. `ISSUE-0012` is also `COMPLETE` (merged) |
| Issue repair round | None open. `ISSUE-0014`'s round-2 residual (zero content findings; blocked only by sandbox execution-evidence limits) is accepted per `DECISION-031`. `ISSUE-0013`'s round-2 residual (F-001: cleanup fails open after ~16-minute retry exhaustion) is accepted per `DECISION-027`, not eliminated. `ISSUE-0012`'s round-2 residual is accepted per `DECISION-025` |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. `M2`'s frozen product commit is `98be0bc562de8f7cf52e3019715bc4cff571ad91`; its milestone-review candidate `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` was accepted by `DECISION-023` |
| Latest implementation handoff | `project/handoffs/ISSUE-0013-handoff.md` (rounds 0-2, real check output for 188 Python + 91 Vitest tests at round 2). `project/handoffs/ISSUE-0012-handoff.md` (rounds 1-2, complete, merged with tracked residual). `project/handoffs/ISSUE-0011-handoff.md` (M2, rounds 0-1, complete) |
| Latest milestone reviews | `M2` round 1 (accepted): Claude general `CHANGES_REQUIRED` (`project/reviews/milestones/M2-9c01749b221d-claude-general.md`); Codex general `BLOCKED` (`project/reviews/milestones/M2-9c01749b221d-codex-general.json`); Claude security `PASS_WITH_NOTES` (`project/reviews/milestones/M2-9c01749b221d-claude-security.md`); Codex security `BLOCKED`, sandbox residual only (`project/reviews/milestones/M2-9c01749b221d-codex-security.json`). Round 0 (superseded, candidate `b55bf97`) retained for the record. M1 round 2 remains accepted (`DECISION-012`) |
| Latest Codex issue review | `ISSUE-0014` round 2 (final, repair budget exhausted, accepted `DECISION-031`): `project/reviews/issues/ISSUE-0014-f63a0dadae91-codex.json` — `BLOCKED`, **zero content findings**, sole blocker the review sandbox's execution-evidence limitations. Round 1: `project/reviews/issues/ISSUE-0014-d72dbd9a5481-codex.json` — `BLOCKED`, F-001 (medium: `CURRENT.md` still round-0-shaped). Round 0: `project/reviews/issues/ISSUE-0014-c4cb4d28f9b7-codex.json` — `BLOCKED`, F-001 (medium: stale `CURRENT.md` rows). `ISSUE-0013` round 2 (final, repair budget exhausted): `project/reviews/issues/ISSUE-0013-8858858a2090-codex.json` — `BLOCKED`, F-001 (high: fails open after retry exhaustion; residual lacks human acceptance). Round 1: `project/reviews/issues/ISSUE-0013-8c273e194622-codex.json` — `BLOCKED`, F-001 (retry window too short) + F-002 (stale `CURRENT.md`). Round 0: `project/reviews/issues/ISSUE-0013-d3866851c7d6-codex.json` — `BLOCKED`, F-001 (fire-and-forget abandon). `ISSUE-0012` round 2 (final, repair budget exhausted): `project/reviews/issues/ISSUE-0012-195bd8e74688-codex.json` — `CHANGES_REQUIRED`, F-001 (high: unawaited/unscoped compensating logout). `ISSUE-0011` round 1 (final, unrelated M2 work): `project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json` — `BLOCKED`, zero findings, sole blocker the accepted sandbox execution-evidence residual |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c`; `ISSUE-0007` `b314d82` (merged `0c35851`, `DECISION-016`); `ISSUE-0008` `2051254` (merged `04e68ee`, `DECISION-017`); `ISSUE-0009` `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (merged `8253c1d7a754a3a967c2687c5ccc45e71794391a`, `DECISION-019`); `ISSUE-0010` `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2` (merged `9d346f64422bf9bd5f89b43837a5f62f3e64d09b`, `DECISION-020`); `ISSUE-0011` `e878cdcd979b7be87ff20cc986cb16d0d457dfe0` (merged `b50cbc2fb67e8066f22ab06a03f61425dbf1a9d1`, `DECISION-022`); `ISSUE-0012` `195bd8e746884c23b4774162667ee5905f2680e1` (merged `5189959392ec2331c799199f5d70457ff361a3ba`, `DECISION-025`, out-of-band, tracked residual → `ISSUE-0013`); `ISSUE-0013` `8858858a2090aa72d8d0b14a6de64a17a447c120` (fast-forwarded to `main` at `80156d32feb6f4b85debc44897d04563bb35998a` — no merge commit; `DECISION-027`, out-of-band, accepted residual); `ISSUE-0014` `f63a0dadae917f35b328b60b1a562aa535d97d10` (merged, `DECISION-031`, accepted sandbox execution-evidence residual). All three of `ISSUE-0012`/`ISSUE-0013`/`ISSUE-0014` are now bound to `M3` under approved roadmap v5 |
| Last human decision | `DECISION-031` (ISSUE-0014 advance and merge, accepted sandbox residual); `DECISION-030` (ISSUE-0014 start authorization); `DECISION-029` (roadmap v5 approval, approved from round-2 record); `DECISION-028` (RISK-009 acceptance, roadmap v5); `DECISION-027` (ISSUE-0013 risk acceptance and merge); `DECISION-026` (ISSUE-0013 start authorization); `DECISION-025` (ISSUE-0012 advance and merge, tracked residual); `DECISION-024` (React/Vite frontend, direct-override, out-of-band); `DECISION-023` (M2 milestone acceptance); `DECISION-022` (ISSUE-0011 advance and merge); `DECISION-021` (ISSUE-0011 start authorization); `DECISION-020` (ISSUE-0010 advance and merge); `DECISION-019` (ISSUE-0009 advance and merge); `DECISION-018` (ISSUE-0009 start authorization); `DECISION-017` (ISSUE-0008 advance and merge); `DECISION-016` (ISSUE-0007 advance and merge); `DECISION-015` (roadmap v4 approval); `DECISION-014` (secret retention, RISK-002-as-widened, tenant validation); `DECISION-013` (brief v2 approval); also `DECISION-012`..`001` |
| Open blockers | None. `ISSUE-0014` merged with an accepted sandbox execution-evidence residual (`DECISION-031`) — its round-2 review found **zero content defects**; the real checks (188 backend tests, `py_compile`, `validate_repo.py`, frontend build, 91 frontend tests) all pass outside the review sandbox, recorded in `project/issues/ISSUE-0014.md`. Roadmap v5 is fully approved (`DECISION-029`). M1/M2 remain accepted and are unaffected |
| Tracked follow-up | Live-tenant sign-in verification (M1 and M2, both auth modes) — deferred pending the human's access restrictions (`DECISION-012`), remains a protected action, not a completion gate for either milestone. `DECISION-023`'s SEC-001 (silent-renewal-after-revocation replay) and SEC-003 (unauthenticated credential-validation oracle, undocumented in `RISK-002`) are tracked, non-blocking follow-ups — see `project/milestones/M2.md` and `DECISION-023`. **CI runs the frontend build and its 91 Vitest tests on every push/PR (`ISSUE-0014`, merged `DECISION-031`); `docs/security-boundaries.md` is resynchronized to that fact.** CI had actually been red since `ISSUE-0012` merged (four backend tests checking the served `web/index.html` fail on a fresh checkout that never builds the frontend) — `ISSUE-0014`'s initial step order didn't fix this (it ran the frontend steps *after* the already-failing Python step); fixed at `861f401` by building the frontend before the Python test step runs. `main`'s CI is now green (confirmed via `gh run watch`). **`RISK-009` (npm build-time supply chain) and `RISK-010` (onboarding regression) are both accepted as residual (`DECISION-028`, `DECISION-029`).** Whether to run M3's milestone gate at all is an open question for the human (`project/milestones/M3.md`) |
| Next required actor | None currently required — `ISSUE-0012`, `ISSUE-0013`, and `ISSUE-0014` are all merged. Any further work (M3's milestone gate or a new issue) needs its own explicit human start |
| Next permitted action | **Wait.** A new task should read this file, `AGENTS.md`, and `ROADMAP.md` fresh before proposing any next step |
| Actions not yet permitted | Starting any new issue/milestone work without an explicit human decision; running M3's milestone gate without a decision to do so; reopening `ISSUE-0013`'s accepted residual, `ISSUE-0014`'s accepted sandbox residual, or `DECISION-028`'s `RISK-009` acceptance, or `DECISION-029`'s `RISK-010`/negative-CI-rigor acceptances, without a fresh authorization; publication, deployment, live tenant auth/fetch (either mode), or any other protected action |

## Verification evidence at the reviewed commit

Re-runnable from a clean checkout; see `project/milestones/M2.md` for the
full milestone record and the four review reports for complete evidence.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 173 passed at the M2 milestone candidate; 174 after `DECISION-024`'s frontend change; **188 passed** at `ISSUE-0013` (new `AbandonTests` + server abandon-endpoint tests), unchanged rounds 0-2 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |
| Frontend tests | `cd frontend && npm test` | **91 passed**, exit 0, at `ISSUE-0013` round 2 (88 at round 0; +1 round-1 retry test; +1 round-2 retry-window test) |

### Roadmap v5 round-1 repair check evidence

At candidate `441b4da0d3ba0d9d13dcf0d710bdae5a1c0685ab` plus this round's
documentation-only fixes (`ISSUE-0014.md` added; stale-SHA and negative-CI
findings corrected): `python3 -m unittest discover -s tests` and
`cd frontend && npm test` are unchanged from `ISSUE-0013`'s figures above (no
product source touched). **`python3 scripts/validate_repo.py` could not be
cleanly re-confirmed from this working tree while `CURRENT.md` itself commits
the repository to stage `ROADMAP_REVIEW`**: the validator's own internal
smoke-test suite copies the live working tree to build its "wrong stage"
negative fixture, and that fixture inherits `ROADMAP_REVIEW` from this file,
which defeats the fixture's assumption that the plan-review stage is *not*
already active — a pre-existing self-test limitation in
`scripts/validate_repo.py`, not a finding about this change. `git stash`
confirms the validator passes cleanly against the last committed state before
this stage was set (67 required files checked) and the same required-files
pass was independently observed by the Codex plan reviewer with a different,
unrelated failure mode (no writable temp directory in its sandbox). Recorded
here rather than silently claimed as passing.

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
