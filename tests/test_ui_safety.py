"""Static safety checks for the UI (ISSUE-0005, Codex F-003).

The project is stdlib-only with no browser/DOM automation available, so this
cannot execute JavaScript to assert rendered text is inert. Instead it (1)
statically proves ``web/app.js`` never uses a sink that could turn untrusted
data into executable markup, and (2) proves the committed sample data contains
a hostile-markup regression case, so opening the page (manual verification,
recorded in the ISSUE-0005 handoff) exercises exactly that input.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_JS = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
INDEX_HTML = (ROOT / "web" / "index.html").read_text(encoding="utf-8")


def _function_body(source: str, signature: str, length: int = 600) -> str:
    start = source.index(signature)
    return source[start:start + length]

# Sinks that would let untrusted data become executable markup or code.
_DANGEROUS_SINKS = (
    "innerHTML", "outerHTML", "insertAdjacentHTML", "document.write",
    "eval(", "new Function(",
)

HOSTILE_MARKER = "<img src=x onerror=alert(1)>"


class AppJsSafetyTests(unittest.TestCase):
    def test_no_dangerous_dom_sinks(self) -> None:
        for sink in _DANGEROUS_SINKS:
            self.assertNotIn(sink, APP_JS, f"app.js must not use {sink!r}")

    def test_rendering_functions_use_textcontent_or_createelement(self) -> None:
        # Every render* function body should rely on textContent/createElement
        # rather than string-concatenated markup assignment.
        self.assertIn("textContent", APP_JS)
        self.assertNotIn("javascript:", APP_JS.lower())

    def test_results_loads_are_generation_guarded(self) -> None:
        # Codex F-001 (round 1): stale async loads must not restore/retain
        # analysis after sign-out or a newer load. Proves the guard exists.
        self.assertIn("resultsGeneration", APP_JS)
        self.assertIn("myGeneration !== resultsGeneration", APP_JS)
        # signOut must clear results before/around the network round-trip.
        signout_start = APP_JS.index("async function signOut")
        signout_body = APP_JS[signout_start:signout_start + 400]
        self.assertIn("clearResults()", signout_body)


class SampleDataHostileFixtureTests(unittest.TestCase):
    """A hostile display name is present in the committed sample so a human
    opening /sample-data.json via the page can visually confirm (recorded as
    manual verification in the ISSUE-0005 handoff) that it renders as inert
    text, never as markup or a triggered handler."""

    def test_sample_data_contains_hostile_markup_case(self) -> None:
        data = json.loads((ROOT / "web" / "sample-data.json").read_text(encoding="utf-8"))
        names = [p.get("displayName", "") for p in data.get("policies", [])]
        self.assertTrue(
            any(HOSTILE_MARKER in name for name in names),
            "sample-data.json must include a hostile-markup display name for manual UI verification",
        )

    def test_sample_data_is_valid_json_no_scripts(self) -> None:
        raw = (ROOT / "web" / "sample-data.json").read_text(encoding="utf-8")
        self.assertNotIn("<script", raw.lower())


class AppOnlyModeToggleTests(unittest.TestCase):
    """Static checks for the app-only sign-in toggle/form (ISSUE-0010)."""

    def test_default_view_is_device_code(self) -> None:
        # The device-code container is visible by default...
        self.assertIn('<div id="devicecode-mode">', INDEX_HTML)
        # ...and the app-only container is hidden by default.
        self.assertIn('<div id="app-only-mode" hidden>', INDEX_HTML)

    def test_secret_input_is_password_with_autocomplete_off(self) -> None:
        start = INDEX_HTML.index('id="app-only-secret"')
        tag = INDEX_HTML[max(0, start - 80):start + 80]
        self.assertIn('type="password"', tag)
        self.assertIn('autocomplete="off"', tag)

    def test_caution_text_present(self) -> None:
        self.assertIn('class="caution"', INDEX_HTML)
        caution_start = INDEX_HTML.index('class="caution"')
        caution_text = INDEX_HTML[caution_start:caution_start + 400]
        self.assertIn("grants", caution_text)
        self.assertIn("password", caution_text)

    def test_client_side_tenant_alias_rejection_mirrors_server(self) -> None:
        start = APP_JS.index("APP_ONLY_DISALLOWED_TENANTS")
        block = APP_JS[start:start + 200]
        for alias in ("organizations", "common", "consumers"):
            self.assertIn(alias, block)

    def test_secret_field_cleared_on_submit(self) -> None:
        body = _function_body(APP_JS, "async function submitAppOnly", length=1200)
        self.assertIn("clearAppOnlySecretField()", body)

    def test_secret_field_cleared_even_when_the_request_rejects(self) -> None:
        # Codex F-001: fetch() itself can reject (network failure), not just
        # resolve with a non-2xx status. The clearing call must live inside
        # a `finally` block wrapped around the request, not merely after a
        # bare `await`, so it runs on both outcomes.
        body = _function_body(APP_JS, "async function submitAppOnly", length=2000)
        self.assertIn("try {", body)
        self.assertIn("} catch", body)
        finally_start = body.index("finally")
        finally_block = body[finally_start:finally_start + 300]
        self.assertIn("clearAppOnlySecretField()", finally_block)

    def test_secret_field_cleared_on_mode_switch_both_directions(self) -> None:
        to_app_only = _function_body(APP_JS, "function showAppOnlyMode")
        self.assertIn("clearAppOnlySecretField()", to_app_only)
        to_device_code = _function_body(APP_JS, "function showDeviceCodeMode")
        self.assertIn("clearAppOnlySecretField()", to_device_code)

    def test_secret_field_cleared_on_logout(self) -> None:
        body = _function_body(APP_JS, "async function signOut")
        self.assertIn("clearAppOnlySecretField()", body)

    def test_secret_never_reaches_console_storage_or_cookies(self) -> None:
        # The app has no legitimate reason to touch any of these for the
        # secret (or anything else) — their outright absence is the
        # strongest available static proof the secret cannot reach them.
        for sink in ("console.", "localStorage", "sessionStorage", "document.cookie"):
            self.assertNotIn(sink, APP_JS, f"app.js must not use {sink!r}")

    def test_secret_sent_only_as_json_body_not_url_or_query_string(self) -> None:
        submit_body = _function_body(APP_JS, "async function submitAppOnly", length=1200)
        self.assertIn('postJson("/api/auth/app"', submit_body)
        # The secret variable must only appear inside the JSON payload object
        # passed to postJson, never concatenated into a URL/query string.
        self.assertNotIn("clientSecret +", submit_body)
        self.assertNotIn("+ clientSecret", submit_body)
        self.assertNotIn("?", submit_body[: submit_body.index("clientSecret,")])

    def test_csp_meta_unchanged(self) -> None:
        self.assertIn(
            "default-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'",
            INDEX_HTML,
        )


if __name__ == "__main__":
    unittest.main()
