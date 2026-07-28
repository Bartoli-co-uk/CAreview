import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  authAppOnly,
  authLogout,
  authPoll,
  authStart,
  fetchAnalysis,
  fetchPolicies,
  fetchSampleData,
} from "../api/client";
import type { Analysis, Policy } from "../api/types";

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

  const stopPolling = useCallback(() => {
    if (pollTimer.current !== null) {
      clearTimeout(pollTimer.current);
      pollTimer.current = null;
    }
  }, []);

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
    stopPolling();
    generation.current += 1; // invalidate any in-flight load immediately
    setPolicies([]);
    setAnalysis(null);
    setStatus("idle");
    setMessage(undefined);
    setDeviceCode({ phase: "idle" });
    setMode("signedOut");
    setTenant(null);
    await authLogout();
  }, [stopPolling]);

  const pollOnce = useCallback(
    async (handle: string, intervalMs: number) => {
      const result = await authPoll(handle);
      if (result.state === "success") {
        stopPolling();
        setDeviceCode({ phase: "idle" });
        setMode("live");
        void loadLive();
        return;
      }
      if (result.state === "pending") {
        pollTimer.current = setTimeout(() => void pollOnce(handle, intervalMs), intervalMs);
        return;
      }
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
      stopPolling();
      setDeviceCode({ phase: "idle" });
      const tenantValue = tenantInput || "organizations";
      const result = await authStart(tenantValue);
      if (!result.ok || !result.data || !("user_code" in result.data)) {
        setDeviceCode({ phase: "error", message: "Could not start sign-in." });
        return;
      }
      setTenant(tenantValue);
      const data = result.data;
      setDeviceCode({
        phase: "pending",
        userCode: data.user_code,
        verificationUri: data.verification_uri || "https://microsoft.com/devicelogin",
      });
      const intervalMs = Math.max(1, Number(data.interval) || 5) * 1000;
      pollTimer.current = setTimeout(() => void pollOnce(data.handle, intervalMs), intervalMs);
    },
    [pollOnce, stopPolling],
  );

  const submitAppOnlySignIn = useCallback(
    async (tenantInput: string, clientId: string, clientSecret: string) => {
      stopPolling();
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
    [loadLive, stopPolling],
  );

  const viewSampleData = useCallback(async () => {
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
  }, []);

  const exitSample = useCallback(() => {
    generation.current += 1;
    setMode("signedOut");
    setStatus("idle");
    setPolicies([]);
    setAnalysis(null);
  }, []);

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
