# Claude handoff: ISSUE-0012, round 1 (repair)

**Claude issue task:** `ISSUE-0012 react-dashboard-frontend implementation (retroactive)`
**Approved issue:** `project/issues/ISSUE-0012.md` at this commit
**Starting SHA:** `8648f2ba11907ac32016c724d8ae49a08bdb6b2d`
**Round 0 candidate SHA:** `4cb61161be32b43506bb0e2c1b6921635561054d`
**Round 1 candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-28`

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

## Changed files (this round, relative to round 0's candidate)

| Path | Change and reason |
|---|---|
| `frontend/src/state/appState.tsx` | F-001 fix: `authAttempt` cancellation token so a stale device-code poll can never mutate state after a competing transition. |
| `frontend/src/test/deviceCodeRace.test.tsx` | New regression tests for F-001. |
| `project/handoffs/ISSUE-0012-handoff.md` | This document (F-002). |
| `project/issues/ISSUE-0012.md` | Round 1 entry recorded in the rounds table. |
| `project/status/CURRENT.md` | Updated for round 1. |
