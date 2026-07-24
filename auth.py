"""OAuth 2.0 device-code authentication for CAreview (ISSUE-0002).

Uses the Microsoft Graph PowerShell first-party public client to obtain a
delegated Microsoft Graph token via the device-code flow. No client secret and no
Azure app registration are involved. Tokens live only in this process's memory and
are never written to disk, logs, or the repository.

The manager is transport- and clock-injectable so the full poll state machine can
be unit-tested without any network access or real sign-in. The default transport
only ever contacts ``login.microsoftonline.com`` for the validated tenant.
"""

from __future__ import annotations

import json
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

# Microsoft Graph PowerShell first-party public client (public by design; not a
# secret). Chosen for broad delegated-scope device-code support.
CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"

# Delegated, read-only Graph scopes (resource-qualified for the v2 endpoint).
# No ``offline_access``: the MVP does not retain refresh tokens; the user
# re-authenticates when the access token expires (see DECISION-004 / ISSUE-0002).
SCOPES = (
    "https://graph.microsoft.com/Policy.Read.All "
    "https://graph.microsoft.com/Application.Read.All "
    "https://graph.microsoft.com/Directory.Read.All"
)

DEFAULT_TENANT = "organizations"
_TENANT_RE = re.compile(r"^[A-Za-z0-9._-]+$")

Transport = Callable[[str, bytes], "tuple[int, dict]"]


class AuthError(Exception):
    """A device-code request failed before a pollable session existed."""


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
    """Default transport: POST form data and return ``(status, parsed_json)``."""
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
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"error": "http_error", "error_description": raw[:200]}
        return exc.code, payload


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
        self._session: _Session | None = None
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    # -- sign-in lifecycle ------------------------------------------------
    def start(self, tenant: str = DEFAULT_TENANT) -> dict:
        """Begin a device-code sign-in, superseding any prior session."""
        url, data = build_devicecode_request(tenant, self.client_id, self.scopes)
        status, payload = self._transport(url, data)
        if status != 200 or "device_code" not in payload:
            raise AuthError(payload.get("error_description") or "device code request failed")
        now = self._clock()
        session = _Session(
            handle=secrets.token_urlsafe(18),
            device_code=payload["device_code"],
            user_code=payload["user_code"],
            verification_uri=payload.get("verification_uri") or payload.get("verification_url", ""),
            interval=int(payload.get("interval", 5)),
            expires_at=now + int(payload.get("expires_in", 900)),
            tenant=tenant,
        )
        # Single-concurrency: a new sign-in supersedes any pending one and clears
        # any existing token so state cannot be mixed across sessions.
        self._session = session
        self._access_token = None
        self._token_expires_at = 0.0
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

        url, data = build_token_request(session.tenant, self.client_id, session.device_code)
        status, payload = self._transport(url, data)
        if status == 200 and "access_token" in payload:
            self._access_token = payload["access_token"]
            self._token_expires_at = now + int(payload.get("expires_in", 3600))
            self._session = None
            return {"state": "success"}

        error = payload.get("error")
        if error == "authorization_pending":
            return {"state": "pending"}
        if error == "slow_down":
            session.interval += 5
            return {"state": "pending"}
        # Terminal errors (expired_token, authorization_declined, access_denied,
        # bad_verification_code, …): end the session.
        self._session = None
        return {"state": "error", "error": error or "unknown_error"}

    def logout(self) -> None:
        """Clear any pending session and token from memory."""
        self._session = None
        self._access_token = None
        self._token_expires_at = 0.0

    # -- token access (used by later issues) ------------------------------
    def get_token(self) -> str | None:
        """Return the access token if present and unexpired, else ``None``."""
        if self._access_token is not None and self._clock() < self._token_expires_at:
            return self._access_token
        # Expired or absent: drop it. The MVP re-authenticates rather than
        # refreshing (no refresh token is retained).
        self._access_token = None
        return None

    def is_authenticated(self) -> bool:
        return self.get_token() is not None
