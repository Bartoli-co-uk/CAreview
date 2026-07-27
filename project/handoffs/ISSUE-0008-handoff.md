# Claude handoff: ISSUE-0008, round 0

**Claude issue task:** `ISSUE-0008 app-only-token implementation`
**Approved issue:** `project/issues/ISSUE-0008.md` at this commit
**Starting SHA:** `e088b33fb78953e9b351618ae3d23bb751bf690f`
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-27`

## Outcome

Implemented in full. `auth.py` gains an app-only (client-credentials) code
path entirely inside `AuthManager`, alongside the existing device-code flow:

- `build_client_credentials_request(tenant, client_id, client_secret, scope)`
  builds a `grant_type=client_credentials` POST with
  `https://graph.microsoft.com/.default` as the default scope.
- `_app_only_authority(tenant)` validates the tenant before any state change
  or network call: rejects `organizations`/`common`/`consumers` explicitly,
  and requires a GUID or a DNS-style domain (at least two dot-separated
  labels) otherwise.
- `AuthManager.start_app_only(tenant, client_id, client_secret)` supersedes
  any existing device-code session, token, or prior app-only secret (bumping
  the same `_generation` counter the device-code path already uses), calls
  the transport, and on success installs the token **and retains the secret**
  in `self._app_only_secret`/`_tenant`/`_client_id` for the session
  (`DECISION-014`).
- `AuthManager._renew_app_only()` is called from `get_token()` when the
  cached token is expired/absent and a secret is retained: it re-issues the
  client-credentials request with the retained secret (no caller input
  needed) and installs the fresh token, guarded by the same generation-check
  pattern `poll()` uses so a stale renewal response arriving after a
  `logout()` or a new sign-in cannot install.
- `logout()` and device-code `start()` both clear the retained app-only
  state as part of their existing generation-bump/clear block.
- All app-only failures raise `AuthError` with one of a fixed set of local
  labels (`invalid_tenant`, `network_error`, `invalid_response`,
  `provider_error`, `superseded`) via `_classify_app_only_error()` — the
  provider's raw error text is never read into any returned value or
  exception, which structurally rules out any secret-in-error-text leak
  rather than relying on scrubbing.

## Changed files

| Path | Change and reason |
|---|---|
| `auth.py` | Added `APP_ONLY_SCOPE`, tenant-validation regexes, `_app_only_authority()`, `build_client_credentials_request()`, `_classify_app_only_error()`, and `AuthManager.start_app_only()` / `_renew_app_only()`; extended `get_token()`, `start()`, and `logout()` for the app-only lifecycle; extended the module docstring to describe the app-only mode and secret retention/renewal/clearing per `DECISION-014`. |
| `tests/test_auth.py` | Added `AppOnlyRequestBuildingTests`, `AppOnlyLifecycleTests`, and `AppOnlySecretLeakTests` (27 new tests); added `contextlib`/`io`/`json`/`logging` imports for the leak tests. |
| `project/issues/ISSUE-0008.md` | New issue record. |

## Decisions and assumptions

- No real threading is used for the "in-flight" race tests, matching the
  existing device-code test suite's own pattern (`test_inflight_poll_after_logout_does_not_restore_token`,
  `test_inflight_start_after_logout_does_not_recreate_session`): the fake
  transport callback itself calls `logout()`/`start()`/`start_app_only()`
  before returning, since the test suite is single-threaded and this
  deterministically exercises the same generation-counter guard a real race
  would hit.
- A renewal failure (network/provider error) drops the cached access token
  but **keeps the retained secret**, so a subsequent `get_token()` call can
  retry renewal without requiring the user to re-enter the secret — this
  matches the roadmap's framing of "no caller-supplied secret needed" for
  renewal and avoids forcing a full re-sign-in on a transient renewal
  hiccup. `logout()` remains the only way to clear the retained secret.
- Did not touch `graph.py`, `server.py`, `web/`, README, or
  `docs/security-boundaries.md` — this issue's scope is `auth.py`-internal
  per the roadmap's allowed-paths table; the endpoint (`ISSUE-0009`), UI
  (`ISSUE-0010`), and documentation (`ISSUE-0011`) are separate issues.

## Acceptance-criteria mapping

| Criterion | Implementation evidence | Status |
|---|---|---|
| Client-credentials request shape, `.default` scope | `auth.py:build_client_credentials_request`; `tests/test_auth.py::AppOnlyRequestBuildingTests::test_build_client_credentials_request_shape` | Met |
| Tenant validation before any state/network | `auth.py:_app_only_authority`; `test_invalid_tenant_rejected_before_any_state_or_network`, `test_organizations_common_consumers_rejected`, `test_non_guid_non_domain_tenant_rejected` | Met |
| Secret retained for the session | `AuthManager.start_app_only`; `test_success_installs_token_and_retains_secret` | Met |
| Silent renewal from retained secret | `AuthManager._renew_app_only`, `get_token`; `test_silent_renewal_after_simulated_expiry` | Met |
| Success/invalid-tenant/wrong-client-id/provider-error/network-error/renewal-failure coverage | `AppOnlyLifecycleTests` | Met |
| Supersession (new app-only start, device-code start) and logout clearing | `test_device_code_start_supersedes_app_only_secret`, `test_app_only_start_supersedes_prior_app_only_secret`, `test_logout_clears_retained_secret_and_stops_renewal` | Met |
| In-flight stale-response races (initial request and renewal, vs logout and vs new start) | `test_inflight_start_app_only_after_logout_does_not_install`, `test_inflight_start_app_only_after_new_start_does_not_install`, `test_inflight_renewal_after_logout_does_not_reinstall_token`, `test_inflight_renewal_after_new_start_app_only_does_not_install` | Met |
| Secret absent from return value/exception/repr/logging/stderr | `AppOnlySecretLeakTests` (7 tests, including URL-encoded and JSON-escaped provider error bodies) | Met |
| Only fixed local error labels ever raised | `_classify_app_only_error`; every `AppOnlyLifecycleTests` exception-message assertion | Met |
| `graph.py`/`server.py` untouched | `git diff --stat` shows only `auth.py`, `tests/test_auth.py` | Met |
| `unittest`, `py_compile`, `validate_repo.py` pass | See Verification below | Met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | `Ran 112 tests ... OK`, exit 0 | None — run locally, real network/tenant not used |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0, no output | None |
| Governance | `python3 scripts/validate_repo.py` | "Repository validation passed (67 required files checked)." | None |

The reviewer or CI must independently confirm required checks; this handoff is not test authority.

## Documentation

- `auth.py` module docstring — extended in this change to describe app-only
  mode and the secret lifecycle.
- README / `docs/security-boundaries.md` — intentionally not touched;
  `ISSUE-0011`'s scope.

## Security and privacy

- Threat-model change: introduces the first live-secret handling path
  (client secret entry). `RISK-002` (widened local-exposure window) and
  `RISK-006` (over-broad `.default` app-only token) are both pre-accepted
  by `DECISION-014`/roadmap v4 and unaffected by this implementation beyond
  what those decisions already priced in. No new risk introduced.
- Residual risk/uncertainty: none identified beyond the pre-accepted
  `RISK-002`/`RISK-006`.
- Protected action attempted: No. No live tenant sign-in; all tests use mock
  transports and synthetic fake-secret literals clearly labelled as such.

## Review request

- Base SHA: `e088b33fb78953e9b351618ae3d23bb751bf690f`
- Head SHA: (this commit; recorded by the launcher)
