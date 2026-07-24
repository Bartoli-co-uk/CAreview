"""Conditional Access analyzer (ISSUE-0004).

Runs the declarative rule set over normalized CA policies and produces a
heuristic 0-100 security score plus a severity-sorted list of findings. The score
is the evaluable-weighted fraction of rules that pass; rules whose required
evidence is absent are *not evaluable* and excluded from both the numerator and
the denominator, so missing evidence is never scored as pass or fail.
"""

from __future__ import annotations

import graph
import rules

# Severity ordering for sorting findings (most severe first).
_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def analyze(policies: list[dict], break_glass_ids: list[str] | None = None) -> dict:
    """Analyze normalized CA ``policies`` and return score + findings.

    ``break_glass_ids`` is the optional local, user-supplied list of emergency
    account object IDs (sanitized to GUIDs); when absent the break-glass rule is
    not evaluable.
    """
    ctx = {"break_glass_ids": graph.sanitize_object_ids(break_glass_ids or [])}

    findings: list[dict] = []
    evaluated: list[dict] = []
    not_evaluable: list[str] = []
    passed_weight = 0
    evaluable_weight = 0

    for rule in rules.RULES:
        # Enforce declared EXTERNAL-input requirements (Codex F-001): a rule that
        # needs an input the caller did not supply (e.g. break-glass IDs) is not
        # evaluable and never scored, driven by its `requires` declaration.
        missing_external = [
            key for key in rule.requires if key in rules.EXTERNAL_INPUTS and not ctx.get(key)
        ]
        if missing_external:
            status, affected = rules.NOT_EVALUABLE, []
        else:
            try:
                status, affected = rule.check(policies, ctx)
            except Exception:  # noqa: BLE001 — a rule bug must not crash the whole analysis
                status, affected = rules.NOT_EVALUABLE, []

        evaluated.append({"id": rule.id, "title": rule.title, "status": status})

        if status == rules.NOT_EVALUABLE:
            not_evaluable.append(rule.id)
            continue

        evaluable_weight += rule.weight
        if status == rules.PASS:
            passed_weight += rule.weight
        else:  # FAIL → a finding
            findings.append(
                {
                    "id": rule.id,
                    "title": rule.title,
                    "severity": rule.severity,
                    "weight": rule.weight,
                    "rationale": rule.rationale,
                    "remediation": rule.remediation,
                    "affectedPolicies": affected,
                }
            )

    score = round(100 * passed_weight / evaluable_weight) if evaluable_weight else 0
    findings.sort(key=lambda f: (_SEVERITY_ORDER.get(f["severity"], 9), f["id"]))

    return {
        "score": score,
        "scoreIsHeuristic": True,
        "policyCount": len(policies),
        "findings": findings,
        "evaluated": evaluated,
        "notEvaluable": not_evaluable,
    }
