# ISSUE-0010: Sign-in card mode toggle and app-only form in web/

**Status:** `REPAIRING`
**Milestone:** `M2`
**Approved roadmap:** `ROADMAP.md` version `4` at `9e5ba6d2f6c2b7f7efa81dcfc415e1f787aaa458` (approved by `DECISION-015`)
**Dependencies:** `ISSUE-0009` (COMPLETE, `DECISION-019`)
**Branch:** `ai/ISSUE-0010-app-only-ui`
**Starting SHA:** `f3b5414a4f2d3104d11bbb1ce6d5669a58123e79`
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA

## Objective

Add a UI toggle to the sign-in card that reveals an app-only (client
credentials) sign-in form alongside the existing, unchanged-by-default
device-code flow, wired to `ISSUE-0009`'s `POST /api/auth/app` endpoint.

## In scope

- `web/index.html` — app-only mode container, form fields, caution text,
  toggle/cancel buttons.
- `web/app.js` — mode-toggle logic, app-only submit handler, client-side
  tenant-alias rejection, and secret-field clearing on submit/mode-switch/
  logout.
- `web/style.css` — minimal styling for the new elements.
- `tests/test_ui_safety.py` — extended static assertions.
- `README.md` — description of the toggle (no screenshots).

## Out of scope

- `server.py`, `auth.py`, `graph.py` — untouched; this issue only calls the
  already-implemented `/api/auth/app` endpoint.
- New external assets or CSP relaxation.
- Certificate-based app-only auth (`ISSUE-0011` scope, if applicable).

## Allowed paths

- `web/index.html`, `web/app.js`, `web/style.css`, `tests/test_ui_safety.py`, `README.md`

## Acceptance criteria

1. Default view is unchanged device-code; an explicit toggle reveals
   tenant ID / client ID / client secret fields.
2. Secret input is `type="password"` with `autocomplete="off"`.
3. The secret value is never written to `console`, `localStorage`,
   `sessionStorage`, a cookie, a URL, or a query string.
4. The secret field is cleared after submit, on mode switch, and on
   logout.
5. A short in-page caution names what the secret grants.
6. Client-side rejection of `organizations`/`common`/`consumers` mirrors
   the server.
7. Existing CSP and text-only rendering rules unchanged.
8. Extended `tests/test_ui_safety.py` static assertions cover each of the
   above against the committed `web/` sources.
9. Because no JavaScript test toolchain exists (stdlib-only constraint),
   the runtime clearing behavior itself — not just the presence of the
   clearing code — is additionally verified by a documented manual browser
   walkthrough (synthetic tenant/client/fake-secret values, browser dev
   tools inspecting the field/DOM/console after each of: successful
   submit, mode switch, and logout) with its observed results recorded in
   the issue handoff as evidence, alongside the static assertions.
10. `unittest`, `py_compile`, `validate_repo.py` pass.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |
| Manual browser walkthrough | See handoff | secret field/DOM/console clean at every checkpoint |

## Documentation

- `README.md` — added a bullet describing the app-only toggle and its
  secret-handling guarantees under "Quick start".

## Security and privacy impact

- Threat-model delta: none beyond `RISK-005` (client secret exposed
  browser-side), already accepted in roadmap v4 with the exact mitigations
  this issue implements (`type="password"`, `autocomplete="off"`, no
  console/storage/URL writes, field cleared on submit/mode-switch/logout,
  in-page caution).
- Data/secret impact: the secret exists in the DOM only for the duration
  the user has it typed into the field, and is cleared programmatically
  immediately after every submit attempt, on mode switch (either
  direction), and on logout. It is sent to the server exactly once per
  submit, as a JSON POST body to `/api/auth/app` (never a URL or query
  string).
- Dependency/supply-chain impact: none — no new external assets, same CSP.
- Protected actions: none. No live tenant sign-in performed by this
  Claude task; the manual walkthrough used synthetic, clearly-fake values
  against a local server instance only.

## Stop conditions

- No browser-automation tool was available to this Claude task to perform
  the required manual browser walkthrough independently. The human ran it
  directly (server started by Claude, exact steps provided) and reported
  the observed results, recorded verbatim in the handoff. This is
  disclosed as the evidence source, not omitted or presented as
  independently Claude-performed.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `project/handoffs/ISSUE-0010-handoff.md` | `1d557b3840f716ad0d25a0f6d4be407cdeeb221b` | 172 tests pass; compile clean; validator passed; manual walkthrough (failure-path submit only) | `project/reviews/issues/ISSUE-0010-1d557b3840f7-codex.json` | `BLOCKED` — F-001 (secret not cleared on a rejected/failed fetch) + F-002 (missing successful-submit browser evidence) |
| 1 | `project/handoffs/ISSUE-0010-handoff.md` (Repair round 1 section) | `451dbe236769760c2384ab3f198c1f5b11f7c1ae` | 173 tests pass; compile clean; validator passed; manual walkthrough (all 5 checkpoints, incl. successful submit) | `project/reviews/issues/ISSUE-0010-451dbe236769-codex.json` | `BLOCKED` — F-001 (`project/status/CURRENT.md` still described the obsolete round-0 candidate/state instead of round 1) |
| 2 | `project/handoffs/ISSUE-0010-handoff.md` (Repair round 2 section) | this commit | 173 tests pass; compile clean; validator passed | pending | pending |

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Not yet complete. Awaiting the fresh Codex issue review and, per the
  workflow, a human advance/merge decision.
