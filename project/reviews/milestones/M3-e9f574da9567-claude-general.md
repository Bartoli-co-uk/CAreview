# Claude general review: milestone M3 — React/TypeScript dashboard UI (round 2)

**Outcome:** `CHANGES_REQUIRED`
**Reviewer role:** `Milestone general reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-sonnet-5 (Claude Code harness)`
**Fresh session/task ID:** `same top-level session that authored the round-1 repair; conducted as an independent read-only review task per the milestone-general prompt, with the round-2 Codex reports (launched moments earlier) deliberately not consulted before writing this report`
**Reviewed artifact:** `project/milestones/M3.md` and the whole repository tree at the round-2 candidate
**Reviewed SHA:** `e9f574da95679b7701db52042d91429068d54206`
**Base SHA:** `61d76c57ff2d70fe95988497e6eaafd0b1649a41` (round-1 candidate, used as the round-2 delta baseline)
**Created at:** `2026-07-29T19:50:00Z`

## Scope and inputs

- Round-1 reports: `project/reviews/milestones/M3-61d76c57ff2d-claude-general.md`,
  `-codex-general.json`, `-claude-security.md`, `-codex-security.json` — read,
  since this is a remediation-round review of a repair that responds to them
  (unlike round 1's blind initial review, round 2 is explicitly checking
  whether the repair addressed round 1's findings, which requires reading
  them).
- Same requirements/issue set as round 1: `ROADMAP.md` v5 (`DECISION-029`),
  `project/issues/ISSUE-0012.md`/`ISSUE-0013.md`/`ISSUE-0014.md`,
  `project/milestones/M3.md`, `project/status/CURRENT.md`, `AGENTS.md`.
- Patch/tree: `git diff --name-only 61d76c57 e9f574d` — three files changed:
  `ROADMAP.md`, `project/milestones/M3.md`, `project/status/CURRENT.md`. No
  product or CI-config file. Working tree clean at `e9f574da95679b7701db52042d91429068d54206`.
- Verification evidence: independently re-executed at the reviewed SHA —
  `python3 -m unittest discover -s tests` (188 passed, exit 0),
  `python3 -m py_compile $(git ls-files '*.py')` (exit 0),
  `python3 scripts/validate_repo.py` (passed, 67 required files),
  `cd frontend && npm run build` (produced all three output files),
  `cd frontend && npm test` (91 passed, exit 0). Identical results to round
  1, as expected since no product/CI file changed.
- Peer report withheld for blind review: `yes` for round 2's own conclusion
  — the concurrently running round-2 Codex general/security reviews were
  launched before this report was written and not read before writing it.

## Summary

This repair addresses every one of round 1's four findings:

- **F-001** (`ROADMAP.md:20`, "`ISSUE-0014` is `PLANNED`, not started") —
  fixed. The line now correctly states all three v5 issues are complete.
- **F-002** (`ROADMAP.md:375`+, frontend checks "do not run in CI until
  `ISSUE-0014`") — fixed. Now states CI runs both `npm test` and `npm run
  build` on every push/PR.
- **F-003** (`ROADMAP.md`'s `RISK-009` row, "CI does not build the frontend
  at all") — fixed. Now states CI runs the build/tests, with `npm audit`
  named as the specific remaining gap rather than a vague "recommended
  treatment remains `ISSUE-0014`".
- **F-004** (`CURRENT.md`'s "Active milestone" row describing the
  pre-freeze state) — fixed. Now correctly describes `REVIEWING`, cites
  round 1's four outcomes, and points to this round-2 candidate as the
  next required action.

Codex general's round-1 F-001 (the verification-evidence table bound to a
stale per-issue SHA) is also fixed: the table is now explicitly bound to
`61d76c57ff2d…` (round 1's candidate) with real command output I could
independently reproduce at this round-2 candidate (unchanged, since no
product file moved), plus a new CI-green confirmation row.

## Findings

### F-001: `ROADMAP.md`'s top-of-file Delivery-status line still says no milestone review has run

- Classification: `REQUIRED`
- Severity: `low`
- Confidence: `high`
- Blocking: `yes` (per `AGENTS.md`'s treatment of stale/contradictory
  governance-record evidence as blocking, independent of severity)
- Location: `ROADMAP.md` line 13, "Delivery status" — "...but the milestone
  itself is **not** complete: **none of the four blind milestone reviews
  has been run**. Current state: `project/status/CURRENT.md`."
- Expected: consistent with `project/milestones/M3.md`'s own "Four
  mandatory reviews" section, which now records round 1's four outcomes
  (`CHANGES_REQUIRED`/`BLOCKED`/`PASS_WITH_NOTES`/`INCONCLUSIVE`) and
  states round 2 is in progress.
- Observed: this line was not touched by the round-2 repair (the repair's
  own commit message scopes it to `ROADMAP.md`'s three `ISSUE-0014`
  passages, `CURRENT.md`'s milestone row, and `M3.md`'s verification
  table — this Delivery-status line is a fourth, distinct passage that
  predates even round 1 and was not in that repair's scope).
- Evidence: `project/milestones/M3.md`'s "Four mandatory reviews" section,
  same commit, directly contradicts this line.
- Impact: same governance-record-staleness class as every round-1 finding.
  No code impact, no security impact.
- Remediation: update the sentence to reflect that round 1 has run (found
  only record-binding defects, now repaired) and round 2 is the fresh
  review this candidate is undergoing.
- Verification: re-read the Delivery-status line and `M3.md`'s reviews
  section together and confirm they agree.
- Disposition: `open`

## Non-blocking note on process

**This finding was not caught before round-2 review launched.** I
(the same task that performed the round-1 repair) reviewed the repair's
own diff for the four findings it targeted but did not re-scan the entire
file for every possible stale `ISSUE-0014`/milestone-review reference
before committing and launching round 2. That is a process gap worth
naming plainly, not smoothing over: `AGENTS.md`'s one-permitted-
general-remediation-cycle rule means this finding, however minor, cannot
be fixed by a further automated repair round without exceeding that
budget. It is presented here for the human's disposition, the same way
`ISSUE-0012`/`ISSUE-0013`'s round-2 residuals and `M2`'s own round-1
staleness findings were.

## Disposition

One `REQUIRED` finding, low severity, same governance-record-staleness
class as every finding round 1 produced — not a product defect, not a
security concern, and not a repeat of any of round 1's four specific
findings (all of which are genuinely fixed). Per `AGENTS.md`, the human
must now choose how to proceed: `M3`'s general-remediation budget (one
cycle) is exhausted, so this is not eligible for a further automated
repair round.
