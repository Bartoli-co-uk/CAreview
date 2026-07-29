# Claude security review: milestone M3 — React/TypeScript dashboard UI

**Outcome:** `PASS_WITH_NOTES`
**Reviewer role:** `Milestone security reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-sonnet-5 (Claude Code harness)`
**Fresh session/task ID:** `same top-level session; conducted as an independent read-only review task per the milestone-security prompt, with project/reviews/milestones/ deliberately not consulted before writing this report`
**Reviewed artifact:** whole repository tree at the frozen candidate, with emphasis on `frontend/`, `server.py`, `auth.py`, `.github/workflows/validate.yml`, `docs/security-boundaries.md`
**Reviewed SHA:** `61d76c57ff2d70fe95988497e6eaafd0b1649a41`
**Base SHA:** `98be0bc562de8f7cf52e3019715bc4cff571ad91` (frozen M2 candidate)
**Created at:** `2026-07-29T19:45:00Z`

- Milestone security outcomes: `PASS`, `PASS_WITH_NOTES`,
  `REMEDIATION_REQUIRED`, `BLOCKED`, or `INCONCLUSIVE`.

This report states only that the review passed within its documented scope
and evidence. It is not a security certification, does not prove the
absence of vulnerabilities, and does not certify compliance.

## Scope and inputs

- `docs/security-boundaries.md` (build-time dependency boundary, frontend
  rendering safety, scoped-abandonment sections — all M3-specific), the
  approved brief/roadmap (`ROADMAP.md` v5, `DECISION-029`), `AGENTS.md`'s
  Security and Protected Actions sections, `frontend/package-lock.json`,
  `.github/workflows/validate.yml`, `server.py`, `auth.py`,
  `frontend/src/` (all source), `frontend/src/test/` (all tests),
  `tests/test_ui_safety.py`, `tests/test_auth.py`, `tests/test_server.py`.
- Independently re-executed at the reviewed SHA: `python3 -m unittest
  discover -s tests` (188 passed), `cd frontend && npm run build && npm
  test` (build succeeded, 91 tests passed), direct source inspection of
  `server.py`'s request-dispatch path and `auth.py`'s `AuthManager.abandon`.
- Excluded: live-tenant sign-in/fetch in either mode (protected action);
  a real npm-registry audit of the 170-package `frontend/package-lock.json`
  dependency tree (no network-based `npm audit` run this session —
  `RISK-009`'s already-accepted gap, not newly discovered here); dynamic
  fuzzing of the frontend or backend.
- Peer report withheld for blind review: `yes`.

## Threat model and trust boundaries

M3 does not move any trust boundary that M1/M2 didn't already establish,
with one genuine exception (`RISK-009`, below). The served application
remains loopback-only (`127.0.0.1:8765`), single-user, with no
authentication beyond that binding — unchanged from M1's `RISK-002`
baseline. `ISSUE-0012` replaced the rendering layer; `ISSUE-0013` added one
new endpoint that clears state, not one that reads or writes anything a
user couldn't already reach; `ISSUE-0014` changed CI only, not anything
that ships to a user.

## Findings

### Rendering safety (`ISSUE-0012`) — verified, no finding

Untrusted tenant-controlled strings (policy/condition display names) render
through JSX's default text-escaping, not `dangerouslySetInnerHTML` or any
hand-rolled HTML construction. I independently re-ran
`frontend/src/test/hostileMarkup.test.tsx` and
`tests/test_ui_safety.py::SampleDataHostileFixtureTests` — both assert the
same hostile fixture (`<img src=x onerror=alert(1)>` embedded in a display
name) renders as literal text with no injected element. I also read
`frontend/src/test/noDangerousSinks.test.ts`: it is a text-pattern scan
(not an AST-based guarantee) across every `.ts`/`.tsx` file under `src/`
for `dangerouslySetInnerHTML`, `eval(`, `new Function(`, `document.write`,
and separately `localStorage`/`sessionStorage`/`document.cookie`. A
text-pattern scan can in principle be defeated by deliberate obfuscation
(e.g. string-concatenated `"ev" + "al("`), but under this project's
single-maintainer, no-external-contributor threat model that gap is
theoretical, not exploitable by an outside party — noted for completeness,
not raised as a blocking finding.

### Static asset serving (`ISSUE-0012`) — verified, no finding

`server.py`'s `STATIC_FILES` remains an explicit allowlist (path → MIME
type), not directory serving — I confirmed the built `web/index.html`,
`index.css`, `index.js` are each named individually, matching
`frontend/vite.config.ts`'s fixed, non-hashed output filenames. The CSP
header (`default-src 'self'; base-uri 'none'; form-action 'none'; ...`,
`server.py` ~line 174) is unchanged by M3 and still sent on every response.

### Scoped device-code abandonment (`ISSUE-0013`) — verified, one accepted residual carried forward

`AuthManager.abandon(handle)` (`auth.py`) clears the pending session or
installed token **only** if it currently matches the exact `_token_handle`
produced by that attempt, under the same lock as every other lifecycle
transition, and never touches `_generation` or app-only state — I read the
method directly and it matches this description exactly (`auth.py:360`).
`server.py`'s `/api/auth/abandon` handler applies the same origin check as
every other POST endpoint (verified in the shared dispatch path before the
path switch) and rejects a missing/non-string handle with 400 before
calling into `AuthManager`. An unknown handle is a safe no-op (asserted by
`tests/test_server.py::test_abandon_unknown_handle_is_ok_and_does_not_clear_a_newer_session`,
which I re-ran). This is a *narrower* endpoint than a full logout: it
cannot be used to sign out a session the caller doesn't already hold the
handle for.

`RISK-011` (abandon-retry "fails open" if every delivery attempt fails
within its ~16-minute window, or the tab closes mid-retry) remains an
accepted residual from `DECISION-027`, unchanged by M3's other two issues.
I re-verified the retry window and the compensating-cleanup logic are
unchanged since that acceptance — no new exposure introduced.

### Build-time dependency boundary (`RISK-009`) — the one genuinely new trust boundary, accepted

`frontend/package-lock.json` introduces 170 packages (I counted
programmatically) that execute with the developer's own privileges at
`npm install`/`npm run build` time — a category of risk the previously
dependency-free, stdlib-only backend never carried. This is accurately
described in `docs/security-boundaries.md`'s "Build-time dependency
boundary" section and accepted as residual by `DECISION-028`, on a
low-traffic/single-user rationale consistent with how this project already
treats `RISK-002`. I have no new finding beyond what's already recorded:
the lockfile is committed (reproducible builds, diffable dependency
changes), the served page loads no external asset (`default-src 'self'`),
and no dependency reaches the Python process that holds tokens/secrets.
`npm audit` still runs nowhere — a real, disclosed gap, not silently
present.

### CI workflow changes (`ISSUE-0014`) — verified, no finding

`.github/workflows/validate.yml`'s `permissions:` block remains
`contents: read` only — the new steps add no write scope, no secret, and
no new `pull_request_target`-style trigger. The new `actions/setup-node`
step is SHA-pinned (`820762786026740c76f36085b0efc47a31fe5020`), matching
the existing `actions/checkout` pin style. `npm ci` (not `npm install`)
builds strictly from the committed lockfile — it cannot silently resolve a
different dependency version in CI than what's committed. No workflow
step introduces network egress beyond what `npm ci`/`actions/setup-node`
already required implicitly (fetching packages from the npm registry,
same as any Node project's CI). I found no token-exposure or
fork-triggered-workflow concern — the workflow runs on `push`/
`pull_request` only, with no elevated permissions granted to fork PRs.

## Residual risks

| Risk | Severity | Treatment | Owner/review date |
|---|---|---|---|
| `RISK-009` (npm build-time supply chain) | Medium | Accepted (`DECISION-028`) | Jay / if scope or user base grows |
| `RISK-010` (onboarding regression — build step now required) | Low | Accepted (`DECISION-029`) | Jay / on build-arrangement change |
| `RISK-011` (abandon-retry fails open after ~16 min) | Low–medium | Accepted (`DECISION-027`) | Jay / if abandon is revisited |

No new critical or high finding. No finding in this report requires a
milestone security-remediation cycle.

## Evidence gaps

- No real npm-registry `npm audit` was run this session against the
  170-package dependency tree — `RISK-009`'s already-disclosed gap, not a
  new one this review introduces.
- No live-tenant end-to-end test (protected action, unchanged from M1/M2).
- No dynamic/fuzz testing of the frontend or backend beyond the committed
  unit/component test suites.

## Disposition

`PASS_WITH_NOTES`: no critical or high finding, one already-accepted
build-time supply-chain residual (`RISK-009`) that this review confirms is
accurately documented and not silently expanded, and one low-severity
observation (text-pattern sink scanning can theoretically be evaded by
obfuscation, immaterial under this project's threat model) recorded for
completeness. This report does not itself accept or re-accept any risk —
`RISK-009`/`RISK-010`/`RISK-011` were each already accepted by the human
in `DECISION-028`/`DECISION-029`/`DECISION-027` respectively, prior to and
independent of this review.
