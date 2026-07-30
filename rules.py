"""Conditional Access analysis rules (ISSUE-0004).

A declarative, data-driven starter rule set. Each rule declares a stable id,
title, severity, weight, remediation, the data-contract fields it requires, and a
``check`` that returns one of ``"pass"``, ``"fail"``, or ``"not_evaluable"`` plus
the affected policy display names. A rule whose required evidence is absent is
reported *not evaluable* and excluded from scoring — never counted as pass or
fail. The score (ISSUE-0004) is a documented heuristic, not a compliance measure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

# Well-known Entra built-in *admin* role template IDs (stable GUIDs). Matching
# these lets the "MFA for admins" rule work without a directory-role lookup.
ADMIN_ROLE_TEMPLATE_IDS = {
    "62e90394-69f5-4237-9190-012177145e10",  # Global Administrator
    "e8611ab8-c189-46e8-94e1-60213ab1f814",  # Privileged Role Administrator
    "7be44c8a-adaf-4e2a-84d6-ab2649e08a13",  # Privileged Authentication Administrator
    "194ae4cb-b126-40b2-bd5b-6091b380977d",  # Security Administrator
    "29232cdf-9323-42fd-ade2-1d097af3e4de",  # Exchange Administrator
    "f28a1f50-f6e7-4571-818b-6a12f2af6b6c",  # SharePoint Administrator
    "158c047a-c907-4556-b7ef-446551a6b5f7",  # Cloud Application Administrator
    "966707d0-3269-4727-9be2-8c3a10f19b9d",  # Password Administrator
    "b0f54661-2d74-4c50-afa3-1ec803f12efe",  # Billing Administrator
}

PASS = "pass"
FAIL = "fail"
NOT_EVALUABLE = "not_evaluable"

CheckResult = "tuple[str, list[str]]"


@dataclass
class Rule:
    id: str
    title: str
    severity: str  # critical | high | medium | low | info
    weight: int
    rationale: str
    remediation: str
    requires: list[str]
    check: Callable[[list[dict], dict], "tuple[str, list[str]]"]


# --- helpers ---------------------------------------------------------------

def _enabled(policy: dict) -> bool:
    return policy.get("state") == "enabled"


def _grant_controls(policy: dict) -> set[str]:
    grant = policy.get("grantControls") or {}
    return {c.lower() for c in grant.get("builtInControls", []) if isinstance(c, str)}


def _cond(policy: dict) -> dict:
    return policy.get("conditions") or {}


def _names(policies: list[dict]) -> list[str]:
    return [p.get("displayName") or p.get("id", "(unnamed)") for p in policies]


def _any(policies: list[dict], predicate: Callable[[dict], bool]) -> list[dict]:
    return [p for p in policies if predicate(p)]


# --- rule checks -----------------------------------------------------------

def _check_block_legacy_auth(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    legacy = {"exchangeactivesync", "other"}
    hits = _any(
        policies,
        lambda p: _enabled(p)
        and "block" in _grant_controls(p)
        and legacy.intersection({c.lower() for c in _cond(p).get("clientAppTypes", [])}),
    )
    return (PASS, _names(hits)) if hits else (FAIL, [])


def _check_mfa_for_admins(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    # A single policy covering one admin role is not enough: require the UNION
    # of enabled MFA policies' includeRoles to cover EVERY documented admin role
    # template (Codex F-003) — a single narrow policy must not overstate coverage.
    mfa_policies = _any(policies, lambda p: _enabled(p) and "mfa" in _grant_controls(p))
    covered: set[str] = set()
    for p in mfa_policies:
        covered |= ADMIN_ROLE_TEMPLATE_IDS.intersection(_cond(p).get("includeRoles", []))
    if covered == ADMIN_ROLE_TEMPLATE_IDS:
        hits = [p for p in mfa_policies if ADMIN_ROLE_TEMPLATE_IDS.intersection(_cond(p).get("includeRoles", []))]
        return PASS, _names(hits)
    return FAIL, _names(mfa_policies) if mfa_policies else []


def _check_mfa_for_all_users(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    # "All users" coverage is undermined by excluding an entire GROUP or ROLE
    # (a material population), not by excluding a handful of individual users
    # (the normal break-glass pattern). Only individual-user exclusions are
    # tolerated (Codex F-003).
    hits = _any(
        policies,
        lambda p: _enabled(p)
        and "mfa" in _grant_controls(p)
        and "All" in _cond(p).get("includeUsers", [])
        and not _cond(p).get("excludeGroups")
        and not _cond(p).get("excludeRoles"),
    )
    return (PASS, _names(hits)) if hits else (FAIL, [])


def _check_device_compliance(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    controls = {"compliantdevice", "domainjoineddevice"}
    hits = _any(policies, lambda p: _enabled(p) and controls.intersection(_grant_controls(p)))
    return (PASS, _names(hits)) if hits else (FAIL, [])


def _check_signin_risk(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    hits = _any(policies, lambda p: _enabled(p) and _cond(p).get("signInRiskLevels"))
    return (PASS, _names(hits)) if hits else (FAIL, [])


def _check_user_risk(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    hits = _any(policies, lambda p: _enabled(p) and _cond(p).get("userRiskLevels"))
    return (PASS, _names(hits)) if hits else (FAIL, [])


def _check_session_controls(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    hits = _any(policies, lambda p: _enabled(p) and p.get("sessionControls"))
    return (PASS, _names(hits)) if hits else (FAIL, [])


def _check_not_all_report_only(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    # If there are policies but none is enabled, the tenant is running blind.
    if not policies:
        return NOT_EVALUABLE, []
    enabled = _any(policies, _enabled)
    return (PASS, []) if enabled else (FAIL, _names(policies))


def _broad_lockout_policies(policies: list[dict]) -> list[dict]:
    """Enabled all-user policies that enforce MFA or block (potential lockout)."""
    return _any(
        policies,
        lambda p: _enabled(p)
        and "All" in _cond(p).get("includeUsers", [])
        and ({"mfa", "block"} & _grant_controls(p)),
    )


def _check_break_glass_excluded(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    # Requires the external break-glass input; the analyzer marks this rule
    # not-evaluable (via `requires`) when the input is absent, so an empty id list
    # here means "no applicable broad policy to check".
    ids = ctx.get("break_glass_ids") or []
    id_set = set(ids)
    broad = _broad_lockout_policies(policies)
    if not broad:
        return NOT_EVALUABLE, []
    # Every break-glass account must be excluded from EVERY applicable broad
    # lockout policy, or an emergency-access account could be locked out. Report
    # the non-compliant policies (never the account identifiers).
    noncompliant = [
        p for p in broad if not id_set.issubset(set(_cond(p).get("excludeUsers", [])))
    ]
    return (PASS, _names(broad)) if not noncompliant else (FAIL, _names(noncompliant))


def _check_location_restriction(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    # Presence only: does any enabled policy condition on a specific named
    # location at all, beyond the default "All"/"AllTrusted" sentinels? This
    # deliberately does not resolve location GUIDs to friendly names or
    # countries (would need the separate namedLocations Graph endpoint).
    default_sentinels = {"all", "alltrusted"}

    def has_location_condition(p: dict) -> bool:
        c = _cond(p)
        locations = {loc.lower() for loc in c.get("includeLocations", [])} | {
            loc.lower() for loc in c.get("excludeLocations", [])
        }
        return bool(locations - default_sentinels)

    hits = _any(policies, lambda p: _enabled(p) and has_location_condition(p))
    return (PASS, _names(hits)) if hits else (FAIL, [])


def _check_no_overly_broad_block(policies: list[dict], ctx: dict) -> tuple[str, list[str]]:
    # An enabled "all users + all apps + block" policy with no exclusions can lock
    # the entire tenant out. Flag any such policy.
    def is_lockout(p: dict) -> bool:
        c = _cond(p)
        return (
            _enabled(p)
            and "block" in _grant_controls(p)
            and "All" in c.get("includeUsers", [])
            and "All" in c.get("includeApplications", [])
            and not c.get("excludeUsers")
            and not c.get("excludeGroups")
            and not c.get("excludeRoles")
        )

    hits = _any(policies, is_lockout)
    return (FAIL, _names(hits)) if hits else (PASS, [])


RULES: list[Rule] = [
    Rule(
        "block-legacy-auth", "Legacy authentication is blocked", "high", 20,
        "Legacy authentication protocols bypass MFA and are a top account-takeover vector.",
        "Create an enabled policy that blocks legacy authentication client apps.",
        ["state", "grantControls", "conditions.clientAppTypes"], _check_block_legacy_auth,
    ),
    Rule(
        "mfa-admins", "MFA is required for administrators", "high", 20,
        "Privileged roles are high-value targets and must always require MFA.",
        "Create an enabled policy targeting admin roles that requires MFA.",
        ["state", "grantControls", "conditions.includeRoles"], _check_mfa_for_admins,
    ),
    Rule(
        "mfa-all-users", "MFA is required for all users", "high", 15,
        "Broad MFA coverage sharply reduces account compromise.",
        "Create an enabled all-users policy that requires MFA (with break-glass exclusions).",
        ["state", "grantControls", "conditions.includeUsers"], _check_mfa_for_all_users,
    ),
    Rule(
        "device-compliance", "Device compliance or hybrid join is required", "medium", 10,
        "Requiring managed/compliant devices limits access from unmanaged endpoints.",
        "Add a policy requiring a compliant or hybrid-joined device for sensitive access.",
        ["state", "grantControls"], _check_device_compliance,
    ),
    Rule(
        "signin-risk", "A sign-in risk policy is present", "medium", 10,
        "Sign-in risk policies respond to risky authentications in real time.",
        "Add an enabled policy conditioned on sign-in risk levels.",
        ["state", "conditions.signInRiskLevels"], _check_signin_risk,
    ),
    Rule(
        "user-risk", "A user risk policy is present", "medium", 10,
        "User risk policies force remediation (e.g. password change) for risky users.",
        "Add an enabled policy conditioned on user risk levels.",
        ["state", "conditions.userRiskLevels"], _check_user_risk,
    ),
    Rule(
        "session-controls", "Session controls are in use", "low", 5,
        "Session controls (sign-in frequency, persistent browser) limit stale sessions.",
        "Add session controls to sensitive-access policies.",
        ["state", "sessionControls"], _check_session_controls,
    ),
    Rule(
        "not-all-report-only", "At least one policy is enforced", "high", 10,
        "Report-only policies do not protect anything; some policy must be enabled.",
        "Move validated report-only policies to the enabled state.",
        ["state"], _check_not_all_report_only,
    ),
    Rule(
        "break-glass-excluded", "Break-glass accounts are excluded from lockout", "medium", 10,
        "A break-glass account excluded from every broad MFA/block policy prevents tenant lockout.",
        "Exclude your emergency-access accounts from all-user MFA/block policies (and monitor them).",
        ["conditions.excludeUsers", "break_glass_ids"], _check_break_glass_excluded,
    ),
    Rule(
        "no-overly-broad-block", "No all-users/all-apps block without exclusions", "high", 10,
        "An enabled all-users + all-apps block policy with no exclusions can lock the whole tenant out.",
        "Scope block policies narrowly or add break-glass/administrator exclusions.",
        ["state", "grantControls", "conditions.includeUsers", "conditions.includeApplications"],
        _check_no_overly_broad_block,
    ),
    Rule(
        "location-restriction-present", "At least one policy conditions on named locations", "medium", 10,
        "Geographic/network conditioning (e.g. blocking or requiring specific locations) narrows the "
        "attack surface for account compromise from unexpected networks.",
        "Add an enabled policy whose conditions include or exclude a specific named location "
        "(not just the default All/AllTrusted).",
        ["state", "conditions.includeLocations", "conditions.excludeLocations"],
        _check_location_restriction,
    ),
]

# --- Evaluability model (Codex F-001/F-002; approach confirmed by the human) ---
#
# `Rule.requires` lists two DIFFERENT kinds of dependency, and only one of them
# can ever be "missing" at runtime:
#
# 1. Policy-JSON field paths (e.g. "conditions.includeRoles", "grantControls").
#    `graph.normalize_policy` GUARANTEES every one of these keys exists on every
#    normalized policy (defaulted to "", [], or {} — see graph.py and
#    test_graph.py::test_normalize_handles_missing_fields /
#    test_normalize_handles_malformed_nested_objects). So a policy-field entry in
#    `requires` can never be "absent" post-normalization; it documents which
#    fields the rule reads, for humans, not a runtime gate. Generically enforcing
#    "is this field present" would therefore be a no-op by construction — the
#    field is always present, possibly empty. An EMPTY field (e.g. no policy sets
#    `includeRoles`) is not missing evidence: for Conditional Access, the tenant
#    genuinely lacks that control, which is exactly the FAIL the rule reports.
# 2. EXTERNAL inputs the caller must supply out-of-band (currently only
#    `break_glass_ids`, via POST /api/breakglass): these CAN be genuinely absent,
#    so the analyzer enforces them (`EXTERNAL_INPUTS` below) before running the
#    rule's check, marking it `NOT_EVALUABLE` rather than scoring a guess.
#
# This is why `analyzer.analyze` only gates on `EXTERNAL_INPUTS`, not on every
# `requires` entry: gating on policy-field entries would be unreachable dead code
# (see test_requires_policy_fields_are_never_missing below).
EXTERNAL_INPUTS = frozenset({"break_glass_ids"})
