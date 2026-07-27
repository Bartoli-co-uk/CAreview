# ISSUE-0008: App-only token acquisition inside auth.py only

**Status:** `COMPLETE`
**Milestone:** `M2`
**Approved roadmap:** `ROADMAP.md` version `4` at `9e5ba6d2f6c2b7f7efa81dcfc415e1f787aaa458` (approved by `DECISION-015`)
**Dependencies:** `ISSUE-0007` (COMPLETE, `DECISION-016`); `DECISION-014` (retention model, `RISK-002` acceptance)
**Branch:** `ai/ISSUE-0008-app-only-token` (merged into `main`)
**Starting SHA:** `e088b33fb78953e9b351618ae3d23bb751bf690f`
**Candidate SHA:** `205125474389932f02e7c484dd59ad612892ac4b` (round 1, final reviewed candidate)
**Merge SHA:** `04e68ee930c44a6c6dc438dfab39c381b6105e6d` (merge commit on `main`)

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
| 0 | `project/handoffs/ISSUE-0008-handoff.md` | `88a4a6d355eb96b6739010744b1b7f7f76751c35` | 112 tests pass; compile clean; validator passed | `project/reviews/issues/ISSUE-0008-88a4a6d355eb-codex.json` | `BLOCKED` — F-001 (scope override possible) + F-002 (missing device-code-supersedes-app-only race tests) + sandbox execution-evidence limitation (accepted residual, `DECISION-015`) |
| 1 | `project/handoffs/ISSUE-0008-handoff.md` (Repair round 1 section) | `205125474389932f02e7c484dd59ad612892ac4b` | 116 tests pass; compile clean; validator passed | `project/reviews/issues/ISSUE-0008-205125474389-codex.json` | `BLOCKED` — zero findings; sole blocker is the accepted sandbox execution-evidence residual (`DECISION-015`) |

Only 1 of 2 permitted issue repair rounds was needed.

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Final reviewed product SHA: `205125474389932f02e7c484dd59ad612892ac4b` —
  clean of all actionable findings; `BLOCKED` solely on the accepted sandbox
  execution-evidence residual.
- Human advance/merge decision: `APPROVE` — `project/decisions/DECISION-017-issue-0008-advance-and-merge.md`.
- Merge/result SHA: `04e68ee930c44a6c6dc438dfab39c381b6105e6d` (merge commit on `main`).
- Residual risks or follow-up: none identified beyond `RISK-002`/`RISK-006`,
  already accepted by `DECISION-014`
- Status record updated: this commit.
