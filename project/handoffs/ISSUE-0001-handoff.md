# Claude handoff: ISSUE-0001, round 0

**Claude issue task:** `CAreview ISSUE-0001 (server shell)`
**Approved issue:** `project/issues/ISSUE-0001.md` at `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
**Starting SHA:** `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
**Candidate SHA:** `recorded in the review-request commit (branch ai/ISSUE-0001-server-shell HEAD)`
**Created at:** `2026-07-24T12:32:57Z`

## Outcome

Implemented the standard-library server shell: a loopback-bound HTTP server that
serves the static UI and `/api/health`, enforces a Host-header loopback allowlist
(DNS-rebinding defence), and provides a tested Origin helper for later
state-changing endpoints. No auth, Graph, or analysis logic added.

## Changed files

| Path | Change and reason |
|---|---|
| `server.py` | New: `ThreadingHTTPServer` on `127.0.0.1:8765`; helpers `host_allowed`, `origin_allowed`, `health_payload`; allowlisted static serving of `web/`; `/api/health`; access logging silenced |
| `web/index.html` | New: minimal UI shell with a restrictive CSP meta and a health badge |
| `web/app.js` | New: fetches `/api/health`; renders via `textContent` only |
| `web/style.css` | New: local-only styles, no external assets |
| `tests/test_server.py` | New: helper unit tests + loopback integration tests (health, root HTML, bad/missing Host → 403, unknown path → 404) |
| `tests/__init__.py`, `tests/fixtures/.gitkeep` | New: test package + fixtures placeholder |
| `project/handoffs/ISSUE-0001-plan.md` | Implementation plan |

## Decisions and assumptions

- Static serving uses an explicit route allowlist plus a `WEB_ROOT` containment
  check — belt-and-braces against path traversal while the UI is small.
- `build_server` learns the real bound port (supports `port=0` in tests) so the
  Host allowlist matches actual requests.
- `CAREVIEW_PORT` env var overrides the default `8765` for local flexibility.
- Access logging is silenced now so later issues never leak tokens/policy data to
  stderr.

## Acceptance-criteria mapping

| Criterion | Implementation evidence | Status |
|---|---|---|
| Serve index at `127.0.0.1:8765` | `server.py` `_send_static`; manual curl root → 200 | met |
| `/api/health` → `{"status":"ok"}` | `health_payload`; `test_health_ok_with_loopback_host` | met |
| Loopback-only bind | `HOST="127.0.0.1"`; `build_server` | met |
| Host allowlist rejects non-loopback | `host_allowed`; `test_bad_host_rejected`, `test_missing_host_rejected` | met |
| Origin helper provided + tested | `origin_allowed`; `test_origin_allowed` | met |
| Tests cover health + accepted/rejected Hosts | `tests/test_server.py` (9 tests) | met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 9 passed, exit 0 | none |
| Manual run | `CAREVIEW_PORT=8799 python3 server.py` + curl | health `{"status":"ok"}`; root 200; bad Host 403 | none |
| Governance | `python3 scripts/validate_repo.py` | passes (run out-of-band; Codex sandbox cannot, per F-004) | none |

The reviewer or CI must independently confirm required checks; this handoff is not
test authority.

## Documentation

- README "Run it" / "Verify it" already match this shell's behaviour.

## Security and residual risk

- Threat-model change: adds a local HTTP listener; loopback bind + Host allowlist
  resist DNS-rebinding; Origin helper ready for `/api/auth/*`.
- Residual risk/uncertainty: no auth on the local API yet (accepted for MVP,
  RISK-002); no tokens/tenant data handled in this issue.
- Protected action attempted: No.

## Review request

- Base SHA: `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
- Head SHA: `recorded at the review-request commit`
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0001 <BASE-SHA> <HEAD-SHA>`
- Areas needing special attention: Host/Origin allowlist correctness; static-path
  containment; that nothing sensitive is logged.
