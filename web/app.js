// CAreview UI shell (ISSUE-0001).
// Confirms the local API is reachable by calling /api/health. Later issues add
// device-code sign-in and policy analysis. All rendering uses textContent so
// that untrusted data introduced in later issues cannot inject markup.
"use strict";

async function refreshHealth() {
  const badge = document.getElementById("health");
  try {
    const response = await fetch("/api/health", { headers: { Accept: "application/json" } });
    const data = await response.json();
    if (response.ok && data.status === "ok") {
      badge.textContent = "ok";
      badge.classList.add("ok");
    } else {
      badge.textContent = "unexpected response";
      badge.classList.add("error");
    }
  } catch (err) {
    badge.textContent = "unreachable";
    badge.classList.add("error");
  }
}

// -- Device-code sign-in (ISSUE-0002) --------------------------------------
let pollTimer = null;

function setAuthStatus(text, kind) {
  const el = document.getElementById("auth-status");
  el.textContent = text;
  el.className = "badge" + (kind ? " " + kind : "");
  el.hidden = false;
}

function showSignedOut() {
  document.getElementById("signin-btn").hidden = false;
  document.getElementById("signout-btn").hidden = true;
  document.getElementById("devicecode").hidden = true;
}

async function postJson(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload || {}),
  });
  return { ok: response.ok, data: await response.json().catch(() => ({})) };
}

function stopPolling() {
  if (pollTimer !== null) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
}

async function pollOnce(handle, intervalMs) {
  const { data } = await postJson("/api/auth/poll", { handle });
  if (data.state === "success") {
    stopPolling();
    document.getElementById("devicecode").hidden = true;
    document.getElementById("signout-btn").hidden = false;
    document.getElementById("signin-btn").hidden = true;
    setAuthStatus("signed in", "ok");
    return;
  }
  if (data.state === "pending") {
    pollTimer = setTimeout(() => pollOnce(handle, intervalMs), intervalMs);
    return;
  }
  // expired or error
  stopPolling();
  document.getElementById("devicecode").hidden = true;
  showSignedOut();
  setAuthStatus(data.state === "expired" ? "code expired — try again" : "sign-in failed", "error");
}

async function startSignIn() {
  stopPolling();
  const tenant = document.getElementById("tenant").value.trim() || "organizations";
  setAuthStatus("requesting a code…", null);
  const { ok, data } = await postJson("/api/auth/start", { tenant });
  if (!ok || !data.user_code) {
    setAuthStatus("could not start sign-in", "error");
    return;
  }
  document.getElementById("dc-code").textContent = data.user_code;
  const link = document.getElementById("dc-link");
  link.href = data.verification_uri || "https://microsoft.com/devicelogin";
  document.getElementById("devicecode").hidden = false;
  document.getElementById("signin-btn").hidden = true;
  setAuthStatus("waiting for approval…", null);
  const intervalMs = Math.max(1, Number(data.interval) || 5) * 1000;
  pollTimer = setTimeout(() => pollOnce(data.handle, intervalMs), intervalMs);
}

async function signOut() {
  stopPolling();
  await postJson("/api/auth/logout", {});
  showSignedOut();
  setAuthStatus("signed out", null);
}

function initAuth() {
  document.getElementById("signin-btn").addEventListener("click", startSignIn);
  document.getElementById("signout-btn").addEventListener("click", signOut);
}

document.addEventListener("DOMContentLoaded", () => {
  refreshHealth();
  initAuth();
});
