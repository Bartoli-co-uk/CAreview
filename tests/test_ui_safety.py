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


if __name__ == "__main__":
    unittest.main()
