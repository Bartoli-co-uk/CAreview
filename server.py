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
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import analyzer
import auth
import graph

# Process-wide in-memory authentication state (device-code session + token).
AUTH = auth.AuthManager()
# Read-only Microsoft Graph client for Conditional Access policies.
GRAPH = graph.GraphClient()

# Optional, user-supplied break-glass account object IDs (sanitized GUIDs), held
# in memory only and never persisted. Used by the break-glass analysis rule.
_BG_LOCK = threading.Lock()
_break_glass_ids: list[str] = []


def set_break_glass_ids(ids: object) -> list[str]:
    with _BG_LOCK:
        _break_glass_ids[:] = graph.sanitize_object_ids(ids)
        return list(_break_glass_ids)


def get_break_glass_ids() -> list[str]:
    with _BG_LOCK:
        return list(_break_glass_ids)

# Reject request bodies larger than this; the JSON we accept is tiny.
MAX_BODY_BYTES = 64 * 1024

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
    # Committed, sanitized sample data so the UI can be reviewed offline without
    # signing in (ISSUE-0005). Contains no real tenant data.
    "/sample-data.json": "application/json; charset=utf-8",
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

    def _send_security_headers(self) -> None:
        # Defense-in-depth alongside the HTML <meta> CSP: a real HTTP header
        # also covers non-HTML responses and supports frame-ancestors, which a
        # meta tag cannot express.
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; base-uri 'none'; form-action 'none'; "
            "object-src 'none'; frame-ancestors 'none'",
        )
        self.send_header("X-Content-Type-Options", "nosniff")

    def _reject(self, status: HTTPStatus, message: str) -> None:
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: HTTPStatus, payload: dict, *, no_store: bool = False) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if no_store:
            # Sensitive tenant data (policies/analysis) must never be cached.
            self.send_header("Cache-Control", "no-store")
        self._send_security_headers()
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
        self._send_security_headers()
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
        if path == "/api/policies":
            self._policies()
            return
        if path == "/api/analysis":
            self._analysis()
            return
        if path in STATIC_FILES:
            self._send_static(path)
            return
        self._reject(HTTPStatus.NOT_FOUND, "not found")

    def _policies(self) -> None:
        token = AUTH.get_token()
        if not token:
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "not_authenticated"})
            return
        try:
            policies = GRAPH.fetch_policies(token)
        except graph.GraphError as exc:
            status = {
                "not_authenticated": HTTPStatus.UNAUTHORIZED,
                "consent_required": HTTPStatus.FORBIDDEN,
            }.get(exc.code, HTTPStatus.BAD_GATEWAY)
            self._send_json(status, {"error": exc.code, "message": str(exc)})
            return
        except Exception:  # noqa: BLE001 — never leak an internal error/stack to the client
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "graph_error", "message": "unexpected error"})
            return
        self._send_json(HTTPStatus.OK, {"policies": policies, "count": len(policies)}, no_store=True)

    def _analysis(self) -> None:
        token = AUTH.get_token()
        if not token:
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "not_authenticated"})
            return
        try:
            policies = GRAPH.fetch_policies(token)
        except graph.GraphError as exc:
            status = {
                "not_authenticated": HTTPStatus.UNAUTHORIZED,
                "consent_required": HTTPStatus.FORBIDDEN,
            }.get(exc.code, HTTPStatus.BAD_GATEWAY)
            self._send_json(status, {"error": exc.code, "message": str(exc)})
            return
        except Exception:  # noqa: BLE001 — never leak an internal error/stack to the client
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "graph_error", "message": "unexpected error"})
            return
        self._send_json(HTTPStatus.OK, analyzer.analyze(policies, get_break_glass_ids()), no_store=True)

    def _read_json_body(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        if length < 0 or length > MAX_BODY_BYTES:
            return None
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        if not host_allowed(self.headers.get("Host"), self.port):
            self._reject(HTTPStatus.FORBIDDEN, "invalid host")
            return
        # State-changing endpoints require a same-origin request (CSRF / cross-site
        # defence layered on top of the Host allowlist).
        if not origin_allowed(self.headers.get("Origin"), self.port):
            self._reject(HTTPStatus.FORBIDDEN, "invalid origin")
            return
        path = urlsplit(self.path).path
        body = self._read_json_body()
        if body is None:
            self._reject(HTTPStatus.BAD_REQUEST, "invalid request body")
            return
        try:
            if path == "/api/auth/start":
                self._auth_start(body)
                return
            if path == "/api/auth/poll":
                self._auth_poll(body)
                return
            if path == "/api/auth/logout":
                AUTH.logout()
                self._send_json(HTTPStatus.OK, {"state": "signed_out"})
                return
            if path == "/api/breakglass":
                # Optional local input: sanitized GUIDs, in memory only. An empty
                # or missing list clears it.
                stored = set_break_glass_ids(body.get("ids", []))
                self._send_json(HTTPStatus.OK, {"count": len(stored)})
                return
        except Exception:  # noqa: BLE001 — never leak an internal error/stack to the client
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"state": "error", "error": "internal_error"})
            return
        self._reject(HTTPStatus.NOT_FOUND, "not found")

    def _auth_start(self, body: dict) -> None:
        tenant = body.get("tenant") or auth.DEFAULT_TENANT
        if not isinstance(tenant, str):
            self._reject(HTTPStatus.BAD_REQUEST, "invalid tenant")
            return
        try:
            result = AUTH.start(tenant)
        except auth.AuthError as exc:
            self._send_json(HTTPStatus.BAD_GATEWAY, {"state": "error", "error": str(exc)})
            return
        self._send_json(HTTPStatus.OK, result)

    def _auth_poll(self, body: dict) -> None:
        handle = body.get("handle")
        if not isinstance(handle, str) or not handle:
            self._reject(HTTPStatus.BAD_REQUEST, "missing handle")
            return
        self._send_json(HTTPStatus.OK, AUTH.poll(handle))

    def log_message(self, *args: object) -> None:
        # Silence default stderr access logging; never log request contents,
        # which will include sensitive data in later issues.
        return


# Bind addresses this server is permitted to listen on. Loopback-only is an
# invariant: the server must never be exposed on a routable interface.
_LOOPBACK_BIND_ADDRESSES = frozenset({"127.0.0.1", "localhost", "::1"})


def build_server(host: str = HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    """Create (but do not start) a loopback-bound server on ``host``/``port``.

    Passing ``port=0`` binds an ephemeral port (used by tests); the handler is
    told the *actual* bound port so its Host allowlist matches real requests.

    ``host`` must be a loopback address; a non-loopback bind (e.g. ``0.0.0.0``)
    is rejected so this factory cannot be reused to expose the listener.
    """
    if host not in _LOOPBACK_BIND_ADDRESSES:
        raise ValueError(f"refusing non-loopback bind address: {host!r}")
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
