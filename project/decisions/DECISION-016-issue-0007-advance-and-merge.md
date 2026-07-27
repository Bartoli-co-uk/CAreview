# Human decision: Advance and merge ISSUE-0007 (trim delegated SCOPES)

**Decision ID:** `DECISION-016`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-27`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0007-trim-scopes` into `main`
- Artifact version: `ISSUE-0007` round-2 candidate
- Commit/candidate SHA: `b314d82087f36b5fadae3119410e838ec2255997`
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0007` only — the delegated-scope trim to `Policy.Read.All`, its
  tests, its documentation corrections, and its own review/status records
- Exclusions: no other pending change; does not pre-approve `ISSUE-0008` or
  any later M2 issue

## Decision text

> "Approve merging ISSUE-0007 and start ISSUE-0008."

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0007-54e207a04b1c-codex.json` — round 0, `BLOCKED` (1 finding, fixed in repair round 1)
- `project/reviews/issues/ISSUE-0007-79f28638411d-codex.json` — round 1, `BLOCKED` (2 findings, fixed in repair round 2)
- `project/reviews/issues/ISSUE-0007-b314d82087f3-codex.json` — round 2 (final permitted round), `BLOCKED` with **zero findings**; sole blocker is the accepted sandbox execution-evidence residual (`DECISION-015`)
- `project/handoffs/ISSUE-0007-handoff.md` — real local check results at the round-2 candidate: 85 tests OK, `py_compile` clean, `validate_repo.py` clean
- `project/issues/ISSUE-0007.md` — full round table and acceptance-criteria mapping
- Precedent: `DECISION-010`, which accepted the identical sandbox-only-blocker pattern for `ISSUE-0006`

## Consequence

- Permitted next action: merge `ai/ISSUE-0007-trim-scopes` (`b314d82087f36b5fadae3119410e838ec2255997`) into `main`; mark `ISSUE-0007` `COMPLETE` in `ROADMAP.md`'s M2 table and `project/issues/ISSUE-0007.md`; update `project/status/CURRENT.md`; push the resulting `main` (and the merged branch) to GitHub; then start `ISSUE-0008` in a new top-level Claude author task per `AGENTS.md`.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Both permitted issue repair rounds were used (round 1 and round 2). The
round-2 candidate is clean of every actionable finding; the residual
`BLOCKED` outcome comes entirely from the review sandbox's known inability
to bind loopback sockets, write `__pycache__`, or create a writable temp
directory for `validate_repo.py` — a structural limitation accepted in
`DECISION-015`, not a product defect, and consistent with every M1 issue
review to date.
