# Claude general review: milestone M2 — dual-mode authentication (device-code + app-only)

**Outcome:** `CHANGES_REQUIRED`
**Reviewer role:** `Milestone general reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-opus-5 (Claude Code harness)`
**Fresh session/task ID:** `fresh independent review task; no prior-session context reused (retry after two transient API failures that produced no partial report)`
**Reviewed artifact:** `project/milestones/M2.md` and the whole repository tree at the frozen candidate
**Reviewed SHA:** `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d`
**Base SHA:** `6311a11a48a0a7e51e83a14ca4081d431cb46698` (frozen M1 candidate, used as the M2 delta baseline)
**Created at:** `2026-07-28T07:25:08Z`

- Plan or issue: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, `BLOCKED`, or
  `USER_DECISION_REQUIRED`.
- Milestone general: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, or
  `BLOCKED`.
- `REMEDIATION_REQUIRED` and `INCONCLUSIVE` are reserved for the separate
  milestone security-review template.

## Scope and inputs

- Requirements/issue: `ROADMAP.md` v4 (approved by `DECISION-015`, binds `9e5ba6d`) — "Milestones" M2 row, "M2 issue sequence" rows 7–11, "Per-issue boundaries", "Verification strategy", "Documentation plan", "Risks and decisions", "Definitions of done"; `project/issues/ISSUE-0007.md` … `ISSUE-0011.md`; `project/handoffs/ISSUE-0007-handoff.md` … `ISSUE-0011-handoff.md`; `project/milestones/M2.md`; `project/status/CURRENT.md`; `START_HERE.md`; `AGENTS.md`; `docs/workflow.md`; `project/README.md`; `README.md`; `docs/security-boundaries.md`.
- Patch/tree: working tree at `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d`, confirmed by `git rev-parse HEAD`. `git status --porcelain=v1 -b` shows `## main...origin/main [ahead 2]` and only two untracked files, both under `project/reviews/milestones/` (a concurrent security report and a superseded prior-candidate general report). No tracked file is modified, so the reviewed tree is the committed candidate.
- Verification evidence: independently re-executed by this reviewer at the reviewed SHA — `python3 -m unittest discover -s tests` (`Ran 173 tests … OK`, exit `0`), `python3 -m py_compile $(git ls-files '*.py')` (exit `0`), `python3 scripts/validate_repo.py` (`Repository validation passed (67 required files checked).`, exit `0`, with a NOTICE that the PowerShell syntax check was skipped because `pwsh` is unavailable locally and runs in CI). Python 3.14.6.
- Excluded or unavailable evidence: `project/reviews/milestones/` was deliberately excluded from reading per the blind-review instruction (see disclosure in Limitations); live-tenant sign-in and Graph fetch in either mode (protected action, not an M2 exit criterion); in-browser automated runtime testing (no browser-automation tool available; the repository records a human-performed, Claude-guided manual walkthrough instead); `pwsh` syntax check.
- Peer report withheld for blind review: `yes` — the concurrently running Codex general review of this candidate was not read, and this report has not been shown to it. One disclosure is recorded in Limitations.

## Summary

M2's product work is, on the evidence I could verify independently, complete
and sound. All five ROADMAP v4 acceptance rows (`ISSUE-0007`..`ISSUE-0011`)
trace to merged code with matching tests; the app-only path works end to end
as a coherent chain (`web/app.js` → `POST /api/auth/app` → `server._auth_app_only`
→ `AuthManager.start_app_only` → the shared in-memory token slot → `/api/policies`
and `/api/analysis`); the device-code path is unchanged apart from the
intended `SCOPES` trim; and all three required checks pass at the exact
reviewed SHA when I run them myself. `README.md` and `docs/security-boundaries.md`
document both modes, the app-only prerequisite, the secret lifecycle,
rotation/revocation, the certificate deferral, and all five applicable risks
(`RISK-001`/`002`/`004`/`005`/`006`) accurately. Migrations are genuinely
N/A (no persistence in either mode).

The metadata defect that the previous candidate carried has been substantively
addressed: `project/milestones/M2.md` no longer binds its Verification-evidence
table to the pre-freeze product SHA, and the `<FREEZE-SHA>` placeholder is
resolved. I independently confirmed the record's byte-identity claim —
`git diff --name-only 98be0bc 9c01749` returns only paths under `project/`, so
the product tree at the reviewed SHA is identical to `98be0bc`.

The outcome is nevertheless `CHANGES_REQUIRED`, for governance-record defects
rather than code defects. Three records in the milestone package are stale or
self-adjudicating in ways `AGENTS.md` treats as blocking: `ROADMAP.md` still
labels M2 `PLANNED (unapproved)` and heads its M2 issue table "PLANNED — not
approved", contradicting `DECISION-015` and the roadmap's own Delivery-status
line; `project/status/CURRENT.md` was not updated in the corrective commit and
still binds the M2 candidate to `98be0bc` with a now-misleading "this commit"
self-reference, while asserting that no round-1 review has been run; and
`project/milestones/M2.md` itself declares the b55bf97 → 9c01749 correction to
be a non-countable remediation cycle, which is an accounting judgement about a
milestone gate that the workflow reserves for the human. None of these require
a product change, and none affect the code's correctness — but they are exactly
the class of contradictory/stale record the milestone rules say must be
repaired before advancement. This report is not a security certification and
does not constitute human approval.

## Findings

### F-001: `ROADMAP.md` still declares M2 unapproved, contradicting `DECISION-015` and its own Delivery-status line

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes`
- Location: `ROADMAP.md` — "Milestones" table, `M2` row `Status` cell (`PLANNED (unapproved)`); `ROADMAP.md` — heading `### M2 issue sequence (PLANNED — not approved)`
- Expected: The approved roadmap should state M2's approval status consistently. `DECISION-015` approves roadmap v4 at `9e5ba6d` and authorizes M2 implementation; the roadmap's own header line reads "`M2` is `PLANNED`, approved (`DECISION-015`)"; all five M2 issues are `COMPLETE` and merged under `DECISION-016`/`017`/`019`/`020`/`022`. Status cells are explicitly designated live delivery tracking that must be kept in step with committed evidence ("Change control" section).
- Observed: The milestone table's `M2` `Status` cell reads `PLANNED (unapproved)` and the M2 issue-sequence heading reads "(PLANNED — not approved)". Both are pre-`DECISION-015` language that survived the v4 approval. A reader consulting `ROADMAP.md` alone — which `START_HERE.md` and `AGENTS.md` both mandate as required reading — would conclude that M2 was implemented without approval.
- Evidence: `ROADMAP.md` line 6 (`**Delivery status:** … M2 is PLANNED, approved (DECISION-015); ISSUE-0007 COMPLETE and merged … ISSUE-0011 COMPLETE and merged`) versus the milestone-table `M2` row's trailing cell `| PLANNED (unapproved) |` and the `### M2 issue sequence (PLANNED — not approved)` heading. `project/decisions/DECISION-015-roadmap-v4-approval.md` exists and is cited throughout. The roadmap's "Change control" section states that status cells are live tracking whose update "changes no scope, sequence, acceptance criterion, or risk".
- Impact: Internal contradiction in an approved governing artifact that is part of the milestone package under review. `AGENTS.md` (Review rules; Milestone gates) treats contradictory evidence as blocking. There is no code impact and no ambiguity about the real approval state once `DECISION-015` is read, so the practical risk is misreading rather than unauthorized work.
- Remediation: Update the two status labels to reflect the recorded evidence — for example `APPROVED (DECISION-015); all five issues COMPLETE; milestone acceptance gate in progress` in the milestone table's `M2` `Status` cell, and drop "— not approved" from the M2 issue-sequence heading. This is a status-cell/heading-label update permitted by "Change control" and requires no new roadmap version.
- Verification: `grep -n "unapproved\|not approved" ROADMAP.md` returns no hit that contradicts `DECISION-015`; re-read the Delivery-status line, the milestone table, and the M2 issue-sequence heading and confirm they agree.
- Disposition: `open`

### F-002: `project/status/CURRENT.md` is stale against the corrected candidate and still binds M2 to the pre-freeze SHA

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes`
- Location: `project/status/CURRENT.md` lines 20–33 (Summary), line 43 (`Active milestone`), line 46 (`Reviewed product commit`), line 48 (`Latest milestone reviews`)
- Expected: `CURRENT.md` is designated "the single authoritative index of the current stage" (`START_HERE.md`) and "the first current-state index [that] must link to the evidence for the current gate and name the next permitted action" (`AGENTS.md`). At the reviewed SHA it should identify `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` as the candidate under review and reflect that a round-1 Codex general review already ran against the superseded candidate `b55bf97`.
- Observed: `git show --stat 9c01749` shows the corrective commit touched only `project/milestones/M2.md` and added `project/reviews/milestones/M2-b55bf97ff4a4-codex-general.json`; `CURRENT.md` was not updated. It therefore still says the candidate is "frozen at product commit `98be0bc562de8f7cf52e3019715bc4cff571ad91` (product-file-identical to this metadata commit's own HEAD)" and "review record commit is this commit" — where "this commit" now resolves to `b55bf97`, not the candidate under review. It also states "The four mandatory fresh, blind reviews … have not yet been run", and `Latest milestone reviews` says "`M2` round 1: not yet run — this commit freezes the candidate and opens the review window", neither of which mentions the completed-and-superseded round-1 Codex general review now committed in the tree.
- Evidence: `git show --stat 9c01749` (two files, neither `CURRENT.md`); `project/status/CURRENT.md:46` (`M2` milestone candidate frozen at `98be0bc…`; review record commit is this commit); `project/status/CURRENT.md:28-30` and `:48`; contrast with `project/milestones/M2.md:42-44` ("Freeze commit for review purposes: the milestone-record commit itself") and `project/milestones/M2.md:57-71` (which does record the superseded review).
- Impact: The two authoritative records disagree about which commit is the milestone candidate and about whether any round-1 review exists. This is the same evidence-binding defect class that the corrective commit set out to fix, relocated from `M2.md` into `CURRENT.md`. A fresh task following `START_HERE.md`'s mandated reading order reads `CURRENT.md` first and would target the wrong SHA. `AGENTS.md` and `.claude/rules/review-boundaries.md` both make stale/contradictory evidence blocking.
- Remediation: In a metadata-only update, restate the M2 candidate in `CURRENT.md` as the literal SHA `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` (noting the product tree is identical to `98be0bc`), record the superseded `b55bf97` Codex general review and its retained report path, and update the review-progress wording. Prefer literal SHAs over "this commit" self-references throughout.
- Verification: Re-read `CURRENT.md` and `project/milestones/M2.md` side by side and confirm both name the same literal candidate SHA and the same round-1 review history; confirm `git show --stat` of the repairing commit shows only governance metadata changed.
- Disposition: `open`

### F-003: The milestone record self-adjudicates the b55bf97 → 9c01749 repair as a non-countable general-remediation cycle

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `medium`
- Blocking: `yes`
- Location: `project/milestones/M2.md` lines 57–78 ("Findings, remediation, and invalidation")
- Expected: `AGENTS.md` ("Milestone gates") states that "Any repair that creates a new milestone candidate invalidates all four reports; rerun both general and both security reviews against that one new SHA", permits "at most one milestone general-remediation cycle", and states that "Neither agent may approve its own work, accept risk, or claim that a gate has passed on the human's behalf." Whether a repair consumes the single permitted general-remediation cycle is a gate-accounting judgement, and where it is genuinely arguable it should be presented to the human rather than settled in the record by the author.
- Observed: The record states "General-remediation cycles used: `0` (maximum 1) so far — the above is a record correction prior to a countable review round, not a remediation cycle", while simultaneously acknowledging that a round-1 Codex general review had already completed against `b55bf97`, returned a `REQUIRED` finding, that a new candidate was created in response, and that all four reviews are being rerun against the new SHA. The premise that the correction was made "before any of the four round-1 reviews had all completed" is accurate but is not obviously the criterion the rule uses — the rule keys on a repair creating a new candidate, which is precisely what happened.
- Evidence: `project/milestones/M2.md:57-78`; `AGENTS.md`, "Milestone gates" ("Any repair that creates a new milestone candidate invalidates all four reports…"; "Allow at most one milestone general-remediation cycle…"); `git log --oneline` showing `9c01749 docs(M2): fix milestone record before round-1 reviews complete` as a distinct candidate after `b55bf97`; `git show --stat 9c01749`.
- Impact: If the correction did consume the one permitted general-remediation cycle, then any further general finding on this milestone exhausts the budget and blocks for the human immediately. Recording `0` used pre-commits the project to the more permissive reading of its own gate, decided by the agent that performed the repair. The interpretive case for `0` is genuinely reasonable (no product file changed; the defect was in the review record itself), which is why this is a human ruling to make rather than a defect to silently correct.
- Remediation: Record an explicit human decision (a `DECISION-0xx`) ruling on whether the `b55bf97` → `9c01749` metadata repair consumes the single general-remediation cycle, and reference that decision from `project/milestones/M2.md` in place of the agent's own classification. Do not change the code.
- Verification: A committed decision record naming both SHAs and stating the cycle count; `project/milestones/M2.md`'s cycle line citing that decision rather than asserting the classification on its own authority.
- Disposition: `user-decision`

### F-004: The milestone record never states its candidate SHA literally

- Classification: `ADVISORY`
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Location: `project/milestones/M2.md` lines 26–37 (Verification evidence) and lines 42–51 (Four mandatory reviews)
- Expected: A commit-bound record should be readable without git archaeology. `.claude/rules/review-boundaries.md` requires binding "every code review to an exact commit SHA".
- Observed: The corrected record replaces the wrong SHA with the self-reference "this commit" in every Verification-evidence row, and the "Four mandatory reviews" table's `Reviewed SHA` column is `<pending>` for all four rows. The literal string `9c01749` appears nowhere in `M2.md`. The record is therefore only interpretable by resolving which commit introduced the file — the same ambiguity that made the previous defect possible. The `<pending>` review rows are legitimate at this point in the gate (the reports do not yet exist), so the gap is narrower than it first appears, and my independent re-execution of all three checks at `9c01749` substantiates the evidence regardless of how the record phrases its binding.
- Evidence: `project/milestones/M2.md:34-37` (`| Tests | … | this commit | 173 passed, exit 0 | none |`); `project/milestones/M2.md:48-51` (all `<pending>`); `grep -c "9c01749" project/milestones/M2.md` → 0.
- Impact: Low. Recurrence risk for the exact defect class that triggered this re-candidate, rather than a present error.
- Remediation: When the four review rows are filled in, also replace "this commit" with the literal SHA `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` in the Verification-evidence table and the freeze-commit sentence.
- Verification: `grep -n "9c01749b221d6f7f2d8ff9ca6282cf9172477a3d" project/milestones/M2.md` returns hits in both the Verification-evidence and Four-mandatory-reviews sections; no remaining "this commit" self-reference in an evidence-binding position.
- Disposition: `open`

### F-005: The new app-only sign-in form carries no ARIA affordances for status or caution text

- Classification: `ADVISORY`
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Location: `web/index.html:38-59` (app-only form, caution paragraph, `#auth-status`); `web/app.js:28-32` (`setAuthStatus`)
- Expected: Status changes driven by script ("signing in…", "app-only sign-in failed: provider_error", "signed in (app-only)") should be announced to assistive technology, and the security caution that explains what the secret grants should be programmatically associated with the secret field.
- Observed: `grep -n "aria-\|role=" web/index.html web/app.js` returns no matches. `#auth-status` is a plain `<p>` toggled via the `hidden` attribute with `textContent` set from script, so a screen-reader user gets no announcement when sign-in succeeds or fails. The caution paragraph at `web/index.html:39-43` is visually adjacent to the fields but not linked by `aria-describedby`. Labels do wrap their inputs, and the mode toggles are real `<button>` elements, so keyboard operability and labelling are fine.
- Evidence: `grep -n "aria-\|role=" web/index.html web/app.js` → no matches; `git show 6311a11:web/index.html | grep -c "aria-"` → `0`, confirming this is inherited from the M1 baseline and is not an M2 regression.
- Impact: Low, and out of M2's stated scope — `ROADMAP.md` sets no accessibility acceptance criterion for `ISSUE-0010`. Raised because M2 is where the first credential-entry form was introduced, which is the point at which an unannounced failure state matters most.
- Remediation: Add `role="status" aria-live="polite"` to `#auth-status`, give the caution paragraph an `id` and reference it from the secret input via `aria-describedby`. Track as a follow-up rather than an M2 change, since `web/` edits at this point would create a new milestone candidate.
- Verification: `grep -n "aria-live\|aria-describedby" web/index.html` returns the new attributes; a screen-reader or accessibility-inspector pass confirms status announcements.
- Disposition: `open`

## Check accounting

| Required check | Evidence against reviewed SHA | Result |
|---|---|---|
| Target identity | `git rev-parse HEAD` → `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d`; `git status --porcelain=v1 -b` → `## main...origin/main [ahead 2]` plus two untracked files under `project/reviews/milestones/`, no tracked modifications | `pass` |
| Tests | `python3 -m unittest discover -s tests` → `Ran 173 tests in 34.361s` / `OK`; exit status captured separately as `TESTS_EXIT=0` | `pass` |
| Compile / lint | `python3 -m py_compile $(git ls-files '*.py')` → no output, `PYCOMPILE_EXIT=0` | `pass` |
| Governance validation | `python3 scripts/validate_repo.py` → `Repository validation passed (67 required files checked).`, `VALIDATE_EXIT=0`; emitted `NOTICE: PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu` | `pass` |
| Requirement traceability — `ISSUE-0007` (trim delegated scope) | `auth.py:55` `SCOPES = "https://graph.microsoft.com/Policy.Read.All"` (single scope); `tests/test_auth.py:67` `test_scopes_is_policy_read_all_only`; `git diff 6311a11 9c01749 -- auth.py` shows the three-scope constant removed; `grep -rn "Application.Read.All\|Directory.Read.All" README.md docs/ web/ *.py` hits only an explanatory comment at `auth.py:53-54`, never a claim of requested scope | `pass` |
| Requirement traceability — `ISSUE-0008` (app-only token acquisition in `auth.py` only) | `auth.py:117-142` (`_app_only_authority`, `build_client_credentials_request`, no caller-supplied scope), `:350-387` (`start_app_only`, retains secret), `:389-420` (`_renew_app_only`, generation-guarded), `:423-444` (`get_token` silent renewal); `tests/test_auth.py` — 53 tests including retention, silent renewal, supersession by device-code start, logout clearing, five in-flight stale-response race tests, and secret-absence from return value / `repr()` / literal, URL-encoded and JSON-escaped exception text / `logging` / stderr; `git diff 6311a11 9c01749 --stat` confirms `graph.py` untouched | `pass` |
| Requirement traceability — `ISSUE-0009` (`POST /api/auth/app`) | `server.py:115-154` (bounded tenant/client_id/secret validation before any retention or outbound call), `:310-312` route, `:347-372` handler (400 on input, 502 with a stable local label on provider failure, `no-store`); `tests/test_server.py` — boundary tests at min/max/one-over-max/malformed for each field, `test_policies_and_analysis_work_after_app_only_sign_in`, `test_silent_renewal_success_is_transparent_to_policies_and_analysis`, `test_silent_renewal_failure_surfaces_stable_non_secret_non_5xx_error`, `test_logout_clears_app_only_state`, `test_secret_absent_from_every_response_body`, `test_nothing_logged_to_stderr` | `pass` |
| Requirement traceability — `ISSUE-0010` (UI mode toggle and app-only form) | `web/index.html:21-56` (device-code default visible, app-only `hidden`, `type="password"` + `autocomplete="off"` secret field, in-page caution); `web/app.js:139-218` (alias mirror, clear on submit/mode-switch/logout, `finally`-block clearing on both resolve and reject); `tests/test_ui_safety.py` — 12 M2-specific static assertions incl. storage/console/cookie/URL absence and CSP unchanged; runtime clearing additionally evidenced by the recorded human-performed manual walkthrough in `project/handoffs/ISSUE-0010-handoff.md:84-123, 196+` | `pass` |
| Requirement traceability — `ISSUE-0011` (documentation finalization) | `README.md:100-193` (prerequisite, secret lifecycle, rotation/revocation, certificate deferral, both walkthroughs with live steps marked protected), `README.md:359` (`/api/auth/app` API row), `README.md:440-456` (Known limitations); `docs/security-boundaries.md:104-119` (trust-boundary delta, widened `RISK-002`, `RISK-005`, `RISK-006`); `git diff 6311a11 9c01749 --stat` shows `ISSUE-0011` changed no product source | `pass` |
| Cross-issue integration (app-only end to end) | Chain verified by reading: `web/app.js:184-188` POSTs `/api/auth/app` → `server.py:310-312` routes after Host + Origin + body-size checks → `server.py:347-372` validates then calls `AUTH.start_app_only` → `auth.py:382-386` installs the token in the same `_access_token` slot the device-code path uses → `server.py:236, 257` `_policies`/`_analysis` read it via `AUTH.get_token()` → `web/app.js:211` `loadLiveAnalysis()`. `web/app.js` `initAppOnly()` is wired at `DOMContentLoaded`. End-to-end behaviour additionally asserted by `tests/test_server.py:345, 374, 417` | `pass` |
| Regression — device-code mode unchanged | `git diff 6311a11 9c01749 -- auth.py` removals are confined to the module docstring, comments, and the intended `SCOPES` constant; `start()`/`poll()` logic gains only the clearing of the three new app-only fields. `git diff 6311a11 9c01749 -- server.py` has zero removed lines (purely additive). `web/index.html` removals are re-indentation into the new `#devicecode-mode` wrapper — every device-code element (`#tenant`, `#signin-btn`, `#signout-btn`, `#devicecode`, `#dc-link`, `#dc-code`) is present at `web/index.html:21-32, 58`. Full suite (173) passes, including the inherited device-code tests | `pass` |
| Correctness and error handling | `auth.py:88-100` `_classify_app_only_error` maps every app-only failure to one of `network_error` / `invalid_response` / `provider_error` and never echoes provider text; `auth.py:373-375` and `:407-409` generation guards reject stale in-flight installs; `server.py:323-325` and `:249-251, 268-270` convert unexpected exceptions to stable JSON without stacks; `server.py:369` maps `invalid_tenant` → 400 and everything else → 502. Corresponding negative tests exist in both suites | `pass` |
| Architecture consistency | App-only reuses the existing single token slot, generation counter, lock discipline, Host/Origin/body-size gates, `no-store` policy, and security headers rather than adding a parallel path; per-issue allowed-path boundaries in `ROADMAP.md` were respected (`graph.py` untouched; `ISSUE-0011` touched no product source); stdlib-only constraint holds — no new imports beyond `re` in `server.py` | `pass` |
| Performance | No hot paths introduced; one extra token request per app-only expiry, executed outside the lock (`auth.py:405-406`) so it cannot serialize other requests. Suite runtime 34.4s, dominated by pre-existing socket-based server tests | `pass` |
| Operability | `README.md` "Quick start", "App-only mode (advanced)", "End-to-end walkthrough", "Verify it offline", and the HTTP API table are accurate against the code (`CAREVIEW_PORT`, `/api/auth/app` body shape and rejection semantics, test count 173 all match) | `pass` |
| Accessibility | `grep -n "aria-\|role=" web/index.html web/app.js` → no matches; see F-005. Labels wrap inputs and controls are real buttons, so the gap is announcement/description only, and it is inherited from M1 rather than introduced by M2 | `pass with note` |
| Documentation | `README.md` and `docs/security-boundaries.md` cover both modes, the exact app-only prerequisite, session-lifetime retention with silent renewal, rotation/revocation, and the certificate deferral with its dependency-approval caveat; Markdown link/anchor validation passes inside `validate_repo.py` | `pass` |
| Known limitations / risk documentation | `README.md:445-453` documents `RISK-001`, `RISK-002` (widened, naming the retained secret), `RISK-004`, `RISK-005`, `RISK-006` — each consistent with the corresponding `ROADMAP.md` "Risks and decisions" row — plus the live-sign-in and browser-rendering evidence gaps | `pass` |
| Migrations | `ROADMAP.md` and `project/milestones/M2.md` record `N/A (no persistence, in either auth mode)`; confirmed by inspection — no filesystem or storage writes in `auth.py`, `server.py`, or `web/app.js` beyond serving the static allowlist | `pass` (N/A) |
| Secret hygiene in tracked files | `grep -rln` for the synthetic literal over `git ls-files` excluding `tests/` returns only `ROADMAP.md` (where it appears as the documented example convention); the actual test sentinel is `test-only-fake-secret-DO-NOT-USE-xyz123`, confined to `tests/test_auth.py` and `tests/test_server.py`. No real-looking credential found | `pass` |
| Milestone record binds evidence to this candidate | `project/milestones/M2.md:32-37` now says "this commit" rather than `98be0bc`, and the `<FREEZE-SHA>` placeholder is gone (`git diff b55bf97 9c01749`). Product-tree identity independently confirmed: `git diff --name-only 98be0bc 9c01749` returns only `project/` paths. However the literal SHA is never written — see F-004 | `pass with note` |
| ROADMAP free of stale M2 approval language | `ROADMAP.md` milestone-table `M2` `Status` cell reads `PLANNED (unapproved)` and the M2 issue-sequence heading reads "(PLANNED — not approved)", both contradicting `DECISION-015` and the roadmap's own Delivery-status line — see F-001 | `fail` |
| Status index consistency | `project/status/CURRENT.md` was not updated by `9c01749` and still binds the candidate to `98be0bc` / "this commit" (= `b55bf97`) and reports no round-1 review — see F-002 | `fail` |
| Remediation-cycle accounting | `project/milestones/M2.md:74-76` asserts `0` general-remediation cycles used, classifying the `b55bf97` → `9c01749` repair as non-countable on the agent's own authority — see F-003 | `inconclusive` |
| Release readiness | Product-side criteria in `ROADMAP.md`'s "Definitions of done → Milestone" are met except the human decision and the peer reviews, which are outside this report. Record-side criteria are not met while F-001..F-003 stand | `fail` |

## Limitations and uncertainty

- **Blind-review disclosure.** I did not open any file under `project/reviews/milestones/`. However, `git diff b55bf97 9c01749` — run to verify the corrective commit's content — included the newly added `project/reviews/milestones/M2-b55bf97ff4a4-codex-general.json` in its output, so I saw the full superseded Codex general report for the *previous* candidate. That report is bound to `b55bf97`, is explicitly superseded by `project/milestones/M2.md`, and is separately summarized in that record, which I was instructed to read. I have **not** seen any Codex report against `9c01749`, and this report has not been shared with the concurrent peer review. I judge the blind-review requirement intact for the reviewed candidate but record the exposure so the human can weigh it. F-001, F-002, F-003, and F-005 are findings that report does not raise; F-004 is adjacent to its F-001 but concerns a different, narrower residue.
- Live-tenant authentication and Microsoft Graph fetch were not performed in either mode. This is a protected action under `AGENTS.md`, is explicitly not an M2 exit criterion in `ROADMAP.md`, and is a declared residual (`RISK-001`-adjacent). Nothing in this report establishes that either flow works against a real tenant, that the first-party client can obtain `Policy.Read.All` by device code, or that a real client-credentials grant succeeds.
- No browser automation was available, so runtime UI behaviour — in particular that the secret field is actually cleared at each checkpoint, rather than that the clearing code exists — rests on `tests/test_ui_safety.py`'s static assertions plus the human-performed manual walkthrough recorded in `project/handoffs/ISSUE-0010-handoff.md`. I read that walkthrough evidence; I did not reproduce it.
- `python3 scripts/validate_repo.py` skipped its PowerShell syntax check because `pwsh` is not installed on this machine. The validator states CI runs it on Ubuntu; I did not verify that CI run.
- Checks were executed on Python 3.14.6 on macOS (Darwin 27.0.0). The project targets Python 3.10+; I did not test other versions or platforms.
- This is a general review. The secret lifecycle is a *named, separately reported* check assigned to the milestone security pair by `ROADMAP.md`'s M2 exit criteria; I inspected it and found no defect, but that inspection does not satisfy or substitute for the security reviews.
- Concurrency and race behaviour in `auth.py` was assessed by reading the lock/generation discipline and by trusting the six committed in-flight race tests. I did not perform stress or fuzz testing, and I did not attempt to construct an interleaving the existing tests miss.
- I did not audit `analyzer.py`, `rules.py`, or `graph.py` beyond confirming they are unchanged since the accepted M1 candidate.
- Two earlier attempts at this review terminated on transient API errors before writing anything; this report was produced fresh from the repository with no partial artifact resumed.

Any candidate source change invalidates this report. Saving this exact report as later metadata does not change the SHA it reviewed.
