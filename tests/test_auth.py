"""Tests for the device-code auth manager (ISSUE-0002).

All tests use an injected fake transport and clock, so no network or real sign-in
is involved.
"""

from __future__ import annotations

import contextlib
import io
import json
import logging
import sys
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import auth  # noqa: E402


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeTransport:
    """Returns scripted (status, payload) pairs and records calls."""

    def __init__(self, script: list[tuple[int, dict]]) -> None:
        self.script = list(script)
        self.calls: list[str] = []

    def __call__(self, url: str, data: bytes) -> tuple[int, dict]:
        self.calls.append(url)
        if len(self.script) == 1:
            return self.script[0]
        return self.script.pop(0)


DEVICE_OK = (
    200,
    {
        "device_code": "DEV-SECRET",
        "user_code": "ABCD-EFGH",
        "verification_uri": "https://microsoft.com/devicelogin",
        "interval": 5,
        "expires_in": 900,
    },
)


def manager(script: list[tuple[int, dict]], clock: FakeClock) -> tuple[auth.AuthManager, FakeTransport]:
    transport = FakeTransport(script)
    return auth.AuthManager(transport=transport, clock=clock), transport


class RequestBuildingTests(unittest.TestCase):
    def test_scopes_is_policy_read_all_only(self) -> None:
        self.assertEqual(auth.SCOPES, "https://graph.microsoft.com/Policy.Read.All")

    def test_devicecode_request_targets_microsoft(self) -> None:
        url, data = auth.build_devicecode_request("organizations", auth.CLIENT_ID, auth.SCOPES)
        self.assertEqual(url, "https://login.microsoftonline.com/organizations/oauth2/v2.0/devicecode")
        self.assertIn(b"client_id=", data)

    def test_devicecode_request_body_carries_only_policy_read_all(self) -> None:
        _, data = auth.build_devicecode_request("organizations", auth.CLIENT_ID, auth.SCOPES)
        parsed = urllib.parse.parse_qs(data.decode("utf-8"))
        self.assertEqual(parsed["scope"], ["https://graph.microsoft.com/Policy.Read.All"])

    def test_token_request_uses_device_code_grant(self) -> None:
        url, data = auth.build_token_request("organizations", auth.CLIENT_ID, "DEV")
        self.assertTrue(url.endswith("/oauth2/v2.0/token"))
        self.assertIn(b"grant-type%3Adevice_code", data)

    def test_invalid_tenant_rejected(self) -> None:
        with self.assertRaises(auth.AuthError):
            auth.build_devicecode_request("evil.com/../foo", auth.CLIENT_ID, auth.SCOPES)


class LifecycleTests(unittest.TestCase):
    def test_start_returns_handle_not_device_code(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK], clock)
        result = mgr.start("organizations")
        self.assertIn("handle", result)
        self.assertEqual(result["user_code"], "ABCD-EFGH")
        self.assertNotIn("device_code", result)

    def test_pending_then_success(self) -> None:
        clock = FakeClock()
        mgr, _ = manager(
            [DEVICE_OK, (400, {"error": "authorization_pending"}),
             (200, {"access_token": "TOKEN", "expires_in": 3600})],
            clock,
        )
        handle = mgr.start()["handle"]
        self.assertEqual(mgr.poll(handle)["state"], "pending")
        clock.advance(6)
        self.assertEqual(mgr.poll(handle)["state"], "success")
        self.assertEqual(mgr.get_token(), "TOKEN")

    def test_server_controlled_cadence_skips_transport(self) -> None:
        clock = FakeClock()
        mgr, transport = manager([DEVICE_OK, (400, {"error": "authorization_pending"})], clock)
        handle = mgr.start()["handle"]
        calls_before = len(transport.calls)
        mgr.poll(handle)  # first poll hits the token endpoint
        mgr.poll(handle)  # immediate second poll must not hit it again
        self.assertEqual(len(transport.calls), calls_before + 1)

    def test_slow_down_widens_interval(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK, (400, {"error": "slow_down"})], clock)
        handle = mgr.start()["handle"]
        self.assertEqual(mgr.poll(handle)["state"], "pending")
        self.assertEqual(mgr._session.interval, 10)  # 5 + 5

    def test_device_code_expiry(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK], clock)
        handle = mgr.start()["handle"]
        clock.advance(901)
        self.assertEqual(mgr.poll(handle)["state"], "expired")

    def test_access_denied_is_terminal_error(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK, (400, {"error": "access_denied"})], clock)
        handle = mgr.start()["handle"]
        result = mgr.poll(handle)
        self.assertEqual(result["state"], "error")
        self.assertEqual(result["error"], "access_denied")

    def test_logout_clears_token(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK, (200, {"access_token": "T", "expires_in": 3600})], clock)
        handle = mgr.start()["handle"]
        mgr.poll(handle)
        self.assertTrue(mgr.is_authenticated())
        mgr.logout()
        self.assertFalse(mgr.is_authenticated())
        self.assertIsNone(mgr.get_token())

    def test_access_token_expiry(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK, (200, {"access_token": "T", "expires_in": 3600})], clock)
        handle = mgr.start()["handle"]
        mgr.poll(handle)
        self.assertEqual(mgr.get_token(), "T")
        clock.advance(3601)
        self.assertIsNone(mgr.get_token())

    def test_single_concurrency_supersedes(self) -> None:
        clock = FakeClock()
        mgr, _ = manager(
            [DEVICE_OK,
             (200, {"device_code": "D2", "user_code": "WXYZ", "verification_uri": "x", "interval": 5, "expires_in": 900})],
            clock,
        )
        first = mgr.start()["handle"]
        second = mgr.start()["handle"]
        self.assertNotEqual(first, second)
        self.assertEqual(mgr.poll(first)["state"], "error")  # old handle superseded

    def test_start_failure_raises(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([(400, {"error": "invalid_client", "error_description": "bad"})], clock)
        with self.assertRaises(auth.AuthError):
            mgr.start()

    def test_inflight_poll_after_logout_does_not_restore_token(self) -> None:
        # Simulate logout happening during the token network call: the stale poll
        # result must not install a token (F-001 concurrency fix).
        clock = FakeClock()
        holder: dict = {}

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            if "devicecode" in url:
                return DEVICE_OK
            holder["mgr"].logout()
            return (200, {"access_token": "T", "expires_in": 3600})

        mgr = auth.AuthManager(transport=transport, clock=clock)
        holder["mgr"] = mgr
        handle = mgr.start()["handle"]
        result = mgr.poll(handle)
        self.assertNotEqual(result.get("state"), "success")
        self.assertFalse(mgr.is_authenticated())

    def test_new_start_immediately_clears_prior_token(self) -> None:
        clock = FakeClock()
        mgr, _ = manager(
            [DEVICE_OK, (200, {"access_token": "T", "expires_in": 3600}),
             (200, {"device_code": "D2", "user_code": "WXYZ", "verification_uri": "x",
                    "interval": 5, "expires_in": 900})],
            clock,
        )
        handle = mgr.start()["handle"]
        mgr.poll(handle)
        self.assertTrue(mgr.is_authenticated())
        mgr.start()  # a new sign-in must invalidate the prior token at once
        self.assertFalse(mgr.is_authenticated())

    def test_inflight_start_after_logout_does_not_recreate_session(self) -> None:
        # logout() during a start()'s device-code call must win: the stale start
        # detects supersession and refuses to install its session (F-001 round 2).
        clock = FakeClock()
        holder: dict = {}

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            holder["mgr"].logout()  # logout during the device-code network call
            return DEVICE_OK

        mgr = auth.AuthManager(transport=transport, clock=clock)
        holder["mgr"] = mgr
        with self.assertRaises(auth.AuthError):
            mgr.start()
        self.assertIsNone(mgr._session)

    def test_network_error_during_poll_is_transient(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK, (0, {"error": "network_error"})], clock)
        handle = mgr.start()["handle"]
        self.assertEqual(mgr.poll(handle)["state"], "pending")
        self.assertIsNotNone(mgr._session)  # session intact for retry

    def test_bad_response_during_poll_is_transient(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([DEVICE_OK, (200, {"error": "bad_response"})], clock)
        handle = mgr.start()["handle"]
        self.assertEqual(mgr.poll(handle)["state"], "pending")

    def test_start_network_error_raises(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([(0, {"error": "network_error"})], clock)
        with self.assertRaises(auth.AuthError):
            mgr.start()

    def test_urllib_transport_normalizes_network_failure(self) -> None:
        # A transport-level failure returns (0, network_error), never raises.
        status, payload = auth.urllib_transport("https://localhost:1/oauth2/v2.0/token", b"x=1")
        self.assertEqual(status, 0)
        self.assertEqual(payload.get("error"), "network_error")


# Synthetic, non-real secret literal used only in tests (never a real credential;
# prohibited from ever appearing in a response, exception, repr, or log per
# AGENTS.md/RISK-008). Also exercised in URL-encoded and JSON-escaped forms below
# to prove no accidental leak survives encoding.
FAKE_SECRET = "test-only-fake-secret-DO-NOT-USE-xyz123"
FAKE_TENANT = "11111111-2222-3333-4444-555555555555"
FAKE_CLIENT_ID = "66666666-7777-8888-9999-aaaaaaaaaaaa"

APP_ONLY_OK = (200, {"access_token": "APP-TOKEN", "expires_in": 3600})


class AppOnlyRequestBuildingTests(unittest.TestCase):
    def test_build_client_credentials_request_shape(self) -> None:
        url, data = auth.build_client_credentials_request(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(url, f"https://login.microsoftonline.com/{FAKE_TENANT}/oauth2/v2.0/token")
        parsed = urllib.parse.parse_qs(data.decode("utf-8"))
        self.assertEqual(parsed["grant_type"], ["client_credentials"])
        self.assertEqual(parsed["client_id"], [FAKE_CLIENT_ID])
        self.assertEqual(parsed["client_secret"], [FAKE_SECRET])
        self.assertEqual(parsed["scope"], ["https://graph.microsoft.com/.default"])

    def test_organizations_common_consumers_rejected(self) -> None:
        for tenant in ("organizations", "common", "consumers"):
            with self.assertRaises(auth.AuthError):
                auth.build_client_credentials_request(tenant, FAKE_CLIENT_ID, FAKE_SECRET)

    def test_non_guid_non_domain_tenant_rejected(self) -> None:
        for tenant in ("not-a-tenant", "single-label", "", "..", "a" * 300):
            with self.assertRaises(auth.AuthError):
                auth.build_client_credentials_request(tenant, FAKE_CLIENT_ID, FAKE_SECRET)

    def test_guid_tenant_accepted(self) -> None:
        url, _ = auth.build_client_credentials_request(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertIn(FAKE_TENANT, url)

    def test_domain_style_tenant_accepted(self) -> None:
        url, _ = auth.build_client_credentials_request("contoso.onmicrosoft.com", FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertIn("contoso.onmicrosoft.com", url)

    def test_invalid_tenant_rejected_before_any_state_or_network(self) -> None:
        clock = FakeClock()
        calls: list[str] = []

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            calls.append(url)
            return APP_ONLY_OK

        mgr = auth.AuthManager(transport=transport, clock=clock)
        with self.assertRaises(auth.AuthError):
            mgr.start_app_only("organizations", FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(calls, [])  # no outbound request
        self.assertIsNone(mgr._app_only_secret)  # no state retained


class AppOnlyLifecycleTests(unittest.TestCase):
    def test_success_installs_token_and_retains_secret(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([APP_ONLY_OK], clock)
        result = mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(result, {"state": "success"})
        self.assertTrue(mgr.is_authenticated())
        self.assertEqual(mgr._app_only_secret, FAKE_SECRET)

    def test_wrong_client_id_is_provider_error(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([(401, {"error": "invalid_client", "error_description": "AADSTS700016 bad client"})], clock)
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(str(ctx.exception), "provider_error")

    def test_generic_provider_error(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([(400, {"error": "unauthorized_client"})], clock)
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(str(ctx.exception), "provider_error")

    def test_network_error_is_local_label(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([(0, {"error": "network_error"})], clock)
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(str(ctx.exception), "network_error")

    def test_transient_provider_error_is_local_label(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([(200, {"error": "bad_response"})], clock)
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(str(ctx.exception), "invalid_response")

    def test_silent_renewal_after_simulated_expiry(self) -> None:
        clock = FakeClock()
        mgr, transport = manager([APP_ONLY_OK, (200, {"access_token": "APP-TOKEN-2", "expires_in": 3600})], clock)
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        clock.advance(3601)  # simulate expiry
        self.assertEqual(mgr.get_token(), "APP-TOKEN-2")
        self.assertEqual(len(transport.calls), 2)  # initial + one renewal, no caller-supplied secret

    def test_renewal_failure_surfaces_as_no_token_not_a_crash(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([APP_ONLY_OK, (0, {"error": "network_error"})], clock)
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        clock.advance(3601)
        self.assertIsNone(mgr.get_token())
        self.assertFalse(mgr.is_authenticated())

    def test_logout_clears_retained_secret_and_stops_renewal(self) -> None:
        clock = FakeClock()
        mgr, transport = manager([APP_ONLY_OK], clock)
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        mgr.logout()
        self.assertIsNone(mgr._app_only_secret)
        clock.advance(3601)
        self.assertIsNone(mgr.get_token())
        self.assertEqual(len(transport.calls), 1)  # no renewal attempt after logout

    def test_device_code_start_supersedes_app_only_secret(self) -> None:
        clock = FakeClock()
        mgr, transport = manager([APP_ONLY_OK, DEVICE_OK], clock)
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        mgr.start()  # a device-code sign-in must supersede the app-only session
        self.assertIsNone(mgr._app_only_secret)
        self.assertFalse(mgr.is_authenticated())
        clock.advance(3601)
        self.assertIsNone(mgr.get_token())
        self.assertEqual(len(transport.calls), 2)  # no renewal call was made

    def test_app_only_start_supersedes_prior_app_only_secret(self) -> None:
        clock = FakeClock()
        mgr, _ = manager(
            [APP_ONLY_OK, (200, {"access_token": "APP-TOKEN-2", "expires_in": 3600})], clock
        )
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        other_secret = "test-only-other-fake-secret-abc789"
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, other_secret)
        self.assertEqual(mgr._app_only_secret, other_secret)

    def test_inflight_start_app_only_after_logout_does_not_install(self) -> None:
        # logout() during the client-credentials network call must win: the
        # stale start_app_only() must not install a token or retain the secret.
        clock = FakeClock()
        holder: dict = {}

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            holder["mgr"].logout()
            return APP_ONLY_OK

        mgr = auth.AuthManager(transport=transport, clock=clock)
        holder["mgr"] = mgr
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(str(ctx.exception), "superseded")
        self.assertIsNone(mgr._app_only_secret)
        self.assertFalse(mgr.is_authenticated())

    def test_inflight_start_app_only_after_new_start_does_not_install(self) -> None:
        clock = FakeClock()
        holder: dict = {}

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            if not holder.get("superseded"):
                holder["superseded"] = True
                holder["mgr"].start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, "test-only-second-fake-secret")
            return APP_ONLY_OK

        mgr = auth.AuthManager(transport=transport, clock=clock)
        holder["mgr"] = mgr
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertEqual(str(ctx.exception), "superseded")
        # The newer, in-flight-triggered start_app_only() call itself must still
        # succeed and own the final state.
        self.assertEqual(mgr._app_only_secret, "test-only-second-fake-secret")

    def test_inflight_renewal_after_logout_does_not_reinstall_token(self) -> None:
        # logout() during a renewal's network call must win: the stale renewal
        # response must not resurrect a token or the cleared secret.
        clock = FakeClock()
        holder: dict = {}
        calls: list[int] = []

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            calls.append(1)
            if len(calls) == 1:
                return APP_ONLY_OK
            holder["mgr"].logout()
            return (200, {"access_token": "STALE-RENEWED-TOKEN", "expires_in": 3600})

        mgr = auth.AuthManager(transport=transport, clock=clock)
        holder["mgr"] = mgr
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        clock.advance(3601)
        self.assertIsNone(mgr.get_token())
        self.assertIsNone(mgr._app_only_secret)

    def test_inflight_renewal_after_new_start_app_only_does_not_install(self) -> None:
        # A fresh start_app_only() issued while a renewal is outstanding must
        # win; the stale renewal response must not overwrite the new state.
        clock = FakeClock()
        holder: dict = {}
        calls: list[int] = []

        def transport(url: str, data: bytes) -> tuple[int, dict]:
            calls.append(1)
            if len(calls) == 1:
                return APP_ONLY_OK
            if len(calls) == 2:
                # This is the renewal call; a new sign-in supersedes it mid-flight.
                holder["mgr"].start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, "test-only-newer-fake-secret")
                return (200, {"access_token": "STALE-RENEWED-TOKEN", "expires_in": 3600})
            return (200, {"access_token": "NEWER-TOKEN", "expires_in": 3600})

        mgr = auth.AuthManager(transport=transport, clock=clock)
        holder["mgr"] = mgr
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        clock.advance(3601)
        mgr.get_token()
        self.assertEqual(mgr._app_only_secret, "test-only-newer-fake-secret")
        self.assertNotEqual(mgr._access_token, "STALE-RENEWED-TOKEN")


class AppOnlySecretLeakTests(unittest.TestCase):
    """Proves the fake secret literal never surfaces anywhere observable."""

    def test_secret_absent_from_success_return_value(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([APP_ONLY_OK], clock)
        result = mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertNotIn(FAKE_SECRET, repr(result))

    def test_secret_absent_from_manager_repr(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([APP_ONLY_OK], clock)
        mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertNotIn(FAKE_SECRET, repr(mgr))

    def test_secret_absent_from_exception_message_literal(self) -> None:
        clock = FakeClock()
        mgr, _ = manager(
            [(400, {"error": "unauthorized_client", "error_description": f"bad secret {FAKE_SECRET}"})], clock
        )
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertNotIn(FAKE_SECRET, str(ctx.exception))

    def test_secret_absent_from_exception_message_url_encoded(self) -> None:
        clock = FakeClock()
        encoded = urllib.parse.quote(FAKE_SECRET)
        mgr, _ = manager(
            [(400, {"error": "unauthorized_client", "error_description": f"bad secret {encoded}"})], clock
        )
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertNotIn(FAKE_SECRET, str(ctx.exception))
        self.assertNotIn(encoded, str(ctx.exception))

    def test_secret_absent_from_exception_message_json_escaped(self) -> None:
        clock = FakeClock()
        escaped = json.dumps(FAKE_SECRET)
        mgr, _ = manager(
            [(400, {"error": "unauthorized_client", "error_description": f"bad secret: {escaped}"})], clock
        )
        with self.assertRaises(auth.AuthError) as ctx:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
        self.assertNotIn(FAKE_SECRET, str(ctx.exception))

    def test_secret_absent_from_logging_output(self) -> None:
        clock = FakeClock()
        mgr, _ = manager([APP_ONLY_OK], clock)
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger()
        logger.addHandler(handler)
        try:
            mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
            mgr.logout()
        finally:
            logger.removeHandler(handler)
        self.assertNotIn(FAKE_SECRET, stream.getvalue())

    def test_secret_absent_from_stderr(self) -> None:
        clock = FakeClock()
        mgr, _ = manager(
            [(400, {"error": "unauthorized_client", "error_description": FAKE_SECRET})], clock
        )
        captured = io.StringIO()
        with contextlib.redirect_stderr(captured):
            try:
                mgr.start_app_only(FAKE_TENANT, FAKE_CLIENT_ID, FAKE_SECRET)
            except auth.AuthError:
                pass
        self.assertNotIn(FAKE_SECRET, captured.getvalue())


if __name__ == "__main__":
    unittest.main()
