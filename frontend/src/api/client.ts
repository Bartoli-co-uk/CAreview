import type {
  ApiErrorCode,
  ApiResult,
  Analysis,
  AuthAppOnlyResponse,
  AuthErrorResponse,
  AuthPollResponse,
  AuthStartResponse,
  PoliciesResponse,
} from "./types";

const KNOWN_ERROR_CODES: ReadonlySet<ApiErrorCode> = new Set([
  "not_authenticated",
  "consent_required",
  "graph_error",
  "invalid_url",
]);

async function getJson<T>(path: string): Promise<ApiResult<T>> {
  let response: Response;
  try {
    response = await fetch(path, { headers: { Accept: "application/json" } });
  } catch {
    return { ok: false, status: 0, error: "network_error" };
  }
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (response.ok) {
    return { ok: true, data: body as T };
  }
  const errBody = (body ?? {}) as { error?: string; message?: string };
  const code = errBody.error;
  const error: ApiErrorCode | "unknown_error" =
    code && KNOWN_ERROR_CODES.has(code as ApiErrorCode) ? (code as ApiErrorCode) : "unknown_error";
  return { ok: false, status: response.status, error, message: errBody.message };
}

async function postJson<T>(path: string, payload: unknown): Promise<{ ok: boolean; status: number; data: T | null }> {
  let response: Response;
  try {
    response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload ?? {}),
    });
  } catch {
    return { ok: false, status: 0, data: null };
  }
  let body: T | null = null;
  try {
    body = (await response.json()) as T;
  } catch {
    body = null;
  }
  return { ok: response.ok, status: response.status, data: body };
}

export function fetchHealth(): Promise<ApiResult<{ status: string }>> {
  return getJson("/api/health");
}

export function fetchPolicies(): Promise<ApiResult<PoliciesResponse>> {
  return getJson("/api/policies");
}

export function fetchAnalysis(): Promise<ApiResult<Analysis>> {
  return getJson("/api/analysis");
}

export async function fetchSampleData(): Promise<ApiResult<{ policies: PoliciesResponse["policies"]; analysis: Analysis }>> {
  return getJson("/sample-data.json");
}

export async function authStart(tenant: string): Promise<{ ok: boolean; data: AuthStartResponse | AuthErrorResponse | null }> {
  const result = await postJson<AuthStartResponse | AuthErrorResponse>("/api/auth/start", { tenant });
  return { ok: result.ok, data: result.data };
}

export async function authPoll(handle: string): Promise<AuthPollResponse> {
  const result = await postJson<AuthPollResponse>("/api/auth/poll", { handle });
  return result.data ?? { state: "error", error: "network_error" };
}

export async function authAppOnly(
  tenant: string,
  clientId: string,
  clientSecret: string,
): Promise<{ ok: boolean; data: AuthAppOnlyResponse | AuthErrorResponse | null }> {
  const result = await postJson<AuthAppOnlyResponse | AuthErrorResponse>("/api/auth/app", {
    tenant,
    client_id: clientId,
    client_secret: clientSecret,
  });
  return { ok: result.ok, data: result.data };
}

export async function authLogout(): Promise<void> {
  await postJson("/api/auth/logout", {});
}

// Tells the server to abandon exactly the device-code attempt named by
// `handle` (ISSUE-0013) — scoped, unlike authLogout(), so it can never clear
// a different, newer session. Returns whether the request was actually
// delivered and acknowledged, so the caller can retry on failure rather than
// silently treating cleanup as done (round-0 review finding).
export async function authAbandon(handle: string): Promise<boolean> {
  const result = await postJson<{ state: string }>("/api/auth/abandon", { handle });
  return result.ok;
}

export async function setBreakGlassIds(ids: string[]): Promise<{ ok: boolean; count: number }> {
  const result = await postJson<{ count: number }>("/api/breakglass", { ids });
  return { ok: result.ok, count: result.data?.count ?? 0 };
}
