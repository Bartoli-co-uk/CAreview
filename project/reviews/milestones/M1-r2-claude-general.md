# Codex/Claude general review: M1 (MVP Conditional Access analyzer)

**Outcome:** PASS_WITH_NOTES
**Reviewer role:** Claude general reviewer (independent fresh subagent, round 2)
**Reviewed SHA:** 6311a11a48a0a7e51e83a14ca4081d431cb46698
**Created at:** 2026-07-24T22:23:04Z (estimated from system clock at time of review)

## Scope and inputs

- Requirements/roadmap: `AGENTS.md`, `project/brief/PROJECT_BRIEF.md` (v1, APPROVED), `ROADMAP.md` (v3, APPROVED), and `project/issues/ISSUE-0001.md` through `ISSUE-0006.md` (all six issues recorded `COMPLETE`, each with its own multi-round Codex review history and human decision records `DECISION-004`..`011`).
- Patch/tree: `server.py`, `auth.py`, `graph.py`, `analyzer.py`, `rules.py`, `web/index.html`, `web/app.js`, `web/style.css`, `web/sample-data.json`, and the full `tests/` package (`test_server.py`, `test_auth.py`, `test_graph.py`, `test_analyzer.py`, `test_ui_safety.py`, plus `tests/fixtures/*.json`). Also read `project/status/CURRENT.md`, `project/decisions/DECISION-011-milestone-validator-fix.md`, and README's "Security and limitations" section to cross-check documented residual risk.
- Verification evidence: the exact commands below, run from the repo root against this checked-out SHA (working tree clean; `git status` showed the branch is 3 commits ahead of `origin/main`, but no uncommitted changes).
- Excluded or unavailable evidence: `project/reviews/` was intentionally not read (independence constraint). No live Microsoft tenant sign-in or Graph fetch was performed — this is by design a protected action deferred from M1 completion per `ROADMAP.md`/Codex F-002/F-003, not an evidence gap I introduced. No browser/DOM automation was available to visually confirm inert rendering of hostile markup in a live browser (the repo compensates with static sink-absence tests and a committed hostile-markup fixture; a human visual check is still recommended, as the repo itself notes in `ISSUE-0005`'s completion record).

## Summary

The candidate at `6311a11a` implements the full M1 flow described in the roadmap — device-code sign-in (`auth.py`), Graph CA-policy fetch/normalization (`graph.py`), a data-driven 0–100 heuristic scoring engine with an explicit "not evaluable" path for missing evidence (`rules.py`/`analyzer.py`), and offline-testable UI rendering with XSS-safe DOM construction (`web/app.js`). All three required checks (`py_compile`, `unittest discover`, `validate_repo.py`) pass cleanly against this exact SHA, and the six issues' own commit-bound repair histories show real, independently-reviewed remediation of prior findings (SSRF, race conditions, evaluability semantics, CSRF/Host defenses) rather than unresolved debt. This candidate itself is the M1 general-remediation round (per `DECISION-011`), and its diff from the prior (round-1) candidate is small, targeted, and verifiably fixes the governance-validator self-test bug plus adds real CSP/`X-Content-Type-Options` HTTP headers and HTTP-level auth endpoint tests — a coherent, non-scope-creeping repair. No blocking defects were found; the residual gaps that remain (live-tenant sign-in untested, unauthenticated loopback API) are already named and explicitly accepted in the project's own risk register (`RISK-001`, `RISK-002`) rather than undocumented.

## Findings

### GEN-001: Live-tenant sign-in and Graph fetch remain unexercised at M1
- Classification: ADVISORY
- Severity: low
- Confidence: high
- Blocking: no
- Location: `auth.py`, `graph.py`; `ROADMAP.md` lines 113–118; `project/brief/PROJECT_BRIEF.md` A1
- Expected: The brief's measurable success criterion 2 is "the app lists that tenant's Conditional Access policies" after a real sign-in.
- Observed: All acceptance evidence for device-code auth and Graph fetching is against mocked transports (`tests/test_auth.py`, `tests/test_graph.py`, `tests/test_server.py`); no real tenant has exercised the flow.
- Evidence: `ROADMAP.md` explicitly states live-tenant sign-in/fetch is "not an M1 completion criterion" and is a separate protected action requiring named-tenant human approval (Codex F-002/F-003); this is consistent across all six issue files.
- Impact: Assumption A1 (a first-party public client can obtain `Policy.Read.All` via device code) remains unverified against a real tenant; if wrong, the MVP's core value proposition fails until an app-registration fallback (currently a non-goal) is built.
- Remediation: None required for M1 per the approved roadmap; the human should perform (or explicitly defer) the protected live-tenant verification step before relying on the tool operationally.
- Verification: N/A — this is a scope/evidence note, not a code defect.

### GEN-002: Local API has no authentication of its own beyond loopback binding and Origin/Host checks
- Classification: ADVISORY
- Severity: low
- Confidence: high
- Blocking: no
- Location: `server.py:73-107` (`host_allowed`, `origin_allowed`), `README.md` "Security and limitations"
- Expected/Observed: Matches the documented and accepted design (`RISK-002`): binding to `127.0.0.1` plus a Host-header allowlist and Origin check on state-changing endpoints, but no session token/PIN gate.
- Evidence: `README.md` lines 186–190 names this explicitly as an accepted residual risk for a single-user machine, not to be run on a shared host.
- Impact: On a genuinely shared/multi-user machine, another local process running as the same OS user could reach the API while a token is in memory (~1 hour access-token lifetime, no refresh-token retention). This is a known, previously accepted risk, not a new discovery.
- Remediation: None required for M1; already accepted per `DECISION-001`. Consider a loopback token/PIN gate if the tool is ever shared beyond a single trusted user.
- Verification: `tests/test_server.py::test_bad_host_rejected`, `test_missing_host_rejected`, `test_post_without_origin_rejected`, `test_post_cross_origin_rejected` all pass, confirming the accepted mitigations function as documented.

### GEN-003: `/api/analysis` re-fetches Graph policies independently of `/api/policies`
- Classification: ADVISORY
- Severity: info
- Confidence: high
- Blocking: no
- Location: `server.py:192-228` (`_policies`, `_analysis`)
- Expected: No explicit requirement either way; noted for efficiency/operability only.
- Observed: `web/app.js::loadLiveAnalysis` calls both `/api/policies` and `/api/analysis` concurrently (`Promise.all`), and each handler independently calls `GRAPH.fetch_policies(token)`, doubling the Graph round-trips (and paging cost) for every page load.
- Evidence: `server.py:198` and `server.py:217` each call `GRAPH.fetch_policies(token)` on every request to their respective endpoint.
- Impact: Purely a latency/throttling consideration on large tenants with many CA policies or slow paging; no correctness or security effect, since Graph access is strictly read-only and idempotent.
- Remediation: Optional future optimization — cache the fetched policy list per request cycle or have the UI request one combined endpoint.
- Verification: Not applicable; behavior is correct, just not optimally efficient.

## Check accounting

| Required check | Evidence | Result |
|---|---|---|
| `python3 -m py_compile $(git ls-files '*.py')` | Command run from repo root against `6311a11a`; exit code captured as `PY_COMPILE_EXIT=0`, no output/errors | PASS |
| `python3 -m unittest discover -s tests` | Verbose run; `Ran 83 tests in 11.125s` / `OK`; all 83 tests listed passed (auth lifecycle, request building, Graph paging/normalization/URL validation, analyzer scoring/evaluability/determinism, server routing/host/origin/auth/policies/analysis endpoints, UI static-safety and hostile-markup fixture checks) | PASS |
| `python3 scripts/validate_repo.py` | Output: `NOTICE: PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu.` then `Repository validation passed (67 required files checked).`; exit code 0 | PASS |

## Limitations and uncertainty

- I could not exercise the browser to visually confirm hostile-markup inertness at runtime (no DOM/browser tool available in this environment); I relied on the repo's own static-sink-absence test (`tests/test_ui_safety.py`) and the committed `<img src=x onerror=alert(1)>` fixture in `web/sample-data.json`, which is a reasonable but not fully equivalent substitute for live rendering.
- I did not and could not perform a real device-code sign-in or live Graph fetch against any tenant — this is intentionally out of scope for M1 completion per the approved roadmap and would itself be a protected action requiring separate named-tenant human approval; I am not asserting it works against a real tenant, only that the mocked/offline evidence for it is present and passing.
- I did not read `project/reviews/` (excluded by the independence constraint), so I cannot state whether this report's conclusions match or diverge from any prior Claude or Codex review; this report was formed solely from the roadmap, issues, source, tests, and my own command runs.
- PowerShell syntax validation inside `scripts/validate_repo.py` was skipped in this environment (`pwsh` unavailable); the script's own notice states CI covers this on Ubuntu, so I could not independently verify the PowerShell launcher script's syntax.
- I did not perform a dedicated security-boundary/threat-model deep-dive (e.g., exhaustive SSRF/redirect/credential-leak analysis) — that is explicitly the separate milestone security review's responsibility per `AGENTS.md`'s four-report gate; my read of `graph.py`'s host-pinning, no-redirect opener, and tenant-string validation in `auth.py` found no obvious gap, but this general review is not a substitute for that dedicated security pass.
