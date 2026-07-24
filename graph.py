"""Microsoft Graph client for Conditional Access policies (ISSUE-0003).

Fetches the tenant's Conditional Access policies read-only, follows paging, and
normalizes each policy into the stable internal data contract the analyzer
(ISSUE-0004) and UI (ISSUE-0005) consume. Transport-injectable so paging and
normalization are unit-tested without any network or live tenant.

A3 resolution (recorded here and in the ISSUE-0003 handoff): the MVP calls only
the ``conditionalAccess/policies`` endpoint. Policies reference users, groups,
roles, applications, and named locations by identifier; the analyzer matches those
identifiers (e.g. built-in admin role template IDs) without extra Graph calls, so
no named-location or directory-role lookups are made in the MVP. Adding such
enrichment would be a separate issue.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

GRAPH_POLICIES_URL = "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies"

# Transport takes (url, headers) and returns (status, parsed_json).
Transport = Callable[[str, "dict[str, str]"], "tuple[int, dict]"]


class GraphError(Exception):
    """A Graph request failed; ``code`` is a stable machine label for the UI."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def urllib_graph_transport(url: str, headers: dict[str, str]) -> tuple[int, dict]:
    """Default transport: GET ``url`` with ``headers``; never raises.

    Only Microsoft Graph URLs are ever passed here by the client.
    """
    request = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 (fixed host)
            raw = response.read().decode("utf-8", "replace")
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, {"error": "network_error"}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return status, {"error": "bad_response"}
    return status, (payload if isinstance(payload, dict) else {"error": "bad_response"})


def _str_list(value: object) -> list[str]:
    """Coerce a Graph array of strings into a clean list of strings."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def normalize_policy(raw: dict) -> dict:
    """Reduce a raw Graph CA policy to the internal data contract."""
    conditions = raw.get("conditions") or {}
    users = conditions.get("users") or {}
    apps = conditions.get("applications") or {}
    locations = conditions.get("locations") or {}
    platforms = conditions.get("platforms") or {}
    grant = raw.get("grantControls") or {}
    session = raw.get("sessionControls") or {}

    # Which session controls are present/enabled (Graph nests each as an object).
    session_controls = [
        name
        for name in (
            "signInFrequency",
            "persistentBrowser",
            "cloudAppSecurity",
            "applicationEnforcedRestrictions",
            "continuousAccessEvaluation",
        )
        if isinstance(session.get(name), dict)
    ]

    return {
        "id": raw.get("id", ""),
        "displayName": raw.get("displayName", ""),
        "state": raw.get("state", ""),
        "conditions": {
            "includeUsers": _str_list(users.get("includeUsers")),
            "excludeUsers": _str_list(users.get("excludeUsers")),
            "includeGroups": _str_list(users.get("includeGroups")),
            "excludeGroups": _str_list(users.get("excludeGroups")),
            "includeRoles": _str_list(users.get("includeRoles")),
            "excludeRoles": _str_list(users.get("excludeRoles")),
            "includeApplications": _str_list(apps.get("includeApplications")),
            "excludeApplications": _str_list(apps.get("excludeApplications")),
            "clientAppTypes": _str_list(conditions.get("clientAppTypes")),
            "includePlatforms": _str_list(platforms.get("includePlatforms")),
            "excludePlatforms": _str_list(platforms.get("excludePlatforms")),
            "includeLocations": _str_list(locations.get("includeLocations")),
            "excludeLocations": _str_list(locations.get("excludeLocations")),
            "signInRiskLevels": _str_list(conditions.get("signInRiskLevels")),
            "userRiskLevels": _str_list(conditions.get("userRiskLevels")),
        },
        "grantControls": {
            "operator": grant.get("operator") or "",
            "builtInControls": _str_list(grant.get("builtInControls")),
        },
        "sessionControls": session_controls,
    }


class GraphClient:
    """Read-only Microsoft Graph client for Conditional Access policies."""

    def __init__(self, *, transport: Transport | None = None) -> None:
        self._transport: Transport = transport or urllib_graph_transport

    def fetch_policies(self, token: str) -> list[dict]:
        """Return all normalized CA policies, following ``@odata.nextLink``.

        Raises ``GraphError`` with a stable ``code`` for auth/consent/other
        failures so the caller can present a clear message.
        """
        if not token:
            raise GraphError("not_authenticated", "no access token")
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        policies: list[dict] = []
        url: str | None = GRAPH_POLICIES_URL
        seen = 0
        while url:
            status, payload = self._transport(url, headers)
            if status == 401:
                raise GraphError("not_authenticated", "token rejected")
            if status == 403:
                raise GraphError("consent_required", "admin consent to Policy.Read.All required")
            if status != 200:
                raise GraphError("graph_error", str(payload.get("error", "graph request failed"))[:200])
            for raw in payload.get("value", []):
                if isinstance(raw, dict):
                    policies.append(normalize_policy(raw))
            next_link = payload.get("@odata.nextLink")
            url = next_link if isinstance(next_link, str) else None
            # Defensive bound against a pathological paging loop.
            seen += 1
            if seen > 1000:
                break
        return policies
