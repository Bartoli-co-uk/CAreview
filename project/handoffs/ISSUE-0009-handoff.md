# Claude handoff: ISSUE-0009, round 0

**Claude issue task:** `ISSUE-0009 app-only-endpoint implementation`
**Approved issue:** `project/issues/ISSUE-0009.md` at this commit
**Starting SHA:** `04e68ee930c44a6c6dc438dfab39c381b6105e6d`
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-27`

## Outcome

Implemented in full. `server.py` gains a new state-changing route,
`POST /api/auth/app`, that wires `auth.py`'s existing (`ISSUE-0008`)
`AuthManager.start_app_only()` to the HTTP layer:

- Reuses the existing `host_allowed()` / `origin_allowed()` guards and
  `MAX_BODY_BYTES` body-size limit already applied to every other `POST`
  route in `do_POST()` — no new bypass surface.
- New module-level validators — `_valid_app_only_tenant()`,
  `_valid_app_only_client_id()`, `_valid_app_only_secret()` — check
  presence, type, and bounded format for all three fields before
  `AuthManager.start_app_only()` is ever called, so a rejected request
  never reaches `auth.py`, retains nothing, and never makes an outbound
  call. The tenant rule mirrors `auth.py`'s own app-only tenant validation
  (GUID or DNS-style domain, rejecting `organizations`/`common`/
  `consumers`) plus an explicit 255-character length bound; `client_id`
  must be exactly a 36-character GUID; `client_secret` must be non-empty
  and at most 512 characters. This duplicates (rather than imports) the
  private tenant regexes already in `auth.py`, since the issue's allowed
  paths permit only *calling* `auth.py`, not reaching into its
  underscore-prefixed internals.
- `CAReviewHandler._auth_app_only(body)` runs those checks, then calls
  `AUTH.start_app_only(tenant, client_id, client_secret)`. On success it
  returns `{"state": "success"}` with `200` and `Cache-Control: no-store`.
  On `auth.AuthError`, the `invalid_tenant` label (the one case that can
  reflect bad caller input despite passing the local checks — defense in
  depth) maps to `400`; every other label (`network_error`,
  `invalid_response`, `provider_error`, `superseded`) maps to `502`, always
  with `no-store` and never the raw provider text (already guaranteed by
  `auth.py`'s `_classify_app_only_error()`).
- `/api/auth/logout` already clears app-only state via the existing
  `AuthManager.logout()` call in `do_POST()` — no server.py change needed
  there; a new test proves it end-to-end at the HTTP layer.
- `README.md`'s HTTP API table gained one row for the new endpoint.

## Changed files

| Path | Change and reason |
|---|---|
| `server.py` | Added `re` import, app-only input-validation constants/functions, the `/api/auth/app` route dispatch, and `_auth_app_only()`. |
| `tests/test_server.py` | Added `FAKE_TENANT`/`FAKE_CLIENT_ID`/`FAKE_SECRET` constants, `contextlib`/`io`/`urllib.parse` imports, and `AppOnlyEndpointTests` (30 new tests, subclassing `ServerIntegrationTests` to reuse its server fixture). |
| `README.md` | Added the `/api/auth/app` row to the HTTP API table; clarified the `/api/auth/logout` row now also mentions the app-only secret. |
| `project/issues/ISSUE-0009.md` | New issue record. |

## Decisions and assumptions

- Duplicated the tenant-validation shape (GUID/domain regexes, disallowed
  aliases) at the HTTP layer rather than importing `auth.py`'s
  underscore-prefixed constants, per the issue's allowed-paths boundary
  ("changes to `auth.py` beyond calling it" are out of scope — reaching
  into its private internals from another module reads as more than a
  call). This is intentional defense-in-depth duplication: `auth.py`
  itself still independently validates the tenant inside
  `start_app_only()`.
- `client_id`'s bound is a single fixed length (36, exact GUID length)
  rather than a separate min/max — a client-credentials `client_id` has no
  legitimate shorter or longer valid form, so "minimum" and "maximum" in
  the acceptance criteria are the same value; a same-length-but-malformed
  string is covered by a distinct boundary test to isolate the format
  check from the length check.
- A malformed (non-JSON) request body is already rejected by
  `_read_json_body()` before path dispatch, returning
  `{"error": "invalid request body"}` — the secret-scan test exercises this
  path directly by posting an invalid-JSON body containing the fake secret
  literal.
- Did not touch `web/`, `graph.py`, or `auth.py` — this issue's scope is
  the HTTP endpoint only; the sign-in card UI is `ISSUE-0010`.

## Acceptance-criteria mapping

| Criterion | Implementation evidence | Status |
|---|---|---|
| Host/Origin/body-size reuse | `server.py:do_POST` (unchanged dispatch guards); `test_requires_origin` | Met |
| Presence/type/bounded-format validation before any outbound call or retained state | `server.py:_valid_app_only_tenant/_valid_app_only_client_id/_valid_app_only_secret`; `test_missing_fields_rejected_with_400`, `test_wrong_type_fields_rejected_with_400`, `test_tenant_one_over_maximum_length_rejected_without_outbound_call`, `test_secret_one_over_maximum_length_rejected_without_outbound_call` | Met |
| Boundary tests: min/max/one-over-max/malformed per field | `test_tenant_minimum_valid_domain_accepted`, `test_tenant_maximum_length_domain_accepted`, `test_tenant_one_over_maximum_length_rejected_without_outbound_call`, `test_tenant_malformed_rejected`, `test_tenant_disallowed_aliases_rejected`; `test_client_id_valid_guid_accepted`, `test_client_id_one_over_maximum_length_rejected`, `test_client_id_malformed_same_length_rejected`; `test_secret_minimum_length_accepted`, `test_secret_maximum_length_accepted`, `test_secret_one_over_maximum_length_rejected_without_outbound_call`, `test_secret_empty_rejected` | Met |
| Success/error response shape | `test_success` | Met |
| Error status mapping (400 vs 502, never 5xx-with-stack) | `test_provider_rejection_maps_to_502_with_stable_label`, `test_network_error_maps_to_502`, `test_tenant_disallowed_aliases_rejected` (400) | Met |
| `/api/policies`/`/api/analysis` unchanged after app-only sign-in | `test_policies_and_analysis_work_after_app_only_sign_in` | Met |
| Silent renewal transparent; renewal failure surfaces stable non-5xx error | `test_silent_renewal_success_is_transparent_to_policies_and_analysis`, `test_silent_renewal_failure_surfaces_stable_non_secret_non_5xx_error` | Met |
| `/api/auth/logout` clears app-only state | `test_logout_clears_app_only_state` | Met |
| Secret absent from every response body (success/failures/malformed-body), incl. URL-encoded/JSON-escaped | `test_secret_absent_from_every_response_body`, `test_provider_error_body_containing_secret_never_leaks` | Met |
| Nothing logged to stderr/access log | `test_nothing_logged_to_stderr` | Met |
| `no-store` on responses reflecting auth state | `test_success` (asserts header); `_auth_app_only` passes `no_store=True` on both branches | Met |
| `unittest`, `py_compile`, `validate_repo.py` pass | See Verification below | Met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | `Ran 163 tests ... OK`, exit 0 | None — run locally, real network/tenant not used |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0, no output | None |
| Governance | `python3 scripts/validate_repo.py` | "Repository validation passed (67 required files checked)." | PowerShell syntax check skipped (no `pwsh` in this environment; CI runs it on Ubuntu) |
| Manual smoke | `python3 server.py` then `curl` `/api/health` and `/api/auth/app` with an invalid tenant | `200`; `400 {"error": "invalid tenant"}`, no outbound network call made | None — no live tenant credentials used, server stopped immediately after |

The reviewer or CI must independently confirm required checks; this handoff is not test authority.

## Documentation

- `README.md` — HTTP API table gained the `/api/auth/app` row; this is the
  issue's own required documentation change.

## Security and privacy

- Threat-model change: none beyond `ISSUE-0008`'s already-accepted
  `RISK-002`/`RISK-006` (`DECISION-014`) — this issue exposes that
  already-reviewed `auth.py` path over the loopback HTTP API behind the
  same Host/Origin/body-size guards every other state-changing endpoint
  uses.
- Residual risk/uncertainty: none identified.
- Protected action attempted: No. No live tenant sign-in; the one manual
  smoke test used a deliberately invalid tenant (`organizations`) so the
  request was rejected locally before any network call, and all automated
  tests use mock transports with synthetic, clearly-labelled fake secret
  literals.

## Review request

- Base SHA: `04e68ee930c44a6c6dc438dfab39c381b6105e6d`
- Head SHA: (this commit; recorded by the launcher)
