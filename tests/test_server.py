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


if __name__ == "__main__":
    unittest.main()
