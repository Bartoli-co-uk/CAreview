"""Tests for the Microsoft Graph CA-policy client (ISSUE-0003).

Uses an injected transport, so no network or live tenant is involved.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import graph  # noqa: E402

POLICY_RAW = {
    "id": "p1",
    "displayName": "Block legacy authentication",
    "state": "enabled",
    "conditions": {
        "users": {"includeUsers": ["All"], "excludeUsers": ["breakglass-id"]},
        "applications": {"includeApplications": ["All"]},
        "clientAppTypes": ["exchangeActiveSync", "other"],
        "locations": {"includeLocations": ["All"]},
    },
    "grantControls": {"operator": "OR", "builtInControls": ["block"]},
    "sessionControls": {"signInFrequency": {"value": 1, "type": "hours"}},
}

POLICY_RAW_2 = {
    "id": "p2",
    "displayName": "Require MFA for admins",
    "state": "enabledForReportingButNotEnforced",
    "conditions": {"users": {"includeRoles": ["62e90394-69f5-4237-9190-012177145e10"]}},
    "grantControls": {"operator": "OR", "builtInControls": ["mfa"]},
}


class SeqTransport:
    def __init__(self, responses: list[tuple[int, dict]]) -> None:
        self.responses = list(responses)
        self.calls: list[str] = []

    def __call__(self, url: str, headers: dict) -> tuple[int, dict]:
        self.calls.append(url)
        return self.responses.pop(0)


class GraphClientTests(unittest.TestCase):
    def test_single_page_normalizes(self) -> None:
        client = graph.GraphClient(transport=SeqTransport([(200, {"value": [POLICY_RAW]})]))
        out = client.fetch_policies("tok")
        self.assertEqual(len(out), 1)
        p = out[0]
        self.assertEqual(p["displayName"], "Block legacy authentication")
        self.assertEqual(p["state"], "enabled")
        self.assertEqual(p["conditions"]["includeUsers"], ["All"])
        self.assertEqual(p["conditions"]["excludeUsers"], ["breakglass-id"])
        self.assertEqual(p["conditions"]["clientAppTypes"], ["exchangeActiveSync", "other"])
        self.assertEqual(p["grantControls"]["builtInControls"], ["block"])
        self.assertEqual(p["sessionControls"], ["signInFrequency"])

    def test_follows_next_link(self) -> None:
        page1 = {"value": [POLICY_RAW], "@odata.nextLink": "https://graph.microsoft.com/v1.0/next"}
        page2 = {"value": [POLICY_RAW_2]}
        transport = SeqTransport([(200, page1), (200, page2)])
        out = graph.GraphClient(transport=transport).fetch_policies("tok")
        self.assertEqual([p["id"] for p in out], ["p1", "p2"])
        self.assertEqual(len(transport.calls), 2)

    def test_403_is_consent_required(self) -> None:
        client = graph.GraphClient(transport=SeqTransport([(403, {"error": {"code": "Authorization_RequestDenied"}})]))
        with self.assertRaises(graph.GraphError) as ctx:
            client.fetch_policies("tok")
        self.assertEqual(ctx.exception.code, "consent_required")

    def test_401_is_not_authenticated(self) -> None:
        client = graph.GraphClient(transport=SeqTransport([(401, {"error": "InvalidAuthenticationToken"})]))
        with self.assertRaises(graph.GraphError) as ctx:
            client.fetch_policies("tok")
        self.assertEqual(ctx.exception.code, "not_authenticated")

    def test_network_error_is_graph_error(self) -> None:
        client = graph.GraphClient(transport=SeqTransport([(0, {"error": "network_error"})]))
        with self.assertRaises(graph.GraphError) as ctx:
            client.fetch_policies("tok")
        self.assertEqual(ctx.exception.code, "graph_error")

    def test_empty_token_rejected(self) -> None:
        with self.assertRaises(graph.GraphError) as ctx:
            graph.GraphClient(transport=SeqTransport([])).fetch_policies("")
        self.assertEqual(ctx.exception.code, "not_authenticated")

    def test_normalize_handles_missing_fields(self) -> None:
        p = graph.normalize_policy({"id": "x"})
        self.assertEqual(p["displayName"], "")
        self.assertEqual(p["conditions"]["includeUsers"], [])
        self.assertEqual(p["grantControls"]["builtInControls"], [])
        self.assertEqual(p["sessionControls"], [])


if __name__ == "__main__":
    unittest.main()
