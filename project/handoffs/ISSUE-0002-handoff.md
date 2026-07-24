# Claude handoff: ISSUE-0002, repair round 1

**Repair history:** round 0 candidate `536f11cb7a9f` → Codex `CHANGES_REQUIRED`
(F-001 concurrency race on token state, F-002 uncaught network/malformed errors);
repair round 1 adds an `AuthManager` lock with a current-session identity check
and full transport-error normalization. See
`project/reviews/issues/ISSUE-0002-536f11cb7a9f-claude-response.md`.


**Claude issue task:** `CAreview ISSUE-0002 (device-code auth)`
**Approved issue:** `project/issues/ISSUE-0002.md` at `eb0490c7b7126dda7a573ef6a6bfbbf3de2398fe`
**Starting SHA (base):** `eb0490c7b7126dda7a573ef6a6bfbbf3de2398fe`
**Candidate SHA:** this commit (branch `ai/ISSUE-0002-device-code-auth` HEAD; the launcher binds the exact SHA)
**Created at:** `2026-07-24T13:12:00Z`

## Outcome

Implemented OAuth 2.0 device-code sign-in against the Microsoft Graph PowerShell
first-party public client, with a full in-memory lifecycle and same-origin-gated
API endpoints. No real sign-in is triggered by tests or the launcher (that is a
protected action).

## Changed files

| Path | Change and reason |
|---|---|
| `auth.py` | New: `AuthManager` (device-code request/poll, in-memory token), transport- and clock-injectable; tenant validated to prevent SSRF; no `offline_access`/refresh persistence |
| `server.py` | Add `do_POST` with Host + Origin checks and a bounded JSON body reader; `/api/auth/start`, `/api/auth/poll`, `/api/auth/logout`; module-level `AUTH` |
| `web/index.html` | Enable sign-in: tenant input, Sign in / Sign out, device-code display |
| `web/app.js` | Device-code flow: start → show code+link → server-interval polling → success/expiry/error; `textContent` only |
| `web/style.css` | Styles for the sign-in/device-code elements |
| `tests/test_auth.py` | New: 13 tests for the poll state machine, expiry, slow_down, denied, logout, token expiry, single-concurrency, request building, tenant validation |
| `tests/test_server.py` | Add POST tests: no-origin/cross-origin rejected (403), same-origin logout 200, poll unknown handle |
| `README.md` | Update status wording: sign-in now implemented; analysis still upcoming (issue Documentation task) |

## Decisions and assumptions

- Client: Graph PowerShell public client `14d82eec-…` with `organizations`
  authority; resource-qualified read-only Graph scopes; **no** `offline_access`,
  so no refresh token is retained — the user re-authenticates on expiry
  (DECISION-004 / brief A-refresh decision).
- `/api/auth/start` returns an **opaque handle** (`secrets.token_urlsafe`), the
  `user_code`, and `verification_uri` — never the raw `device_code`.
- Polling cadence is **server-controlled**: polls faster than the interval return
  `pending` without contacting Microsoft; `slow_down` widens the interval.
- **Single concurrency**: a new `start` supersedes any pending session and clears
  any token; the old handle then returns an error.
- State-changing `/api/auth/*` require a same-origin `Origin` header (CSRF/cross
  -site defence) on top of the Host allowlist.
- Tenant strings are validated (`^[A-Za-z0-9._-]+$`) so they cannot redirect the
  auth request to another host (SSRF defence).

## Acceptance-criteria mapping

| Criterion | Evidence | Status |
|---|---|---|
| start returns handle+user_code, not device_code | `auth.AuthManager.start`; `test_start_returns_handle_not_device_code` | met |
| poll pending→success; error states no crash | `test_pending_then_success`, `test_access_denied_is_terminal_error` | met |
| server-controlled cadence | `test_server_controlled_cadence_skips_transport`, `test_slow_down_widens_interval` | met |
| device-code expiry | `test_device_code_expiry` | met |
| logout clears memory | `test_logout_clears_token` | met |
| access-token expiry deterministic | `test_access_token_expiry` | met |
| refresh decision (no persistence) | no `offline_access`; documented | met |
| single-concurrency | `test_single_concurrency_supersedes` | met |
| token in memory only | `AuthManager` holds token in an attribute; never written | met |
| live sign-in (protected) | deferred; requires human approval | not attempted (by design) |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 32 passed, exit 0 | none |
| Manual origin | `curl -X POST … /api/auth/logout` with/without Origin | no-origin 403; same-origin `{"state":"signed_out"}` | none |
| Governance | `python3 scripts/validate_repo.py` | passes (out-of-band; sandbox cannot per DECISION-004) | none |

## Documentation

- README status wording updated for the implemented sign-in.

## Security and residual risk

- Threat-model change: introduces token acquisition/storage (in memory only),
  outbound calls to `login.microsoftonline.com` only, tenant-validated;
  same-origin gate on state-changing endpoints.
- Residual risk: unauthenticated loopback API (RISK-002, accepted); live sign-in
  not exercised in automated checks (protected action).
- Protected action attempted: No (no real tenant sign-in).

## Review request

- Base SHA: `eb0490c7b7126dda7a573ef6a6bfbbf3de2398fe`
- Head SHA: this candidate's commit (launcher binds the exact SHA).
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0002 <BASE-SHA> <HEAD-SHA>`
- Gate policy: per `DECISION-004`, static review + author out-of-band evidence;
  human merge under `DECISION-005`.
- Attention: token never leaves memory; opaque handle; tenant SSRF validation;
  Origin gate; no refresh persistence.
