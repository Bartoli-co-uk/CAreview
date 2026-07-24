"""Tests for the CAreview server shell (ISSUE-0001)."""

from __future__ import annotations

import http.client
import json
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server  # noqa: E402


class HelperTests(unittest.TestCase):
    def test_health_payload(self) -> None:
        self.assertEqual(server.health_payload(), {"status": "ok"})

    def test_host_allowed_accepts_loopback(self) -> None:
        for host in ("127.0.0.1:8765", "localhost:8765", "[::1]:8765", "LOCALHOST:8765"):
            self.assertTrue(server.host_allowed(host, 8765), host)

    def test_host_allowed_rejects_non_loopback_and_missing(self) -> None:
        for host in ("evil.com", "evil.com:8765", "127.0.0.1:9999", "", None):
            self.assertFalse(server.host_allowed(host, 8765), repr(host))

    def test_origin_allowed(self) -> None:
        self.assertTrue(server.origin_allowed("http://127.0.0.1:8765", 8765))
        self.assertTrue(server.origin_allowed("http://localhost:8765", 8765))
        for origin in ("https://evil.com", "http://127.0.0.1:9999", "", None):
            self.assertFalse(server.origin_allowed(origin, 8765), repr(origin))

    def test_build_server_rejects_non_loopback_bind(self) -> None:
        # No socket is opened: the guard runs before binding.
        for host in ("0.0.0.0", "::", "192.168.1.10", "example.com"):
            with self.assertRaises(ValueError):
                server.build_server(host, 0)


class ServerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        # Ephemeral port on loopback; the handler learns the real bound port.
        self.server = server.build_server("127.0.0.1", 0)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def _request(self, path: str, host: str | None) -> http.client.HTTPResponse:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        # Suppress the auto Host header so we can set it explicitly (or omit it).
        headers = {} if host is None else {"Host": host}
        conn.putrequest("GET", path, skip_host=True, skip_accept_encoding=True)
        for key, value in headers.items():
            conn.putheader(key, value)
        conn.endheaders()
        return conn.getresponse()

    def test_health_ok_with_loopback_host(self) -> None:
        resp = self._request("/api/health", f"127.0.0.1:{self.port}")
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(resp.read()), {"status": "ok"})

    def test_root_serves_html(self) -> None:
        resp = self._request("/", f"localhost:{self.port}")
        body = resp.read()
        self.assertEqual(resp.status, 200)
        self.assertIn(b"<title>CAreview", body)

    def test_bad_host_rejected(self) -> None:
        resp = self._request("/api/health", "evil.com")
        self.assertEqual(resp.status, 403)

    def test_missing_host_rejected(self) -> None:
        resp = self._request("/api/health", None)
        self.assertEqual(resp.status, 403)

    def test_unknown_path_404(self) -> None:
        resp = self._request("/nope", f"127.0.0.1:{self.port}")
        self.assertEqual(resp.status, 404)

    def _post(self, path: str, host: str, origin: str | None, body: bytes) -> http.client.HTTPResponse:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.putrequest("POST", path, skip_host=True, skip_accept_encoding=True)
        conn.putheader("Host", host)
        if origin is not None:
            conn.putheader("Origin", origin)
        conn.putheader("Content-Type", "application/json")
        conn.putheader("Content-Length", str(len(body)))
        conn.endheaders()
        conn.send(body)
        return conn.getresponse()

    def test_post_without_origin_rejected(self) -> None:
        resp = self._post("/api/auth/logout", f"127.0.0.1:{self.port}", None, b"{}")
        self.assertEqual(resp.status, 403)

    def test_post_cross_origin_rejected(self) -> None:
        resp = self._post("/api/auth/logout", f"127.0.0.1:{self.port}", "https://evil.com", b"{}")
        self.assertEqual(resp.status, 403)

    def test_logout_same_origin_ok(self) -> None:
        origin = f"http://127.0.0.1:{self.port}"
        resp = self._post("/api/auth/logout", f"127.0.0.1:{self.port}", origin, b"{}")
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(resp.read()), {"state": "signed_out"})

    def test_poll_unknown_handle_returns_error(self) -> None:
        origin = f"http://127.0.0.1:{self.port}"
        body = json.dumps({"handle": "nope"}).encode()
        resp = self._post("/api/auth/poll", f"127.0.0.1:{self.port}", origin, body)
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(resp.read())["state"], "error")

    def test_policies_unauthenticated_401(self) -> None:
        # No sign-in has happened, so there is no token.
        server.AUTH.logout()
        resp = self._request("/api/policies", f"127.0.0.1:{self.port}")
        self.assertEqual(resp.status, 401)
        self.assertEqual(json.loads(resp.read())["error"], "not_authenticated")

    def _with_token(self) -> None:
        # Inject an unexpired in-memory token without a real sign-in.
        server.AUTH._access_token = "TESTTOKEN"
        server.AUTH._token_expires_at = server.AUTH._clock() + 3600

    def test_policies_success(self) -> None:
        self._with_token()
        original = server.GRAPH

        class FakeGraph:
            def fetch_policies(self, token: str) -> list[dict]:
                return [{"id": "p1", "displayName": "x"}]

        server.GRAPH = FakeGraph()
        try:
            resp = self._request("/api/policies", f"127.0.0.1:{self.port}")
            body = json.loads(resp.read())
            self.assertEqual(resp.status, 200)
            self.assertEqual(body["count"], 1)
            self.assertEqual(body["policies"][0]["id"], "p1")
        finally:
            server.GRAPH = original
            server.AUTH.logout()

    def test_policies_consent_required_403(self) -> None:
        import graph as graph_mod

        self._with_token()
        original = server.GRAPH

        class ConsentGraph:
            def fetch_policies(self, token: str) -> list[dict]:
                raise graph_mod.GraphError("consent_required", "need consent")

        server.GRAPH = ConsentGraph()
        try:
            resp = self._request("/api/policies", f"127.0.0.1:{self.port}")
            self.assertEqual(resp.status, 403)
            self.assertEqual(json.loads(resp.read())["error"], "consent_required")
        finally:
            server.GRAPH = original
            server.AUTH.logout()

    def test_policies_graph_error_502(self) -> None:
        import graph as graph_mod

        self._with_token()
        original = server.GRAPH

        class BrokenGraph:
            def fetch_policies(self, token: str) -> list[dict]:
                raise graph_mod.GraphError("graph_error", "boom")

        server.GRAPH = BrokenGraph()
        try:
            resp = self._request("/api/policies", f"127.0.0.1:{self.port}")
            self.assertEqual(resp.status, 502)
        finally:
            server.GRAPH = original
            server.AUTH.logout()

    def test_analysis_unauthenticated_401(self) -> None:
        server.AUTH.logout()
        resp = self._request("/api/analysis", f"127.0.0.1:{self.port}")
        self.assertEqual(resp.status, 401)

    def test_breakglass_endpoint_sanitizes_and_stores(self) -> None:
        origin = f"http://127.0.0.1:{self.port}"
        good = "62e90394-69f5-4237-9190-012177145e10"
        body = json.dumps({"ids": [good, "not-a-guid"]}).encode()
        try:
            resp = self._post("/api/breakglass", f"127.0.0.1:{self.port}", origin, body)
            self.assertEqual(resp.status, 200)
            self.assertEqual(json.loads(resp.read())["count"], 1)  # junk dropped
            self.assertEqual(server.get_break_glass_ids(), [good])
        finally:
            server.set_break_glass_ids([])  # clear

    def test_breakglass_requires_origin(self) -> None:
        resp = self._post("/api/breakglass", f"127.0.0.1:{self.port}", None, b"{}")
        self.assertEqual(resp.status, 403)

    def test_analysis_success(self) -> None:
        self._with_token()
        original = server.GRAPH

        class FakeGraph:
            def fetch_policies(self, token: str) -> list[dict]:
                # One enabled block-legacy-auth policy → some score, no crash.
                return [{
                    "id": "p", "displayName": "block legacy", "state": "enabled",
                    "conditions": {"clientAppTypes": ["other"], "includeUsers": ["All"]},
                    "grantControls": {"operator": "OR", "builtInControls": ["block"]},
                    "sessionControls": [],
                }]

        server.GRAPH = FakeGraph()
        try:
            resp = self._request("/api/analysis", f"127.0.0.1:{self.port}")
            body = json.loads(resp.read())
            self.assertEqual(resp.status, 200)
            self.assertIn("score", body)
            self.assertIn("findings", body)
            self.assertTrue(body["scoreIsHeuristic"])
        finally:
            server.GRAPH = original
            server.AUTH.logout()


if __name__ == "__main__":
    unittest.main()
