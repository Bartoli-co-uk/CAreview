# Claude handoff: ISSUE-0001, repair round 2

**Claude issue task:** `CAreview ISSUE-0001 (server shell)`
**Approved issue:** `project/issues/ISSUE-0001.md` at `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
**Starting SHA (base):** `840b8ffe3f1a2c9d2b5c36d9f0046a4cde1f5eab`
**Reviewed candidates:** round 1 `5a239c3225b6a7a190fccf6eb2ffa9b4efdc9bf6`; round 2 `f1a9db0be692d3adf04b474a1f24d6358c70ea1f`
**This repaired candidate:** branch `ai/ISSUE-0001-server-shell` HEAD (the launcher records the exact SHA at review time)
**Created at:** `2026-07-24T12:46:57Z`

## Outcome

Implemented the standard-library server shell: a loopback-bound HTTP server that
serves the static UI and `/api/health`, enforces a Host-header loopback allowlist
(DNS-rebinding defence), enforces loopback-only bind addresses, and provides a
tested Origin helper for later state-changing endpoints. No auth, Graph, or
analysis logic added.

## Review and repair history

- Round 1 review (`5a239c3`): BLOCKED — F-001 README stale, F-002 CURRENT.md
  contradiction, F-003 build_server non-loopback bind (advisory) + execution gaps.
- Repair 1 → candidate `f1a9db0`: fixed README, synced status, added loopback-bind
  guard + test (10 tests).
- Round 2 review (`f1a9db0`): BLOCKED — no code defect found; F-001 execution
  evidence (accepted via DECISION-004), F-002 residual CURRENT.md table/stage
  mismatch, F-003 stale handoff, F-004 whitespace.
- Repair 2 (this candidate): synced CURRENT.md fully, rewrote this handoff, removed
  whitespace, updated the issue round table.

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
| Tests cover health + accepted/rejected Hosts | `tests/test_server.py` (10 tests) | met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 10 passed, exit 0 | none |
| Manual run | `CAREVIEW_PORT=8799 python3 server.py` + curl | health `{"status":"ok"}`; root 200; bad Host 403 | none |
| Governance | `python3 scripts/validate_repo.py` | passes (run out-of-band; Codex sandbox cannot execute checks, per DECISION-004) | none |

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
- Head SHA: this repaired candidate's commit (branch HEAD; the launcher binds the
  exact SHA — it cannot be embedded in the commit that contains this handoff).
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0001 <BASE-SHA> <HEAD-SHA>`
- Gate policy: per `DECISION-004`, the review is static; the author's out-of-band
  checks above are the execution evidence and the human makes the merge decision.
- Areas needing special attention: Host/Origin allowlist correctness; loopback-only
  bind guard; static-path containment; that nothing sensitive is logged.
