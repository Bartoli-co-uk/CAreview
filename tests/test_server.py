"""Tests for the CAreview server shell (ISSUE-0001)."""

from __future__ import annotations

import contextlib
import http.client
import io
import json
import sys
import threading
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import auth  # noqa: E402
import server  # noqa: E402

# Synthetic, clearly-fake values for the app-only (ISSUE-0009) endpoint tests —
# never real Entra identifiers or secrets.
FAKE_TENANT = "11111111-2222-3333-4444-555555555555"
FAKE_CLIENT_ID = "66666666-7777-8888-9999-aaaaaaaaaaaa"
FAKE_SECRET = "test-only-fake-secret-DO-NOT-USE-xyz123"


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

    def test_sample_data_served(self) -> None:
        resp = self._request("/sample-data.json", f"127.0.0.1:{self.port}")
        self.assertEqual(resp.status, 200)
        body = json.loads(resp.read())
        self.assertIn("policies", body)
        self.assertIn("analysis", body)
        self.assertIn("score", body["analysis"])

    def test_index_has_csp_meta(self) -> None:
        resp = self._request("/", f"127.0.0.1:{self.port}")
        body = resp.read().decode()
        self.assertIn("Content-Security-Policy", body)

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

    def test_auth_start_success_through_http_handler(self) -> None:
        # Exercises /api/auth/start at the HTTP layer (Codex GEN-001, milestone
        # general review): the response must never contain the raw device_code,
        # only the opaque handle plus user_code/verification_uri/interval.
        origin = f"http://127.0.0.1:{self.port}"
        original_start = server.AUTH.start
        server.AUTH.start = lambda tenant=auth.DEFAULT_TENANT: {  # type: ignore[method-assign]
            "handle": "opaque-handle-123",
            "user_code": "ABCD-EFGH",
            "verification_uri": "https://microsoft.com/devicelogin",
            "expires_in": 900,
            "interval": 5,
        }
        try:
            body = json.dumps({"tenant": "organizations"}).encode()
            resp = self._post("/api/auth/start", f"127.0.0.1:{self.port}", origin, body)
            data = json.loads(resp.read())
            self.assertEqual(resp.status, 200)
            self.assertEqual(data["handle"], "opaque-handle-123")
            self.assertEqual(data["user_code"], "ABCD-EFGH")
            self.assertNotIn("device_code", data)
        finally:
            server.AUTH.start = original_start

    def test_auth_start_then_poll_success_through_http_handler(self) -> None:
        # Full start -> poll round trip at the HTTP layer, using a real
        # AuthManager with a mocked transport (no network).
        origin = f"http://127.0.0.1:{self.port}"
        original_auth = server.AUTH
        device_ok = (200, {
            "device_code": "DEV", "user_code": "WXYZ",
            "verification_uri": "https://microsoft.com/devicelogin",
            "interval": 0, "expires_in": 900,
        })
        token_ok = (200, {"access_token": "T", "expires_in": 3600})
        responses = [device_ok, token_ok]
        server.AUTH = auth.AuthManager(transport=lambda url, data: responses.pop(0))
        try:
            start_body = json.dumps({}).encode()
            start_resp = self._post("/api/auth/start", f"127.0.0.1:{self.port}", origin, start_body)
            handle = json.loads(start_resp.read())["handle"]

            poll_body = json.dumps({"handle": handle}).encode()
            poll_resp = self._post("/api/auth/poll", f"127.0.0.1:{self.port}", origin, poll_body)
            self.assertEqual(json.loads(poll_resp.read())["state"], "success")
        finally:
            server.AUTH = original_auth

    def test_security_headers_present(self) -> None:
        resp = self._request("/", f"127.0.0.1:{self.port}")
        resp.read()
        self.assertIn("nosniff", resp.getheader("X-Content-Type-Options", ""))
        self.assertIn("default-src 'self'", resp.getheader("Content-Security-Policy", ""))

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

    def test_abandon_missing_handle_rejected(self) -> None:
        origin = f"http://127.0.0.1:{self.port}"
        resp = self._post("/api/auth/abandon", f"127.0.0.1:{self.port}", origin, b"{}")
        self.assertEqual(resp.status, 400)

    def test_abandon_requires_origin(self) -> None:
        resp = self._post("/api/auth/abandon", f"127.0.0.1:{self.port}", None, b'{"handle": "x"}')
        self.assertEqual(resp.status, 403)

    def test_abandon_unknown_handle_is_ok_and_does_not_clear_a_newer_session(self) -> None:
        # ISSUE-0013 (F-001 from the round-2 Codex review): a device-code
        # attempt abandoned via this endpoint must never clear a different,
        # newer session installed after it. Exercised at the HTTP layer with
        # a real AuthManager (mocked transport, no network).
        origin = f"http://127.0.0.1:{self.port}"
        original_auth = server.AUTH
        old_device_ok = (200, {
            "device_code": "OLD", "user_code": "OLD1", "verification_uri": "x",
            "interval": 0, "expires_in": 900,
        })
        old_token_ok = (200, {"access_token": "OLD-TOKEN", "expires_in": 3600})
        new_device_ok = (200, {
            "device_code": "NEW", "user_code": "NEW1", "verification_uri": "x",
            "interval": 0, "expires_in": 900,
        })
        new_token_ok = (200, {"access_token": "NEW-TOKEN", "expires_in": 3600})
        responses = [old_device_ok, old_token_ok, new_device_ok, new_token_ok]
        server.AUTH = auth.AuthManager(transport=lambda url, data: responses.pop(0))
        try:
            old_handle = json.loads(
                self._post("/api/auth/start", f"127.0.0.1:{self.port}", origin, b"{}").read()
            )["handle"]
            self.assertEqual(
                json.loads(self._post("/api/auth/poll", f"127.0.0.1:{self.port}", origin, json.dumps({"handle": old_handle}).encode()).read())["state"],
                "success",
            )
            self.assertEqual(server.AUTH.get_token(), "OLD-TOKEN")

            # A brand new sign-in completes, superseding the old one.
            new_handle = json.loads(
                self._post("/api/auth/start", f"127.0.0.1:{self.port}", origin, b"{}").read()
            )["handle"]
            self.assertEqual(
                json.loads(self._post("/api/auth/poll", f"127.0.0.1:{self.port}", origin, json.dumps({"handle": new_handle}).encode()).read())["state"],
                "success",
            )
            self.assertEqual(server.AUTH.get_token(), "NEW-TOKEN")

            # The old, now-irrelevant handle's abandon request arrives late.
            abandon_resp = self._post(
                "/api/auth/abandon", f"127.0.0.1:{self.port}", origin, json.dumps({"handle": old_handle}).encode()
            )
            self.assertEqual(abandon_resp.status, 200)
            self.assertEqual(json.loads(abandon_resp.read()), {"state": "ok"})
            self.assertEqual(server.AUTH.get_token(), "NEW-TOKEN")  # untouched
        finally:
            server.AUTH = original_auth

    def test_abandon_pending_session_prevents_later_success(self) -> None:
        origin = f"http://127.0.0.1:{self.port}"
        original_auth = server.AUTH
        device_ok = (200, {
            "device_code": "DEV", "user_code": "WXYZ", "verification_uri": "x",
            "interval": 0, "expires_in": 900,
        })
        token_ok = (200, {"access_token": "T", "expires_in": 3600})
        responses = [device_ok, token_ok]
        server.AUTH = auth.AuthManager(transport=lambda url, data: responses.pop(0))
        try:
            handle = json.loads(
                self._post("/api/auth/start", f"127.0.0.1:{self.port}", origin, b"{}").read()
            )["handle"]
            abandon_resp = self._post(
                "/api/auth/abandon", f"127.0.0.1:{self.port}", origin, json.dumps({"handle": handle}).encode()
            )
            self.assertEqual(abandon_resp.status, 200)
            # The (already-scripted) successful token response is never
            # installed: the session was cleared before poll() could use it.
            poll_resp = self._post(
                "/api/auth/poll", f"127.0.0.1:{self.port}", origin, json.dumps({"handle": handle}).encode()
            )
            self.assertEqual(json.loads(poll_resp.read())["state"], "error")
            self.assertIsNone(server.AUTH.get_token())
        finally:
            server.AUTH = original_auth

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
            self.assertEqual(resp.getheader("Cache-Control"), "no-store")
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
            self.assertEqual(resp.getheader("Cache-Control"), "no-store")
        finally:
            server.GRAPH = original
            server.AUTH.logout()


class AppOnlyEndpointTests(ServerIntegrationTests):
    """Tests for POST /api/auth/app (ISSUE-0009)."""

    def tearDown(self) -> None:
        server.AUTH.logout()
        super().tearDown()

    def _app_only(self, body: dict, *, origin: bool = True) -> http.client.HTTPResponse:
        origin_header = f"http://127.0.0.1:{self.port}" if origin else None
        return self._post(
            "/api/auth/app", f"127.0.0.1:{self.port}", origin_header, json.dumps(body).encode()
        )

    # -- happy path -----------------------------------------------------
    def test_success(self) -> None:
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
            self.assertEqual(json.loads(resp.read()), {"state": "success"})
            self.assertEqual(resp.getheader("Cache-Control"), "no-store")
        finally:
            server.AUTH = original_auth

    def test_policies_and_analysis_work_after_app_only_sign_in(self) -> None:
        original_auth = server.AUTH
        original_graph = server.GRAPH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )

        class FakeGraph:
            def fetch_policies(self, token: str) -> list[dict]:
                return [{"id": "p1", "displayName": "x"}]

        server.GRAPH = FakeGraph()
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
            resp.read()

            policies_resp = self._request("/api/policies", f"127.0.0.1:{self.port}")
            self.assertEqual(policies_resp.status, 200)
            self.assertEqual(json.loads(policies_resp.read())["count"], 1)

            analysis_resp = self._request("/api/analysis", f"127.0.0.1:{self.port}")
            self.assertEqual(analysis_resp.status, 200)
        finally:
            server.AUTH = original_auth
            server.GRAPH = original_graph

    def test_silent_renewal_success_is_transparent_to_policies_and_analysis(self) -> None:
        # Proves the *renewed* token (T2, not the original T1) is what
        # actually reaches Graph for both endpoints, not merely that some
        # non-empty token was accepted (Codex F-002).
        original_auth = server.AUTH
        original_graph = server.GRAPH
        responses = [
            (200, {"access_token": "T1", "expires_in": 3600}),  # start_app_only
            (200, {"access_token": "T2", "expires_in": 3600}),  # renewal
        ]
        server.AUTH = auth.AuthManager(transport=lambda url, data: responses.pop(0))

        received_tokens: list[str] = []

        class FakeGraph:
            def fetch_policies(self, token: str) -> list[dict]:
                received_tokens.append(token)
                return [{"id": "p1", "displayName": "x"}]

        server.GRAPH = FakeGraph()
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
            resp.read()
            # Simulate the previously-issued token having expired.
            server.AUTH._token_expires_at = server.AUTH._clock() - 1

            policies_resp = self._request("/api/policies", f"127.0.0.1:{self.port}")
            self.assertEqual(policies_resp.status, 200)
            self.assertEqual(json.loads(policies_resp.read())["count"], 1)

            analysis_resp = self._request("/api/analysis", f"127.0.0.1:{self.port}")
            self.assertEqual(analysis_resp.status, 200)

            # Renewal happens once (the token is then cached and unexpired
            # for the second call); both endpoint calls must have used it.
            self.assertEqual(received_tokens, ["T2", "T2"])
        finally:
            server.AUTH = original_auth
            server.GRAPH = original_graph

    def test_silent_renewal_failure_surfaces_stable_non_secret_non_5xx_error(self) -> None:
        # Covers both /api/policies and /api/analysis independently (Codex
        # F-002): every renewal attempt after the first fails, so each
        # endpoint call retries and fails cleanly on its own.
        original_auth = server.AUTH
        calls = {"n": 0}

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            calls["n"] += 1
            if calls["n"] == 1:
                return 200, {"access_token": "T1", "expires_in": 3600}
            return 400, {"error": "invalid_client", "error_description": FAKE_SECRET}

        server.AUTH = auth.AuthManager(transport=transport)
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
            resp.read()
            server.AUTH._token_expires_at = server.AUTH._clock() - 1

            policies_resp = self._request("/api/policies", f"127.0.0.1:{self.port}")
            policies_body = policies_resp.read()
            self.assertEqual(policies_resp.status, 401)
            self.assertEqual(json.loads(policies_body)["error"], "not_authenticated")
            self.assertLess(policies_resp.status, 500)
            self.assertNotIn(FAKE_SECRET.encode(), policies_body)

            server.AUTH._token_expires_at = server.AUTH._clock() - 1
            analysis_resp = self._request("/api/analysis", f"127.0.0.1:{self.port}")
            analysis_body = analysis_resp.read()
            self.assertEqual(analysis_resp.status, 401)
            self.assertLess(analysis_resp.status, 500)
            self.assertNotIn(FAKE_SECRET.encode(), analysis_body)
        finally:
            server.AUTH = original_auth

    def test_logout_clears_app_only_state(self) -> None:
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
            resp.read()
            self.assertIsNotNone(server.AUTH._app_only_secret)

            logout_resp = self._post(
                "/api/auth/logout", f"127.0.0.1:{self.port}", f"http://127.0.0.1:{self.port}", b"{}"
            )
            self.assertEqual(logout_resp.status, 200)
            self.assertIsNone(server.AUTH._app_only_secret)
        finally:
            server.AUTH = original_auth

    # -- CSRF / host reuse ------------------------------------------------
    def test_requires_origin(self) -> None:
        resp = self._app_only(
            {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET},
            origin=False,
        )
        self.assertEqual(resp.status, 403)

    # -- provider/network failure mapping ---------------------------------
    def test_provider_rejection_maps_to_502_with_stable_label(self) -> None:
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (400, {"error": "unauthorized_client"})
        )
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 502)
            self.assertEqual(json.loads(resp.read())["error"], "provider_error")
        finally:
            server.AUTH = original_auth

    def test_network_error_maps_to_502(self) -> None:
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(transport=lambda url, data: (0, {"error": "network_error"}))
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 502)
            self.assertEqual(json.loads(resp.read())["error"], "network_error")
        finally:
            server.AUTH = original_auth

    # -- input validation: presence / type ---------------------------------
    def test_missing_fields_rejected_with_400(self) -> None:
        for body in (
            {},
            {"tenant": FAKE_TENANT},
            {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID},
        ):
            resp = self._app_only(body)
            self.assertEqual(resp.status, 400, body)

    def test_wrong_type_fields_rejected_with_400(self) -> None:
        for body in (
            {"tenant": 123, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET},
            {"tenant": FAKE_TENANT, "client_id": ["x"], "client_secret": FAKE_SECRET},
            {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": None},
        ):
            resp = self._app_only(body)
            self.assertEqual(resp.status, 400, body)

    # -- input validation: tenant boundaries --------------------------------
    def test_tenant_disallowed_aliases_rejected(self) -> None:
        for tenant in ("organizations", "common", "consumers"):
            resp = self._app_only(
                {"tenant": tenant, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 400, tenant)

    def test_tenant_malformed_rejected(self) -> None:
        resp = self._app_only(
            {"tenant": "not a tenant!/", "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
        )
        self.assertEqual(resp.status, 400)

    def test_tenant_minimum_valid_domain_accepted(self) -> None:
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": "a.io", "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
        finally:
            server.AUTH = original_auth

    def test_tenant_maximum_length_domain_accepted(self) -> None:
        tenant = ".".join(["a" * 63] * 4)  # 4*63 + 3 dots = 255
        self.assertEqual(len(tenant), server.MAX_APP_ONLY_TENANT_LEN)
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": tenant, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
        finally:
            server.AUTH = original_auth

    def test_tenant_one_over_maximum_length_rejected_without_outbound_call(self) -> None:
        # A validly-shaped domain, one character longer than the maximum:
        # labels of 63, 63, 63, 62, 1 with 4 dots = 256 chars.
        tenant = ".".join(["a" * 63, "a" * 63, "a" * 63, "a" * 62, "a"])
        self.assertEqual(len(tenant), server.MAX_APP_ONLY_TENANT_LEN + 1)
        called = []
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(transport=lambda url, data: called.append(1) or (200, {}))
        try:
            resp = self._app_only(
                {"tenant": tenant, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 400)
            self.assertFalse(called)
            self.assertIsNone(server.AUTH._app_only_secret)
        finally:
            server.AUTH = original_auth

    # -- input validation: client_id boundaries -----------------------------
    def test_client_id_valid_guid_accepted(self) -> None:
        self.assertEqual(len(FAKE_CLIENT_ID), server.APP_ONLY_CLIENT_ID_LEN)
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
        finally:
            server.AUTH = original_auth

    def test_client_id_one_over_maximum_length_rejected(self) -> None:
        client_id = FAKE_CLIENT_ID + "a"  # 37 chars
        resp = self._app_only(
            {"tenant": FAKE_TENANT, "client_id": client_id, "client_secret": FAKE_SECRET}
        )
        self.assertEqual(resp.status, 400)

    def test_client_id_malformed_same_length_rejected(self) -> None:
        client_id = "z" * server.APP_ONLY_CLIENT_ID_LEN  # right length, not a GUID
        resp = self._app_only(
            {"tenant": FAKE_TENANT, "client_id": client_id, "client_secret": FAKE_SECRET}
        )
        self.assertEqual(resp.status, 400)

    # -- input validation: client_secret boundaries -------------------------
    def test_secret_minimum_length_accepted(self) -> None:
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": "x"}
            )
            self.assertEqual(resp.status, 200)
        finally:
            server.AUTH = original_auth

    def test_secret_maximum_length_accepted(self) -> None:
        secret = "x" * server.MAX_APP_ONLY_SECRET_LEN
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": secret}
            )
            self.assertEqual(resp.status, 200)
        finally:
            server.AUTH = original_auth

    def test_secret_one_over_maximum_length_rejected_without_outbound_call(self) -> None:
        secret = "x" * (server.MAX_APP_ONLY_SECRET_LEN + 1)
        called = []
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(transport=lambda url, data: called.append(1) or (200, {}))
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": secret}
            )
            self.assertEqual(resp.status, 400)
            self.assertFalse(called)
            self.assertIsNone(server.AUTH._app_only_secret)
        finally:
            server.AUTH = original_auth

    def test_secret_empty_rejected(self) -> None:
        resp = self._app_only(
            {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": ""}
        )
        self.assertEqual(resp.status, 400)

    # -- secret never leaks -------------------------------------------------
    def test_secret_absent_from_every_response_body(self) -> None:
        # Every distinct endpoint response path — validation rejections
        # (missing/type/boundary/malformed, all three disallowed tenant
        # aliases), the malformed-JSON-body path, success, every AuthError
        # label the endpoint can surface, and a superseded race — scanned
        # for the fake secret in its literal, URL-encoded, and JSON-escaped
        # forms (Codex F-003).
        encoded = FAKE_SECRET.encode()
        url_encoded = urllib.parse.quote(FAKE_SECRET).encode()
        json_escaped = json.dumps(FAKE_SECRET).encode()

        def assert_secret_absent(raw: bytes) -> None:
            self.assertNotIn(encoded, raw)
            self.assertNotIn(url_encoded, raw)
            self.assertNotIn(json_escaped, raw)

        original_auth = server.AUTH

        # -- validation-rejected cases: no AuthManager call is made, so a
        # harmless success stub transport is installed just in case.
        validation_cases = [
            {},  # missing all fields
            {"tenant": FAKE_TENANT},  # missing client_id/secret
            {"tenant": 123, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET},  # wrong type
            {"tenant": "organizations", "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET},
            {"tenant": "common", "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET},
            {"tenant": "consumers", "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET},
            {"tenant": "not a tenant!/", "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET},
            {"tenant": FAKE_TENANT, "client_id": "not-a-guid", "client_secret": FAKE_SECRET},
            {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID + "a", "client_secret": FAKE_SECRET},
            {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": ""},
            {
                "tenant": FAKE_TENANT,
                "client_id": FAKE_CLIENT_ID,
                "client_secret": "x" * (server.MAX_APP_ONLY_SECRET_LEN + 1),
            },
        ]
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            for body in validation_cases:
                resp = self._app_only(body)
                self.assertEqual(resp.status, 400, body)
                assert_secret_absent(resp.read())

            # Malformed request body (not valid JSON) containing the secret.
            malformed = (FAKE_SECRET + "{not json").encode()
            resp = self._post(
                "/api/auth/app",
                f"127.0.0.1:{self.port}",
                f"http://127.0.0.1:{self.port}",
                malformed,
            )
            self.assertEqual(resp.status, 400)
            assert_secret_absent(resp.read())
        finally:
            server.AUTH = original_auth

        # -- success
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            self.assertEqual(resp.status, 200)
            assert_secret_absent(resp.read())
        finally:
            server.AUTH = original_auth

        # -- every AuthError label the endpoint can surface as 502, with the
        # provider payload also carrying the secret literally, URL-encoded,
        # and JSON-escaped, to prove no representation ever reaches a
        # response body.
        def provider_error_transport(description: str):
            def transport(url: str, data: bytes) -> tuple[int, dict]:
                return 400, {"error": "unauthorized_client", "error_description": description}

            return transport

        secret_forms = (FAKE_SECRET, urllib.parse.quote(FAKE_SECRET), json.dumps(FAKE_SECRET))
        error_transports = [
            lambda url, data: (0, {"error": "network_error"}),  # -> network_error
            lambda url, data: (200, {"error": "bad_response"}),  # -> invalid_response
        ] + [provider_error_transport(f"bad secret {form}") for form in secret_forms]  # -> provider_error
        for transport in error_transports:
            server.AUTH = auth.AuthManager(transport=transport)
            try:
                resp = self._app_only(
                    {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
                )
                self.assertEqual(resp.status, 502)
                assert_secret_absent(resp.read())
            finally:
                server.AUTH = original_auth

        # -- superseded: a synchronous in-flight second sign-in races the
        # first (mirrors auth.py's own race-test pattern: the transport
        # callback itself issues the superseding call before returning).
        holder: dict = {}

        def superseding_transport(url: str, data: bytes) -> tuple[int, dict]:
            if not holder.get("superseded"):
                holder["superseded"] = True
                holder["mgr"].start_app_only(
                    FAKE_TENANT, FAKE_CLIENT_ID, f"test-only-second-fake-secret {FAKE_SECRET}"
                )
            return 200, {"access_token": "T", "expires_in": 3600}

        mgr = auth.AuthManager(transport=superseding_transport)
        holder["mgr"] = mgr
        server.AUTH = mgr
        try:
            resp = self._app_only(
                {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
            )
            raw = resp.read()
            self.assertEqual(resp.status, 502)
            self.assertEqual(json.loads(raw)["error"], "superseded")
            assert_secret_absent(raw)
        finally:
            server.AUTH = original_auth

    def test_nothing_logged_to_stderr(self) -> None:
        original_auth = server.AUTH
        server.AUTH = auth.AuthManager(
            transport=lambda url, data: (200, {"access_token": "T", "expires_in": 3600})
        )
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured):
                resp = self._app_only(
                    {"tenant": FAKE_TENANT, "client_id": FAKE_CLIENT_ID, "client_secret": FAKE_SECRET}
                )
                resp.read()
        finally:
            server.AUTH = original_auth
        self.assertNotIn(FAKE_SECRET, captured.getvalue())
        self.assertEqual(captured.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
