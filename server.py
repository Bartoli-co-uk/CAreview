#!/usr/bin/env python3
"""CAreview local server.

A dependency-free, standard-library HTTP server that serves the static UI and a
small JSON API on the loopback interface only. This first issue (ISSUE-0001)
provides the server shell: static file serving, a ``/api/health`` endpoint, a
Host-header loopback allowlist that resists browser DNS-rebinding into the
loopback API, and a reusable Origin check for the state-changing endpoints added
in later issues. No authentication, Microsoft Graph access, or analysis lives
here yet.
"""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
WEB_ROOT = (Path(__file__).resolve().parent / "web").resolve()

# Static files this shell will serve, mapped to their content types. Keeping an
# explicit allowlist (rather than serving the whole directory) avoids any path
# traversal surprises while the UI is tiny.
STATIC_FILES: dict[str, str] = {
    "/": "text/html; charset=utf-8",
    "/index.html": "text/html; charset=utf-8",
    "/app.js": "text/javascript; charset=utf-8",
    "/style.css": "text/css; charset=utf-8",
}

# Loopback host names that legitimately reach this server. The port is appended
# at request time because browsers include it in the Host header.
_LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "[::1]")


def allowed_hosts(port: int) -> frozenset[str]:
    """Return the exact set of acceptable ``Host`` header values for ``port``."""
    return frozenset(f"{host}:{port}" for host in _LOOPBACK_HOSTS)


def host_allowed(host_header: str | None, port: int) -> bool:
    """True when the request's ``Host`` header is an expected loopback value.

    A remote page performing DNS rebinding to the loopback address still sends
    its own hostname in ``Host``; rejecting anything not on the loopback
    allowlist is the smallest effective defence.
    """
    if not host_header:
        return False
    return host_header.strip().lower() in allowed_hosts(port)


def allowed_origins(port: int) -> frozenset[str]:
    """Return the acceptable ``Origin`` values for state-changing requests."""
    return frozenset(
        f"http://{host}:{port}" for host in ("127.0.0.1", "localhost", "[::1]")
    )


def origin_allowed(origin_header: str | None, port: int) -> bool:
    """True when ``Origin`` is a loopback origin for ``port``.

    Provided here so the state-changing ``/api/auth/*`` endpoints added in
    ISSUE-0002 can reject cross-site requests. A missing Origin is treated as not
    allowed for state-changing use; callers decide how strictly to apply it.
    """
    if not origin_header:
        return False
    return origin_header.strip().lower() in allowed_origins(port)


def health_payload() -> dict[str, str]:
    """The body returned by ``/api/health``."""
    return {"status": "ok"}


class CAReviewHandler(BaseHTTPRequestHandler):
    """Request handler for the CAreview local server."""

    server_version = "CAreview/0.1"
    # Bound at server construction so the handler knows which port to validate.
    port: int = DEFAULT_PORT

    def _reject(self, status: HTTPStatus, message: str) -> None:
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self, path: str) -> None:
        relative = "index.html" if path == "/" else path.lstrip("/")
        target = (WEB_ROOT / relative).resolve()
        # Defence in depth: never serve outside WEB_ROOT even though the route is
        # already restricted to a known allowlist.
        if WEB_ROOT not in target.parents and target != WEB_ROOT:
            self._reject(HTTPStatus.NOT_FOUND, "not found")
            return
        try:
            data = target.read_bytes()
        except OSError:
            self._reject(HTTPStatus.NOT_FOUND, "not found")
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", STATIC_FILES[path])
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        if not host_allowed(self.headers.get("Host"), self.port):
            self._reject(HTTPStatus.FORBIDDEN, "invalid host")
            return
        path = urlsplit(self.path).path
        if path == "/api/health":
            self._send_json(HTTPStatus.OK, health_payload())
            return
        if path in STATIC_FILES:
            self._send_static(path)
            return
        self._reject(HTTPStatus.NOT_FOUND, "not found")

    def log_message(self, *args: object) -> None:
        # Silence default stderr access logging; never log request contents,
        # which will include sensitive data in later issues.
        return


def build_server(host: str = HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    """Create (but do not start) a loopback-bound server on ``host``/``port``.

    Passing ``port=0`` binds an ephemeral port (used by tests); the handler is
    told the *actual* bound port so its Host allowlist matches real requests.
    """
    handler = type("BoundHandler", (CAReviewHandler,), {})
    server = ThreadingHTTPServer((host, port), handler)
    handler.port = server.server_address[1]
    return server


def main() -> None:
    port = int(os.environ.get("CAREVIEW_PORT", DEFAULT_PORT))
    server = build_server(HOST, port)
    bound_host, bound_port = server.server_address[:2]
    print(f"CAreview serving on http://{bound_host}:{bound_port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
