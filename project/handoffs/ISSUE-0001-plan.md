# Implementation plan: ISSUE-0001

**Claude issue task:** `CAreview ISSUE-0001 (server shell)`
**Approved issue:** `project/issues/ISSUE-0001.md` at `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
**Starting SHA:** `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
**Prepared at:** `2026-07-24T12:32:57Z`

## Restatement

- Objective: stand up the stdlib HTTP server serving the static UI and a JSON
  `/api/health`, with a loopback Host-header allowlist and an Origin helper, plus
  test/lint scaffolding.
- Boundaries: no auth, Graph, or analysis. `server.py`, `web/**`, `tests/**`,
  README wording only.
- Acceptance criteria: serve index at `127.0.0.1:8765`; `/api/health` → `{"status":"ok"}`;
  loopback-only bind; Host allowlist rejects non-loopback Hosts; Origin helper
  provided+tested; `unittest` covers health + accepted/rejected Hosts.
- Assumptions: single trusted local user; browser includes `Host: host:port`.
- Security implications: introduces a local listener; Host allowlist mitigates
  DNS-rebinding; no secrets/tokens yet.

## Steps

| Order | Change | Allowed path | Criterion addressed | Check |
|---:|---|---|---|---|
| 1 | `server.py`: ThreadingHTTPServer on 127.0.0.1:8765; helpers `host_allowed`, `origin_allowed`, `health_payload`; safe static serving of `web/`; `/api/health` | `server.py` | 1,2,3,4,5 | unittest + manual curl |
| 2 | `web/index.html`, `web/app.js`, `web/style.css`: minimal shell that fetches `/api/health` | `web/**` | 1 | manual load |
| 3 | `tests/test_server.py` (+ `tests/__init__.py`, `tests/fixtures/.gitkeep`): unit + light integration on an ephemeral port | `tests/**` | 4,6 | `python3 -m unittest discover -s tests` |
| 4 | README: keep Run/Verify accurate | `README.md` | docs | read |

## Documentation and tests

- Tests: health payload; `host_allowed` accepts `127.0.0.1/localhost/[::1]:port`,
  rejects `evil.com` and missing Host; `origin_allowed`; integration GET
  `/api/health` (200) and GET with bad Host (403); path-traversal rejected.
- Documentation: README "Run it"/"Verify it" already match; adjust if needed.

## Risks and rollback

- Risk: over-strict Host check breaks local use → include all loopback forms with port; tested.
- Rollback: revert the branch; no shared state.

## Stop conditions

- Any need to bind beyond loopback, add a dependency, or exceed allowed paths.

This plan does not expand the approved issue or authorize protected actions.
