# Human decision: Advance and merge ISSUE-0012 despite an unresolved round-2 residual

**Decision ID:** `DECISION-025`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-28`

## Exact binding

- Artifact/action: merge `ai/react-dashboard-frontend` into `main`
- Artifact version: `ISSUE-0012` round-2 (final attempted) candidate
- Commit/candidate SHA: `195bd8e746884c23b4774162667ee5905f2680e1` (product
  candidate); `5189959392ec2331c799199f5d70457ff361a3ba` (metadata-only
  follow-up recording the round-2 review outcome, not itself re-reviewed)
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: all of `ISSUE-0012` (the React/Vite frontend dashboard) and its
  own review/status/decision records
- Exclusions: does not resolve or waive the round-2 `CHANGES_REQUIRED`
  finding (F-001: the compensating `authLogout()` call added in round 2 is
  unawaited and unconditional/unscoped) — that finding is accepted as a
  tracked, non-blocking residual risk for now, with its proper fix
  authorized as a new, separately-reviewed issue (`ISSUE-0013`, see
  `DECISION-026`), not waived outright. Does not pre-approve any other
  future work; does not open or approve an M3 milestone.

## Decision text

> "first merge to main to save current work, then open a new issue, make
> sure to follow governance set in place to use it."

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0012-4cb61161be32-codex.json` — round 0,
  `BLOCKED` (F-001 client-side device-code polling race; F-002 missing
  check evidence)
- `project/reviews/issues/ISSUE-0012-3748ff133182-codex.json` — round 1,
  `BLOCKED` (F-001 deeper form: orphaned server-side session after a stale
  successful poll)
- `project/reviews/issues/ISSUE-0012-195bd8e74688-codex.json` — round 2
  (final permitted repair round), `CHANGES_REQUIRED` (F-001 narrower form:
  the round-2 fix's compensating logout is unawaited/unscoped)
- `project/handoffs/ISSUE-0012-handoff.md` — real command output for all
  required checks at rounds 1 and 2 (174 Python tests, 88 Vitest tests,
  `py_compile`, `validate_repo.py`, `tsc`/`vite build`, all passing), plus
  a manual browser walkthrough
- `project/issues/ISSUE-0012.md` — full round table, acceptance criteria,
  and the "Human decision required" section presenting three options
- `project/decisions/DECISION-024-react-frontend-build-step.md` — the
  original authorization for this out-of-band frontend work

## Consequence

- Permitted next action: fast-forward merge `ai/react-dashboard-frontend`
  (`5189959392ec2331c799199f5d70457ff361a3ba`) into `main`; mark
  `ISSUE-0012` `COMPLETE (merged, with tracked residual)` in
  `project/issues/ISSUE-0012.md`; update `project/status/CURRENT.md`; open
  `ISSUE-0013` to fix the round-2 residual under its own fresh repair
  budget (`DECISION-026`).
- Invalidated approvals/reviews: none. The round-2 `CHANGES_REQUIRED`
  finding is not overturned or marked resolved by this decision — it is
  explicitly accepted as an open, tracked residual pending `ISSUE-0013`.
- Rollback/recovery expectation: standard `git revert` of the merge (a
  fast-forward, so reverting means resetting `main` back to
  `8648f2ba11907ac32016c724d8ae49a08bdb6b2d`) if a defect surfaces
  post-merge; no destructive history rewrite.

## Notes

Unlike prior issue advance-and-merge decisions in this repository (e.g.
`DECISION-022`), this one explicitly accepts an issue with an unresolved
`CHANGES_REQUIRED` finding rather than a clean or sandbox-limitation-only
outcome. The residual (F-001: an abandoned device-code sign-in can, in a
narrow timing window, leave an orphaned server-side session that a
delayed cleanup call could either fail to clear or, in the opposite
timing, incorrectly clear a newer legitimate session) is judged acceptable
to ship now because: (a) it requires a specific, narrow race — an
abandoned-then-approved device code overlapping a second successful
sign-in within a short window; (b) the existing behavior before this
frontend rebuild had no better protection against this class of issue
either; and (c) `ISSUE-0013` is opened immediately, with its own full
repair budget, to fix it properly (a server-side scoped-abandon mechanism)
rather than leaving it merely noted and forgotten.
