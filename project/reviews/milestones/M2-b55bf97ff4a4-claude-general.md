# Claude general review: milestone M2 — dual-mode authentication (device-code + app-only)

**Outcome:** `PASS_WITH_NOTES`
**Reviewer role:** `Claude milestone general reviewer (independent, read-only)`
**Provider/model:** `Anthropic — Claude Opus 5 (claude-opus-5), via Claude Code`
**Fresh session/task ID:** `fresh top-level read-only milestone-general task (no peer report seen)`
**Reviewed artifact:** `whole repository tree at the frozen M2 candidate`
**Reviewed SHA:** `b55bf97ff4a4f850a21390443581e26e22f3179a`
**Base SHA:** `6311a11a48a0a7e51e83a14ca4081d431cb46698` (frozen M1 candidate, used as the M2 product-delta baseline)
**Created at:** `2026-07-28T06:53:24Z`

- Plan or issue: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, `BLOCKED`, or
  `USER_DECISION_REQUIRED`.
- Milestone general: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, or
  `BLOCKED`.
- `REMEDIATION_REQUIRED` and `INCONCLUSIVE` are reserved for the separate
  milestone security-review template.

## Scope and inputs

- Requirements/issue: `ROADMAP.md` v4 (approved by `DECISION-015`, binds `9e5ba6d`) — M2 milestone
  exit criteria, the M2 issue-sequence table rows 7–11, the per-issue boundaries table, the
  Verification strategy, and the Risks and decisions table. Plus `project/issues/ISSUE-0007.md`
  through `project/issues/ISSUE-0011.md` and `project/handoffs/ISSUE-0007-handoff.md` through
  `project/handoffs/ISSUE-0011-handoff.md`. Governance inputs read first: `START_HERE.md`,
  `AGENTS.md`, `CLAUDE.md`, `.claude/rules/*`, `docs/workflow.md`, `project/README.md`,
  `project/status/CURRENT.md`, `project/milestones/M2.md`, `project/templates/review.md`.
- Patch/tree: working tree at `b55bf97ff4a4f850a21390443581e26e22f3179a`, `main`, clean
  (`git status --porcelain` empty; branch is 1 ahead of `origin/main`). Product delta reviewed as
  `git diff 6311a11a48a0a7e51e83a14ca4081d431cb46698 b55bf97 -- ':!project'`. Candidate-vs-frozen-SHA
  identity independently verified: `git diff --stat 98be0bc562de8f7cf52e3019715bc4cff571ad91 b55bf97`
  touches only `project/milestones/M2.md` and `project/status/CURRENT.md` — **no product file**, so
  the candidate reviewed here is product-identical to the SHA `project/milestones/M2.md` freezes.
- Verification evidence: re-run independently by this reviewer against the candidate, not taken from
  the handoffs — see [Check accounting](#check-accounting). Handoff-recorded evidence
  (`project/handoffs/ISSUE-0007..0011-handoff.md`, `project/milestones/M2.md`) was read and
  cross-checked against those independent results.
- Excluded or unavailable evidence:
  - Live-tenant sign-in and Graph fetch in **either** mode (protected action per `AGENTS.md` and
    `ROADMAP.md`; explicitly not an M2 exit criterion; accepted residual).
  - Automated in-browser/DOM execution of `web/app.js` (no JavaScript toolchain under the
    stdlib-only constraint; runtime secret-clearing was verified by a human-performed,
    Claude-guided manual walkthrough recorded in `project/handoffs/ISSUE-0010-handoff.md`,
    which I read but did not re-perform).
  - `pwsh` is unavailable locally, so `scripts/validate_repo.py` skipped its PowerShell syntax
    check (it prints a NOTICE; CI runs it on Ubuntu).
  - `project/reviews/milestones/` was deliberately **not** read, per the blind-review instruction.
- Peer report withheld for blind review: `yes`

## Summary

M2 is delivered as specified and is, on the evidence available to me, release-ready for the
documented scope. All five issues (`ISSUE-0007`..`ISSUE-0011`) are `COMPLETE` and merged with human
decision records (`DECISION-016`, `-017`, `-019`, `-020`, `-022`), and each roadmap acceptance
criterion I could check maps to code or a test I read at this SHA.

The three required checks pass at the reviewed SHA when I ran them myself: 173 tests OK / exit 0,
`py_compile` exit 0, and `validate_repo.py` "Repository validation passed (67 required files
checked)". Those match what `project/milestones/M2.md` and the handoffs claim, so the recorded
evidence is neither stale nor overstated.

Cross-issue integration genuinely works end to end. I traced the app-only path
`web/index.html` (`#app-only-mode` form, `type="password"`, `autocomplete="off"`) →
`web/app.js:submitAppOnly()` (JSON body, secret cleared in a `finally`) →
`server.py:_auth_app_only()` (Host + Origin + bounded-format validation before any retention or
egress) → `auth.py:start_app_only()` (tenant validated first, token installed in the *same* slot the
device-code flow uses, secret retained per `DECISION-014`) → `AuthManager.get_token()` silent renewal
→ `server.py:_policies()`/`_analysis()`. `tests/test_server.py::AppOnlyEndpointTests` exercises that
whole chain, including silent renewal succeeding transparently through `/api/policies` and
`/api/analysis`, and a renewal *failure* surfacing a stable non-5xx error. A live loopback smoke test
I ran confirmed the Host allowlist (403), the Origin requirement (403), the pre-egress 400 on a
disallowed tenant alias, the security headers, and an empty server log.

Device-code mode is genuinely unchanged. `git diff` from the M1 candidate to this SHA shows **zero
deleted lines** in `tests/test_auth.py`, `tests/test_server.py`, `tests/test_ui_safety.py`, and
`web/app.js` — every pre-existing device-code test survives unmodified and passes. The only
behavioural change to the device-code flow is the intentional `SCOPES` trim, which *is*
`ISSUE-0007`'s acceptance criterion, asserted by
`tests/test_auth.py::test_scopes_is_policy_read_all_only` and
`::test_devicecode_request_body_carries_only_policy_read_all`. `web/index.html`'s only deletions are
re-indentation of the existing device-code block into the new `#devicecode-mode` wrapper (all IDs
preserved), and `#signout-btn` correctly moved to be a sibling of both modes so it is reachable after
an app-only sign-in. `graph.py`, `analyzer.py`, and `rules.py` are byte-identical to M1, which is the
evidence (not the assertion) that brief A6 holds.

Secret-handling discipline is the strongest part of the change and is proven by construction rather
than claimed: `auth.py::_classify_app_only_error()` discards provider text entirely in favour of
three local labels; `tests/test_server.py::test_secret_absent_from_every_response_body` scans every
validation-rejection, malformed-body, success, each 502 label, and a superseded-race response for the
literal, URL-encoded, and JSON-escaped forms of the synthetic secret; `tests/test_auth.py`'s
`AppOnlySecretLeakTests` does the same for return values, `repr()`, exception messages, `logging`,
and stderr. I independently confirmed the only secret-shaped literal anywhere in tracked files is
`test-only-fake-secret-DO-NOT-USE-xyz123`, in `tests/` only. Documentation (`README.md`,
`docs/security-boundaries.md`) covers both modes, the exact app-only prerequisite, that CAreview
never creates an app registration, the secret lifecycle and rotation/revocation, the certificate
deferral, and names `RISK-001`/`002`/`004`/`005`/`006` in the Known limitations table — all five the
milestone requires.

This is not a `PASS` for two reasons, neither of them a defect in the shipped behaviour. First,
`project/milestones/M2.md` still carries placeholder fields — the freeze SHA is literally
`<FREEZE-SHA>` and all four review rows are `<pending>` — so the milestone record does not yet name
the commit these reviews target (F-006); that is expected mid-gate but must be closed before the
human decision. Second, `ROADMAP.md` still describes M2 as "PLANNED — not approved" and says
`ISSUE-0009` may start "once the human decides to begin it", which contradicts
`project/status/CURRENT.md`, `DECISION-015`, and the merged reality (F-003). Alongside four low/info
engineering notes (a duplicated silent-renewal request under concurrency, a missing `no-store` on the
400 path, a stale README headline claim, and some accessibility gaps in the new form), that is enough
uncertainty in the *records* to withhold a clean `PASS`. No finding is critical, high, or blocking,
and none requires a new candidate before the human sees the package.

Reviews passing means only that they passed for the documented scope, SHA, and evidence. This is not
a security certification, and it does not constitute milestone acceptance — that decision is the
human's alone.

## Findings

### FINDING-001: Concurrent silent renewal issues duplicate client-credentials requests

- Classification: `ADVISORY`
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Location: `auth.py:423-444` (`AuthManager.get_token`), `auth.py:389-420` (`_renew_app_only`);
  triggered by `server.py:236` / `server.py:255` (`_policies`/`_analysis` each call
  `AUTH.get_token()`) driven from `web/app.js:360-363` (`Promise.all([fetch("/api/policies"),
  fetch("/api/analysis")])`)
- Expected: one expired app-only token produces exactly one silent renewal request to
  `login.microsoftonline.com`, and concurrent callers share its result.
- Observed: `get_token()` releases the lock before calling `_renew_app_only()`, and
  `_renew_app_only()` performs its network call outside the lock with no in-flight-renewal guard, so
  N concurrent callers each issue their own client-credentials POST. The UI's own `Promise.all` fires
  `/api/policies` and `/api/analysis` simultaneously, so under `ThreadingHTTPServer` this is the
  normal path, not an edge case: every app-only token expiry costs two identity requests instead of
  one.
- Evidence: reproduced deterministically at this SHA with an injected mock transport and clock (no
  network):

  ```text
  $ python3 - <<'PY'  # mock transport + fake clock, two concurrent get_token() calls
  calls after initial sign-in: 1
  both got a token: [True, True]
  total identity calls (1 sign-in + renewals): 3
  PY
  ```

  i.e. two renewals for one expiry. Code reading confirms the generation guard prevents *stale*
  installs but does not coalesce *concurrent* renewals.
- Impact: doubles load on the tenant token endpoint at each expiry and doubles how often the retained
  secret is placed on the wire per renewal cycle. Could contribute to Entra request throttling under
  repeated refreshes. No incorrect state results — the guard makes the last valid install win, and
  both tokens are legitimate — and there is no disclosure path, so the impact is efficiency and
  robustness, not correctness or confidentiality.
- Remediation: coalesce renewals — e.g. hold a dedicated renewal lock (or a "renewal in progress"
  event) so the second caller waits for the first result instead of starting its own request; or
  re-check `self._access_token` validity immediately after acquiring the lock at the top of
  `_renew_app_only()` and return `True` if another thread already installed a fresh token.
- Verification: extend `tests/test_auth.py::AppOnlyLifecycleTests` with a blocking mock transport
  that counts invocations while two threads call `get_token()` on an expired token, asserting exactly
  one client-credentials request is made and both callers receive a token.
- Disposition: `open`

### FINDING-002: 400 validation rejections on `POST /api/auth/app` omit `Cache-Control: no-store`

- Classification: `ADVISORY`
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Location: `server.py:175-182` (`_reject`) as used by `server.py:353-361` (`_auth_app_only`
  validation branches); contrast `server.py:370` and `server.py:372`, which both pass
  `no_store=True`
- Expected: `ROADMAP.md` row 9 requires "`no-store` on any response reflecting auth state". The
  success (200) and provider-failure (502) responses honour this.
- Observed: the three input-validation rejections (invalid tenant, invalid `client_id`, invalid
  `client_secret`) go through `_reject()`, which never emits `Cache-Control`. Confirmed live against
  the running candidate:

  ```text
  $ curl -s -i -X POST -H "Host: 127.0.0.1:8791" -H "Origin: http://127.0.0.1:8791" \
      -d '{"tenant":"organizations","client_id":"6666...","client_secret":"zzz"}' \
      http://127.0.0.1:8791/api/auth/app
  HTTP/1.0 400 Bad Request
  Content-Type: application/json; charset=utf-8
  Content-Security-Policy: default-src 'self'; ...
  X-Content-Type-Options: nosniff
  {"error": "invalid tenant"}          <- no Cache-Control header
  ```

  The same gap applies to the pre-existing `/api/auth/start`, `/api/auth/poll`, and
  `/api/auth/logout` responses, which is M1 behaviour rather than an M2 regression.
- Evidence: the live `curl` transcript above, plus `tests/test_server.py:225,310,341` showing
  `no-store` is asserted only for `/api/policies`, `/api/analysis`, and the app-only 200.
- Impact: minimal. These bodies are fixed local error labels containing no tenant data and — proven
  by `test_secret_absent_from_every_response_body` — no representation of the secret. A cached copy
  discloses only that a malformed sign-in attempt was rejected.
- Remediation: add `Cache-Control: no-store` in `_reject()` (or pass a `no_store` flag from
  `_auth_app_only`'s validation branches) so every `/api/auth/*` response is consistently
  non-cacheable.
- Verification: extend `AppOnlyEndpointTests` to assert
  `resp.getheader("Cache-Control") == "no-store"` on each 400 branch as well as the 200 and 502.
- Disposition: `open`

### FINDING-003: `ROADMAP.md` still describes M2 as unapproved and not started

- Classification: `ADVISORY`
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Location: `ROADMAP.md:16-17` ("`ISSUE-0009` may start … once the human decides to begin it"),
  `ROADMAP.md:186` (M2 milestone Status cell: `PLANNED` (unapproved)), `ROADMAP.md:202`
  (heading "### M2 issue sequence (PLANNED — not approved)")
- Expected: `AGENTS.md` ("if instructions conflict … stop and ask") and `START_HERE.md` ("if the two
  ever disagree … the disagreement itself should be repaired before any other work") require the
  records to agree. `DECISION-015` approved roadmap v4 and authorized M2;
  `project/status/CURRENT.md` records "M2 — `PLANNED`, approved; all 5 issues complete; milestone
  review in progress".
- Observed: three places in `ROADMAP.md` still assert the pre-approval, pre-implementation state.
  The `Delivery status` line (`ROADMAP.md:12`) and the per-issue Status cells *were* correctly
  refreshed to `COMPLETE`/merged in commit `98be0bc`, so the file contradicts itself internally as
  well as contradicting `CURRENT.md`.
- Evidence: `git diff 9d346f6 b55bf97 -- ROADMAP.md` shows only the `Delivery status` line and rows
  10/11 of the issue table were updated; the milestone-table Status cell, the section heading, and
  the narrative paragraph were not. Read directly at the reviewed SHA.
- Impact: a fresh agent or contributor reading `ROADMAP.md` alone — which `START_HERE.md` and
  `AGENTS.md` both put in the required reading list — could conclude M2 was never approved and that
  implementation was unauthorized. No effect on shipped behaviour, scope, sequence, or risk, and the
  authoritative records (`DECISION-015`, `CURRENT.md`, `project/milestones/M2.md`) are correct and
  unambiguous.
- Remediation: refresh the M2 milestone Status cell and the section heading to match the merged
  reality, and rewrite the stale `ISSUE-0009` narrative sentence. `ROADMAP.md`'s own Change control
  section explicitly permits Status-cell updates without a new approval; the heading and narrative
  sentence are outside that exception and should be corrected as an explicitly-scoped record repair
  rather than silently.
- Verification: re-read `ROADMAP.md:6-17`, `:186`, and `:202` and confirm they agree with
  `project/status/CURRENT.md` and `DECISION-015`; `python3 scripts/validate_repo.py` still passes.
- Disposition: `open`

### FINDING-004: `README.md` headline still claims "no Azure app registration" without qualification

- Classification: `ADVISORY`
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Location: `README.md:5-7`
- Expected: after M2, statements about registration requirements should be scoped to the default
  device-code mode, as `README.md:387-391` ("Zero registration, zero build **by default**") and
  `ROADMAP.md`'s Project outcome ("to use the default (M1) path") correctly do.
- Observed: the opening paragraph still reads "Everything runs on your own machine: one Python
  process, no installs, no Azure app registration, no build step" with no qualifier, immediately
  above a status banner that advertises dual-mode auth. App-only mode's documented prerequisite
  (`README.md:107-114`) is precisely a user-owned app registration.
- Evidence: `README.md:5-7` read at the reviewed SHA, contrasted with `README.md:100-121` and
  `README.md:387-391`.
- Impact: cosmetic and self-correcting within one screen of scrolling — the Contents list, the
  "What it does" section, and the dedicated App-only section all qualify it. A skim-reader could
  briefly believe app-only mode also needs no registration.
- Remediation: add "for the default sign-in mode" (or similar) to that sentence, matching the
  wording already used in Design goals and scope.
- Verification: re-read `README.md:5-7`; confirm `python3 scripts/validate_repo.py` still passes
  (it link/anchor-checks the README).
- Disposition: `open`

### FINDING-005: Accessibility gaps in the new app-only sign-in form

- Classification: `ADVISORY`
- Severity: `low`
- Confidence: `medium`
- Blocking: `no`
- Location: `web/index.html:33-35` (`#app-only-toggle-btn`), `web/index.html:38-56`
  (`#app-only-mode`), `web/index.html:59` (`#auth-status`); status updates written by
  `web/app.js:28-33` (`setAuthStatus`)
- Expected: status changes that are the sole feedback for a submit (including failures) should be
  announced to assistive technology, a disclosure control should expose its expanded state, and a
  credential form should support Enter-to-submit.
- Observed: (a) `#auth-status` is toggled via the `hidden` attribute and `textContent` with no
  `role="status"`/`aria-live`, so "signed in (app-only)" and "app-only sign-in failed: …" are not
  announced — this is the only feedback the app-only path gives; (b) `#app-only-toggle-btn` has no
  `aria-expanded`/`aria-controls` for the region it reveals; (c) the app-only inputs are not inside a
  `<form>`, so pressing Enter in the secret field does nothing. Labels themselves are correct
  (wrapping `<label>` elements), the CSP `<meta>` is unchanged, and `[hidden]` is not overridden by
  any `display` rule in `web/style.css` (checked lines 50-99), so the show/hide mechanism is sound.
- Evidence: `web/index.html` and `web/app.js` read at the reviewed SHA; `grep -n "hidden\|display"
  web/style.css` confirms no `display` rule targets `#app-only-mode` or `#devicecode-mode`.
- Impact: screen-reader and keyboard users get degraded feedback on the new advanced path. (a) is
  partly pre-existing M1 behaviour for `#auth-status`, but M2 routes new error messaging through it.
  (c) is likely deliberate: `web/index.html:7` sets `form-action 'none'` in the CSP, so a real
  `<form>` was probably avoided on purpose — hence medium rather than high confidence that this is
  unintended.
- Remediation: add `role="status"` (or `aria-live="polite"`) to `#auth-status`; add
  `aria-expanded`/`aria-controls` to `#app-only-toggle-btn`, updated in `showAppOnlyMode()` /
  `showDeviceCodeMode()`; optionally add a `keydown` handler on the secret field mapping Enter to
  `submitAppOnly()` (no `<form>` needed, so the CSP stays untouched). Accessibility is not named in
  M2's exit criteria, so treat this as follow-up rather than remediation of this candidate.
- Verification: extend `tests/test_ui_safety.py::AppOnlyModeToggleTests` with static assertions for
  the ARIA attributes; re-run the manual browser walkthrough with a screen reader if the owner wants
  runtime confirmation.
- Disposition: `open`

### FINDING-006: `project/milestones/M2.md` still holds placeholder freeze/report fields

- Classification: `ADVISORY`
- Severity: `info`
- Confidence: `high`
- Blocking: `no`
- Location: `project/milestones/M2.md:36-47` (freeze SHA `<FREEZE-SHA>`; all four review rows and
  the blind-withholding line `<pending>`), `:51-58` (findings fields `<pending>`), `:94-96` (human
  decision `<pending>`)
- Expected: `docs/workflow.md` §8 requires every report to name the same full candidate SHA and the
  milestone record to collect the four reports; `AGENTS.md` requires that missing or stale evidence
  block advancement.
- Observed: the record names the *product* freeze SHA `98be0bc562de8f7cf52e3019715bc4cff571ad91` and
  explains that the milestone-record commit is metadata-only, but the literal freeze SHA the four
  reviews target is still the placeholder `<FREEZE-SHA>`. The record therefore does not yet name
  `b55bf97ff4a4f850a21390443581e26e22f3179a`.
- Evidence: `project/milestones/M2.md` read at the reviewed SHA. I independently verified the
  identity claim the record rests on: `git diff --stat 98be0bc562de8f7cf52e3019715bc4cff571ad91
  b55bf97ff4a4f850a21390443581e26e22f3179a` returns only `project/milestones/M2.md` and
  `project/status/CURRENT.md` — no product file — so reviewing `b55bf97` is equivalent to reviewing
  `98be0bc`'s product tree, and traceability holds despite the placeholder.
- Impact: none on the software. It is an expected mid-gate state — the record cannot contain its own
  commit SHA at the moment it is written, and `docs/workflow.md` explicitly says reports are copied
  in after all four initial reviews finish. Flagged only so it is not forgotten: leaving it
  unresolved would make the milestone package unverifiable at the human decision point.
- Remediation: when the four initial reports are recorded, replace `<FREEZE-SHA>` with
  `b55bf97ff4a4f850a21390443581e26e22f3179a`, fill the four review rows with their paths, SHAs, and
  outcomes, set "Initial peer conclusions were withheld" to `yes`, and complete the findings and
  human-decision sections.
- Verification: re-read `project/milestones/M2.md` and confirm no `<pending>`/`<FREEZE-SHA>` token
  remains and that all four rows name the same full SHA; `python3 scripts/validate_repo.py` passes.
- Disposition: `open`

## Check accounting

| Required check | Evidence against reviewed SHA | Result |
|---|---|---|
| Target identity — reviewing the intended candidate | `git rev-parse HEAD` → `b55bf97ff4a4f850a21390443581e26e22f3179a`; `git status --short --branch` → `## main...origin/main [ahead 1]`, no modified files | `pass` |
| Candidate is product-identical to the SHA frozen in `project/milestones/M2.md` | `git diff --stat 98be0bc562de8f7cf52e3019715bc4cff571ad91 b55bf97` → only `project/milestones/M2.md` (+99) and `project/status/CURRENT.md` (+25/-31); no product file | `pass` |
| Tests | `python3 -m unittest discover -s tests` → `Ran 173 tests in 34.413s` / `OK` / `EXIT=0` | `pass` |
| Lint / compile | `python3 -m py_compile $(git ls-files '*.py')` → `EXIT=0`, no output | `pass` |
| Governance validation | `python3 scripts/validate_repo.py` → "Repository validation passed (67 required files checked)." / `EXIT=0`; NOTICE: PowerShell syntax check skipped (no `pwsh`; CI runs it on Ubuntu) | `pass` (with the documented `pwsh` gap) |
| Requirement traceability — `ISSUE-0007` (scope trim) | `auth.py:55` `SCOPES = "https://graph.microsoft.com/Policy.Read.All"`; `tests/test_auth.py:67,75` assert the constant and the device-code request body; `README.md:393-395` and `docs/security-boundaries.md:133-140` no longer claim three scopes | `pass` |
| Requirement traceability — `ISSUE-0008` (app-only in `auth.py` only) | `auth.py:127-142` `build_client_credentials_request` (scope not overridable), `:350-387` `start_app_only`, `:389-420` `_renew_app_only`, `:338-347` `logout` clears secret; `tests/test_auth.py` `AppOnlyRequestBuildingTests`/`AppOnlyLifecycleTests`/`AppOnlySecretLeakTests` (incl. 6 in-flight race tests); `graph.py` + `server.py` untouched by that issue | `pass` |
| Requirement traceability — `ISSUE-0009` (`POST /api/auth/app`) | `server.py:115-154` bounded validators, `:347-372` handler (Host/Origin/body-size reused; 400 before egress; 502 stable label; `no_store` on 200/502); `tests/test_server.py:316-812` boundary min/max/one-over/malformed per field, renewal success + failure through `/api/policies` and `/api/analysis`, logout clearing, secret-absence scan, empty stderr | `pass` (see FINDING-002 for the 400 `no-store` gap) |
| Requirement traceability — `ISSUE-0010` (UI toggle/form) | `web/index.html:21-56` default device-code + hidden app-only form, `type="password"`, `autocomplete="off"`, `.caution`; `web/app.js:139-218` alias mirror, `clearAppOnlySecretField()` on submit/`finally`, both mode switches, and `signOut`; `tests/test_ui_safety.py:77-151` (10 static tests); manual browser walkthrough recorded in `project/handoffs/ISSUE-0010-handoff.md` (human-performed, rounds 0+1) | `pass` |
| Requirement traceability — `ISSUE-0011` (documentation) | `README.md:100-202` app-only prerequisite, "CAreview never creates this for you", secret lifecycle, rotation/revocation, certificate deferral, dual-mode end-to-end walkthrough with live steps marked protected; `docs/security-boundaries.md:97-132` trust-boundary delta + widened `RISK-002` + `RISK-006` + certificate deferral | `pass` |
| Cross-issue integration — app-only works end to end | Traced `web/index.html` → `web/app.js:submitAppOnly` → `server.py:_auth_app_only` → `auth.py:start_app_only` → shared token slot → `server.py:_policies`/`_analysis`; proven by `tests/test_server.py::test_policies_and_analysis_work_after_app_only_sign_in` and `::test_silent_renewal_success_is_transparent_to_policies_and_analysis` | `pass` |
| Regressions — device-code mode genuinely unchanged | `git diff 6311a11a48a0 b55bf97 -- tests/test_auth.py tests/test_server.py tests/test_ui_safety.py web/app.js \| grep '^-'` → **no deletions**; `web/index.html` deletions are re-indentation into `#devicecode-mode` only, all IDs preserved; the single behavioural change is the intended `SCOPES` trim | `pass` |
| Regressions — `graph.py` unchanged (brief A6) | `git diff --stat 6311a11a48a0 b55bf97 -- graph.py analyzer.py rules.py` → empty | `pass` |
| Correctness — auth state machine and races | `auth.py` generation-counter guards on `start`, `start_app_only`, `_renew_app_only`; network calls outside the lock with post-call identity/generation checks; 6 dedicated in-flight race tests in `tests/test_auth.py:410-544` | `pass` (see FINDING-001, a concurrency inefficiency, not a correctness fault) |
| Error handling | `auth.py:88-100` provider text discarded for 3 local labels; `server.py:323-325` broad catch → `internal_error`, never a stack; `server.py:249-251,268-270` Graph errors mapped; `web/app.js:183-200` `try/catch/finally` around the submit so a rejected `fetch()` still clears the secret | `pass` |
| Secret hygiene in tracked files | `git grep` for `client_secret` assignments outside `tests/` → no hits; only literal is `test-only-fake-secret-DO-NOT-USE-xyz123` (`tests/test_auth.py:259`, `tests/test_server.py:24`), which `ROADMAP.md` expects | `pass` |
| Operability — server runs and enforces its boundaries | Live smoke at `CAREVIEW_PORT=8791`: `/api/health` → 200 `{"status": "ok"}` with CSP + `nosniff`; `Host: evil.example` → 403; `POST /api/auth/app` without `Origin` → 403; disallowed tenant alias → 400 `{"error": "invalid tenant"}` before egress; server log file empty | `pass` |
| Performance | Only relevant path is app-only token renewal; measured duplicate renewal under concurrency (FINDING-001). Test suite 34.4s for 173 tests; no other hot path introduced (no persistence, no polling change) | `pass with note` |
| Accessibility | `web/index.html` wrapping `<label>`s correct; `[hidden]` not overridden in `web/style.css:50-99`; missing `aria-live` on `#auth-status`, `aria-expanded` on the toggle, and Enter-to-submit (FINDING-005). Not an M2 exit criterion | `pass with note` |
| Documentation | `README.md` (both modes, prerequisite, lifecycle, rotation, certificate deferral, dual walkthrough, API table entry for `/api/auth/app`, 173-test count accurate) and `docs/security-boundaries.md` (trust-boundary delta) verified by reading at this SHA; anchors validated by `validate_repo.py` | `pass` (see FINDING-004) |
| Migrations | N/A — no persistence in either auth mode; `project/milestones/M2.md:68` records "N/A (no persistence, in either auth mode)". Confirmed: no disk/DB/config write anywhere in `auth.py`/`server.py` | `n/a` |
| Known limitations — `RISK-001/002/004/005/006` accurately in README | `README.md:445-453` table carries all five by ID plus "Live sign-in unverified" and "Browser rendering"; each matches its `ROADMAP.md:290-295` description, including `RISK-002`-as-widened covering the retained secret and `RISK-006` stating `.default` cannot be narrowed | `pass` |
| Release readiness — issue closure and human decisions | `ISSUE-0007`..`ISSUE-0011` all `Status: COMPLETE` with candidate and merge SHAs recorded; merges confirmed in `git log`; `DECISION-016`, `-017`, `-019`, `-020`, `-022` present in `project/decisions/` | `pass` |
| Milestone record completeness | `project/milestones/M2.md` freeze SHA and four review rows still placeholders (FINDING-006); `ROADMAP.md` M2 status narrative stale (FINDING-003) | `pass with note` |
| Live end-to-end sign-in (either mode) | Not performed — protected action per `AGENTS.md`; explicitly excluded from M2 exit criteria by `ROADMAP.md`; declared as an accepted residual in `project/milestones/M2.md:32` and `README.md:447` | `n/a (declared gap)` |

## Limitations and uncertainty

- **No live-tenant evidence.** Nothing here establishes that device-code sign-in or a
  client-credentials grant actually succeeds against a real Entra tenant, that the first-party client
  is permitted there, or that `.default` returns the expected permissions. Every auth assertion in
  this report rests on mock transports. This is a deliberate, roadmap-sanctioned gap, not an
  oversight — but it is the single largest thing this review does **not** establish.
- **No JavaScript execution.** I read `web/app.js` and confirmed the clearing calls exist on all
  three paths, and I verified the static assertions in `tests/test_ui_safety.py` genuinely check what
  they claim. I did not execute the page. That the clearing code actually *runs* rests on the
  human-performed manual walkthrough recorded in `project/handoffs/ISSUE-0010-handoff.md`, which I
  read but could not independently reproduce (no browser-automation tool in this session). The
  roadmap anticipates exactly this and accepts the manual walkthrough as the substitute evidence.
- **`pwsh` unavailable**, so `validate_repo.py`'s PowerShell syntax check of the review launcher was
  skipped locally. The validator prints this itself and CI covers it on Ubuntu; I did not verify the
  CI run.
- **Concurrency findings are bounded by what a mock can show.** FINDING-001 was reproduced with an
  injected transport and fake clock. I did not attempt to characterise behaviour under real network
  latency, real Entra throttling, or many simultaneous clients.
- **This is a general review, not a security review.** I looked at secret handling because M2's
  requirements are written in those terms and because integration correctness depends on it, but the
  named end-to-end secret-lifecycle check is the separate security pair's responsibility under
  `ROADMAP.md`'s M2 exit criteria and `docs/security-boundaries.md`. Nothing here should be read as
  discharging that check.
- **Blindness maintained.** I did not read anything under `project/reviews/milestones/`, so I have
  no knowledge of the peer Codex general review's conclusion. If our conclusions diverge, that
  divergence is genuine and should be reconciled on the evidence rather than assumed resolved.
- **Governance scope.** I verified the *records* (decisions, issue states, handoffs, status file) are
  internally consistent and name the SHAs they claim, except as noted in FINDING-003 and FINDING-006.
  I did not and cannot verify who authorized anything, only that the decision records exist in Git.
- **No approval implied.** This report supports the human's milestone decision; it does not make it,
  and it is not a security certification.

Any candidate source change invalidates this report. Saving this exact report as later metadata does not change the SHA it reviewed.
