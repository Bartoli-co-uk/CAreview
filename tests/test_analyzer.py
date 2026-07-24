"""Tests for the analyzer + rule set (ISSUE-0004).

Fixtures are sanitized raw Graph policies; each test normalizes them through
``graph.normalize_policy`` and then analyzes, exercising the full pipeline
offline with no network.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import analyzer  # noqa: E402
import graph  # noqa: E402
import rules  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load(name: str) -> list[dict]:
    raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return [graph.normalize_policy(p) for p in raw]


class AnalyzerTests(unittest.TestCase):
    def test_strong_tenant_scores_high(self) -> None:
        result = analyzer.analyze(load("strong_tenant.json"))
        self.assertEqual(result["score"], 100)  # all evaluable rules pass
        self.assertEqual(result["findings"], [])
        self.assertIn("break-glass-excluded", result["notEvaluable"])
        self.assertTrue(result["scoreIsHeuristic"])

    def test_weak_tenant_scores_low(self) -> None:
        result = analyzer.analyze(load("weak_tenant.json"))
        self.assertEqual(result["score"], 0)
        ids = {f["id"] for f in result["findings"]}
        self.assertIn("mfa-admins", ids)
        self.assertIn("not-all-report-only", ids)

    def test_findings_sorted_by_severity(self) -> None:
        result = analyzer.analyze(load("weak_tenant.json"))
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        severities = [order[f["severity"]] for f in result["findings"]]
        self.assertEqual(severities, sorted(severities))

    def test_incomplete_tenant_marks_not_evaluable(self) -> None:
        result = analyzer.analyze(load("incomplete_tenant.json"))
        # No policies at all: the "enforced policy" and break-glass rules cannot
        # be judged and must be not-evaluable rather than pass/fail.
        self.assertIn("not-all-report-only", result["notEvaluable"])
        self.assertIn("break-glass-excluded", result["notEvaluable"])

    def test_break_glass_evaluable_with_ids(self) -> None:
        bg = ["11111111-1111-1111-1111-111111111111"]
        result = analyzer.analyze(load("strong_tenant.json"), break_glass_ids=bg)
        self.assertNotIn("break-glass-excluded", result["notEvaluable"])
        self.assertEqual(result["score"], 100)  # break-glass rule also passes

    def test_break_glass_fail_when_not_excluded(self) -> None:
        # A break-glass ID that is NOT excluded anywhere → the rule fails.
        result = analyzer.analyze(load("strong_tenant.json"),
                                  break_glass_ids=["99999999-9999-9999-9999-999999999999"])
        ids = {f["id"] for f in result["findings"]}
        self.assertIn("break-glass-excluded", ids)
        self.assertLess(result["score"], 100)

    def test_deterministic(self) -> None:
        a = analyzer.analyze(load("strong_tenant.json"))
        b = analyzer.analyze(load("strong_tenant.json"))
        self.assertEqual(a, b)

    def test_every_rule_has_metadata(self) -> None:
        for rule in rules.RULES:
            self.assertIn(rule.severity, {"critical", "high", "medium", "low", "info"})
            self.assertGreater(rule.weight, 0)
            self.assertTrue(rule.remediation)
            self.assertTrue(rule.requires)


if __name__ == "__main__":
    unittest.main()
