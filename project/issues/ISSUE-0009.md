# ISSUE-0009: POST /api/auth/app endpoint wiring app-only mode to the server

**Status:** `COMPLETE`
**Milestone:** `M2`
**Approved roadmap:** `ROADMAP.md` version `4` at `9e5ba6d2f6c2b7f7efa81dcfc415e1f787aaa458` (approved by `DECISION-015`)
**Dependencies:** `ISSUE-0008` (COMPLETE, `DECISION-017`); `DECISION-018` (start authorization)
**Branch:** `ai/ISSUE-0009-app-only-endpoint` (merged into `main`)
**Starting SHA:** `4fdfa9f65b1e32bc0992dc3b7bd7d2357c3a8339`
**Candidate SHA:** `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` (round 1, final reviewed candidate)
**Merge SHA:** `8253c1d7a754a3a967c2687c5ccc45e71794391a` (merge commit on `main`)

## Objective

Add `POST /api/auth/app`, wiring the app-only (client-credentials)
authentication mode already implemented in `auth.py` (`ISSUE-0008`) to the
existing HTTP server, so a caller can sign in with a tenant, client ID, and
client secret over the same loopback API used for device-code sign-in.

## In scope

- `server.py` — new route `/api/auth/app`, bounded input validation
  (presence, type, format) for `tenant`/`client_id`/`client_secret`, and a
  handler that calls `AuthManager.start_app_only()` and maps its outcomes to
  HTTP responses.
- `tests/test_server.py` — full coverage per acceptance criteria below.
- `README.md` — API table entry for the new endpoint.

## Out of scope

- `web/`, `graph.py` — untouched.
- Any change to `auth.py` beyond calling its existing public
  `AuthManager.start_app_only()` method.
- Sign-in card mode toggle / app-only form UI (`ISSUE-0010`).
- Live tenant sign-in (protected action, not attempted).

## Allowed paths

- `server.py`, `tests/test_server.py`, `README.md`

## Acceptance criteria

1. The endpoint reuses the existing Host allowlist and Origin check (same
   guard as every other state-changing `POST` route) and the existing
   `MAX_BODY_BYTES` request-size limit.
2. `tenant`, `client_id`, and `client_secret` presence, type, and bounded
   format are validated before any value is retained or transported
   outbound: `tenant` must be a GUID or a DNS-style domain label under a
   documented maximum length, rejecting `organizations`/`common`/`consumers`
   (`DECISION-014`); `client_id` must match the GUID shape Entra app IDs
   use; `client_secret` must be a non-empty string under a documented
   maximum length (512 characters). Oversized or malformed values on any of
   the three fields are rejected with `400` before an identity request is
   made and without being retained in `AuthManager` state.
3. Boundary tests cover minimum, maximum, one-over-maximum, and malformed
   values for each of the three fields.
4. Returns `{"state": "success"}` on success and a stable machine-label
   error otherwise.
5. Error mapping: invalid input → `400`; provider rejection (any
   `AuthError` label other than `invalid_tenant`) → `502` with a stable
   local error label only (never the raw provider response body or text);
   never `5xx` with a stack trace.
6. `/api/policies` and `/api/analysis` work unchanged after an app-only
   sign-in (mock Graph transport).
7. With mocked identity and Graph transports and a simulated expired
   app-only token, a test verifies silent renewal succeeds transparently and
   both `/api/policies` and `/api/analysis` complete against the newly
   renewed token; a separate test verifies a renewal failure (provider or
   network error) surfaces a stable, non-secret, non-`5xx` error from those
   endpoints rather than a stale or missing token.
8. `/api/auth/logout` clears app-only state (already true via
   `AuthManager.logout()`; covered by a server-layer test).
9. A test scans every response body — across success, each failure path,
   and the malformed-JSON-body path — for the fake secret literal,
   including its URL-encoded and JSON-escaped forms, and fails if found.
10. A test asserts nothing is written to stderr/access log for a request
    to this endpoint.
11. `no-store` is present on any response reflecting auth state from this
    endpoint.
12. `unittest`, `py_compile`, `validate_repo.py` all pass.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

## Documentation

- `README.md` — API table entry documenting `POST /api/auth/app`, its body
  shape, and the reject-before-outbound-call behavior for disallowed
  tenants and malformed/oversized fields.

## Security and privacy impact

- Threat-model delta: none beyond what `ISSUE-0008` (`DECISION-014`)
  already priced in (`RISK-002` as widened, `RISK-006` over-broad
  `.default` token) — this issue only exposes the already-reviewed
  `auth.py` app-only path over the existing loopback HTTP surface, subject
  to the same Host/Origin/body-size guards every other state-changing
  endpoint already has.
- Data/secret impact: the client secret passes through this endpoint's
  request body once per sign-in call; it is validated for shape and bound
  length here but not logged, and is retained only inside `AuthManager`
  (`auth.py`, `ISSUE-0008`'s existing behavior) — this issue adds no new
  retention path.
- Dependency/supply-chain impact: none — stdlib only (`re`, already-used
  `json`/`http`).
- Protected actions: none. No live tenant sign-in performed; all tests use
  mock transports and synthetic, clearly-labelled fake secret literals.

## Stop conditions

- None encountered. No ambiguity, no path expansion beyond `server.py` /
  `tests/test_server.py` / `README.md`, no protected action attempted.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `project/handoffs/ISSUE-0009-handoff.md` | `c029199c5671069917c13c268a6c4a32ac73881f` | 163 tests pass; compile clean; validator passed | `project/reviews/issues/ISSUE-0009-c029199c5671-codex.json` | `BLOCKED` — F-001 (missing durable start-authorization record; stale base SHA pulled in an unrelated intervening commit) + F-002 (renewal tests didn't prove the renewed token reached both endpoints) + F-003 (secret-scan didn't cover every response path/label) |
| 1 | `project/handoffs/ISSUE-0009-handoff.md` (Repair round 1 section) | `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` | 162 tests pass; compile clean; validator passed | `project/reviews/issues/ISSUE-0009-7b0600f0831f-codex.json` | `BLOCKED` — zero findings; sole blocker is the sandbox execution-evidence residual (same pattern accepted by `DECISION-010`/`DECISION-015`/`DECISION-016`/`DECISION-017`) |

Only 1 of 2 permitted issue repair rounds was needed.

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Final reviewed product SHA: `7b0600f0831f68f8933b68ca0bba34f58a00b0cc` —
  `findings: []`; `BLOCKED` solely on the accepted sandbox
  execution-evidence residual (loopback sockets, `__pycache__` writes, and
  a writable temp directory are all unavailable inside the read-only
  review sandbox).
- Human advance/merge decision: `APPROVE` — `project/decisions/DECISION-019-issue-0009-advance-and-merge.md`.
- Merge/result SHA: `8253c1d7a754a3a967c2687c5ccc45e71794391a` (merge commit on `main`). Required checks re-run on the merged tree: 162 tests passed, `py_compile` clean, `validate_repo.py` clean.
- Residual risks or follow-up: none identified beyond the pre-accepted
  `RISK-002`/`RISK-006` (`DECISION-014`), unaffected by this issue.
- Status record updated: this commit.
