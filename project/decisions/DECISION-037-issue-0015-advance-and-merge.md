# Human decision: Advance and merge ISSUE-0015 (location-restriction-present analyzer rule)

**Decision ID:** `DECISION-037`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0015-location-restriction-rule` into `main`
- Artifact version: `ISSUE-0015` round-1 (final) candidate
- Commit/candidate SHA: `31c94a824cc7ae85e0baadc926f9cd94faaab8fc` (product/
  documentation candidate reviewed by Codex); `b197966` (metadata-only
  follow-up recording the round-1 outcome, not itself re-reviewed)
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0015` only — `rules.py`, `README.md`,
  `tests/test_analyzer.py`, `tests/fixtures/strong_tenant.json` (per the
  `DECISION-036` scope amendment), and its own handoff/review/status/
  decision records
- Exclusions: no other pending change; does not start `ISSUE-0016`–
  `ISSUE-0018`; does not open `M4`'s milestone gate; does not accept any
  risk beyond the sandbox execution-evidence residual described below

## Decision text

> "Accept residual, merge to main" (selected from the options presented
> after the round-1 fresh Codex review)

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0015-1ff0b987d2f7-codex.json` — round 0,
  `BLOCKED` (F-001: candidate-identity mismatch; F-002: fixture change
  outside allowed paths; F-003: missing start-authorization record — all
  three repaired in round 1)
- `project/reviews/issues/ISSUE-0015-31c94a824cc7-codex.json` — round 1
  (final), `BLOCKED` with **zero content findings**; sole blocker is the
  review sandbox's own execution-evidence limitations (denied
  `__pycache__` write, denied loopback socket binding, no writable temp
  directory)
- `project/issues/ISSUE-0015.md` — full round table, real local check
  results at the round-1 candidate (190 tests passed, `py_compile` clean,
  `validate_repo.py` clean)
- `project/decisions/DECISION-035-issue-0015-start-authorization.md` — the
  durable record of authorization to start this issue
- `project/decisions/DECISION-036-issue-0015-fixture-path-amendment.md` —
  the durable record approving the one in-scope fixture change
- Precedent: `DECISION-031` (`ISSUE-0014`) and the chain it cites
  (`DECISION-010`, `-016`, `-017`, `-019`, `-020`, `-022`) — the same
  sandbox-only-blocker pattern, each previously accepted the same way

## Consequence

- Permitted next action: merge `ai/ISSUE-0015-location-restriction-rule`
  (`31c94a8`..`b197966`) into `main`; mark `ISSUE-0015` `COMPLETE` in
  `project/issues/ISSUE-0015.md` and `ROADMAP.md`'s `M4` issue table;
  update `project/status/CURRENT.md`; push the resulting `main` to GitHub.
  `M4`'s next issue (`ISSUE-0016`) remains unauthorized to start without
  its own separate human start decision.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit
  if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Round 1 (the first of at most two permitted issue repair rounds) resolved
all three round-0 findings and left the candidate clean of every
actionable finding. The residual `BLOCKED` outcome comes entirely from the
review sandbox's inability to write bytecode, bind a loopback socket, or
provide a writable temp directory in this environment — a structural
limitation already accepted repeatedly for other issues in this project
(most recently `ISSUE-0014`, `DECISION-031`), not a product or
documentation defect. The rule's own deliberate scope limit — it is
presence-only and does not assess whether the named location or the
policy's grant/session behavior provides an effective restriction — was
already recorded as a stop condition in `ISSUE-0015.md` and is not a new
residual introduced by this decision.
