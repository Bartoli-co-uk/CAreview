"""Static safety checks for the UI (ISSUE-0005, Codex F-003; updated for the
React/Vite frontend introduced in DECISION-0NN).

The project is stdlib-only on the Python side with no browser/DOM automation
available here, so this cannot execute JavaScript to assert rendered text is
inert. Instead it (1) statically proves the frontend source never uses a sink
that could turn untrusted data into executable markup, (2) proves the
committed sample data contains a hostile-markup regression case, and (3)
mirrors the app-only sign-in safety checks that used to target the vanilla
web/app.js against their new home in frontend/src. Equivalent, deeper checks
also run as Vitest tests under frontend/src/test/ (npm test) — this file is
the defense-in-depth copy that runs even when Node isn't available, via
`python3 -m unittest discover -s tests`.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_SRC = ROOT / "frontend" / "src"
SIGNIN_TSX = (FRONTEND_SRC / "pages" / "SignIn.tsx").read_text(encoding="utf-8")
APP_STATE_TSX = (FRONTEND_SRC / "state" / "appState.tsx").read_text(encoding="utf-8")
API_CLIENT_TS = (FRONTEND_SRC / "api" / "client.ts").read_text(encoding="utf-8")
APP_TSX = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
FRONTEND_INDEX_HTML = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")

# Sinks that would let untrusted data become executable markup or code.
_DANGEROUS_SINKS = (
    "dangerouslySetInnerHTML", "innerHTML", "outerHTML", "insertAdjacentHTML",
    "document.write", "eval(", "new Function(",
)
_STORAGE_SINKS = ("localStorage", "sessionStorage", "document.cookie")

HOSTILE_MARKER = "<img src=x onerror=alert(1)>"


def _all_frontend_source_files() -> list[Path]:
    return [
        p
        for p in FRONTEND_SRC.rglob("*")
        if p.is_file() and p.suffix in (".ts", ".tsx") and "test" not in p.parts
    ]


def _function_body(source: str, signature: str, length: int = 800) -> str:
    start = source.index(signature)
    return source[start:start + length]


class FrontendSourceSafetyTests(unittest.TestCase):
    """JSX auto-escapes text content by default (no innerHTML-equivalent
    sink), so the "untrusted tenant strings never become markup" property
    holds structurally as long as none of these sinks are introduced — this
    proves their absence across the whole frontend source tree, not just the
    sign-in form."""

    def test_no_dangerous_dom_sinks_anywhere_in_frontend_src(self) -> None:
        files = _all_frontend_source_files()
        self.assertGreater(len(files), 10, "expected to find frontend source files")
        for path in files:
            content = path.read_text(encoding="utf-8")
            for sink in _DANGEROUS_SINKS:
                self.assertNotIn(sink, content, f"{path} must not use {sink!r}")

    def test_no_storage_or_cookie_access_anywhere_in_frontend_src(self) -> None:
        for path in _all_frontend_source_files():
            content = path.read_text(encoding="utf-8")
            for sink in _STORAGE_SINKS:
                self.assertNotIn(sink, content, f"{path} must not use {sink!r}")


class SampleDataHostileFixtureTests(unittest.TestCase):
    """A hostile display name is present in the committed sample so a human
    opening the sample-data view can visually confirm (recorded as manual
    verification in the ISSUE-0005 handoff, still applicable to the React UI)
    that it renders as inert text, never as markup or a triggered handler."""

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
    """Static checks for the app-only sign-in toggle/form, updated for the
    React SignIn page (frontend/src/pages/SignIn.tsx) that replaced
    web/app.js's imperative DOM toggling."""

    def test_default_view_is_device_code(self) -> None:
        self.assertIn('useState(false)', SIGNIN_TSX.split("showAppOnly")[1][:40])

    def test_secret_input_is_password_with_autocomplete_off(self) -> None:
        start = SIGNIN_TSX.index('type="password"')
        block = SIGNIN_TSX[start:start + 200]
        self.assertIn('autoComplete="off"', block)

    def test_caution_text_present(self) -> None:
        self.assertIn('caution-text', SIGNIN_TSX)
        caution_start = SIGNIN_TSX.index('caution-text')
        caution_text = SIGNIN_TSX[caution_start:caution_start + 400]
        self.assertIn("grants", caution_text)
        self.assertIn("password", caution_text)

    def test_client_side_tenant_alias_rejection_mirrors_server(self) -> None:
        start = SIGNIN_TSX.index("APP_ONLY_DISALLOWED_TENANTS")
        block = SIGNIN_TSX[start:start + 200]
        for alias in ("organizations", "common", "consumers"):
            self.assertIn(alias, block)

    def test_secret_field_cleared_on_submit_success_path(self) -> None:
        body = _function_body(SIGNIN_TSX, "async function submitAppOnly", length=1600)
        self.assertIn("clearAppOnlySecretField()", body)

    def test_secret_field_cleared_even_when_the_request_rejects(self) -> None:
        # The clearing call must live inside a `finally` block wrapped around
        # the request, not merely after a bare `await`, so it runs whether
        # the promise resolves or rejects (Codex F-001, still applicable).
        body = _function_body(SIGNIN_TSX, "async function submitAppOnly", length=2000)
        self.assertIn("try {", body)
        self.assertIn("} finally", body)
        finally_start = body.index("} finally")
        finally_block = body[finally_start:finally_start + 300]
        self.assertIn("clearAppOnlySecretField()", finally_block)

    def test_secret_field_cleared_on_mode_switch_both_directions(self) -> None:
        to_app_only = _function_body(SIGNIN_TSX, "function switchToAppOnly")
        self.assertIn("clearAppOnlySecretField()", to_app_only)
        to_device_code = _function_body(SIGNIN_TSX, "function switchToDeviceCode")
        self.assertIn("clearAppOnlySecretField()", to_device_code)

    def test_signin_only_rendered_while_signed_out_so_secret_state_is_discarded_on_signout(self) -> None:
        # There is no separate "clear on logout" call to make in SignIn.tsx:
        # App.tsx only mounts <SignIn/> while mode === "signedOut", so
        # signing out unmounts the component and its local secret state with
        # it, rather than leaving a stale form around to explicitly clear.
        self.assertIn('mode === "signedOut"', APP_TSX)
        self.assertIn("<SignIn", APP_TSX)

    def test_secret_never_reaches_console_storage_or_cookies(self) -> None:
        for sink in ("console.",) + _STORAGE_SINKS:
            self.assertNotIn(sink, SIGNIN_TSX, f"SignIn.tsx must not use {sink!r}")

    def test_secret_sent_only_as_json_body_not_url_or_query_string(self) -> None:
        # api/client.ts's authAppOnly() is the sole place the secret leaves
        # the browser; it must go through postJson's JSON body, never a URL.
        start = API_CLIENT_TS.index("export async function authAppOnly")
        body = API_CLIENT_TS[start:start + 600]
        self.assertIn("postJson<AuthAppOnlyResponse | AuthErrorResponse>(\"/api/auth/app\"", body)
        self.assertNotIn("clientSecret +", body)
        self.assertNotIn("+ clientSecret", body)
        self.assertNotIn("?", body[: body.index("client_secret")])

    def test_csp_meta_unchanged(self) -> None:
        self.assertIn(
            "default-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'",
            FRONTEND_INDEX_HTML,
        )


class ResultsLoadRaceGuardTests(unittest.TestCase):
    """Codex F-001 (round 1): stale async loads must not restore/retain
    analysis after sign-out or a newer load. The React port moved this guard
    from a module-level counter in app.js to a useRef counter in
    state/appState.tsx; proves the same invariant holds there."""

    def test_generation_guard_present(self) -> None:
        self.assertIn("generation.current", APP_STATE_TSX)
        self.assertIn("myGeneration !== generation.current", APP_STATE_TSX)

    def test_signout_clears_state_before_the_network_round_trip(self) -> None:
        signout_start = APP_STATE_TSX.index("const signOut = useCallback")
        signout_body = APP_STATE_TSX[signout_start:signout_start + 500]
        self.assertIn("setPolicies([])", signout_body)
        self.assertIn("setAnalysis(null)", signout_body)
        clear_index = signout_body.index("setPolicies([])")
        await_index = signout_body.index("await authLogout()")
        self.assertLess(clear_index, await_index, "state must be cleared before the logout network call")


if __name__ == "__main__":
    unittest.main()
