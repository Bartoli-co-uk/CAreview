# ISSUE-0002: Device-code authentication

**Status:** `REPAIRING`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `3` at `125d74f6d4bfe85f1a727293064d0887f2d121c7`
**Dependencies:** `ISSUE-0001` (COMPLETE)
**Branch:** `ai/ISSUE-0002-device-code-auth`
**Starting SHA:** `eb0490c7b7126dda7a573ef6a6bfbbf3de2398fe`
**Candidate SHA:** `this commit (branch HEAD); the launcher records the full SHA`

## Objective

Implement OAuth 2.0 device-code sign-in against the Microsoft Graph PowerShell
first-party public client, exposing start/poll endpoints and holding the access
token in memory, with the Sign-in UI showing the code and reflecting success.

## In scope

- `auth.py` — device-code request to `login.microsoftonline.com/{tenant}/oauth2/v2.0/devicecode`
  and token polling at `.../oauth2/v2.0/token`, using stdlib `urllib`. In-memory
  token store keyed to the process; tenant default `organizations`.
- `server.py` — `/api/auth/start` (returns `user_code`, `verification_uri`,
  polling handle) and `/api/auth/poll` (returns pending/success/error).
- `web/` — Sign-in panel: button, displayed code + link, status updates.
- `tests/` — unit tests for request building and poll-state handling against a
  mocked token endpoint (`authorization_pending`, `slow_down`, success, error).

## Out of scope

- Graph policy calls (ISSUE-0003) and analysis (ISSUE-0004).
- Any token persistence, refresh-token storage on disk, or app registration.

## Allowed paths

- `auth.py`, `server.py`, `web/**`, `tests/**`

## Acceptance criteria

Completion is gated on the mocked checks below (criteria 1–9). Criterion 10 (live
sign-in) is a protected action and is NOT a completion precondition (Codex F-002).

1. `/api/auth/start` builds a correct device-code request for the configured
   client and tenant and returns an **opaque, bounded polling handle** plus the
   `user_code` and `verification_uri` (never the raw `device_code`).
2. `/api/auth/poll` transitions pending → success, and surfaces
   `authorization_pending`/`slow_down`/`expired_token`/`access_denied`/errors
   without crashing.
3. **Polling cadence is server-controlled:** the server enforces the interval
   returned by Microsoft (honouring `slow_down`) rather than trusting the client.
4. **Device-code expiry** is handled: after `expires_in`, the handle is invalidated
   and a re-start is required.
5. **Logout / cancellation** clears the token and any pending handle from memory.
6. **Access-token expiry** is deterministic: an expired token yields a clear
   "re-authenticate" state rather than a failed Graph call surfacing as a crash.
7. **Refresh-token decision (explicit):** the MVP does **not** persist refresh
   tokens; on access-token expiry the user re-authenticates. Documented in code.
8. **Single-concurrency policy:** at most one active sign-in/session at a time; a
   new `start` supersedes any pending handle.
9. The access token is held only in memory; never written to disk, logs, response
   bodies beyond a success flag, or the repository.
10. (Protected, post-approval) A real device-code sign-in against a **named**
    tenant yields a usable token — performed only after separate human approval
    (see Security and privacy impact); evidence recorded without the token value.

Unit tests cover criteria 1–8 against a mocked token endpoint (pending, slow_down,
expired, denied, success, expiry, logout, concurrency).

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Manual sign-in | Run app, click Sign in, approve code | poll reports success; no token in logs |

## Documentation

- README: confirm the Sign-in steps and the `Policy.Read.All` consent note.

## Security and privacy impact

- Threat-model delta: introduces token acquisition and storage; tokens in memory only.
- Data/secret impact: access/refresh tokens are sensitive; must never be logged or persisted.
- Dependency/supply-chain impact: none; `urllib` only.
- Protected actions (Codex F-002): performing a **real device-code sign-in
  against a named tenant** is a protected action (authentication) requiring
  separate, explicit human approval that names the tenant/test identity.
  Automated completion uses mocked checks only; the launcher and unit tests never
  trigger a real sign-in. No client secret is introduced (public client).

## Stop conditions

- Any need to persist tokens/refresh tokens, add a client secret, add a
  dependency, perform a live sign-in without recorded human approval, or if the
  first-party client cannot obtain the scopes (record and escalate per RISK-001).

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `ISSUE-0002-handoff.md` | `536f11cb7a9f…` | py_compile 0; 27 tests pass; validator pass; manual origin OK | `ISSUE-0002-536f11cb7a9f-codex.json` | CHANGES_REQUIRED (F-001 concurrency, F-002 error handling) |
| 1 (repair) | `ISSUE-0002-handoff.md` | `4b30e05f6219…` | py_compile 0; 32 tests pass; validator pass | `ISSUE-0002-4b30e05f6219-codex.json` | BLOCKED (F-001 in-flight start; execution evidence) |
| 2 (repair) | `ISSUE-0002-handoff.md` | `752cd75a8770…` | py_compile 0; 33 tests pass; validator pass | `ISSUE-0002-752cd75a8770-codex.json` | BLOCKED (F-001 immediate supersession; F-002 README advisory) |
| 3 (repair, authorized) | `ISSUE-0002-handoff.md` | repair-3 candidate (launcher binds SHA) | py_compile 0; 34 tests pass; validator pass | pending final review | pending |

Two repair rounds are the default; `DECISION-006` authorized one extra round for
ISSUE-0002 to resolve F-001/F-002. Per `DECISION-004`, a `BLOCKED` outcome whose
only basis is the execution-evidence limitation is acceptable and the human merges.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
