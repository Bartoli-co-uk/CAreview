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
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

GRAPH_HOST = "graph.microsoft.com"
GRAPH_POLICIES_URL = f"https://{GRAPH_HOST}/v1.0/identity/conditionalAccess/policies"

# Upper bound on pages followed; a normal tenant has far fewer.
MAX_PAGES = 200

# Entra object-ID (GUID) shape, used to sanitize the optional break-glass input
# (part of the normalized data contract consumed by the analyzer, ISSUE-0004).
_GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

# Transport takes (url, headers) and returns (status, parsed_json).
Transport = Callable[[str, "dict[str, str]"], "tuple[int, dict]"]


class GraphError(Exception):
    """A Graph request failed; ``code`` is a stable machine label for the UI."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def is_graph_url(url: str) -> bool:
    """True only for an HTTPS URL whose host is exactly Microsoft Graph.

    The bearer token is attached to every request, so before trusting an initial
    or paged (``@odata.nextLink``) URL we require ``https`` and the exact Graph
    host with no embedded credentials — otherwise a crafted next link could
    exfiltrate the token to an arbitrary host.
    """
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.hostname is not None
        and parts.hostname.lower() == GRAPH_HOST
        and not parts.username
        and not parts.password
    )


def sanitize_object_ids(values: object) -> list[str]:
    """Keep only well-formed GUID strings from a list (break-glass input)."""
    if not isinstance(values, list):
        return []
    return [v for v in values if isinstance(v, str) and _GUID_RE.match(v)]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow HTTP redirects: a 3xx must not carry the bearer token to a
    new host. Graph paging uses ``@odata.nextLink`` in the body, not redirects."""

    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def urllib_graph_transport(url: str, headers: dict[str, str]) -> tuple[int, dict]:
    """Default transport: GET ``url`` with ``headers``; never raises, never
    follows redirects. The caller validates the host before calling this."""
    request = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with _OPENER.open(request, timeout=30) as response:  # noqa: S310 (host pre-validated)
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


def _control_enabled(obj: object) -> bool:
    """True when a Graph session-control object is enabled.

    Most controls carry ``isEnabled``; continuous access evaluation uses
    ``mode`` ("disabled" means off). A present object with neither field is
    treated as enabled.
    """
    if not isinstance(obj, dict):
        return False
    if "isEnabled" in obj:
        return obj.get("isEnabled") is True
    mode = obj.get("mode")
    if isinstance(mode, str):
        return mode.lower() != "disabled"
    return True


def _str_list(value: object) -> list[str]:
    """Coerce a Graph array of strings into a clean list of strings."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _as_dict(value: object) -> dict:
    """Return ``value`` if it is a dict, else an empty dict.

    Graph nested objects are attacker/tenant-influenced; a malformed non-dict
    (list, string, null) must not crash normalization.
    """
    return value if isinstance(value, dict) else {}


def normalize_policy(raw: object) -> dict:
    """Reduce a raw Graph CA policy to the internal data contract.

    Defensive against malformed nested objects: any field that is not the
    expected type is coerced to an empty default rather than raising.
    """
    raw = _as_dict(raw)
    conditions = _as_dict(raw.get("conditions"))
    users = _as_dict(conditions.get("users"))
    apps = _as_dict(conditions.get("applications"))
    locations = _as_dict(conditions.get("locations"))
    platforms = _as_dict(conditions.get("platforms"))
    grant = _as_dict(raw.get("grantControls"))
    session = _as_dict(raw.get("sessionControls"))

    # Which session controls are actually ENABLED. Graph nests each control as an
    # object that may carry ``isEnabled: false`` (present but off) or, for CAE, a
    # ``mode`` of "disabled"; treating mere presence as enabled would misreport
    # posture, so only enabled controls are listed.
    session_controls = [
        name
        for name in (
            "signInFrequency",
            "persistentBrowser",
            "cloudAppSecurity",
            "applicationEnforcedRestrictions",
            "continuousAccessEvaluation",
        )
        if _control_enabled(session.get(name))
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
            "termsOfUse": _str_list(grant.get("termsOfUse")),
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
        visited: set[str] = set()
        while url:
            # Validate the destination before attaching the bearer token.
            if not is_graph_url(url):
                raise GraphError("invalid_url", "refusing to send credentials to a non-Graph host")
            if url in visited:
                raise GraphError("graph_error", "paging cycle detected")
            if len(visited) >= MAX_PAGES:
                raise GraphError("graph_error", "paging exceeded the maximum page count")
            visited.add(url)

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
        return policies
