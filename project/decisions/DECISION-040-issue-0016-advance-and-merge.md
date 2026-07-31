# Human decision: Advance and merge ISSUE-0016 (terms-of-use-required analyzer rule)

**Decision ID:** `DECISION-040`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0016-terms-of-use-rule` into `main`
- Artifact version: `ISSUE-0016` round-2 (final) candidate
- Commit/candidate SHA: `5a63f84c7a58611b1e7185f202cf131d7def2de3` (product/
  documentation candidate reviewed by Codex); `e5567fe` (metadata-only
  follow-up recording the round-2 outcome, not itself re-reviewed)
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0016` only — `graph.py`, `rules.py`, `README.md`,
  `tests/test_graph.py`, `tests/test_analyzer.py`,
  `tests/fixtures/strong_tenant.json` (per the `DECISION-039` scope
  amendment), and its own handoff/review/status/decision records
- Exclusions: no other pending change; does not start `ISSUE-0017`/
  `ISSUE-0018`; does not open `M4`'s milestone gate; does not accept any
  risk beyond the sandbox execution-evidence residual described below

## Decision text

> "Accept residual, merge to main" (selected from the options presented
> after the round-2 fresh Codex review)

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0016-bfa12f76053b-codex.json` — round 0,
  `BLOCKED` (F-001 sandbox-only; F-002 low/advisory, stale README count,
  fixed in round 1)
- `project/reviews/issues/ISSUE-0016-3b2020bc30d0-codex.json` — round 1,
  `BLOCKED` (F-001 sandbox-only; F-002 medium/REQUIRED, stale governance
  records, fixed in round 2)
- `project/reviews/issues/ISSUE-0016-5a63f84c7a58-codex.json` — round 2
  (final), `BLOCKED` with **zero content findings**; sole blocker is the
  review sandbox's own execution-evidence limitations (denied
  `__pycache__` write, denied loopback socket binding, no writable temp
  directory)
- `project/issues/ISSUE-0016.md` — full round table, real local check
  results at every round (195 tests passed, `py_compile` clean,
  `validate_repo.py` clean)
- `project/decisions/DECISION-038-issue-0016-start-authorization.md` — the
  durable record of authorization to start this issue
- `project/decisions/DECISION-039-issue-0016-fixture-path-amendment.md` —
  the durable record approving the one in-scope fixture change
- Precedent: `DECISION-037` (`ISSUE-0015`) and `DECISION-031`
  (`ISSUE-0014`) — the same sandbox-only-blocker pattern, each previously
  accepted the same way

## Consequence

- Permitted next action: merge `ai/ISSUE-0016-terms-of-use-rule`
  (`5a63f84`..`e5567fe`) into `main`; mark `ISSUE-0016` `COMPLETE` in
  `project/issues/ISSUE-0016.md` and `ROADMAP.md`'s `M4` issue table;
  update `project/status/CURRENT.md`; push the resulting `main` to GitHub.
  `M4`'s next issue (`ISSUE-0017`) remains unauthorized to start without
  its own separate human start decision.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit
  if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Both permitted issue repair rounds were used — round 1 for a documentation
staleness finding, round 2 for a governance-record staleness finding
uncovered in round 1's own review. The round-2 candidate is clean of every
actionable finding; the residual `BLOCKED` outcome comes entirely from the
review sandbox's inability to write bytecode, bind a loopback socket, or
provide a writable temp directory in this environment — a structural
limitation already accepted repeatedly for other issues in this project
(`ISSUE-0014`, `ISSUE-0015`), not a product or documentation defect. The
rule's own deliberate scope limit — Terms of Use identifiers are not
resolved to agreement names/content — was already recorded as an
out-of-scope item in `ISSUE-0016.md` and is not a new residual introduced
by this decision.
