# Claude handoff: ISSUE-0012, rounds 1-2 (repair)

**Claude issue task:** `ISSUE-0012 react-dashboard-frontend implementation (retroactive)`
**Approved issue:** `project/issues/ISSUE-0012.md` at this commit
**Starting SHA:** `8648f2ba11907ac32016c724d8ae49a08bdb6b2d`
**Round 0 candidate SHA:** `4cb61161be32b43506bb0e2c1b6921635561054d` (`BLOCKED`)
**Round 1 candidate SHA:** `3748ff13318241e8cbe2bc38debc55e3d3042ecb` (`BLOCKED`)
**Round 2 candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-28`
**Repair rounds used:** 2 of the maximum 2 permitted for an issue (`AGENTS.md`) — if round 2's fresh review does not return `PASS`/`PASS_WITH_NOTES`, this issue stops and the unresolved findings go to the human, per the bounded-repair rule.

## Why this round exists

Round 0's fresh Codex issue review
(`project/reviews/issues/ISSUE-0012-4cb61161be32-codex.json`) returned
`BLOCKED` with two findings:

- **F-001 (high, blocking):** a genuine device-code polling race.
  `pollOnce()` awaited `authPoll()` and then unconditionally scheduled
  another timer, or set `mode` to `"live"` and loaded tenant data, with no
  check that the attempt was still current. `viewSampleData()`,
  `submitAppOnlySignIn()`, and `signOut()` called `stopPolling()` (which
  only clears a not-yet-fired `setTimeout`) but had no way to invalidate an
  `authPoll()` request that had already been sent and was awaiting a
  response. A stale poll settling after any of those transitions could
  overwrite sample mode, app-only mode, or the signed-out state.
- **F-002 (medium, blocking):** no durable, commit-bound record of the
  required checks' real output existed in the repository — only prose
  claims in `project/issues/ISSUE-0012.md` and the conversation. Codex's
  own review sandbox additionally could not independently reproduce them
  (no `frontend/node_modules`, no loopback socket binding, no writable
  temp directory), which the finding treats as a sandbox limitation, not
  evidence the checks actually failed.

## What changed this round

### F-001 fix — `frontend/src/state/appState.tsx`

Added `authAttempt`, a `useRef` cancellation token for the device-code flow,
parallel to the existing `generation` counter used for data loads:

- `startDeviceCodeSignIn()` increments it and captures `myAttempt`; after
  the awaited `authStart()` call, it checks `myAttempt !== authAttempt.current`
  before touching any state (a second in-flight `authStart()` call, or any
  competing transition, invalidates the first).
- `pollOnce()` now takes `myAttempt` and checks it immediately after the
  awaited `authPoll()` call, before scheduling another timer or committing
  `"success"` — a stale response is silently dropped rather than mutating
  state.
- A new `cancelDeviceCodeAttempt()` helper (bump the token + `stopPolling()`)
  is called from `signOut()`, `submitAppOnlySignIn()`, `viewSampleData()`,
  and `exitSample()`, so every competing transition invalidates any
  in-flight device-code attempt, not just a not-yet-fired timer.

### F-001 regression tests — `frontend/src/test/deviceCodeRace.test.tsx` (new)

Two tests using deferred promises and fake timers:

1. A poll that resolves `"success"` after `viewSampleData()` has already run
   must not flip `mode` back to `"live"` or trigger a `/api/policies` fetch.
2. A poll that resolves `"pending"` after `signOut()` must not schedule
   another poll.

Both fail against the pre-fix code (confirmed locally before applying the
fix) and pass after it.

### F-002 — this handoff document

Records the exact commands and real output for every required check, run
against this round's candidate, so a durable commit-bound artifact exists
independent of chat.

## Required check evidence (round 1 candidate)

All commands below were run from the repository root immediately before
this commit, against a clean worktree matching this commit's tree exactly
(the only subsequent change is this handoff file and the issue/status
record updates, which are documentation/metadata, not product source).

### `python3 -m unittest discover -s tests`

```
..............................................................................................................................................................................
----------------------------------------------------------------------
Ran 174 tests in 34.453s

OK
exit=0
```

### `python3 -m py_compile $(git ls-files '*.py')`

```
exit=0
```
(no output on success)

### `python3 scripts/validate_repo.py`

```
NOTICE: PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu.
Repository validation passed (67 required files checked).
exit=0
```

### `cd frontend && npx tsc -b`

```
exit=0
```
(no output on success)

### `cd frontend && npx vite build`

```
vite v8.1.5 building client environment for production...
transforming...✓ 42 modules transformed.
rendering chunks...
computing gzip size...
../web/index.html    0.54 kB │ gzip:  0.34 kB
../web/index.css     6.56 kB │ gzip:  1.87 kB
../web/index.js    236.72 kB │ gzip: 71.43 kB

✓ built in 49ms
exit=0
```

### `cd frontend && npx vitest run`

```
 RUN  v4.1.10 /Users/jaybartoli/CAreview/frontend

 Test Files  7 passed (7)
      Tests  88 passed (88)
   Start at  22:16:38
   Duration  1.09s
exit=0
```

(86 tests from round 0 plus the 2 new `deviceCodeRace.test.tsx` regression
tests.)

### Manual browser walkthrough

Repeated after the fix, via `mcp__claude-in-chrome__*` tools against
`http://127.0.0.1:8765/` serving this round's `npm run build` output:
Overview, Recommendations, Policies (hostile display name renders as
literal text, no injected `<img>`), Policy Explorer (search/filter +
detail drill-down), and Insights (donut charts) all rendered correctly
against `web/sample-data.json` with no console errors. Not independently
re-verifiable by a future reader from this document alone (no screen
recording was saved) — the automated checks above and the regression
tests are the durable, re-runnable evidence for this round.

## Changed files (round 1, relative to round 0's candidate)

| Path | Change and reason |
|---|---|
| `frontend/src/state/appState.tsx` | F-001 fix: `authAttempt` cancellation token so a stale device-code poll can never mutate state after a competing transition. |
| `frontend/src/test/deviceCodeRace.test.tsx` | New regression tests for F-001. |
| `project/handoffs/ISSUE-0012-handoff.md` | This document (F-002). |
| `project/issues/ISSUE-0012.md` | Round 1 entry recorded in the rounds table. |
| `project/status/CURRENT.md` | Updated for round 1. |

---

## Round 2: fresh review of round 1 also returned `BLOCKED`

Round 1's fresh Codex issue review against candidate
`3748ff13318241e8cbe2bc38debc55e3d3042ecb`
(`project/reviews/issues/ISSUE-0012-3748ff133182-codex.json`) confirmed
F-001's client-side race was fixed, but raised a **new, deeper form of the
same finding (still labeled F-001, high, blocking)**: blocking the client
state mutation isn't sufficient on its own. A stale `"success"` poll
response means the *server* has already exchanged the device code and
installed a live token in `AuthManager` — the client dropping that response
leaves the dashboard correctly in sample/signed-out mode, but the backend
now silently retains an authenticated session for an attempt the user
believes they abandoned. Since `Settings`' "Sign out" control only renders
while `mode === "live"`, the user has no way to ever reach it for that
orphaned session — only restarting the whole `server.py` process would
clear it.

### F-001 (round 2) fix — `frontend/src/state/appState.tsx`

In `pollOnce()`, the stale-response branch now distinguishes `"success"`
from every other outcome: a stale `"success"` compensates by calling
`authLogout()` (clearing the orphaned server-side session immediately),
while a stale `"pending"`/`"expired"`/`"error"` needs no compensation
since no token was ever installed for those. Comment added in place
explaining why this asymmetry is correct.

### F-001 (round 2) regression test — `frontend/src/test/deviceCodeRace.test.tsx`

Extended the existing "poll resolves 'success' after `viewSampleData()`"
test to also assert exactly one `/api/auth/logout` call happened as a
result of the stale success — proving the compensating cleanup fires and
fires only once.

## Required check evidence (round 2 candidate)

All commands below were run from the repository root immediately before
this commit, against a clean worktree matching this commit's tree exactly
(the only subsequent changes are this handoff section and the issue/status
record updates, which are documentation/metadata, not product source).

### `python3 -m unittest discover -s tests`

```
..............................................................................................................................................................................
----------------------------------------------------------------------
Ran 174 tests in 34.459s

OK
exit=0
```

### `python3 -m py_compile $(git ls-files '*.py')`

```
exit=0
```
(no output on success)

### `python3 scripts/validate_repo.py`

```
NOTICE: PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu.
Repository validation passed (67 required files checked).
exit=0
```

### `cd frontend && npx tsc -b`

```
exit=0
```
(no output on success)

### `cd frontend && npx vite build`

```
vite v8.1.5 building client environment for production...
transforming...✓ 42 modules transformed.
rendering chunks...
computing gzip size...
../web/index.html    0.54 kB │ gzip:  0.34 kB
../web/index.css     6.56 kB │ gzip:  1.87 kB
../web/index.js    236.75 kB │ gzip: 71.44 kB

✓ built in 61ms
exit=0
```

### `cd frontend && npx vitest run`

```
 RUN  v4.1.10 /Users/jaybartoli/CAreview/frontend

 Test Files  7 passed (7)
      Tests  88 passed (88)
   Start at  22:22:10
   Duration  1.22s
exit=0
```

(Same 88 tests as round 1 — `deviceCodeRace.test.tsx` extended in place
rather than adding a new file.)

## Changed files (round 2, relative to round 1's candidate)

| Path | Change and reason |
|---|---|
| `frontend/src/state/appState.tsx` | F-001 (round 2) fix: stale successful device-code polls now trigger a compensating `authLogout()` call. |
| `frontend/src/test/deviceCodeRace.test.tsx` | Extended to assert the compensating logout call. |
| `project/handoffs/ISSUE-0012-handoff.md` | This round-2 section. |
| `project/issues/ISSUE-0012.md` | Round 2 entry recorded in the rounds table. |
| `project/status/CURRENT.md` | Updated for round 2. |
| `project/reviews/issues/ISSUE-0012-3748ff133182-codex.json` | Round 1's `BLOCKED` review report, committed for the record. |

This is the second of the two repair rounds `AGENTS.md` permits for an
issue. If this round's fresh Codex review does not return `PASS` or
`PASS_WITH_NOTES`, this issue stops here and the unresolved findings are
presented to the human rather than attempting a third repair.

---

## Round 2 review result: `CHANGES_REQUIRED` — repair budget exhausted, stopping here

Round 2's fresh Codex issue review against candidate
`195bd8e746884c23b4774162667ee5905f2680e1`
(`project/reviews/issues/ISSUE-0012-195bd8e74688-codex.json`) returned
`CHANGES_REQUIRED` (not `BLOCKED` — a real, narrower finding than the prior
two rounds, but still blocking): the round-2 compensating `authLogout()`
call is **fire-and-forget** (a failed logout silently leaves the orphaned
token installed) and **unconditional/unscoped** (server-side
`AuthManager.logout()` clears all current auth state, so a delayed logout
racing a newer, legitimately-completed sign-in could sign that newer
session out too).

Per `AGENTS.md`'s bounded-repair rule, this was the second and final
repair round permitted for this issue. This Claude task stops here rather
than attempting a third fix, and the finding is presented to the human in
`project/issues/ISSUE-0012.md`'s "Human decision required" section. Closing
this properly likely needs a server-side change (`auth.py`/`server.py`) to
scope cleanup to the specific abandoned attempt rather than "whatever is
currently live" — out of scope for a same-day frontend repair round.
