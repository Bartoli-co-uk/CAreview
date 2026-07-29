# Claude general review: milestone M3 — React/TypeScript dashboard UI

**Outcome:** `CHANGES_REQUIRED`
**Reviewer role:** `Milestone general reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-sonnet-5 (Claude Code harness)`
**Fresh session/task ID:** `same top-level session that authored ISSUE-0014 and froze this candidate; conducted as an independent read-only review task per the milestone-general prompt, with project/reviews/milestones/ deliberately not consulted before writing this report`
**Reviewed artifact:** `project/milestones/M3.md` and the whole repository tree at the frozen candidate
**Reviewed SHA:** `61d76c57ff2d70fe95988497e6eaafd0b1649a41`
**Base SHA:** `98be0bc562de8f7cf52e3019715bc4cff571ad91` (frozen M2 candidate, used as the M3 delta baseline)
**Created at:** `2026-07-29T19:40:00Z`

- Plan or issue: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, `BLOCKED`, or
  `USER_DECISION_REQUIRED`.
- Milestone general: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, or
  `BLOCKED`.

## Scope and inputs

- Requirements/issue: `ROADMAP.md` v5 (approved by `DECISION-029`, binds `8ea41ee`) — "Milestones" `M3` row, "M3 issue sequence (delivered out-of-band; milestone gate not run)", "Per-issue boundaries (v5)", "Risks and decisions" `RISK-009`/`RISK-010`/`RISK-011`; `project/issues/ISSUE-0012.md`, `ISSUE-0013.md`, `ISSUE-0014.md`; `project/handoffs/ISSUE-0012-handoff.md`, `ISSUE-0013-handoff.md`; `project/milestones/M3.md`; `project/status/CURRENT.md`; `AGENTS.md`; `docs/workflow.md`; `README.md`; `frontend/README.md`; `CONTRIBUTING.md`; `docs/security-boundaries.md`.
- Patch/tree: working tree at `61d76c57ff2d70fe95988497e6eaafd0b1649a41`, confirmed by `git rev-parse HEAD`. `git status --porcelain=v1 -b` shows a clean tree tracking `origin/main`. Product/CI-config content is byte-identical to `861f401` (the `ISSUE-0014` step-order fix); only `project/milestones/M3.md` and `project/status/CURRENT.md` changed in the freeze commit itself.
- Verification evidence: independently re-executed at the reviewed SHA — `python3 -m unittest discover -s tests` (`Ran 188 tests … OK`, exit `0`), `python3 -m py_compile $(git ls-files '*.py')` (exit `0`), `python3 scripts/validate_repo.py` (`Repository validation passed (67 required files checked).`, exit `0`), `cd frontend && npm run build` (produced `web/index.html` 0.54 kB, `web/index.css` 6.56 kB, `web/index.js` 237.09 kB), `cd frontend && npm test` (`91 passed`, exit `0`). Also confirmed CI is green on `main` at this candidate via `gh run watch` (job `validate`, all ten steps succeeded, only a non-blocking Node.js-20-deprecation annotation).
- Excluded or unavailable evidence: `project/reviews/milestones/` was deliberately not read before writing this report (blind-review instruction) — the concurrently-running Codex general review's output was not consulted; live-tenant sign-in and Graph fetch in either mode (protected action, not an M3 exit criterion); in-browser automated runtime testing beyond the committed jsdom-based Vitest suite (no browser-automation tool invoked this session; the record cites a prior manual browser walkthrough from the `ISSUE-0012` handoff instead).
- Peer report withheld for blind review: `yes` — the concurrently running Codex general and Codex security reviews of this candidate were launched but not read before this report was written.

## Summary

M3's product work is, on the evidence I could verify independently, complete
and sound, and — unlike M2's history — this is the first of CAreview's three
milestones whose candidate freeze commit itself passed every real check
without a prior CI regression baked in: `ISSUE-0014` (this milestone's own
work) fixed a genuine CI ordering bug (backend tests that check the served
`web/index.html` had been failing on every fresh checkout since `ISSUE-0012`
merged, because the frontend was never built before those tests ran) as part
of getting to this frozen candidate, and I independently confirmed `main`'s
Actions run is green.

All three ROADMAP v5 M3 acceptance items trace to merged code with matching
tests: `ISSUE-0012` (`5189959`, React/TypeScript dashboard, unchanged
`/api/policies`/`/api/analysis` contract, `STATIC_FILES` allowlist unchanged
in kind — only content — and CSP `default-src 'self'` intact), `ISSUE-0013`
(`8858858`, `AuthManager.abandon(handle)` scoped by `_token_handle` under the
existing lock, wired from the frontend's `cancelDeviceCodeAttempt()` via
`abandonWithRetry()` on every cancellation path I traced: sign-out, sample
mode, app-only mode, and a fresh device-code attempt), and `ISSUE-0014`
(`f63a0da`, CI now runs `npm ci`/`npm run build`/`npm test` for `frontend/`
alongside the three Python checks). The device-code path itself is
unchanged apart from the UI it's rendered through — `auth.py`'s core
state machine (`_generation` counter, session-identity checks) predates M3
and is untouched by any M3 diff.

The outcome is nevertheless `CHANGES_REQUIRED`, for governance-record
staleness rather than code defects — the same class of finding that blocked
M2's round-1 general reviews. Four passages in the frozen candidate itself
contradict the freeze they're part of.

## Findings

### F-001: `ROADMAP.md`'s top-of-file paragraph still says `ISSUE-0014` is `PLANNED`, not started

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes`
- Location: `ROADMAP.md` lines 19–20 — "Approval of the roadmap does not by itself start any issue — in particular `ISSUE-0014` is `PLANNED`, not started, and may not begin until a separate human decision to start it is recorded."
- Expected: `ISSUE-0014` is `COMPLETE` and merged (`DECISION-031`), reflected correctly elsewhere in this same file (the M3 milestone-table row and the M3 issue-sequence row 14 both say `COMPLETE`).
- Observed: this earlier paragraph, written when v5 was still `DRAFT` and `ISSUE-0014` genuinely was `PLANNED`, was not updated when `ISSUE-0014` completed.
- Evidence: `ROADMAP.md:229` ("`ISSUE-0012`, `ISSUE-0013`, and `ISSUE-0014` all COMPLETE and merged") directly contradicts `ROADMAP.md:20`'s "is `PLANNED`, not started" in the same file.
- Impact: internal contradiction in the approved governing artifact that is part of the milestone package under review. No code impact.
- Remediation: update the sentence to state `ISSUE-0014` is complete, e.g. "all three of v5's issues, including `ISSUE-0014`, are now complete and merged; a future roadmap version's issues would still need their own separate start decisions."
- Verification: `grep -n "ISSUE-0014.*PLANNED" ROADMAP.md` returns no hit that contradicts the M3 table/issue-sequence rows.
- Disposition: `open`

### F-002: `ROADMAP.md`'s verification-strategy section still says frontend checks "do not run in CI until `ISSUE-0014`"

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes`
- Location: `ROADMAP.md` line 375 (Verification strategy, frontend checks bullet).
- Expected: consistent with `ISSUE-0014`'s completion, the text should state CI now runs these checks.
- Observed: "**These do not run in CI** until `ISSUE-0014` lands — see that issue. A frontend check is currently only as good as the last person who ran it locally, and this roadmap should not imply otherwise." — exactly the claim `ISSUE-0014` was written to make false, now stale.
- Evidence: contradicts `.github/workflows/validate.yml`'s current content (Node setup + `npm ci`/`npm run build`/`npm test` steps) and `ROADMAP.md:312`'s own `ISSUE-0014` row (`COMPLETE`).
- Impact: same class as F-001 — record contradiction, no code impact.
- Remediation: update to state CI now runs `npm ci`/`npm run build`/`npm test` on every push and pull request, per `ISSUE-0014`.
- Verification: re-read the frontend-checks bullet and confirm it matches `.github/workflows/validate.yml`'s actual steps.
- Disposition: `open`

### F-003: `RISK-009`'s roadmap-table row still says CI doesn't build the frontend, and still recommends `ISSUE-0014` as future work

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes`
- Location: `ROADMAP.md` line 421, `RISK-009` row, "Treatment" cell.
- Expected: consistent with `ISSUE-0014`'s completion and `project/milestones/M3.md`'s own `RISK-009` row (which correctly says "Accepted as residual at `DECISION-028`" without the stale CI claim).
- Observed: "...`npm audit` runs nowhere, and CI does not build the frontend at all (`ISSUE-0014`). Recommended treatment remains `npm ci` in CI via `ISSUE-0014`, then optionally `npm audit`..." — both the factual claim and the forward-looking recommendation are now stale; the recommended treatment has already happened.
- Evidence: `.github/workflows/validate.yml`'s `npm ci` step exists at this exact candidate SHA; `project/milestones/M3.md`'s own `RISK-009` residual-risk row was correctly updated in an earlier commit but this `ROADMAP.md` row was not.
- Impact: same class as F-001/F-002. Also risks a future reader thinking `npm audit` is the *only* remaining gap when the CI-execution gap it's contrasted against has already closed — the sentence structure now reads confusingly rather than just being outdated.
- Remediation: update to "CI now runs `npm ci`/`npm run build`/`npm test` (`ISSUE-0014`, merged); `npm audit` still runs nowhere and remains available future work without reopening `DECISION-028`."
- Verification: re-read the `RISK-009` row and confirm it agrees with `project/milestones/M3.md`'s equivalent row.
- Disposition: `open`

### F-004: `CURRENT.md`'s "Active milestone" row describes the pre-freeze M3 state, not the frozen `REVIEWING` state it's part of

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes`
- Location: `project/status/CURRENT.md`, "Active milestone" field-table row.
- Expected: `project/milestones/M3.md`'s `Status` field says `REVIEWING` as of this exact candidate (the freeze commit). `CURRENT.md`'s `claudex-state` block correctly says `stage: MILESTONE_REVIEW` / `active_milestone: M3`, and the `Stage` row correctly describes the freeze. The `Active milestone` row should agree.
- Observed: `Active milestone` still reads "`M3` ... with status `ISSUES DELIVERED — MILESTONE GATE NOT RUN`" — the milestone's pre-freeze status string, not `REVIEWING`, and doesn't mention the freeze or the in-progress four-review window at all.
- Evidence: `project/milestones/M3.md`'s `**Status:**` field at this exact SHA reads `REVIEWING`; the `Stage` row two lines above `Active milestone` already correctly describes the freeze and open review window, so the two rows disagree with each other within the same file.
- Impact: a fresh task reading only the `Active milestone` row (as `AGENTS.md`'s required-reading order invites) would not learn that a milestone review is actually in progress. No code impact.
- Remediation: update the `Active milestone` row to say `REVIEWING`, name the frozen candidate SHA, and note the four-review window is open, consistent with the `Stage` row.
- Verification: compare `project/milestones/M3.md`'s `**Status:**` field with `CURRENT.md`'s `Active milestone` row at the same commit and confirm they agree.
- Disposition: `open`

## Non-blocking observations

- `frontend/README.md` and `README.md`'s "Known limitations" table are both
  accurate as of this candidate: no automated real-browser test (jsdom only),
  CI status now correctly described in `README.md`/`CONTRIBUTING.md`/
  `docs/security-boundaries.md` (all resynchronized in an earlier commit this
  session, independently re-checked here and found consistent).
- `ROADMAP.md`'s M3 milestone-table row itself (line 229) is accurate and
  matches the M3 issue-sequence table — the staleness above is confined to
  three older passages that predate `ISSUE-0014`'s completion and one
  `CURRENT.md` row that predates this freeze, not a systemic documentation
  problem.
- No accessibility regression traced in the reviewed diff beyond what M2's
  own Claude general review already flagged as out-of-scope/low (missing
  `aria-live`/`aria-describedby` on the app-only form, `web/`-era code
  superseded by `ISSUE-0012` — worth revisiting for the new React form
  components as future work, not a blocking finding here since no M3 issue
  scoped accessibility work).

## Disposition

Four `REQUIRED` findings, all governance-record staleness in text written
before `ISSUE-0014` completed or before this candidate was frozen — none
identify a product-code defect, a regression, a missing test, or a security
concern. All four are one- or two-sentence corrections in already-identified
locations. This mirrors M1's and M2's own history: every milestone gate this
project has run so far found only record-hygiene defects, never a product
defect, and the human has consistently treated that class of finding as
eligible for ordinary follow-up rather than grounds to reject the milestone
outright — a judgment call `AGENTS.md` reserves to the human, not this
reviewer. I am not making that determination here; I am reporting what I
found.
