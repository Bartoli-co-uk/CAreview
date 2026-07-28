"""OAuth 2.0 device-code and app-only authentication for CAreview.

Device-code flow (ISSUE-0002) uses the Microsoft Graph PowerShell first-party
public client to obtain a delegated Microsoft Graph token. No client secret and
no Azure app registration are involved.

App-only flow (ISSUE-0008, opt-in, brief v2 / ``DECISION-014``) uses the OAuth
2.0 client-credentials grant against a user-supplied tenant, app registration
client ID, and client secret. Per ``DECISION-014``, the submitted secret is
retained in this manager instance's memory for the whole app-only session (not
discarded after the first request) and reused to silently mint a fresh token on
expiry with no re-entry required; it is cleared on logout, on supersession by a
new sign-in (either mode), and on process exit. It is never written to disk,
logs, or any tracked file, and never appears in a returned value, a raised
exception, or this manager's ``repr()`` — failures map to a small fixed set of
local error labels rather than echoing provider response text.

Tokens (either mode) live only in this process's memory and are never written to
disk, logs, or the repository.

The manager is transport- and clock-injectable so the full poll state machine and
the app-only lifecycle can be unit-tested without any network access or real
sign-in. The default transport only ever contacts ``login.microsoftonline.com``
for the validated tenant.
"""

from __future__ import annotations

import json
import re
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

# Transport-level failures (network, timeout, malformed response) are surfaced as
# these sentinel error codes rather than raised, so a blip during polling is
# retried instead of crashing the request handler.
_TRANSIENT_ERRORS = frozenset({"network_error", "bad_response"})

# Microsoft Graph PowerShell first-party public client (public by design; not a
# secret). Chosen for broad delegated-scope device-code support.
CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"

# Delegated, read-only Graph scope (resource-qualified for the v2 endpoint).
# No ``offline_access``: the MVP does not retain refresh tokens; the user
# re-authenticates when the access token expires (see DECISION-004 / ISSUE-0002).
# Trimmed to Policy.Read.All alone (ISSUE-0007): graph.py only ever calls
# identity/conditionalAccess/policies, so Application.Read.All and
# Directory.Read.All were requested but never used.
SCOPES = "https://graph.microsoft.com/Policy.Read.All"

DEFAULT_TENANT = "organizations"
_TENANT_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# App-only mode requests whatever application permissions the app registration
# already holds (brief A7: the client cannot request a narrower app-only scope).
APP_ONLY_SCOPE = "https://graph.microsoft.com/.default"

# App-only tenant validation is stricter than the device-code path's: the
# multi-tenant aliases below are meaningless for a specific app registration's
# client-credentials grant, and only a GUID or a DNS-style domain identifies one
# tenant unambiguously (DECISION-014, brief v2 Q5).
_APP_ONLY_DISALLOWED_TENANTS = frozenset({"organizations", "common", "consumers"})
_GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_DOMAIN_LABEL = r"(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
_DOMAIN_RE = re.compile(rf"^{_DOMAIN_LABEL}(\.{_DOMAIN_LABEL})+$")

Transport = Callable[[str, bytes], "tuple[int, dict]"]


class AuthError(Exception):
    """A device-code request failed before a pollable session existed."""


def _safe_error(payload: dict) -> str:
    """A short, non-sensitive error label from a provider payload."""
    value = payload.get("error_description") or payload.get("error")
    return str(value)[:200] if value else ""


def _classify_app_only_error(status: int, payload: dict) -> str:
    """Map any app-only failure to one of a small, fixed set of local labels.

    Never returns provider-supplied text (error description, error code, or
    any other field): the client secret must never be able to reach a raised
    exception even if a compromised or misconfigured provider response were to
    echo it back, literally, URL-encoded, or JSON-escaped.
    """
    if status == 0:
        return "network_error"
    if payload.get("error") == "bad_response":
        return "invalid_response"
    return "provider_error"


def _authority(tenant: str) -> str:
    # Validate the tenant so it cannot redirect the request to another host
    # (SSRF/open-redirect defence): only a GUID or a simple label is allowed.
    if not _TENANT_RE.fullmatch(tenant):
        raise AuthError("invalid tenant")
    return f"https://login.microsoftonline.com/{tenant}"


def build_devicecode_request(tenant: str, client_id: str, scopes: str) -> tuple[str, bytes]:
    url = f"{_authority(tenant)}/oauth2/v2.0/devicecode"
    data = urllib.parse.urlencode({"client_id": client_id, "scope": scopes}).encode("utf-8")
    return url, data


def _app_only_authority(tenant: str) -> str:
    # Reject the multi-tenant aliases and anything that is not a GUID or a
    # DNS-style domain, before any outbound request (DECISION-014).
    if tenant in _APP_ONLY_DISALLOWED_TENANTS:
        raise AuthError("invalid_tenant")
    if not (_GUID_RE.fullmatch(tenant) or _DOMAIN_RE.fullmatch(tenant)):
        raise AuthError("invalid_tenant")
    return f"https://login.microsoftonline.com/{tenant}"


def build_client_credentials_request(
    tenant: str, client_id: str, client_secret: str
) -> tuple[str, bytes]:
    # No caller-supplied scope: app-only mode always requests exactly
    # APP_ONLY_SCOPE (brief A7 — narrower app-only scopes cannot be requested;
    # ISSUE-0008 F-001 — the scope must not be overridable at all).
    url = f"{_app_only_authority(tenant)}/oauth2/v2.0/token"
    data = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": APP_ONLY_SCOPE,
        }
    ).encode("utf-8")
    return url, data


def build_token_request(tenant: str, client_id: str, device_code: str) -> tuple[str, bytes]:
    url = f"{_authority(tenant)}/oauth2/v2.0/token"
    data = urllib.parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": client_id,
            "device_code": device_code,
        }
    ).encode("utf-8")
    return url, data


def urllib_transport(url: str, data: bytes) -> tuple[int, dict]:
    """Default transport: POST form data and return ``(status, parsed_json)``.

    All failure modes are converted to a ``(status, dict)`` result rather than
    raised: network/timeout/connection errors become ``(0, {"error":
    "network_error"})`` and a non-JSON or non-object body becomes
    ``{"error": "bad_response"}``. No response body is echoed back.
    """
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
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
    if not isinstance(payload, dict):
        return status, {"error": "bad_response"}
    return status, payload


@dataclass
class _Session:
    handle: str
    device_code: str
    user_code: str
    verification_uri: str
    interval: int
    expires_at: float
    tenant: str
    last_poll: float = field(default=0.0)


class AuthManager:
    """In-memory device-code session and token holder (single active session)."""

    def __init__(
        self,
        *,
        client_id: str = CLIENT_ID,
        scopes: str = SCOPES,
        transport: Transport | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.client_id = client_id
        self.scopes = scopes
        self._transport: Transport = transport or urllib_transport
        self._clock = clock
        # A single lock serializes all lifecycle transitions. The blocking network
        # call in poll() happens OUTSIDE the lock; the result is only installed if
        # the same session object is still current (identity check), so a logout or
        # a superseding start during the call cannot be overwritten by a stale poll.
        self._lock = threading.RLock()
        # Monotonic lifecycle counter: every start() and logout() bumps it, so an
        # in-flight start whose network call overlaps a newer start or a logout can
        # detect that it is stale and refuse to install its session.
        self._generation = 0
        self._session: _Session | None = None
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0
        # The device-code handle that produced the currently installed access
        # token, if any (ISSUE-0013). None for an app-only token, or once no
        # device-code-derived token is installed. Lets abandon() clear exactly
        # the attempt named by its handle without disturbing a different,
        # newer session — unlike logout(), which clears whatever is current
        # unconditionally.
        self._token_handle: str | None = None
        # App-only (client-credentials) state, retained for the session per
        # DECISION-014 so get_token() can silently renew on expiry. None outside
        # an active app-only session.
        self._app_only_tenant: str | None = None
        self._app_only_client_id: str | None = None
        self._app_only_secret: str | None = None

    # -- sign-in lifecycle ------------------------------------------------
    def start(self, tenant: str = DEFAULT_TENANT) -> dict:
        """Begin a device-code sign-in, superseding any prior session."""
        with self._lock:
            self._generation += 1
            generation = self._generation
            # Immediately supersede any existing session/token: a new sign-in
            # invalidates the old handle the instant it begins — even before the
            # new device code arrives and even if the request then fails — so the
            # old handle can never be polled during the in-flight window
            # (single-concurrency acceptance criterion).
            self._session = None
            self._access_token = None
            self._token_expires_at = 0.0
            self._token_handle = None
            self._app_only_tenant = None
            self._app_only_client_id = None
            self._app_only_secret = None
        url, data = build_devicecode_request(tenant, self.client_id, self.scopes)
        status, payload = self._transport(url, data)
        if status != 200 or "device_code" not in payload or "user_code" not in payload:
            raise AuthError(_safe_error(payload) or "device code request failed")
        try:
            interval = int(payload.get("interval", 5))
            expires_in = int(payload.get("expires_in", 900))
        except (TypeError, ValueError):
            raise AuthError("malformed device code response")
        with self._lock:
            # A newer start() or a logout() during the network call wins.
            if generation != self._generation:
                raise AuthError("superseded")
            now = self._clock()
            session = _Session(
                handle=secrets.token_urlsafe(18),
                device_code=payload["device_code"],
                user_code=payload["user_code"],
                verification_uri=payload.get("verification_uri") or payload.get("verification_url", ""),
                interval=interval,
                expires_at=now + expires_in,
                tenant=tenant,
            )
            # Single-concurrency: supersede any pending session and clear any token.
            self._session = session
            self._access_token = None
            self._token_expires_at = 0.0
            self._token_handle = None
            return {
                "handle": session.handle,
                "user_code": session.user_code,
                "verification_uri": session.verification_uri,
                "expires_in": int(session.expires_at - now),
                "interval": session.interval,
            }

    def poll(self, handle: str) -> dict:
        """Advance the sign-in for ``handle``; returns a state dict.

        States: ``pending``, ``success``, ``expired``, ``error``. Polling cadence
        is server-controlled: calls faster than the interval return ``pending``
        without contacting the token endpoint, and ``slow_down`` widens it.
        """
        with self._lock:
            session = self._session
            if session is None or handle != session.handle:
                return {"state": "error", "error": "unknown_or_superseded_handle"}
            now = self._clock()
            if now >= session.expires_at:
                self._session = None
                return {"state": "expired"}
            if session.last_poll and (now - session.last_poll) < session.interval:
                return {"state": "pending"}
            session.last_poll = now
            tenant, device_code = session.tenant, session.device_code

        url, data = build_token_request(tenant, self.client_id, device_code)
        status, payload = self._transport(url, data)

        with self._lock:
            # Only act if this poll's session is still the current one; a logout or
            # a superseding start during the network call invalidates the result.
            if self._session is not session:
                return {"state": "error", "error": "superseded"}
            if status == 200 and "access_token" in payload:
                try:
                    expires_in = int(payload.get("expires_in", 3600))
                except (TypeError, ValueError):
                    expires_in = 3600
                self._access_token = payload["access_token"]
                self._token_expires_at = self._clock() + expires_in
                self._token_handle = session.handle
                self._session = None
                return {"state": "success"}
            error = payload.get("error")
            if error in _TRANSIENT_ERRORS or error == "authorization_pending":
                return {"state": "pending"}
            if error == "slow_down":
                session.interval += 5
                return {"state": "pending"}
            # Terminal provider errors (expired_token, authorization_declined,
            # access_denied, bad_verification_code, unexpected response, …).
            self._session = None
            return {"state": "error", "error": error or "unexpected_response"}

    def logout(self) -> None:
        """Clear any pending session, token, and retained app-only secret."""
        with self._lock:
            self._generation += 1  # invalidate any in-flight start()/start_app_only()
            self._session = None
            self._access_token = None
            self._token_expires_at = 0.0
            self._token_handle = None
            self._app_only_tenant = None
            self._app_only_client_id = None
            self._app_only_secret = None

    def abandon(self, handle: str) -> None:
        """Clear only the device-code attempt named by ``handle`` (ISSUE-0013).

        Unlike ``logout()``, this never touches ``_generation`` or app-only
        state, and only clears the pending session or installed token if
        either is still the one ``handle`` produced. A handle that no longer
        matches anything current — because a newer sign-in, or an earlier
        ``abandon()``/``logout()``, has already superseded it — is a safe
        no-op: this is what lets a client tell the server "I've given up on
        this attempt" without any risk of clearing a different, newer,
        legitimately-current session, regardless of network timing.
        """
        with self._lock:
            if self._session is not None and self._session.handle == handle:
                self._session = None
            if self._token_handle == handle:
                self._access_token = None
                self._token_expires_at = 0.0
                self._token_handle = None

    # -- app-only (client-credentials) lifecycle (ISSUE-0008) --------------
    def start_app_only(self, tenant: str, client_id: str, client_secret: str) -> dict:
        """Acquire an app-only token, superseding any prior session/token.

        Validates ``tenant`` before touching any state or the network. On
        success, retains ``client_secret`` for the session (DECISION-014) so
        ``get_token()`` can silently renew. Raises ``AuthError`` with a stable
        local label on any failure; the raw provider response is never
        returned or retained.
        """
        _app_only_authority(tenant)  # raises AuthError("invalid_tenant") first
        with self._lock:
            self._generation += 1
            generation = self._generation
            # Immediately supersede any existing session/token/secret, mirroring
            # start()'s single-concurrency guarantee.
            self._session = None
            self._access_token = None
            self._token_expires_at = 0.0
            self._token_handle = None
            self._app_only_tenant = None
            self._app_only_client_id = None
            self._app_only_secret = None
        url, data = build_client_credentials_request(tenant, client_id, client_secret)
        status, payload = self._transport(url, data)
        with self._lock:
            if generation != self._generation:
                raise AuthError("superseded")
            if status != 200 or "access_token" not in payload:
                raise AuthError(_classify_app_only_error(status, payload))
            try:
                expires_in = int(payload.get("expires_in", 3600))
            except (TypeError, ValueError):
                raise AuthError("invalid_response")
            self._access_token = payload["access_token"]
            self._token_expires_at = self._clock() + expires_in
            self._app_only_tenant = tenant
            self._app_only_client_id = client_id
            self._app_only_secret = client_secret
            return {"state": "success"}

    def _renew_app_only(self) -> bool:
        """Silently mint a fresh app-only token from the retained secret.

        Returns ``True`` if a valid token is installed afterward. The network
        call happens outside the lock; the result is only installed if this
        manager's generation has not changed meanwhile (logout or a new
        sign-in during the call wins), mirroring ``poll()``'s stale-response
        guard.
        """
        with self._lock:
            if self._app_only_secret is None:
                return False
            generation = self._generation
            tenant = self._app_only_tenant
            client_id = self._app_only_client_id
            secret = self._app_only_secret
        url, data = build_client_credentials_request(tenant, client_id, secret)
        status, payload = self._transport(url, data)
        with self._lock:
            if generation != self._generation:
                return False
            if status != 200 or "access_token" not in payload:
                self._access_token = None
                self._token_expires_at = 0.0
                return False
            try:
                expires_in = int(payload.get("expires_in", 3600))
            except (TypeError, ValueError):
                expires_in = 3600
            self._access_token = payload["access_token"]
            self._token_expires_at = self._clock() + expires_in
            return True

    # -- token access -------------------------------------------------------
    def get_token(self) -> str | None:
        """Return the access token if present and unexpired, else ``None``.

        For an app-only session, an expired token triggers one silent renewal
        attempt using the retained secret (DECISION-014) before giving up.
        """
        with self._lock:
            if self._access_token is not None and self._clock() < self._token_expires_at:
                return self._access_token
            # Expired or absent: drop it. The device-code path re-authenticates
            # rather than refreshing (no refresh token is retained); the
            # app-only path below renews instead.
            self._access_token = None
            has_app_only = self._app_only_secret is not None
        if not has_app_only:
            return None
        if not self._renew_app_only():
            return None
        with self._lock:
            if self._access_token is not None and self._clock() < self._token_expires_at:
                return self._access_token
            return None

    def is_authenticated(self) -> bool:
        return self.get_token() is not None
