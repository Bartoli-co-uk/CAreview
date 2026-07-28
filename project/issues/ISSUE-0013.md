# ISSUE-0013: Scoped, server-side device-code session abandonment

**Status:** `REVIEWING`
**Milestone:** `None` — out-of-band, remediating a residual from `ISSUE-0012`
(itself out-of-band per `DECISION-024`). Not governed by `ROADMAP.md` v4.
**Approved roadmap:** `N/A` — see `ISSUE-0012.md`'s equivalent note.
**Dependencies:** `ISSUE-0012` (`COMPLETE`, merged with this tracked residual)
**Branch:** `ai/ISSUE-0013-scoped-device-code-abandon`
**Starting SHA:** `959fbcf` (`main` tip after the `ISSUE-0012` merge)
**Candidate SHA:** this commit (branch HEAD); the launcher records the full HEAD SHA.

## Objective

Replace `ISSUE-0012` round 2's unawaited, unconditional `authLogout()`
compensating call with a properly scoped server-side mechanism: abandoning
a device-code sign-in attempt must reliably clear *only that attempt's*
server-side state (its pending session, or the token it produced if the
poll already succeeded), and must never be able to clear a different,
newer, legitimately-current session — regardless of network timing.

## Background

`AuthManager` (`auth.py`) already has a private `_generation` counter and
session-identity checks that make `start()`/`start_app_only()`/`logout()`
correctly supersede an old device-code attempt when the user begins a new
sign-in through the normal flow — this already-existing mechanism is why
`ISSUE-0012` round 0/1's client-side race (mode flipping back to "live")
was fixable purely client-side. The remaining gap is narrower: when the
user abandons a device-code attempt *without* starting a new sign-in
(clicking "View a sample analysis", or exiting sample mode back to
signed-out), nothing tells the server that attempt was abandoned, so if
its poll subsequently succeeds, the server correctly (from its own
perspective) installs a live token — there was no signal telling it not
to. `ISSUE-0012` round 2 tried to react to this from the client *after*
detecting a stale success, using the existing unconditional
`POST /api/auth/logout`, which the round-2 Codex review correctly found
unsafe: unawaited (a failed request leaves the token installed) and
unscoped (it can clear a different, newer session if one is racing it).

## In scope

- `auth.py` — `AuthManager`: track which handle produced the *currently
  installed* access token (not just the pending session, which is already
  cleared once a poll resolves). Add a new method, e.g.
  `abandon(handle: str) -> None`, that atomically (under the existing
  lock) clears only state associated with that exact handle:
  - if a pending session with that handle still exists, clear it (so a
    later `poll()` for it returns `superseded` instead of installing a
    token);
  - if the currently installed access token was produced by that handle,
    clear the token (and its expiry) — but leave everything alone if the
    handle doesn't match what's currently installed/pending, since that
    means a newer session has already superseded it.
  - Must not touch `_generation`, app-only state, or anything unrelated
    to device-code sessions, and must be a safe no-op for an
    unknown/already-cleared handle (idempotent, no exception).
- `server.py` — new `POST /api/auth/abandon` endpoint, body
  `{"handle": "<opaque handle>"}`, calling `AUTH.abandon(handle)` and
  returning `{"state": "ok"}`. Same Origin/Host checks and body-size limit
  as the other `/api/auth/*` POST endpoints; basic type validation on
  `handle` (non-empty string) before calling into `AuthManager`.
- `frontend/src/api/client.ts` — `authAbandon(handle: string): Promise<void>`.
- `frontend/src/state/appState.tsx` — track the current device-code
  attempt's handle (e.g. a `pendingHandle` ref, set once `authStart()`
  returns a handle, cleared on any terminal outcome — success, expired,
  error, or explicit abandonment). `cancelDeviceCodeAttempt()` now calls
  `authAbandon(handle)` for that specific handle (if one is pending) in
  addition to bumping the existing `authAttempt` token and stopping the
  timer. Remove the round-2 fire-and-forget `authLogout()` call from
  `pollOnce()`'s stale-response branch entirely — it's superseded by this
  scoped mechanism and was the source of the round-2 finding.
- Tests: Python unit tests for `AuthManager.abandon()` (pending-session
  case, already-succeeded case, unknown-handle no-op case, and — the case
  that directly proves this fixes the round-2 finding — a newer session's
  token is untouched by a late `abandon()` call for an old, different
  handle); a server integration test for the new endpoint; frontend tests
  updated/extended to assert `authAbandon` is called with the correct
  handle and that the old `authLogout()`-on-stale-success behavior is
  gone.
- Documentation: `README.md`'s HTTP API table (new endpoint),
  `docs/security-boundaries.md` if the trust-boundary write-up needs a
  line about this.

## Out of scope

- Any other `AuthManager` behavior (app-only lifecycle, silent renewal,
  generation-based supersession for `start()`/`start_app_only()`) — those
  are already correct and untouched.
- Any new UI section or unrelated frontend change.
- Opening or amending an M3 milestone/roadmap.

## Allowed paths

- `auth.py`, `server.py`, `frontend/src/api/client.ts`,
  `frontend/src/state/appState.tsx`, `frontend/src/test/**`,
  `tests/test_auth.py`, `tests/test_server.py`, `README.md`,
  `docs/security-boundaries.md`, `project/issues/ISSUE-0013.md`,
  `project/status/CURRENT.md`, `project/handoffs/ISSUE-0013-handoff.md`.

## Acceptance criteria

1. Abandoning a device-code attempt whose poll has not yet succeeded
   causes any subsequent poll for that handle to return an error state
   (never `"success"`), without needing the client to have already
   detected anything — the server itself refuses to complete it.
2. Abandoning a device-code attempt whose poll *already* succeeded (a
   token is already installed) clears that specific token, but **does
   not** clear a different, newer, currently-installed session/token
   produced by a different handle.
3. Calling abandon with an unknown or already-cleared handle is a safe
   no-op — no exception, no effect on any current session.
4. `pollOnce()` no longer calls `authLogout()` reactively; the round-2
   `deviceCodeRace.test.tsx` assertion for that behavior is replaced with
   an assertion that `authAbandon` was called with the correct handle at
   cancellation time.
5. `python3 -m unittest discover -s tests` and `cd frontend && npm test`
   both pass; `cd frontend && npx tsc -b && npx vite build` succeed.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Backend tests | `python3 -m unittest discover -s tests` | all passed, exit 0 |
| Frontend tests | `cd frontend && npm test` | all passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |
| Typecheck/build | `cd frontend && npx tsc -b && npx vite build` | exit 0 |

## Documentation

- `README.md`'s HTTP API table — add `POST /api/auth/abandon`.
- `docs/security-boundaries.md` — note if the abandon mechanism changes
  any trust-boundary description (expected: no widening, since it can
  only ever narrow what a session can do, never grant anything new).

## Security and privacy impact

- Threat-model delta: narrows an existing gap; abandon can only ever
  *clear* state scoped to a specific already-issued handle, never install
  or extend a session, never accept a credential, never affect a
  different handle's state. No new trust boundary.
- Data/secret impact: none — no new secret handling; `abandon()` never
  touches the app-only credential path.
- Dependency/supply-chain impact: none.
- Protected actions: none anticipated.

## Stop conditions

- Any finding that `abandon()` can clear a different session's token
  than the one named by its handle.
- Any finding that `abandon()` introduces a new way to probe or infer
  session state without prior knowledge of a real handle.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `project/handoffs/ISSUE-0013-handoff.md` | this commit | Real command output recorded in the handoff, bound to the candidate SHA (188 Python tests, 89 Vitest tests, `py_compile`, `validate_repo.py`, `tsc`/`vite build`, all passing) | *pending* | *pending* |

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Final reviewed product SHA: *pending*
- Human advance/merge decision: *pending*
- Merge/result SHA: *pending*
- Residual risks or follow-up: *pending*
- Status record updated: *pending*
