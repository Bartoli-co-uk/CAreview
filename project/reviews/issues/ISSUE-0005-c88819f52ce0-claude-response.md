# Claude response to Codex issue review — ISSUE-0005 (round 0 → repair 1)

**Reviewed candidate:** `c88819f52ce031416787355eebf3c2eaf0a81fc7`
**Codex report:** `project/reviews/issues/ISSUE-0005-c88819f52ce0-codex.json` (outcome `CHANGES_REQUIRED`)
**Responder:** Claude issue task, 2026-07-24 (repair round 1)

| Finding | Disposition | Action |
|---|---|---|
| F-001 (REQUIRED) Sign-out leaves tenant analysis visible | Accepted | `signOut()` now calls `clearResults()` (hides/empties score, findings, cards) and sets the results state to "sign in to see your tenant's analysis". |
| F-002 (REQUIRED) Policy cards omit Conditions | Accepted | Added a "Conditions" flow step (client-app types, locations, sign-in/user risk, exclusion count) between Users and Apps, preserving the required flow order. |
| F-003 (REQUIRED) Hostile-markup regression fixture/test missing | Accepted, adapted to the stdlib-only constraint | No browser/DOM automation is available in this environment (no third-party packages permitted; no browser tool available this session). Added `tests/test_ui_safety.py`: a static check that `app.js` never uses a dangerous sink (`innerHTML`, `eval`, `document.write`, etc.), plus a fixture check that `web/sample-data.json` contains a hostile display name (`<img src=x onerror=alert(1)>` + quotes/angle brackets), confirmed present via `curl`. **Live browser rendering of this string was NOT performed** — that residual is recorded explicitly below rather than claimed. |
| F-004 (REQUIRED/low) README not updated | Accepted | README "Run it" now describes the score, findings, flow cards, and the sample-analysis path. |

## Out-of-band check evidence (repaired candidate)

- `python3 -m py_compile $(git ls-files '*.py')` → exit 0.
- `python3 -m unittest discover -s tests` → 79 passed, exit 0.
- `python3 scripts/validate_repo.py` → passes.
- Manual (data-level only, no browser available): server started
  (`CAREVIEW_PORT=8822 python3 server.py`), `curl` confirms root serves 200 and
  `/sample-data.json` contains the exact hostile display name string.

## Residual evidence gap

Live in-browser confirmation that the hostile string renders as inert text (no
executed script, no injected element) was **not performed** — no browser
automation tool was available this session. The static-sink check and the
committed hostile fixture are the available evidence; a human opening
`http://127.0.0.1:8765/` and clicking "View a sample analysis" can visually
confirm this directly, or a future session with a browser tool can automate it.

Remaining review limitation is the execution-evidence sandbox constraint
(DECISION-004). A fresh re-review follows.
