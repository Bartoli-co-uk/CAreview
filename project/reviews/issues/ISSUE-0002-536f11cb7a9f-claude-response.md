# Claude response to Codex issue review — ISSUE-0002 (round 0 → repair 1)

**Reviewed candidate:** `536f11cb7a9f76eb2c3bcf9fafcfb08b0dba50ba`
**Codex report:** `project/reviews/issues/ISSUE-0002-536f11cb7a9f-codex.json` (outcome `CHANGES_REQUIRED`)
**Responder:** Claude issue task, 2026-07-24 (repair round 1)

| Finding | Disposition | Action |
|---|---|---|
| F-001 (REQUIRED/high) In-flight poll can restore a token after logout/supersession | Accepted | `AuthManager` now holds a `threading.RLock`. The blocking token call runs outside the lock; on return the result is installed only if `self._session is` the same session object, so a concurrent `logout()` or superseding `start()` invalidates a stale poll. All lifecycle transitions (`start`/`poll`/`logout`/`get_token`) are lock-guarded. New test `test_inflight_poll_after_logout_does_not_restore_token`. |
| F-002 (REQUIRED/medium) Network/timeout/malformed failures escape as uncaught exceptions | Accepted | `urllib_transport` now converts `URLError`/timeout/`OSError` to `(0, {"error":"network_error"})` and non-JSON/non-object bodies to `{"error":"bad_response"}`, echoing no response data. `start()` validates required fields and numeric ranges (raising a bounded `AuthError`); `poll()` treats transient transport errors as retryable `pending`. `server.do_POST` wraps routing so any unexpected error returns a controlled `{"error":"internal_error"}` 500. New tests for transient network/bad-response during poll, start network failure, and transport normalization. |

## Out-of-band check evidence (repaired candidate)

- `python3 -m py_compile $(git ls-files '*.py')` → exit 0.
- `python3 -m unittest discover -s tests` → 32 passed, exit 0.
- `python3 scripts/validate_repo.py` → passes.

The remaining review limitation is the execution-evidence sandbox constraint
(DECISION-004); both substantive findings are fixed. A fresh re-review follows.
