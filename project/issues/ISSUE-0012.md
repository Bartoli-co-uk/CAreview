# ISSUE-0012: React/Vite frontend dashboard (retroactive issue record)

**Status:** `BLOCKED` — repair-round budget exhausted (2 of 2 used, `AGENTS.md`);
unresolved `CHANGES_REQUIRED` finding presented to the human, not
implemented further by this task.
**Milestone:** `None` — no M3 exists; this work is out-of-band relative to the
approved M1/M2 roadmap, authorized directly by the human rather than through
the normal brief/roadmap cycle (see `DECISION-024`).
**Approved roadmap:** `N/A` — not governed by `ROADMAP.md` v4 (which governs
M1/M2 only); the human explicitly chose the direct-override path over
drafting a roadmap amendment first, per `AGENTS.md`'s own instruction-order
rule (the human's current explicit instructions outrank `AGENTS.md`).
**Dependencies:** None
**Branch:** `ai/react-dashboard-frontend`
**Starting SHA:** `8648f2ba11907ac32016c724d8ae49a08bdb6b2d`
**Candidate SHA:** round 0 `4cb61161be32b43506bb0e2c1b6921635561054d`
(`BLOCKED`); round 1 `3748ff13318241e8cbe2bc38debc55e3d3042ecb` (`BLOCKED`);
round 2 candidate is this commit — the launcher records the full HEAD SHA.
This is the last repair round `AGENTS.md` permits for an issue.

## Objective

Replace the vanilla-JS/HTML/CSS `web/` UI with a React + TypeScript dashboard
(built with Vite), modeled on a reviewed mockup, serving both technicians
(full findings/policy detail) and senior management (at-a-glance summary),
against the existing `/api/policies` and `/api/analysis` contract — with no
backend behavior change beyond `server.py`'s static-file allowlist.

This issue record is being created **retroactively**: the implementation was
already done and manually verified (build, tests, live browser walkthrough)
before this record and the Codex review it enables were requested. It exists
to give this out-of-band work the same per-issue review gate any other
CAreview issue gets, per the human's explicit request, even though it did not
go through the normal pre-implementation brief/roadmap/Codex-plan-review
cycle.

## In scope

- `frontend/` — new React + TypeScript + Vite source (pages, components,
  API client, state, tests).
- `server.py` — `STATIC_FILES` updated to the new build output's fixed
  filenames (`index.html`, `index.js`, `index.css`); no other server.py
  behavior changed.
- `web/app.js`, `web/style.css` — removed (superseded by the Vite build
  output). `web/sample-data.json` unchanged.
- `tests/test_ui_safety.py` — rewritten against the React source (the old
  file read `web/app.js`/`web/index.html` directly, which no longer exist as
  hand-written source).
- `.gitignore` — build output (`web/index.html`, `index.js`, `index.css`)
  ignored as generated artifacts.
- `scripts/validate_repo.py` — excludes `node_modules` from file scans and
  tolerates JSONC comments in `tsconfig*.json`, both needed once a
  Node-based `frontend/` exists in the tree.
- `README.md`, `AGENTS.md`, `ROADMAP.md`, `project/status/CURRENT.md`,
  new `frontend/README.md` — documentation of the new build step and the
  governance exception.
- `project/decisions/DECISION-024-react-frontend-build-step.md` — the human
  decision record this issue implements.

## Out of scope

- Fixing the device-code sign-in regression the human separately reported —
  investigated and found likely tenant-side, not a code defect; explicitly
  deferred, not part of this issue.
- Any new backend data source (Reports, Audit Log, persisted Settings) — the
  corresponding UI sections are honest "not available yet" placeholders.
- CI wiring for the new `npm` commands (tracked as follow-up in
  `DECISION-024`).
- Opening or drafting an M3 milestone/roadmap amendment.

## Allowed paths

- `frontend/**`, `web/**` (excluding `web/sample-data.json` content),
  `server.py`, `tests/test_ui_safety.py`, `.gitignore`,
  `scripts/validate_repo.py`, `README.md`, `AGENTS.md`, `ROADMAP.md`,
  `project/status/CURRENT.md`, `project/decisions/DECISION-024-*.md`,
  `project/issues/ISSUE-0012.md`.

## Acceptance criteria

1. `cd frontend && npm run build` produces `web/index.html`, `index.js`,
   `index.css` with fixed (non-hashed) filenames; `web/sample-data.json` is
   unchanged.
2. `python3 server.py` serves the built dashboard at `/` with the CSP header
   unchanged (`default-src 'self'; base-uri 'none'; form-action 'none';
   object-src 'none'; frame-ancestors 'none'`) and no non-loopback network
   access.
3. The dashboard renders Overview, Recommendations, Policies, Policy
   Explorer, Insights, Settings, and About against `web/sample-data.json`
   with no sign-in, and against live `/api/policies`/`/api/analysis` once
   signed in.
4. The sample data's hostile display name
   (`<img src=x onerror=alert(1)>...`) renders as literal text with no
   injected `<img>` element anywhere in the dashboard.
5. `python3 -m unittest discover -s tests` and
   `cd frontend && npm test` both pass.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Backend tests | `python3 -m unittest discover -s tests` | 174 passed, exit 0 |
| Frontend tests | `cd frontend && npm test` | 86 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |
| Typecheck/build | `cd frontend && npx tsc -b && npx vite build` | exit 0; fixed-name output in `web/` |
| Manual | Live browser walkthrough (sample data + policy drill-down) | Renders correctly, no console errors |

## Documentation

- `README.md` — Quick start, walkthroughs, "How the code fits together",
  HTTP API static routes, "Design goals and scope", and the Windows beginner
  guide all updated for the Node.js build step and the new UI.
- `AGENTS.md` — "Project commands" table updated with the frontend
  build/test commands and the `DECISION-024` exception reference.
- `frontend/README.md` — new; install/dev/build/test instructions.
- `ROADMAP.md` — constraints section annotated with the `DECISION-024`
  exception rather than left silently contradicted.
- `project/status/CURRENT.md` — records this as out-of-band work with its
  open follow-ups (CI, no prior Codex review until this record).

## Security and privacy impact

- Threat-model delta: none intended. Same loopback-only bind, same CSP, same
  Host/Origin checks, same in-memory-only auth/session model. The frontend
  never handles a bearer token or persists anything client-side
  (no `localStorage`/`sessionStorage`/cookies used — mechanically checked by
  both a Python test and a Vitest source scan).
- Data/secret impact: the app-only client secret's handling (never logged,
  cleared on submit/reject/mode-switch, `type="password"`,
  `autocomplete="off"`) is preserved in the new React form; equivalent tests
  now cover it in both Python (static source check) and Vitest (behavioral
  check).
- Dependency/supply-chain impact: introduces a Node.js/npm dependency tree
  (`frontend/node_modules`, not committed) for the build step only — a
  documented, human-approved exception (`DECISION-024`) to the backend's
  stdlib-only constraint. The backend itself gained no new dependency.
- Protected actions: installing Node.js via Homebrew was a protected action
  (installing software) and was confirmed with the human before proceeding
  (see conversation record; not a repository-tracked artifact).

## Stop conditions

- Any finding that the frontend can reach a non-loopback host, weaken the
  CSP, or introduce a client-side secret/token persistence path.
- Any finding that the retained-secret or hostile-markup safety properties
  regressed relative to the previous vanilla UI.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | This issue record (retroactive) | `4cb61161be32b43506bb0e2c1b6921635561054d` | Claimed in the issue record only at this round; no commit-bound artifact (Codex flagged this as F-002) | `project/reviews/issues/ISSUE-0012-4cb61161be32-codex.json` | `BLOCKED` — F-001 (high): device-code polling race could overwrite sample/app-only/signed-out state; F-002 (medium): no durable check evidence |
| 1 | `project/handoffs/ISSUE-0012-handoff.md` (rounds 1-2) | `3748ff13318241e8cbe2bc38debc55e3d3042ecb` | Real command output for all required checks recorded in the handoff, bound to this SHA | `project/reviews/issues/ISSUE-0012-3748ff133182-codex.json` | `BLOCKED` — F-001 (high, deeper form): client-side race fixed, but a stale successful poll left an orphaned authenticated session on the server with no client-reachable way to clear it |
| 2 | `project/handoffs/ISSUE-0012-handoff.md` (round 2 section) | `195bd8e746884c23b4774162667ee5905f2680e1` | Real command output for all required checks recorded in the handoff, bound to this SHA | `project/reviews/issues/ISSUE-0012-195bd8e74688-codex.json` | `CHANGES_REQUIRED` — F-001 (high): the round-2 compensating `authLogout()` is unawaited (a failed logout silently leaves the orphaned token) and unconditional/unscoped (a delayed logout can clear a newer, legitimately-current session, since server-side `AuthManager.logout()` clears all current auth state, not just the abandoned attempt) |

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

**Repair-round budget exhausted at round 2 with an unresolved
`CHANGES_REQUIRED` outcome.** Per `AGENTS.md`, this Claude task stops here
rather than attempting a third fix; the finding below is presented for a
human decision.

## Human decision required

Round 2's remaining **F-001** (high, blocking): the compensating
`authLogout()` call added to handle a stale-successful device-code poll
(round 2) is (a) fire-and-forget — `void authLogout()` — so a failed
logout request silently leaves the orphaned server-side token installed,
and (b) unconditional/unscoped — `POST /api/auth/logout` clears *all*
current `AuthManager` state (device session, access token, retained
app-only credential), not just the specific abandoned attempt, so if a
newer legitimate sign-in (app-only, or a fresh device-code attempt)
completes between the stale poll's detection and this delayed logout
actually reaching the server, that logout call can sign the user back out
of their newer, valid session.

This is a real, narrow race (requires an abandoned-then-approved device
code, in a tight window, overlapping a second successful sign-in) rather
than a routine defect — closing it properly likely needs either a
server-side change (e.g. a poll/session identifier so `/api/auth/logout`
or a new endpoint can clear only the abandoned attempt's token, not
whatever is currently live) or an awaited, ordered client-side cleanup
that checks the session is still the stale one before clearing it. Both
options touch `auth.py`/`server.py` behavior, which is beyond what this
already-out-of-band frontend issue's allowed paths cover, and beyond what
another same-day repair round can safely attempt.

**Options for the human:**
1. Accept this as a documented, narrow residual risk (similar in spirit to
   `DECISION-023`'s SEC-001/SEC-003) and proceed to merge, tracking a
   proper fix as separate future work.
2. Authorize a new issue (with its own fresh repair budget) scoped to fix
   this server-session-scoping gap, potentially touching `auth.py`.
3. Direct a different mitigation (e.g., remove the compensating logout
   entirely and instead document that an abandoned-then-approved
   device-code sign-in requires the user to manually sign out, accepting
   the smaller original F-001 window as-is).

## Completion

- Final reviewed product SHA: not yet — blocked pending the human decision above
- Human advance/merge decision: *pending*
- Merge/result SHA: *pending*
- Residual risks or follow-up: the round-2 F-001 residual above; CI not yet
  updated for `npm` commands; no M3 milestone opened; device-code sign-in
  regression (separately reported, believed tenant-side) tracked separately.
- Status record updated: `project/status/CURRENT.md`, this commit
