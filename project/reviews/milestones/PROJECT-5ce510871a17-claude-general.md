# Claude general review: project-level final review — CAreview

**Outcome:** `CHANGES_REQUIRED`
**Reviewer role:** `Project general reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-sonnet-5 (Claude Code harness)`
**Fresh session/task ID:** `same top-level session that froze this candidate; conducted as an independent read-only review task per the milestone-general prompt (reused for project scope), with project/reviews/milestones/PROJECT-* deliberately not consulted before writing this report`
**Reviewed artifact:** `project/milestones/PROJECT.md` and the whole repository tree at the frozen candidate
**Reviewed SHA:** `5ce510871a17677fe862e3098972d9a85a6727a9`
**Base SHA:** `N/A — whole-project review, not a delta`
**Created at:** `2026-07-29T20:15:00Z`

## Scope and inputs

- Requirements: `ROADMAP.md`'s "Definitions of done" → "Project" section
  (`M1`/`M2`/`M3` complete; fresh full-project general/security reviews;
  installation/onboarding/rollback/support/security/known-limitations
  accuracy; human final approval).
- Artifacts: `project/milestones/PROJECT.md`, `project/milestones/M1.md`/`M2.md`/`M3.md`,
  `README.md`, `frontend/README.md`, `CONTRIBUTING.md`,
  `docs/security-boundaries.md`, `AGENTS.md`, `docs/workflow.md`,
  `LICENSE`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md`.
- Verification evidence, independently executed at the reviewed SHA
  `5ce510871a17677fe862e3098972d9a85a6727a9`: `python3 -m unittest
  discover -s tests` (188 passed, exit 0); `python3 -m py_compile
  $(git ls-files '*.py')` (exit 0); `python3 scripts/validate_repo.py`
  (passed, 67 required files); `cd frontend && npm run build` (produced
  all three output files) and `npm test` (91 passed, exit 0).
- **Onboarding independently reproduced from a genuinely fresh clone**
  (`git clone /Users/jaybartoli/CAreview /tmp/careview-fresh-check`, no
  local cache reuse beyond git's own object sharing): `cd frontend && npm
  install && npm run build` exit 0, `python3 server.py` started, `GET
  /api/health` → 200, `GET /` → 200 with `Content-Security-Policy`
  present. No `requirements.txt`/`Pipfile`/`pyproject.toml` exists,
  confirming the backend's "no installs" claim independently. Fresh
  checkout deleted after verification.
- Repository/branch hygiene, independently checked: `git ls-remote
  --heads origin` and `gh api repos/Bartoli-co-uk/CAreview/branches` both
  show exactly one branch, `main`; local `main` identical to
  `origin/main`; `gh pr list --state all` shows all four historical PRs
  already merged or closed.
- Excluded or unavailable evidence: live-tenant sign-in/fetch, either
  mode (protected action); real-browser automated testing beyond the
  committed jsdom-based suites; `project/reviews/milestones/PROJECT-*`
  (blind-review instruction — not read before writing this report).
- Peer report withheld for blind review: `yes`.

## Summary

`M1`, `M2`, and `M3` are each independently accepted (`DECISION-012`,
`DECISION-023`, `DECISION-032`) with no outstanding product defect at any
of those gates — the project's history across all three milestones and
fourteen issues shows a consistent pattern: real reviewer findings when
they occur are almost always governance-record staleness, not code
defects, and every actual security-relevant property (auth scoping, CSP,
rendering safety, secret handling, CI least-privilege) has held up under
repeated independent re-verification, including my own in this review.
Onboarding works exactly as documented, verified from a truly fresh
clone rather than trusting the record's own claim.

The outcome is nevertheless `CHANGES_REQUIRED`, for two real, if
different-in-kind, defects.

## Findings

### F-001: `PROJECT.md`'s frozen-candidate binding does not match the launcher-reviewed SHA

- Classification: `REQUIRED`
- Severity: `high`
- Confidence: `high`
- Blocking: `yes`
- Location: `project/milestones/PROJECT.md` lines 4–5 (header), line ~53
  (verification-evidence table).
- Expected: the record's "Frozen candidate SHA" and its verification
  table should identify the exact commit the Codex launcher is bound to
  review — the same discipline `M3`'s round-1 repair established for
  exactly this class of defect two review cycles ago in this same
  session.
- Observed: `PROJECT.md` names `802ea4d` (the `M3`-acceptance commit,
  product-identical parent) as the frozen candidate and binds its
  verification table to that SHA, while the actual candidate this
  session's freeze commit produced — and which the launcher was invoked
  against — is `5ce5108` (the freeze commit itself, which added
  `PROJECT.md` and updated `CURRENT.md`). Both Codex general and Codex
  security independently caught this and blocked on it (`F-001`/`SEC-001`
  in their reports respectively) — a direct repeat of `M3`'s own round-1
  Codex general finding, which I should have applied here from the start
  rather than re-learning.
- Evidence: `git rev-parse HEAD` at review time is `5ce5108…`;
  `PROJECT.md:5` reads "Frozen candidate SHA: `802ea4d…`".
- Impact: a reviewer (or a human reading the record) could not establish
  which commit's evidence the four reviews actually cover. No product
  code defect — this is entirely a record-binding issue, the same class
  every milestone gate in this project has hit at least once.
- Remediation: rebind `PROJECT.md`'s header and verification table to
  the actual reviewed SHA, following the exact pattern `M3.md` round 1
  used to fix its own instance of this defect.
- Verification: confirm `git rev-parse HEAD` at the new candidate matches
  `PROJECT.md`'s "Frozen candidate SHA" field exactly.
- Disposition: `open`

### F-002: `README.md`'s "Known limitations" table has one stale row and is missing three accepted risks

- Classification: `REQUIRED`
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes`
- Location: `README.md`, "Known limitations" table (~line 512–517).
- Expected: the table's own preamble says "these are the recorded,
  accepted residual risks (tracked in `ROADMAP.md`)" — it should
  therefore list every accepted risk with accurate status.
- Observed: (a) the "Device-code abandon delivery (`ISSUE-0013`)" row
  says "Blocked pending a human decision — see `project/issues/
  ISSUE-0013.md`," but that residual (`RISK-011`) was accepted by the
  human at `DECISION-027`, not left blocked — stale since that decision.
  (b) `RISK-009` (npm build-time supply chain, accepted `DECISION-028`)
  and `RISK-010` (onboarding regression, accepted `DECISION-029`) are
  both absent from the table entirely, despite being exactly the class
  of "recorded, accepted residual risk" the table's own preamble
  describes, and despite `RISK-010` being independently demonstrable (I
  reproduced it myself in this review's fresh-clone check: `web/` serves
  nothing until the frontend build runs).
- Evidence: `README.md`'s table content vs. `ROADMAP.md`'s risk register
  (`RISK-009`/`-010`/`-011` all present there with accepted status) and
  `docs/security-boundaries.md`'s equivalent, accurate treatment of all
  three.
- Impact: a reader relying on `README.md` alone (a reasonable thing to
  do — it's the first file most readers open) would get a stale and
  incomplete picture of the project's own accepted risk posture. This is
  exactly the "known limitations accurate" property `ROADMAP.md`'s
  project-level definition of done names explicitly.
- Remediation: update the `ISSUE-0013` row to reflect `DECISION-027`'s
  acceptance; add rows for `RISK-009` and `RISK-010` matching
  `ROADMAP.md`'s language.
- Verification: compare `README.md`'s table against `ROADMAP.md`'s risk
  register and confirm every accepted M1/M2/M3 risk appears with current
  status.
- Disposition: `open`

## Non-blocking observations

- `frontend/README.md`, `CONTRIBUTING.md`, and `docs/security-boundaries.md`
  are all accurate as of this candidate — independently re-checked, no
  further staleness found beyond what was already fixed in this session's
  `ISSUE-0014` follow-up commits.
- `LICENSE`, `SECURITY.md`, `SUPPORT.md`, `CODE_OF_CONDUCT.md` all exist
  and contain no stale claims about project state.
- Repository/branch hygiene is clean: one branch on GitHub, local and
  remote identical, no stray open PRs.

## Disposition

Two `REQUIRED` findings: one is the same class of record-binding defect
this project has now hit at every single review gate (M1 sandbox
residuals, M2/M3 CURRENT.md staleness, and now this project-level
review's own candidate binding) — never a product defect. The other is a
genuine, previously-unflagged documentation-accuracy gap in `README.md`'s
risk disclosure. Neither is a product-code correctness or security
defect.
