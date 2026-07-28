import { afterEach, describe, expect, it, vi } from "vitest";
import { fetchAnalysis, fetchPolicies } from "../api/client";

function mockFetchOnce(status: number, body: unknown, ok = status >= 200 && status < 300) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status,
      json: async () => body,
    }),
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fetchPolicies / fetchAnalysis error branches", () => {
  it("returns ok:true with data on 200", async () => {
    mockFetchOnce(200, { policies: [], count: 0 });
    const result = await fetchPolicies();
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.data.count).toBe(0);
  });

  it("maps 401 to not_authenticated", async () => {
    mockFetchOnce(401, { error: "not_authenticated" });
    const result = await fetchPolicies();
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toBe("not_authenticated");
  });

  it("maps 403 to consent_required with message", async () => {
    mockFetchOnce(403, { error: "consent_required", message: "admin consent needed" });
    const result = await fetchAnalysis();
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toBe("consent_required");
      expect(result.message).toBe("admin consent needed");
    }
  });

  it("maps 502 graph_error", async () => {
    mockFetchOnce(502, { error: "graph_error", message: "unexpected error" });
    const result = await fetchPolicies();
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toBe("graph_error");
  });

  it("maps 502 invalid_url", async () => {
    mockFetchOnce(502, { error: "invalid_url" });
    const result = await fetchAnalysis();
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toBe("invalid_url");
  });

  it("maps an unrecognized error code to unknown_error", async () => {
    mockFetchOnce(500, { error: "something_else" });
    const result = await fetchPolicies();
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toBe("unknown_error");
  });

  it("maps a network failure (fetch throws) to network_error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("connection refused")),
    );
    const result = await fetchPolicies();
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toBe("network_error");
  });
});
