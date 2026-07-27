# Claude handoff: ISSUE-0010, round 0

**Claude issue task:** `ISSUE-0010 app-only-ui implementation`
**Approved issue:** `project/issues/ISSUE-0010.md` at this commit
**Starting SHA:** `f3b5414a4f2d3104d11bbb1ce6d5669a58123e79`
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-27`

## Outcome

Implemented in full. The sign-in card gains a second, initially-hidden mode
alongside the unchanged default device-code flow:

- `web/index.html` — wraps the existing device-code fields in
  `#devicecode-mode` (visible by default) and adds `#app-only-mode`
  (`hidden` by default) containing tenant/client-ID/client-secret inputs, a
  caution paragraph naming what the secret grants, and submit/cancel
  buttons. The secret input is `type="password"` with `autocomplete="off"`.
  A single toggle button (`#app-only-toggle-btn`) switches into app-only
  mode; a cancel button (`#app-only-cancel-btn`) switches back.
- `web/app.js` — `showAppOnlyMode()`/`showDeviceCodeMode()` toggle
  visibility and call `clearAppOnlySecretField()` on every switch (both
  directions); `submitAppOnly()` validates presence and the client-side
  tenant-alias rule (mirroring `auth.py`/`server.py`'s
  `organizations`/`common`/`consumers` rejection) before calling
  `postJson("/api/auth/app", ...)`, then clears the secret field
  immediately after every submit attempt regardless of outcome; `signOut()`
  additionally clears the secret field and resets the view to device-code
  mode. No new DOM sink is introduced — the file still uses only
  `textContent`/`createElement`/property assignment, never `innerHTML` or
  similar.
- `web/style.css` — minimal styling for the new form fields, the `.caution`
  box, and a `.link-btn` style for the toggle/cancel buttons.
- `tests/test_ui_safety.py` — new `AppOnlyModeToggleTests` class (10 tests)
  covering every acceptance criterion statically.
- `README.md` — one new bullet under "Quick start" describing the toggle
  and its secret-handling guarantees.

## Changed files

| Path | Change and reason |
|---|---|
| `web/index.html` | Wrapped device-code fields in `#devicecode-mode`; added `#app-only-mode` (tenant/client-ID/secret form, caution text, toggle/cancel buttons). |
| `web/app.js` | Added `APP_ONLY_DISALLOWED_TENANTS`, `isDisallowedAppOnlyTenant()`, `clearAppOnlySecretField()`, `showAppOnlyMode()`, `showDeviceCodeMode()`, `submitAppOnly()`, `initAppOnly()`; extended `signOut()` to clear the secret field and reset the view; wired `initAppOnly()` into `DOMContentLoaded`. |
| `web/style.css` | Styles for `#app-only-mode` inputs/labels, `.link-btn`, `.caution`. |
| `tests/test_ui_safety.py` | Added `_function_body()` helper and `AppOnlyModeToggleTests` (10 tests). |
| `README.md` | Added an app-only sign-in bullet under "Quick start". |
| `project/issues/ISSUE-0010.md` | New issue record. |

## Decisions and assumptions

- The secret field is what gets cleared on submit/mode-switch/logout — not
  the tenant/client-ID fields — matching the roadmap's acceptance-criteria
  wording ("the field is cleared...") and `RISK-005`'s framing, which is
  specifically about the *secret*. Leaving tenant/client-ID populated
  across a mode-switch-and-back is a minor convenience with no security
  implication (`RISK-005` and `DECISION-014` do not treat those two fields
  as sensitive).
- Client-side validation only re-implements the multi-tenant alias
  rejection (the one acceptance criterion that explicitly calls for a
  client-side mirror). Full GUID/domain-shape and length validation is
  intentionally left to the server (`ISSUE-0009`'s existing
  `/api/auth/app` validation) — duplicating it client-side would be
  unvalidated-by-review surface for no acceptance-criteria benefit, and
  the server's `400` response is surfaced to the user via `setAuthStatus`.
- Did not touch `server.py`, `auth.py`, or `graph.py` — this issue's scope
  is `web/`-only per the roadmap's allowed-paths table.

## Acceptance-criteria mapping

| Criterion | Implementation evidence | Status |
|---|---|---|
| Default device-code view; explicit toggle reveals app-only form | `web/index.html` (`#devicecode-mode` visible, `#app-only-mode hidden`); `tests/test_ui_safety.py::AppOnlyModeToggleTests::test_default_view_is_device_code` | Met |
| Secret input `type="password"`, `autocomplete="off"` | `web/index.html`; `test_secret_input_is_password_with_autocomplete_off` | Met |
| Secret never in console/storage/cookie/URL/query string | `web/app.js` (no such sinks used anywhere in the file); `postJson` sends a JSON body, not a URL; `test_secret_never_reaches_console_storage_or_cookies`, `test_secret_sent_only_as_json_body_not_url_or_query_string` | Met |
| Secret field cleared after submit, on mode switch, on logout | `clearAppOnlySecretField()` calls in `submitAppOnly`, `showAppOnlyMode`, `showDeviceCodeMode`, `signOut`; `test_secret_field_cleared_on_submit`, `test_secret_field_cleared_on_mode_switch_both_directions`, `test_secret_field_cleared_on_logout`; manual walkthrough below | Met |
| In-page caution names what the secret grants | `web/index.html` `.caution` paragraph; `test_caution_text_present` | Met |
| Client-side rejection of disallowed tenant aliases mirrors server | `APP_ONLY_DISALLOWED_TENANTS`/`isDisallowedAppOnlyTenant()`; `test_client_side_tenant_alias_rejection_mirrors_server` | Met |
| CSP and text-only rendering rules unchanged | CSP meta tag untouched (`test_csp_meta_unchanged`); no new DOM sink (`AppJsSafetyTests::test_no_dangerous_dom_sinks`, which covers the whole file) | Met |
| Static assertions cover every criterion | `AppOnlyModeToggleTests` (10 tests) | Met |
| Manual browser walkthrough (runtime clearing proof) | See below | Met |
| `unittest`, `py_compile`, `validate_repo.py` pass | See Verification below | Met |

## Manual browser walkthrough (evidence)

**No browser-automation tool was available to this Claude task** (no
connected `claude-in-chrome` MCP; the `computer-use` MCP treats browsers at
a read-only tier that blocks clicks/typing). Per `AGENTS.md` ("stop when a
task requires unavailable isolation, access, evidence, or expertise"),
Claude started the local server (`python3 server.py`, confirmed live via
`curl /api/health`) and asked the human to perform the walkthrough directly
in their own browser, using synthetic values, with dev tools open on
Console / Application → Storage / Elements. Steps given:

1. Open the app-only form via the toggle; confirm the secret input is
   `type="password"`/`autocomplete="off"` in Elements; type a fake secret
   (`fake-secret-walkthrough-123`).
2. Switch back to device-code mode, then back to app-only mode; check the
   secret field's value in Elements.
3. Fill in a synthetic tenant/client ID and the fake secret again; submit
   (expected to fail — no real tenant); check the secret field's value
   immediately after, and scan Console and Storage (Local/Session/Cookies)
   for the fake secret string.
4. Re-enter the fake secret, then trigger sign-out; check the field.

**Human-reported result:** "Field was empty at every check, nothing in
console or storage." — i.e. the secret field was empty after the mode
switch, empty immediately after submit, empty after logout, and the fake
secret literal did not appear in the Console or in any Local Storage,
Session Storage, or Cookie entry at any checkpoint.

This is disclosed as human-performed, Claude-guided evidence, not
independently Claude-executed — consistent with the issue's own stop
condition recorded in `project/issues/ISSUE-0010.md`.

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | `Ran 172 tests ... OK`, exit 0 | None — run locally, real network/tenant not used |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0, no output | None |
| Governance | `python3 scripts/validate_repo.py` | "Repository validation passed (67 required files checked)." | None |
| Manual browser walkthrough | See above | Field empty at every checkpoint; nothing in console/storage | Human-performed (no browser-automation tool available to Claude), Claude-guided; steps and result recorded above |

The reviewer or CI must independently confirm required checks; this handoff is not test authority.

## Documentation

- `README.md` — added a bullet under "Quick start" describing the toggle
  and secret-handling guarantees; this is the issue's own required
  documentation change.

## Security and privacy

- Threat-model change: none beyond `RISK-005`, already accepted in
  roadmap v4 with exactly the mitigations implemented here.
- Residual risk/uncertainty: none identified beyond `RISK-005` itself
  (browser-side secret exposure is an accepted, owner-chosen trade-off,
  not something this issue could eliminate).
- Protected action attempted: No. No live tenant sign-in; the manual
  walkthrough used synthetic, clearly-fake values against a local server
  instance only, and the server was stopped immediately after.

## Review request

- Base SHA: `f3b5414a4f2d3104d11bbb1ce6d5669a58123e79`
- Head SHA: (this commit; recorded by the launcher)

## Repair round 1

Round-0 Codex review
(`project/reviews/issues/ISSUE-0010-1d557b3840f7-codex.json`, candidate
`1d557b3840f716ad0d25a0f6d4be407cdeeb221b`) returned `BLOCKED` with two
findings:

- **F-001 fix (high):** `submitAppOnly()` only called
  `clearAppOnlySecretField()` after `await postJson(...)` resolved. Since
  `postJson()` doesn't catch a rejected `fetch()` (network down, connection
  refused, etc.), that rejection would propagate as an unhandled promise
  rejection and skip the clearing call entirely, leaving the secret in the
  DOM. Fixed by wrapping the request in `try { ... } catch (err) { ... }
  finally { clearAppOnlySecretField(); }` — the field is now cleared the
  instant the request settles, resolved or rejected, and a rejection now
  surfaces the same stable "app-only sign-in failed" status instead of an
  unhandled rejection. Added
  `test_secret_field_cleared_even_when_the_request_rejects`, which asserts
  the clearing call lives inside the `finally` block specifically (not
  merely present somewhere after a bare `await`).
- **F-002 fix (medium):** the round-0 manual walkthrough's submit step used
  a tenant/client ID with no real backing app registration, so it was
  *expected* to fail — it never exercised the successful-submit checkpoint
  acceptance criterion 9 requires (form hides, "signed in" status, and,
  implicitly, the secret still clears on the success path too). Rather
  than attempt a live tenant sign-in (a protected action, and out of
  scope), Claude wrote a small local-only helper script
  (`/private/tmp/.../scratchpad/mock_app_only_server.py`, not part of the
  repository) that starts the real `server.py` with `AUTH`'s transport and
  `GRAPH` replaced by in-process mocks returning a synthetic success —
  no outbound network call, no live credentials, nothing beyond what the
  existing test suite's own mock-transport pattern already does, just
  driven through a real browser instead of `unittest`. The human repeated
  the walkthrough against this mock-success server: filled in a synthetic
  tenant/client ID/secret, submitted, and confirmed the sign-in succeeded
  (status changed to "signed in (app-only)", the app-only form hid) with
  the secret field empty immediately after and nothing in console/storage.
  Reported verbatim: "no looks all goood" (in response to "is the secret
  input's value empty immediately after? Anything with
  `fake-secret-walkthrough-456` in Console or Storage?" — i.e. confirming
  no).
- Rechecked after both fixes: `python3 -m unittest discover -s tests` →
  173 passed, exit 0; `python3 -m py_compile $(git ls-files '*.py')` →
  exit 0; `python3 scripts/validate_repo.py` → "Repository validation
  passed (67 required files checked)."
- This is round 1 of at most two permitted issue repair rounds.

### Manual walkthrough — full evidence (rounds 0 + 1 combined)

| Checkpoint | Method | Observed |
|---|---|---|
| Secret input attributes | Round 0, real server, no mock | `type="password"`, `autocomplete="off"` confirmed in Elements |
| Mode switch (both directions) | Round 0, real server | Secret field empty after switching away and back |
| Submit — failure path (invalid/no real tenant) | Round 0, real server | Secret field empty immediately after; nothing in console/storage |
| Submit — success path | Round 1, local mock-success server (no live network/credentials) | Sign-in succeeded (status "signed in (app-only)", form hidden); secret field empty immediately after; nothing in console/storage |
| Logout | Round 0, real server | Secret field empty after triggering logout |

All five checkpoints required by acceptance criterion 9 (submit — both
outcomes, mode switch, logout) are now covered.
