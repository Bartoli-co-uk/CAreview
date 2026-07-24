# ISSUE-0001: Local HTTP server + static UI shell + health endpoint

**Status:** `REPAIRING`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `3` at `125d74f6d4bfe85f1a727293064d0887f2d121c7`
**Dependencies:** `None`
**Branch:** `ai/ISSUE-0001-server-shell`
**Starting SHA:** `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
**Candidate SHA:** `this commit (branch HEAD); the launcher records the full SHA`

## Objective

Stand up the standard-library HTTP server that serves the static UI and a JSON
API, with a working `/api/health` endpoint and the test/lint scaffolding, so
later issues can add auth, Graph, and analysis behind a stable shell.

## In scope

- `server.py` — `ThreadingHTTPServer` bound to `127.0.0.1:8765`, static file
  serving for `web/`, a small JSON router with `/api/health`, a **Host-header
  loopback allowlist** rejecting non-loopback Hosts, and a reusable **Origin
  check** helper for later state-changing endpoints.
- `web/index.html`, `web/app.js`, `web/style.css` — minimal page shell.
- `tests/` package with a health-endpoint test; `tests/fixtures/` placeholder.

## Out of scope

- Any authentication, Graph calls, or analysis logic (later issues).
- Any network egress; the server only serves local content.

## Allowed paths

- `server.py`, `web/**`, `tests/**`, `README.md` (run/verify wording only)

## Acceptance criteria

1. `python3 server.py` serves `index.html` at `http://127.0.0.1:8765/`.
2. `GET /api/health` returns `200` with JSON body `{"status": "ok"}`.
3. The server binds only to loopback (`127.0.0.1`), never `0.0.0.0`.
4. **Host-header allowlist (Codex F-001):** requests whose `Host` is not on an
   explicit loopback allowlist (`127.0.0.1:<port>`, `[::1]:<port>`,
   `localhost:<port>`) are rejected with `400`/`403`, defending against browser
   DNS-rebinding into the loopback API. This behaviour and the safe values are
   established here so every later endpoint inherits it.
5. **Origin defense for state-changing endpoints:** a helper is provided (and unit
   tested) that rejects cross-origin/`null`-origin requests, to be applied to
   `/api/auth/*` in ISSUE-0002.
6. `python3 -m unittest discover -s tests` passes, including tests for the health
   endpoint, accepted loopback Hosts, and rejected attacker-controlled Hosts.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Manual run | `python3 server.py` then `curl -s localhost:8765/api/health` | `{"status": "ok"}` |

## Documentation

- README "Run it" / "Verify it" wording remains accurate for the shell.

## Security and privacy impact

- Threat-model delta: introduces a local HTTP listener; loopback-only binding
  plus a Host-header allowlist to resist browser DNS-rebinding, and an Origin
  helper for later state-changing endpoints (Codex F-001).
- Data/secret impact: none; no tokens or tenant data yet.
- Dependency/supply-chain impact: none; standard library only.
- Protected actions: none. Binding beyond localhost would be a protected change.

## Stop conditions

- Any need to bind beyond loopback, add a dependency, or exceed allowed paths.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `[path]` | `[SHA]` | `[path/summary]` | `[path]` | `[outcome]` |

Maximum two repair rounds; every Codex review is a fresh ephemeral read-only
process against the named SHA.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
