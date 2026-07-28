# Claude handoff: ISSUE-0013, rounds 0-1

**Claude issue task:** `ISSUE-0013 scoped-device-code-abandon implementation`
**Approved issue:** `project/issues/ISSUE-0013.md` at this commit
**Starting SHA:** `959fbcfc1f127289eb1a1798374fae1c96d7cbc2` (`main` tip after the `ISSUE-0012` merge)
**Round 0 candidate SHA:** `d3866851c7d65c5e237e6e9f46ae94adc153a166` (`BLOCKED`)
**Round 1 candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-28`

## Outcome

Implemented in full, replacing `ISSUE-0012` round 2's unsafe compensating
`authLogout()` call with a properly scoped server-side mechanism.

### `auth.py`

- `AuthManager.__init__` gained `self._token_handle: str | None`, tracking
  which device-code handle produced the *currently installed* access
  token (not just the pending session, which `poll()` already clears once
  it resolves).
- `start()`, `start_app_only()`, and `logout()` each now also clear
  `_token_handle` at the same points they already clear `_access_token` —
  so it never lingers across a mode switch or a brand new sign-in.
- `poll()`'s success branch sets `self._token_handle = session.handle`
  alongside installing the token.
- New `AuthManager.abandon(handle: str) -> None`: under the existing lock,
  clears the pending session if its handle matches, and/or clears the
  installed token if `_token_handle` matches — an unknown or
  already-superseded handle is a no-op. Deliberately does not touch
  `_generation` or any app-only state, so it can never affect anything
  other than the exact attempt named.

### `server.py`

- New `POST /api/auth/abandon` route, `_auth_abandon()` handler: validates
  `handle` is a non-empty string (same pattern as `_auth_poll`), calls
  `AUTH.abandon(handle)`, returns `{"state": "ok"}`. Same Host/Origin/body-
  size handling as every other `/api/auth/*` POST.

### `frontend/src/api/client.ts`

- New `authAbandon(handle: string): Promise<void>`.

### `frontend/src/state/appState.tsx`

- New `pendingHandle` ref tracks the current device-code attempt's handle
  (set in `startDeviceCodeSignIn` once `authStart()` returns one; cleared
  on any terminal `pollOnce()` outcome).
- `cancelDeviceCodeAttempt()` (already called from `signOut`,
  `submitAppOnlySignIn`, `viewSampleData`, `exitSample`) now also calls
  `authAbandon(pendingHandle.current)` for that specific handle, in
  addition to bumping `authAttempt` and stopping the poll timer.
- `pollOnce()`'s stale-response branch no longer reacts to `"success"`
  with a compensating `authLogout()` call at all — removed entirely. It
  was the source of `ISSUE-0012` round 2's finding; the new scoped
  `abandon()` call at cancellation time makes it unnecessary, since the
  server itself will never have kept a token for a properly-abandoned
  handle.

### Tests

- `tests/test_auth.py`: new `AbandonTests` (6 tests) — pending-session
  abandonment, already-succeeded-token abandonment, unknown-handle no-op,
  **the exact round-2 race** (a late `abandon()` for an old handle must
  not clear a newer, currently-installed session), generation/app-only
  isolation, and abandoning a pending device-code session doesn't touch a
  different app-only token.
- `tests/test_server.py`: 4 new HTTP-layer tests on `ServerIntegrationTests`
  (inherited by `AppOnlyEndpointTests` too, so 8 total) — missing-handle
  rejection, Origin requirement, the same late-abandon-doesn't-clobber-a-
  newer-session race at the HTTP layer, and abandoning a pending session
  prevents its later success from installing a token.
- `frontend/src/test/deviceCodeRace.test.tsx`: rewritten. First test now
  asserts `viewSampleData()` calls `authAbandon` with the exact handle,
  and that `pollOnce()` no longer calls `authLogout` reactively. Second
  test (sign-out) unchanged in intent, updated for the new mock surface.
  New third test: no `authAbandon` call when there's no in-flight attempt
  to cancel.

## Required check evidence (this candidate)

All commands run from the repository root against a clean worktree
matching this commit's tree.

### `python3 -m unittest discover -s tests`

```
............................................................................................................................................................................................
----------------------------------------------------------------------
Ran 188 tests in 38.597s

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
../web/index.js    236.89 kB │ gzip: 71.50 kB

✓ built in 53ms
exit=0
```

### `cd frontend && npx vitest run`

```
 RUN  v4.1.10 /Users/jaybartoli/CAreview/frontend

 Test Files  7 passed (7)
      Tests  89 passed (89)
   Start at  23:06:50
   Duration  1.34s
exit=0
```

## Changed files

| Path | Change and reason |
|---|---|
| `auth.py` | `_token_handle` tracking; new `AuthManager.abandon()`. |
| `server.py` | New `POST /api/auth/abandon` route + handler. |
| `frontend/src/api/client.ts` | New `authAbandon()`. |
| `frontend/src/state/appState.tsx` | `pendingHandle` tracking; `cancelDeviceCodeAttempt()` now calls `authAbandon`; removed the round-2 reactive `authLogout()` call from `pollOnce()`. |
| `tests/test_auth.py` | New `AbandonTests` (6 tests). |
| `tests/test_server.py` | New abandon-endpoint tests (4, inherited ×2 = 8). |
| `frontend/src/test/deviceCodeRace.test.tsx` | Rewritten for the new design. |
| `README.md` | HTTP API table: new `/api/auth/abandon` row; test-count corrections. |
| `docs/security-boundaries.md` | New bullet describing the scoped-abandon mechanism and why it can't widen its own effect. |
| `project/issues/ISSUE-0013.md` | Round 0 entry, this handoff reference. |
| `project/status/CURRENT.md` | Updated for round 0. |

---

## Round 1: fixing round 0's `BLOCKED` finding

Round 0's fresh Codex issue review against candidate
`d3866851c7d65c5e237e6e9f46ae94adc153a166`
(`project/reviews/issues/ISSUE-0013-d3866851c7d6-codex.json`) confirmed
`AuthManager.abandon()` itself is correctly lock-protected and scoped, but
found **F-001** (high, blocking): `cancelDeviceCodeAttempt()` called
`void authAbandon(pendingHandle.current)` — fire-and-forget, no retry, no
error handling — and immediately discarded the handle. A single failed
delivery (network blip, transient 5xx) would silently leave the abandoned
attempt's token installed server-side if its poll happened to succeed
around the same time, reproducing the exact class of problem this issue
exists to fix.

### F-001 fix

- `frontend/src/api/client.ts`: `authAbandon()` now returns a `boolean`
  (whether the request was delivered and acknowledged) instead of `void`,
  so callers can detect failure.
- `frontend/src/state/appState.tsx`: new `abandonWithRetry(handle)` —
  attempts `authAbandon(handle)`, and on failure retries up to 3 more
  times with a `[500, 1500, 4000]`ms backoff before giving up.
  `cancelDeviceCodeAttempt()` now calls this instead of a single bare
  `authAbandon()` call. (There is no way to *guarantee* delivery from a
  browser tab that might close mid-retry — this narrows the failure
  window from "any single request" to "several requests over several
  seconds all failing outright," which is the honest limit of what a
  fire-and-forget browser-side cleanup call can offer; a stronger
  guarantee would require the browser to block navigation/exit pending
  confirmation, which is out of scope for this issue.)
- `frontend/src/test/deviceCodeRace.test.tsx`: new regression test — the
  first `authAbandon` delivery attempt fails (mocked `502`), and advancing
  fake timers past the first backoff delay proves a second, successful
  attempt fires.

## Required check evidence (round 1 candidate)

### `python3 -m unittest discover -s tests`

```
............................................................................................................................................................................................
----------------------------------------------------------------------
Ran 188 tests in 38.508s

OK
exit=0
```

### `python3 -m py_compile $(git ls-files '*.py')`

```
exit=0
```

### `python3 scripts/validate_repo.py`

```
NOTICE: PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu.
Repository validation passed (67 required files checked).
exit=0
```

### `cd frontend && npx tsc -b && npx vite build`

```
vite v8.1.5 building client environment for production...
transforming...✓ 42 modules transformed.
rendering chunks...
computing gzip size...
../web/index.html    0.54 kB │ gzip:  0.34 kB
../web/index.css     6.56 kB │ gzip:  1.87 kB
../web/index.js    237.08 kB │ gzip: 71.56 kB

✓ built in 62ms
exit=0
```

### `cd frontend && npx vitest run`

```
 RUN  v4.1.10 /Users/jaybartoli/CAreview/frontend

 Test Files  7 passed (7)
      Tests  90 passed (90)
   Start at  23:15:39
   Duration  1.14s
exit=0
```

## Changed files (round 1, relative to round 0's candidate)

| Path | Change and reason |
|---|---|
| `frontend/src/api/client.ts` | `authAbandon()` returns success boolean. |
| `frontend/src/state/appState.tsx` | New `abandonWithRetry()` with bounded backoff; `cancelDeviceCodeAttempt()` uses it. |
| `frontend/src/test/deviceCodeRace.test.tsx` | New retry regression test. |
| `project/handoffs/ISSUE-0013-handoff.md` | This round-1 section. |
| `project/issues/ISSUE-0013.md` | Round 1 entry recorded. |
| `project/status/CURRENT.md` | Updated for round 1. |
| `project/reviews/issues/ISSUE-0013-d3866851c7d6-codex.json` | Round 0's `BLOCKED` review report, committed for the record. |

---

## Round 2: fixing round 1's `BLOCKED` finding (final permitted repair round)

Round 1's fresh Codex issue review against candidate
`8c273e19462203c9ba8c2f29a693b47c984eb52b`
(`project/reviews/issues/ISSUE-0013-8c273e194622-codex.json`) returned
`BLOCKED` with two findings:

- **F-001 (high, blocking, narrower form of the same id):** `abandonWithRetry()`'s
  3-attempt/~6-second retry window was still too short — persistent
  failures (or the tab navigating away before the window elapsed) could
  still leave cleanup unacknowledged, reproducing the class of problem
  this issue exists to fix, just with a smaller window than round 0.
- **F-002 (medium):** `project/status/CURRENT.md` was stale — still
  described round 0 as current, listed the round-0 handoff/test counts,
  and instructed launching a round-0 review, despite round 1 already being
  committed with a `BLOCKED` report.

### F-001 (round 2) fix

`abandonWithRetry()` now retries every 3 seconds for up to ~16 minutes
(`ABANDON_RETRY_INTERVAL_MS` / `ABANDON_RETRY_MAX_DURATION_MS` in
`frontend/src/state/appState.tsx`) — safely past a device-code attempt's
own ~15-minute server-side expiry, rather than giving up after 3 attempts.
Rationale (also recorded in `docs/security-boundaries.md` and
`project/issues/ISSUE-0013.md`'s security-impact section): this call is
loopback-only (browser → this machine's own CAreview process, not the
public internet), so a failed delivery means either a transient local
hiccup — now covered by the much longer retry window — or the CAreview
process itself being unreachable, in which case `AuthManager`'s in-memory
state (including any installed token) is gone with it regardless of
whether cleanup "succeeds." The one case that cannot be covered — the
browser tab closing before delivery succeeds — is documented as an
accepted residual, not claimed to be eliminated.

New regression test: every `abandon` delivery attempt fails, and advancing
fake timers by 60 seconds proves retries continue well past the old
3-attempt limit (>15 attempts), rather than giving up early.

### F-002 fix

`project/status/CURRENT.md` fully resynchronized to round 2: `claudex-state`
stage, active-issue/repair-round fields, latest handoff/review references,
test counts (188 Python / 91 Vitest), and the next permitted action all
updated to describe this exact candidate.

## Required check evidence (round 2 candidate)

### `python3 -m unittest discover -s tests`

```
............................................................................................................................................................................................
----------------------------------------------------------------------
Ran 188 tests in 38.510s

OK
exit=0
```

### `python3 -m py_compile $(git ls-files '*.py')`

```
exit=0
```

### `python3 scripts/validate_repo.py`

```
NOTICE: PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu.
Repository validation passed (67 required files checked).
exit=0
```

### `cd frontend && npx tsc -b && npx vite build`

```
vite v8.1.5 building client environment for production...
transforming...✓ 42 modules transformed.
rendering chunks...
computing gzip size...
../web/index.html    0.54 kB │ gzip:  0.34 kB
../web/index.css     6.56 kB │ gzip:  1.87 kB
../web/index.js    237.09 kB │ gzip: 71.55 kB

✓ built in 52ms
exit=0
```

### `cd frontend && npx vitest run`

```
 RUN  v4.1.10 /Users/jaybartoli/CAreview/frontend

 Test Files  7 passed (7)
      Tests  91 passed (91)
   Start at  23:24:58
   Duration  1.15s
exit=0
```

## Changed files (round 2, relative to round 1's candidate)

| Path | Change and reason |
|---|---|
| `frontend/src/state/appState.tsx` | Extended `abandonWithRetry()` to a ~16-minute retry window with loopback-only rationale documented in comments. |
| `frontend/src/test/deviceCodeRace.test.tsx` | New test proving retries continue well past the old 3-attempt limit. |
| `docs/security-boundaries.md` | Documented the accepted delivery-reliability residual. |
| `project/issues/ISSUE-0013.md` | Security-impact section updated; round 2 entry recorded. |
| `project/status/CURRENT.md` | Fully resynchronized (F-002 fix). |
| `project/reviews/issues/ISSUE-0013-8c273e194622-codex.json` | Round 1's `BLOCKED` review report, committed for the record. |

This is the second and final repair round `AGENTS.md` permits for an
issue. If this round's fresh Codex review does not return `PASS` or
`PASS_WITH_NOTES`, this issue stops here and the unresolved findings are
presented to the human rather than attempting a third repair.
