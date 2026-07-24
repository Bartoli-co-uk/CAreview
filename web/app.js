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

document.addEventListener("DOMContentLoaded", refreshHealth);
