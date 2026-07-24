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

# Reference shape used to generically validate every `Rule.requires` entry
# (Codex F-002): the empty-input normalization is the contract's own guarantee
# of which top-level keys always exist. Built once at import time.
_REFERENCE_POLICY = graph.normalize_policy({})


def _field_declared_in_contract(field_path: str) -> bool:
    """True when ``field_path``'s top-level key exists in the normalized
    policy contract (per ``graph.normalize_policy``), i.e. it can never be
    absent on a real policy — only empty."""
    top = field_path.split(".", 1)[0]
    return top in _REFERENCE_POLICY


def _missing_requirements(rule: rules.Rule, ctx: dict) -> list[str]:
    """Generically enforce every declared requirement in ``rule.requires``.

    - External inputs (``rules.EXTERNAL_INPUTS``, e.g. ``break_glass_ids``) are
      missing when the caller did not supply them in ``ctx``.
    - Policy-JSON field paths are validated against the normalized contract's
      guaranteed shape (`_REFERENCE_POLICY`): every one of them is always
      present there, so this branch enforces the declaration without ever
      spuriously blocking a rule — the guarantee is proven for every rule by
      ``tests/test_analyzer.py::test_requires_policy_fields_are_never_missing``.
    """
    missing: list[str] = []
    for field_path in rule.requires:
        if field_path in rules.EXTERNAL_INPUTS:
            if not ctx.get(field_path):
                missing.append(field_path)
        elif not _field_declared_in_contract(field_path):
            missing.append(field_path)  # would indicate a stale/incorrect declaration
    return missing


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
        # Enforce EVERY declared requirement generically (Codex F-001/F-002):
        # external inputs missing from ctx, or a policy-field declaration that
        # (contrary to the contract's guarantee) is not part of the normalized
        # shape. See `_missing_requirements` for why policy-field entries never
        # actually trigger this in practice.
        if _missing_requirements(rule, ctx):
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
