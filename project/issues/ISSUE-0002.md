# ISSUE-0002: Device-code authentication

**Status:** `PLANNED`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `1` at `[SHA pending roadmap approval]`
**Dependencies:** `ISSUE-0001`
**Branch:** `ai/ISSUE-0002-device-code-auth`
**Starting SHA:** `[set at implementation start]`
**Candidate SHA:** `Not created`

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

1. `/api/auth/start` returns a real device code and verification URI for the
   configured client and tenant.
2. `/api/auth/poll` transitions pending → success once the user approves, and
   surfaces `authorization_pending`/`slow_down`/errors without crashing.
3. The access token is held only in memory; it is never written to disk, logs,
   response bodies beyond a success flag, or the repository.
4. Unit tests cover the poll state machine with a mocked token endpoint.
5. Manual evidence: a real device-code sign-in against a tenant yields a token
   (recorded in the handoff, without the token value).

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
- Protected actions: none new. No client secret is introduced (public client).

## Stop conditions

- Any need to persist tokens, add a client secret, add a dependency, or if the
  first-party client cannot obtain the scopes (record and escalate per RISK-001).

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `[path]` | `[SHA]` | `[path/summary]` | `[path]` | `[outcome]` |

Maximum two repair rounds; every Codex review is a fresh ephemeral read-only
process against the named SHA.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
