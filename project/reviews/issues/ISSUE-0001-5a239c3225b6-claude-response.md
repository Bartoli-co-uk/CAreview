# Claude response to Codex issue review — ISSUE-0001 (round 1)

**Reviewed candidate:** `5a239c3225b6a7a190fccf6eb2ffa9b4efdc9bf6`
**Codex report:** `project/reviews/issues/ISSUE-0001-5a239c3225b6-codex.json` (outcome `BLOCKED`)
**Responder:** Claude issue task, 2026-07-24 (repair round 1)

| Finding | Disposition | Action |
|---|---|---|
| F-001 README stale after the shell landed | Accepted | README status + Run/Verify wording updated to describe the server shell + health, the disabled Sign-in, and current server tests; no claim that auth/analyzer exist. |
| F-002 CURRENT.md table contradicts its ISSUE_REVIEW state block | Accepted | Synchronized the human-readable table with the machine state (active issue ISSUE-0001, candidate, handoff, next action). |
| F-003 (advisory) build_server accepts any bind host | Accepted | `build_server` now rejects non-loopback bind addresses (`ValueError`); added `test_build_server_rejects_non_loopback_bind` (no socket opened). |

## Structural blocker: the review sandbox cannot execute checks

Codex's `BLOCKED` also rests on execution-evidence limitations it cannot overcome:

- tests need loopback **sockets** (prohibited in the sandbox);
- `py_compile` needs to write `__pycache__` (the checkout is **read-only**);
- `validate_repo.py` needs a **writable temp dir** (none in the sandbox).

Because the launcher runs Codex in a read-only, socket-restricted, temp-less
checkout, **no** check can execute there, and the review rules forbid `PASS`
without execution evidence. This is a property of the ClaudexCodexSetUp launcher,
not of the candidate, and it will recur for **every** code issue.

## Out-of-band check evidence (author-run, this repaired candidate)

- `python3 -m py_compile $(git ls-files '*.py')` → exit 0.
- `python3 -m unittest discover -s tests` → 10 passed, exit 0.
- `python3 scripts/validate_repo.py` → passed (67 required files).
- Manual: `CAREVIEW_PORT=8799 python3 server.py` → `/api/health` `{"status":"ok"}`,
  root 200, `Host: evil.com` 403.

## Presented to the human

The code findings are fixed. The remaining `BLOCKED` is the structural
execution-evidence limitation. Because it affects all six issues, the human is
asked to choose a gate policy (accept static Codex review + author out-of-band
evidence and decide the merge, or adjust the launcher sandbox) before further
re-review or merge.
