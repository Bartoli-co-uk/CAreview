# Claude handoff: ISSUE-0013, round 0

**Claude issue task:** `ISSUE-0013 scoped-device-code-abandon implementation`
**Approved issue:** `project/issues/ISSUE-0013.md` at this commit
**Starting SHA:** `959fbcf` (`main` tip after the `ISSUE-0012` merge)
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
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
