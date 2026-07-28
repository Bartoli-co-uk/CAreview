import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  authAbandon,
  authAppOnly,
  authLogout,
  authPoll,
  authStart,
  fetchAnalysis,
  fetchPolicies,
  fetchSampleData,
} from "../api/client";
import type { Analysis, Policy } from "../api/types";

// Bounded retry/backoff for authAbandon (ISSUE-0013 round-0 review finding):
// a single fire-and-forget POST can fail (network blip, transient server
// error) and silently leave the abandoned attempt's token installed. This
// retries a few times before giving up — there is no way to guarantee
// delivery from a browser tab that might close, but this narrows the
// failure window from "any single request" to "several requests over a few
// seconds all failing outright."
const ABANDON_RETRY_DELAYS_MS = [500, 1500, 4000];

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function abandonWithRetry(handle: string): Promise<void> {
  if (await authAbandon(handle)) return;
  for (const ms of ABANDON_RETRY_DELAYS_MS) {
    await delay(ms);
    if (await authAbandon(handle)) return;
  }
}

export type DataStatus =
  | "idle"
  | "loading"
  | "ready"
  | "unauthenticated"
  | "consent_required"
  | "error";

export type Mode = "signedOut" | "live" | "sample";

export type DeviceCodeState =
  | { phase: "idle" }
  | { phase: "pending"; userCode: string; verificationUri: string }
  | { phase: "error"; message: string };

interface AppState {
  mode: Mode;
  status: DataStatus;
  message?: string;
  policies: Policy[];
  analysis: Analysis | null;
  isSample: boolean;
  deviceCode: DeviceCodeState;
  startDeviceCodeSignIn: (tenant: string) => Promise<void>;
  submitAppOnlySignIn: (tenant: string, clientId: string, clientSecret: string) => Promise<{ ok: boolean; message?: string }>;
  signOut: () => Promise<void>;
  viewSampleData: () => Promise<void>;
  exitSample: () => void;
  refreshLive: () => Promise<void>;
  lastRefreshed: Date | null;
  /** Tenant string as entered at sign-in — not a verified directory name; the
   * API never echoes back a resolved tenant identity. */
  tenant: string | null;
}

const AppStateContext = createContext<AppState | null>(null);

export function useAppState(): AppState {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppState must be used within AppStateProvider");
  return ctx;
}

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<Mode>("signedOut");
  const [status, setStatus] = useState<DataStatus>("idle");
  const [message, setMessage] = useState<string | undefined>(undefined);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [deviceCode, setDeviceCode] = useState<DeviceCodeState>({ phase: "idle" });
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);
  const [tenant, setTenant] = useState<string | null>(null);

  // Monotonic generation guard so a stale in-flight fetch (superseded by a
  // sign-out or a newer load) never overwrites fresher state — the same
  // race class web/app.js's resultsGeneration counter guards against.
  const generation = useRef(0);
  const pollTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Per-attempt cancellation token for device-code polling. clearTimeout()
  // alone cannot stop an authPoll() request that has already been sent and
  // is awaiting a response — bumping this token and having pollOnce check it
  // after every await is what actually invalidates that in-flight attempt,
  // so it can never schedule another timer or flip mode back to "live" after
  // the user has moved to sample mode, app-only mode, or signed out.
  const authAttempt = useRef(0);
  // The current device-code attempt's server-issued handle, if one is
  // outstanding (set once authStart() returns one; cleared on any terminal
  // outcome or cancellation). Lets cancellation tell the server exactly
  // which attempt to abandon (ISSUE-0013) — scoped by handle, so it can
  // never clear a different, newer session the way an unconditional
  // authLogout() call could.
  const pendingHandle = useRef<string | null>(null);

  const stopPolling = useCallback(() => {
    if (pollTimer.current !== null) {
      clearTimeout(pollTimer.current);
      pollTimer.current = null;
    }
  }, []);

  const cancelDeviceCodeAttempt = useCallback(() => {
    authAttempt.current += 1;
    stopPolling();
    if (pendingHandle.current) {
      void abandonWithRetry(pendingHandle.current);
      pendingHandle.current = null;
    }
  }, [stopPolling]);

  const loadLive = useCallback(async () => {
    generation.current += 1;
    const myGeneration = generation.current;
    setStatus("loading");
    setMessage(undefined);
    const [policiesResult, analysisResult] = await Promise.all([fetchPolicies(), fetchAnalysis()]);
    if (myGeneration !== generation.current) return;

    if (!policiesResult.ok || !analysisResult.ok) {
      const failed = !policiesResult.ok ? policiesResult : analysisResult.ok ? null : analysisResult;
      if (failed && !failed.ok) {
        if (failed.error === "not_authenticated") {
          setStatus("unauthenticated");
        } else if (failed.error === "consent_required") {
          setStatus("consent_required");
          setMessage(failed.message);
        } else {
          setStatus("error");
          setMessage(failed.message ?? "Could not load analysis.");
        }
      }
      return;
    }
    setPolicies(policiesResult.data.policies);
    setAnalysis(analysisResult.data);
    setStatus("ready");
    setLastRefreshed(new Date());
  }, []);

  const signOut = useCallback(async () => {
    cancelDeviceCodeAttempt();
    generation.current += 1; // invalidate any in-flight load immediately
    setPolicies([]);
    setAnalysis(null);
    setStatus("idle");
    setMessage(undefined);
    setDeviceCode({ phase: "idle" });
    setMode("signedOut");
    setTenant(null);
    await authLogout();
  }, [cancelDeviceCodeAttempt]);

  const pollOnce = useCallback(
    async (handle: string, intervalMs: number, myAttempt: number) => {
      const result = await authPoll(handle);
      // The awaited request may settle after a competing transition (sample
      // mode, app-only mode, sign-out, or a fresh device-code attempt) has
      // already moved authAttempt on. That transition's cancelDeviceCodeAttempt()
      // already called authAbandon(handle) for this exact attempt (ISSUE-0013),
      // so the server itself will never have installed/kept a token for it —
      // no reactive cleanup is needed here; just don't mutate client state.
      if (myAttempt !== authAttempt.current) return;
      if (result.state === "success") {
        pendingHandle.current = null;
        stopPolling();
        setDeviceCode({ phase: "idle" });
        setMode("live");
        void loadLive();
        return;
      }
      if (result.state === "pending") {
        pollTimer.current = setTimeout(() => void pollOnce(handle, intervalMs, myAttempt), intervalMs);
        return;
      }
      pendingHandle.current = null;
      stopPolling();
      setDeviceCode({
        phase: "error",
        message: result.state === "expired" ? "Code expired — try again." : "Sign-in failed.",
      });
    },
    [loadLive, stopPolling],
  );

  const startDeviceCodeSignIn = useCallback(
    async (tenantInput: string) => {
      authAttempt.current += 1;
      const myAttempt = authAttempt.current;
      stopPolling();
      setDeviceCode({ phase: "idle" });
      const tenantValue = tenantInput || "organizations";
      const result = await authStart(tenantValue);
      if (myAttempt !== authAttempt.current) return; // superseded while authStart was in flight
      if (!result.ok || !result.data || !("user_code" in result.data)) {
        setDeviceCode({ phase: "error", message: "Could not start sign-in." });
        return;
      }
      setTenant(tenantValue);
      const data = result.data;
      pendingHandle.current = data.handle;
      setDeviceCode({
        phase: "pending",
        userCode: data.user_code,
        verificationUri: data.verification_uri || "https://microsoft.com/devicelogin",
      });
      const intervalMs = Math.max(1, Number(data.interval) || 5) * 1000;
      pollTimer.current = setTimeout(() => void pollOnce(data.handle, intervalMs, myAttempt), intervalMs);
    },
    [pollOnce, stopPolling],
  );

  const submitAppOnlySignIn = useCallback(
    async (tenantInput: string, clientId: string, clientSecret: string) => {
      // Invalidates any in-flight device-code attempt so it can never later
      // flip mode back to "live" out from under this app-only attempt.
      cancelDeviceCodeAttempt();
      const result = await authAppOnly(tenantInput, clientId, clientSecret);
      if (!result.ok || !result.data || result.data.state !== "success") {
        const message =
          result.data && "error" in result.data ? `App-only sign-in failed: ${result.data.error}` : "App-only sign-in failed.";
        return { ok: false, message };
      }
      setTenant(tenantInput);
      setMode("live");
      void loadLive();
      return { ok: true };
    },
    [cancelDeviceCodeAttempt, loadLive],
  );

  const viewSampleData = useCallback(async () => {
    // Invalidates any in-flight device-code attempt so a pending/success poll
    // response can never overwrite sample mode after the user has moved to it.
    cancelDeviceCodeAttempt();
    generation.current += 1;
    const myGeneration = generation.current;
    setMode("sample");
    setStatus("loading");
    const result = await fetchSampleData();
    if (myGeneration !== generation.current) return;
    if (!result.ok) {
      setStatus("error");
      setMessage("Could not load sample data.");
      return;
    }
    setPolicies(result.data.policies);
    setAnalysis(result.data.analysis);
    setStatus("ready");
    setLastRefreshed(new Date());
  }, [cancelDeviceCodeAttempt]);

  const exitSample = useCallback(() => {
    cancelDeviceCodeAttempt();
    generation.current += 1;
    setMode("signedOut");
    setStatus("idle");
    setPolicies([]);
    setAnalysis(null);
  }, [cancelDeviceCodeAttempt]);

  useEffect(() => stopPolling, [stopPolling]);

  const value: AppState = {
    mode,
    status,
    message,
    policies,
    analysis,
    isSample: mode === "sample",
    deviceCode,
    startDeviceCodeSignIn,
    submitAppOnlySignIn,
    signOut,
    viewSampleData,
    exitSample,
    refreshLive: loadLive,
    lastRefreshed,
    tenant,
  };

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}
