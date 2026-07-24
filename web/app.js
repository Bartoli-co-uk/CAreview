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
    loadLiveAnalysis();
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

// Monotonic generation counter: every sign-out, sample load, and live-analysis
// load bumps it and captures its own value. An async fetch that resolves after
// a newer load or a sign-out started discards its result instead of rendering
// stale/superseded tenant data (the same race class fixed in auth.py).
let resultsGeneration = 0;

function clearResults() {
  resultsGeneration += 1; // invalidate any in-flight load
  document.getElementById("score-block").hidden = true;
  document.getElementById("findings-block").hidden = true;
  document.getElementById("policies-block").hidden = true;
  document.getElementById("findings-list").textContent = "";
  document.getElementById("policy-cards").textContent = "";
}

async function signOut() {
  stopPolling();
  // Clear immediately (before the network round-trip) so sensitive analysis
  // cannot remain visible even briefly, and so it wins over any in-flight load.
  clearResults();
  setResultsState("sign in to see your tenant's analysis", null);
  await postJson("/api/auth/logout", {});
  showSignedOut();
  setAuthStatus("signed out", null);
}

function initAuth() {
  document.getElementById("signin-btn").addEventListener("click", startSignIn);
  document.getElementById("signout-btn").addEventListener("click", signOut);
}

// -- Analysis rendering (ISSUE-0005) -----------------------------------------
// Every value below is inserted via textContent/createElement only. Tenant and
// finding strings are untrusted input and must never be treated as HTML.

const SEVERITY_LABEL = {
  critical: "Critical", high: "High", medium: "Medium", low: "Low", info: "Info",
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function setResultsState(text, kind) {
  const state = document.getElementById("results-state");
  document.getElementById("results").hidden = false;
  if (!text) {
    state.hidden = true;
    return;
  }
  state.hidden = false;
  state.textContent = text;
  state.className = "badge" + (kind ? " " + kind : "");
}

function renderScore(score) {
  const block = document.getElementById("score-block");
  block.hidden = false;
  document.getElementById("score-value").textContent = String(score);
}

function renderFindings(findings) {
  const block = document.getElementById("findings-block");
  const list = document.getElementById("findings-list");
  list.textContent = "";
  if (!findings.length) {
    block.hidden = true;
    return;
  }
  block.hidden = false;
  for (const finding of findings) {
    const item = el("li", "finding finding-" + finding.severity);
    const title = el("strong", null, finding.title);
    const severity = el("span", "badge severity-" + finding.severity,
      SEVERITY_LABEL[finding.severity] || finding.severity);
    const rationale = el("p", "finding-rationale", finding.rationale);
    const remediation = el("p", "finding-remediation", "Remediation: " + finding.remediation);
    item.append(severity, " ", title, rationale, remediation);
    if (finding.affectedPolicies && finding.affectedPolicies.length) {
      const affected = el("p", "finding-affected",
        "Affected: " + finding.affectedPolicies.join(", "));
      item.append(affected);
    }
    list.append(item);
  }
}

function renderPolicyCard(policy) {
  const card = el("article", "policy-card");
  card.append(el("h4", null, policy.displayName || policy.id || "(unnamed policy)"));
  card.append(el("p", "policy-state", "State: " + (policy.state || "unknown")));

  const flow = el("div", "policy-flow");
  const c = policy.conditions || {};
  const users = [...(c.includeUsers || []), ...(c.includeRoles || []).map((r) => "role:" + r)];
  const apps = c.includeApplications || [];
  const controls = (policy.grantControls && policy.grantControls.builtInControls) || [];

  const conditionParts = [];
  if (c.clientAppTypes && c.clientAppTypes.length) {
    conditionParts.push("client apps: " + c.clientAppTypes.join(", "));
  }
  if (c.includeLocations && c.includeLocations.length) {
    conditionParts.push("locations: " + c.includeLocations.join(", "));
  }
  if (c.signInRiskLevels && c.signInRiskLevels.length) {
    conditionParts.push("sign-in risk: " + c.signInRiskLevels.join(", "));
  }
  if (c.userRiskLevels && c.userRiskLevels.length) {
    conditionParts.push("user risk: " + c.userRiskLevels.join(", "));
  }
  const excluded = [...(c.excludeUsers || []), ...(c.excludeGroups || []), ...(c.excludeRoles || [])];
  if (excluded.length) conditionParts.push("excludes " + excluded.length + " principal(s)");

  flow.append(el("div", "flow-step", "Users: " + (users.length ? users.join(", ") : "(none)")));
  flow.append(el("div", "flow-step", "Conditions: " + (conditionParts.length ? conditionParts.join("; ") : "(none)")));
  flow.append(el("div", "flow-step", "Apps: " + (apps.length ? apps.join(", ") : "(none)")));
  flow.append(el("div", "flow-step", "Controls: " + (controls.length ? controls.join(", ") : "(none)")));
  card.append(flow);
  return card;
}

function renderPolicies(policies) {
  const block = document.getElementById("policies-block");
  const cards = document.getElementById("policy-cards");
  cards.textContent = "";
  if (!policies.length) {
    block.hidden = true;
    return;
  }
  block.hidden = false;
  for (const policy of policies) cards.append(renderPolicyCard(policy));
}

function renderAnalysis(policies, analysis) {
  setResultsState(null);
  if (!policies.length) {
    setResultsState("No Conditional Access policies found.", null);
    document.getElementById("score-block").hidden = true;
    document.getElementById("findings-block").hidden = true;
    document.getElementById("policies-block").hidden = true;
    return;
  }
  renderScore(analysis.score);
  renderFindings(analysis.findings);
  renderPolicies(policies);
}

async function loadSample() {
  resultsGeneration += 1;
  const myGeneration = resultsGeneration;
  setResultsState("loading sample…", null);
  try {
    const response = await fetch("/sample-data.json");
    const data = await response.json();
    if (myGeneration !== resultsGeneration) return; // superseded by sign-out/another load
    renderAnalysis(data.policies, data.analysis);
  } catch (err) {
    if (myGeneration !== resultsGeneration) return;
    setResultsState("could not load sample data", "error");
  }
}

async function loadLiveAnalysis() {
  resultsGeneration += 1;
  const myGeneration = resultsGeneration;
  setResultsState("loading…", null);
  try {
    const [policiesResp, analysisResp] = await Promise.all([
      fetch("/api/policies", { headers: { Accept: "application/json" } }),
      fetch("/api/analysis", { headers: { Accept: "application/json" } }),
    ]);
    if (myGeneration !== resultsGeneration) return; // superseded by sign-out/another load
    if (policiesResp.status === 401 || analysisResp.status === 401) {
      setResultsState("sign in to see your tenant's analysis", null);
      return;
    }
    if (policiesResp.status === 403 || analysisResp.status === 403) {
      setResultsState("admin consent to Policy.Read.All is required", "error");
      return;
    }
    if (!policiesResp.ok || !analysisResp.ok) {
      setResultsState("could not load analysis", "error");
      return;
    }
    const policiesBody = await policiesResp.json();
    const analysis = await analysisResp.json();
    if (myGeneration !== resultsGeneration) return; // superseded during body parsing
    renderAnalysis(policiesBody.policies, analysis);
  } catch (err) {
    if (myGeneration !== resultsGeneration) return;
    setResultsState("could not load analysis", "error");
  }
}

function initResults() {
  document.getElementById("sample-btn").addEventListener("click", loadSample);
}

document.addEventListener("DOMContentLoaded", () => {
  refreshHealth();
  initAuth();
  initResults();
});
