# ISSUE-0008: App-only token acquisition inside auth.py only

**Status:** `REVIEWING`
**Milestone:** `M2`
**Approved roadmap:** `ROADMAP.md` version `4` at `9e5ba6d2f6c2b7f7efa81dcfc415e1f787aaa458` (approved by `DECISION-015`)
**Dependencies:** `ISSUE-0007` (COMPLETE, `DECISION-016`); `DECISION-014` (retention model, `RISK-002` acceptance)
**Branch:** `ai/ISSUE-0008-app-only-token`
**Starting SHA:** `e088b33fb78953e9b351618ae3d23bb751bf690f`
**Candidate SHA:** `this commit (branch HEAD); the launcher records the full SHA`

## Objective

Add app-only (OAuth 2.0 client-credentials) token acquisition to `auth.py`,
entirely inside the existing `AuthManager` — no HTTP endpoint, no UI — so a
user with their own Entra app registration (application `Policy.Read.All`
already consented) can authenticate CAreview with a tenant, client ID, and
client secret instead of the device-code flow.

## In scope

- `auth.py` — `build_client_credentials_request()`, `_app_only_authority()`
  tenant validator, `AuthManager.start_app_only()`, `AuthManager._renew_app_only()`,
  and `AuthManager.get_token()` extended for silent renewal.
- `tests/test_auth.py` — full coverage per acceptance criteria below.
- Module docstring in `auth.py` documenting the secret lifecycle and
  retention decision (`DECISION-014`).

## Out of scope

- Any HTTP endpoint or UI (`ISSUE-0009`, `ISSUE-0010`).
- `graph.py`, `server.py`, `web/` — untouched.
- Certificate-based app-only auth — deferred (`ISSUE-0011` records it as a
  future enhancement).
- Any persistence, environment-variable input, or live tenant sign-in
  (protected action, not attempted).

## Allowed paths

- `auth.py`, `tests/test_auth.py`

## Acceptance criteria

1. `build_client_credentials_request()` builds a `grant_type=client_credentials`
   request with the caller's `tenant`/`client_id`/`client_secret` and
   `https://graph.microsoft.com/.default` as scope (brief A7: app-only cannot
   request a narrower scope).
2. Tenant validation rejects `organizations`/`common`/`consumers` and
   anything that is not a GUID or a DNS-style domain, before any outbound
   request or state change (`DECISION-014` Q5).
3. `AuthManager.start_app_only()` installs an app-only token in the existing
   token slot and **retains the secret in the manager instance for the
   session** (`DECISION-014` Q6 — not discarded after the first request).
4. A renewal path (`get_token()` → `_renew_app_only()`) uses the retained
   secret to silently request a fresh token on expiry with no caller-supplied
   secret needed.
5. Mock-transport unit tests cover: success; invalid tenant; wrong client id
   (provider rejection); generic provider error; transient/network error;
   silent renewal after simulated expiry; a renewal failure that surfaces as
   "no token" rather than a crash; supersession by a fresh `start_app_only()`
   call; supersession by a device-code `start()`; and `logout()` clearing the
   retained secret.
6. Using a synchronous transport-callback race pattern (mirroring the
   existing device-code tests' style — this test suite is single-threaded and
   does not use real OS threads), tests cover in-flight stale-response races:
   a `logout()` or a new `start()`/`start_app_only()` issued while an initial
   client-credentials request or a silent-renewal request is still
   "outstanding" (i.e., the transport callback triggers it before returning)
   must not let that stale response install a token, retain, or recreate
   secret state once it completes — mirroring the existing device-code
   `AuthManager`'s generation-counter guard.
7. A test asserts the fake secret literal appears in no return value, no
   exception message, no `repr()` of the manager, and no captured
   `logging`/stderr output.
8. Raw provider error text is never returned by any public method or stored
   — a failed request maps to one of a small, fixed set of local error
   labels (`invalid_tenant`, `network_error`, `invalid_response`,
   `provider_error`, `superseded`) regardless of the provider's response
   body; a test asserts this holds even when the mock provider's error body
   contains the secret literally, URL-encoded, or JSON-escaped.
9. `graph.py` and `server.py` are untouched (proves brief A6).
10. `unittest`, `py_compile`, `validate_repo.py` all pass.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | all pass (112 tests) |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

## Documentation

- `auth.py` module docstring: extended to describe the app-only mode, the
  session-lifetime secret retention and silent-renewal decision
  (`DECISION-014`), and that the secret never appears in a returned value,
  exception, or `repr()`.
- README / `docs/security-boundaries.md`: **not** touched by this issue —
  that is `ISSUE-0011`'s scope (dual-mode documentation finalization).

## Security and privacy impact

- Threat-model delta: introduces the first live-secret handling path
  (`RISK-002` as widened, `RISK-006` over-broad `.default` token — both
  already accepted in `DECISION-014`/roadmap v4). No new risk beyond what
  those decisions already priced in.
- Data/secret impact: the submitted client secret is retained in process
  memory for the app-only session and used for silent renewal; never written
  to disk, logs, or any tracked file; cleared on logout, on supersession by
  a new sign-in (either mode), and on process exit.
- Dependency/supply-chain impact: none — stdlib only (`urllib`, `re`, `json`,
  `threading`, `secrets`, `time`).
- Protected actions: none. No live tenant sign-in performed; all tests use
  mock transports and synthetic, clearly-labelled fake secret literals.

## Stop conditions

- None encountered. No ambiguity, no path expansion beyond `auth.py` /
  `tests/test_auth.py`, no protected action attempted.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `project/handoffs/ISSUE-0008-handoff.md` | (this branch HEAD) | 112 tests pass; compile clean; validator passed | pending | pending |

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Final reviewed product SHA: `pending`
- Human advance/merge decision: `pending`
- Merge/result SHA: `pending`
- Residual risks or follow-up: none identified beyond `RISK-002`/`RISK-006`,
  already accepted by `DECISION-014`
- Status record updated: `pending`
