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
        self.assertLess(result["score"], 20)  # only the "no overly-broad block" rule passes
        ids = {f["id"] for f in result["findings"]}
        self.assertIn("mfa-admins", ids)
        self.assertIn("not-all-report-only", ids)

    def test_overly_broad_block_flagged(self) -> None:
        lockout = graph.normalize_policy({
            "id": "x", "displayName": "Block everything", "state": "enabled",
            "conditions": {"users": {"includeUsers": ["All"]}, "applications": {"includeApplications": ["All"]}},
            "grantControls": {"builtInControls": ["block"]},
        })
        ids = {f["id"] for f in analyzer.analyze([lockout])["findings"]}
        self.assertIn("no-overly-broad-block", ids)

    def test_overly_broad_block_not_flagged_with_exclusion(self) -> None:
        ok = graph.normalize_policy({
            "id": "x", "displayName": "Block with exclusion", "state": "enabled",
            "conditions": {
                "users": {"includeUsers": ["All"], "excludeUsers": ["22222222-2222-2222-2222-222222222222"]},
                "applications": {"includeApplications": ["All"]},
            },
            "grantControls": {"builtInControls": ["block"]},
        })
        ids = {f["id"] for f in analyzer.analyze([ok])["findings"]}
        self.assertNotIn("no-overly-broad-block", ids)

    def test_break_glass_requires_exclusion_from_every_broad_policy(self) -> None:
        bg = ["11111111-1111-1111-1111-111111111111"]
        policies = load("strong_tenant.json")
        # All broad policies exclude the break-glass id → pass.
        result_pass = analyzer.analyze(policies, break_glass_ids=bg)
        self.assertNotIn("break-glass-excluded", {f["id"] for f in result_pass["findings"]})
        # Remove the exclusion from one broad policy → fail.
        for p in policies:
            if "11111111-1111-1111-1111-111111111111" in p["conditions"]["excludeUsers"] \
                    and "mfa" in [c.lower() for c in p["grantControls"]["builtInControls"]]:
                p["conditions"]["excludeUsers"] = []
                break
        result_fail = analyzer.analyze(policies, break_glass_ids=bg)
        self.assertIn("break-glass-excluded", {f["id"] for f in result_fail["findings"]})

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

    def test_mfa_admins_requires_full_role_coverage(self) -> None:
        # A single policy covering only ONE admin role must not overstate
        # coverage as a full pass (Codex F-003).
        partial = graph.normalize_policy({
            "id": "x", "displayName": "MFA one role", "state": "enabled",
            "conditions": {"users": {"includeRoles": ["62e90394-69f5-4237-9190-012177145e10"]}},
            "grantControls": {"builtInControls": ["mfa"]},
        })
        ids = {f["id"] for f in analyzer.analyze([partial])["findings"]}
        self.assertIn("mfa-admins", ids)

    def test_mfa_all_users_group_exclusion_is_a_gap(self) -> None:
        # Excluding an entire group from all-user MFA is a material coverage
        # gap, unlike excluding a handful of individual break-glass users.
        gap = graph.normalize_policy({
            "id": "x", "displayName": "MFA all users minus a group", "state": "enabled",
            "conditions": {"users": {"includeUsers": ["All"], "excludeGroups": ["some-group"]}},
            "grantControls": {"builtInControls": ["mfa"]},
        })
        ids = {f["id"] for f in analyzer.analyze([gap])["findings"]}
        self.assertIn("mfa-all-users", ids)

    def test_mfa_all_users_individual_exclusion_ok(self) -> None:
        ok = graph.normalize_policy({
            "id": "x", "displayName": "MFA all users minus break-glass", "state": "enabled",
            "conditions": {"users": {"includeUsers": ["All"], "excludeUsers": ["bg-id"]}},
            "grantControls": {"builtInControls": ["mfa"]},
        })
        ids = {f["id"] for f in analyzer.analyze([ok])["findings"]}
        self.assertNotIn("mfa-all-users", ids)

    def test_every_rule_has_metadata(self) -> None:
        for rule in rules.RULES:
            self.assertIn(rule.severity, {"critical", "high", "medium", "low", "info"})
            self.assertGreater(rule.weight, 0)
            self.assertTrue(rule.remediation)
            self.assertTrue(rule.requires)

    def test_generic_requires_enforcement_triggers_for_bad_declaration(self) -> None:
        """Proves _missing_requirements is a real, generic check (Codex F-002),
        not dead code: a rule declaring a field the contract doesn't have is
        correctly reported not_evaluable."""
        bogus = rules.Rule(
            "bogus-rule", "Bogus", "low", 1, "x", "x",
            ["conditions.thisFieldDoesNotExist"],  # top-level exists, nested segment does not
            lambda policies, ctx: (rules.PASS, []),
        )
        self.assertEqual(
            analyzer._missing_requirements(bogus, {}), ["conditions.thisFieldDoesNotExist"]
        )

        real_nested = rules.Rule(
            "real-nested-rule", "Real nested", "low", 1, "x", "x",
            ["conditions.includeRoles"],  # a genuinely valid nested path
            lambda policies, ctx: (rules.PASS, []),
        )
        self.assertEqual(analyzer._missing_requirements(real_nested, {}), [])

        bogus2 = rules.Rule(
            "bogus-rule-2", "Bogus 2", "low", 1, "x", "x",
            ["notARealTopLevelField"],
            lambda policies, ctx: (rules.PASS, []),
        )
        self.assertEqual(analyzer._missing_requirements(bogus2, {}), ["notARealTopLevelField"])

    def test_generic_requires_enforcement_gates_external_input(self) -> None:
        rule = next(r for r in rules.RULES if r.id == "break-glass-excluded")
        self.assertEqual(analyzer._missing_requirements(rule, {"break_glass_ids": []}), ["break_glass_ids"])
        self.assertEqual(analyzer._missing_requirements(rule, {"break_glass_ids": ["x"]}), [])

    def test_requires_policy_fields_are_never_missing(self) -> None:
        """Documents the evaluability model (rules.py, Codex F-001/F-002):
        every policy-JSON field path any rule declares in `requires` is
        guaranteed present (possibly empty) by `graph.normalize_policy`, even for
        a maximally malformed input. Only `rules.EXTERNAL_INPUTS` entries (never
        produced by normalize_policy) can be genuinely absent, which is exactly
        what `analyzer.analyze` gates on.
        """
        for rule in rules.RULES:
            for field_path in rule.requires:
                if field_path in rules.EXTERNAL_INPUTS:
                    continue
                self.assertTrue(
                    analyzer._field_declared_in_contract(field_path),
                    f"{rule.id} declares policy field {field_path!r}, "
                    "but normalize_policy does not guarantee the full nested path",
                )


if __name__ == "__main__":
    unittest.main()
