"""Tests for the device-code auth manager (ISSUE-0002).

All tests use an injected fake transport and clock, so no network or real sign-in
is involved.
"""

from __future__ import annotations

import sys
import unittest
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
    def test_devicecode_request_targets_microsoft(self) -> None:
        url, data = auth.build_devicecode_request("organizations", auth.CLIENT_ID, auth.SCOPES)
        self.assertEqual(url, "https://login.microsoftonline.com/organizations/oauth2/v2.0/devicecode")
        self.assertIn(b"client_id=", data)

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


if __name__ == "__main__":
    unittest.main()
