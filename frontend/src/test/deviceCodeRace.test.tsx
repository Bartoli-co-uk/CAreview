import { afterEach, describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { AppStateProvider, useAppState } from "../state/appState";

// Codex issue review finding F-001 (ISSUE-0012, round 0): a device-code poll
// that is still in flight when the user moves to sample mode, app-only mode,
// or signs out must never be allowed to later flip mode back to "live" or
// load tenant data. clearTimeout() alone can't stop an in-flight authPoll()
// request — this proves the authAttempt cancellation token actually blocks
// a stale poll response from mutating state after each such transition.
//
// Round 1 finding (also F-001): blocking the client-side state mutation
// isn't enough on its own — a stale "success" response means the *server*
// has already installed a live token for the abandoned attempt, and the
// client never reaches a mode with a "Sign out" control for it. The second
// test below proves the stale-success path compensates by calling
// authLogout() so that orphaned server-side session can't linger forever.

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((r) => {
    resolve = r;
  });
  return { promise, resolve };
}

function jsonResponse(body: unknown) {
  return { ok: true, status: 200, json: async () => body } as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("device-code polling cancellation", () => {
  it("a poll that resolves 'success' after viewSampleData() runs does not flip mode back to live", async () => {
    const pollDeferred = deferred<Response>();
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/auth/start")) {
        return Promise.resolve(
          jsonResponse({ handle: "h1", user_code: "ABC-123", verification_uri: "https://example.test", expires_in: 900, interval: 5 }),
        );
      }
      if (url.includes("/api/auth/poll")) {
        return pollDeferred.promise;
      }
      if (url.includes("/sample-data.json")) {
        return Promise.resolve(jsonResponse({ policies: [], analysis: { score: 100, scoreIsHeuristic: true, policyCount: 0, findings: [], evaluated: [], notEvaluable: [] } }));
      }
      if (url.includes("/api/auth/logout")) {
        return Promise.resolve(jsonResponse({ state: "signed_out" }));
      }
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    vi.useFakeTimers();

    const { result } = renderHook(() => useAppState(), { wrapper: AppStateProvider });

    // Start device-code sign-in; this fires authStart and, once the interval
    // elapses, schedules the first authPoll — which we'll leave pending.
    await act(() => result.current.startDeviceCodeSignIn("organizations"));
    await act(() => vi.advanceTimersByTimeAsync(5000));
    expect(fetchMock.mock.calls.some(([u]) => String(u).includes("/api/auth/poll"))).toBe(true);

    // User moves to sample mode while that poll is still in flight.
    await act(() => result.current.viewSampleData());
    expect(result.current.mode).toBe("sample");

    // The stale poll now resolves "success" — this must NOT flip mode back
    // to "live" or start loading tenant data out from under sample mode.
    pollDeferred.resolve({ ok: true, status: 200, json: async () => ({ state: "success" }) } as Response);
    await act(() => vi.runOnlyPendingTimersAsync());

    expect(result.current.mode).toBe("sample");
    expect(fetchMock.mock.calls.some(([u]) => String(u).includes("/api/policies"))).toBe(false);
    // The client dropped the stale success, but the server had already
    // installed a token for it — the client must compensate with a logout
    // so that session doesn't linger with no user-visible way to clear it.
    expect(fetchMock.mock.calls.filter(([u]) => String(u).includes("/api/auth/logout")).length).toBe(1);
  });

  it("a poll that resolves 'pending' after sign-out does not schedule another timer", async () => {
    const pollDeferred = deferred<Response>();
    let pollCallCount = 0;
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/auth/start")) {
        return Promise.resolve(
          jsonResponse({ handle: "h1", user_code: "ABC-123", verification_uri: "https://example.test", expires_in: 900, interval: 5 }),
        );
      }
      if (url.includes("/api/auth/poll")) {
        pollCallCount += 1;
        return pollDeferred.promise;
      }
      if (url.includes("/api/auth/logout")) {
        return Promise.resolve(jsonResponse({ state: "signed_out" }));
      }
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    vi.useFakeTimers();

    const { result } = renderHook(() => useAppState(), { wrapper: AppStateProvider });

    await act(() => result.current.startDeviceCodeSignIn("organizations"));
    await act(() => vi.advanceTimersByTimeAsync(5000));
    expect(pollCallCount).toBe(1);

    await act(() => result.current.signOut());
    expect(result.current.mode).toBe("signedOut");

    pollDeferred.resolve({ ok: true, status: 200, json: async () => ({ state: "pending" }) } as Response);
    await act(() => vi.runOnlyPendingTimersAsync());

    // A second poll would mean the stale attempt rescheduled itself.
    expect(pollCallCount).toBe(1);
    expect(result.current.mode).toBe("signedOut");
  });
});
