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
// Round 1/round 2 (also F-001): reacting to a stale "success" client-side
// (round 1) or with an unawaited, unscoped authLogout() call (round 2) both
// proved unsafe — round 2's fresh review found the compensating logout could
// itself clear a different, newer session. ISSUE-0013 replaces both with a
// server-side scoped mechanism: cancellation calls authAbandon(handle) for
// the specific attempt being given up, at the moment of cancellation, and
// pollOnce() no longer reacts to staleness at all — the tests below assert
// exactly that division of responsibility.

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
  it("viewSampleData() abandons the in-flight attempt's exact handle and a later 'success' does not flip mode back to live", async () => {
    const pollDeferred = deferred<Response>();
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      void init;
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
      if (url.includes("/api/auth/abandon") || url.includes("/api/auth/logout")) {
        return Promise.resolve(jsonResponse({ state: "ok" }));
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

    // User moves to sample mode while that poll is still in flight. This
    // must abandon exactly handle "h1" server-side.
    await act(() => result.current.viewSampleData());
    expect(result.current.mode).toBe("sample");
    const abandonCall = fetchMock.mock.calls.find(([u]) => String(u).includes("/api/auth/abandon"));
    expect(abandonCall).toBeDefined();
    expect(JSON.parse(String(abandonCall?.[1]?.body))).toEqual({ handle: "h1" });

    // The stale poll now resolves "success" — the server-side abandon() call
    // already means this can never have installed/kept a token, and the
    // client must not flip mode back to "live" or fetch tenant data either way.
    pollDeferred.resolve({ ok: true, status: 200, json: async () => ({ state: "success" }) } as Response);
    await act(() => vi.runOnlyPendingTimersAsync());

    expect(result.current.mode).toBe("sample");
    expect(fetchMock.mock.calls.some(([u]) => String(u).includes("/api/policies"))).toBe(false);
    // pollOnce() no longer reacts to staleness with its own logout call —
    // cleanup happens once, at cancellation time, via authAbandon above.
    expect(fetchMock.mock.calls.some(([u]) => String(u).includes("/api/auth/logout"))).toBe(false);
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
      if (url.includes("/api/auth/abandon") || url.includes("/api/auth/logout")) {
        return Promise.resolve(jsonResponse({ state: "ok" }));
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
    expect(fetchMock.mock.calls.some(([u]) => String(u).includes("/api/auth/abandon"))).toBe(true);

    pollDeferred.resolve({ ok: true, status: 200, json: async () => ({ state: "pending" }) } as Response);
    await act(() => vi.runOnlyPendingTimersAsync());

    // A second poll would mean the stale attempt rescheduled itself.
    expect(pollCallCount).toBe(1);
    expect(result.current.mode).toBe("signedOut");
  });

  it("does not call authAbandon when there is no in-flight device-code attempt to cancel", async () => {
    const fetchMock = vi.fn((_input: RequestInfo | URL) => Promise.resolve(jsonResponse({ policies: [], analysis: { score: 100, scoreIsHeuristic: true, policyCount: 0, findings: [], evaluated: [], notEvaluable: [] } })));
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useAppState(), { wrapper: AppStateProvider });
    await act(() => result.current.viewSampleData());

    expect(fetchMock.mock.calls.some(([u]) => String(u).includes("/api/auth/abandon"))).toBe(false);
  });
});
