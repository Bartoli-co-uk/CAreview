# Human decision: Amend ISSUE-0016 allowed paths to include the strong-tenant fixture

**Decision ID:** `DECISION-039`
**Type:** `issue scope amendment`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Context

`ISSUE-0016`'s original allowed paths were `graph.py`, `rules.py`,
`README.md`, `tests/test_graph.py`, and `tests/test_analyzer.py`, and
acceptance criterion 5 stated no fixture changes were needed. Running the
required test suite against the implemented `terms-of-use-required` rule
showed the same pattern already resolved once for `ISSUE-0015`
(`DECISION-036`): `strong_tenant.json` (the fixture representing a fully
compliant tenant) had no policy requiring Terms of Use, so the new rule
newly failed against it, regressing the pre-existing
`test_strong_tenant_scores_high` and `test_break_glass_evaluable_with_ids`
assertions (score 100 → 96).

## Exact binding

- Artifact/action: amend `project/issues/ISSUE-0016.md`'s allowed paths
- Target: `project/issues/ISSUE-0016.md`'s "Allowed paths" and acceptance
  criterion 5
- Scope: adds exactly one path, `tests/fixtures/strong_tenant.json`, to
  `ISSUE-0016`'s allowed paths, solely to add one additive policy
  (`00000000-0000-0000-0000-000000000009`, "Require Terms of Use for all
  users") requiring Terms of Use with `operator: "AND"` and no
  `builtInControls`, so it cannot satisfy or interfere with any other
  rule's `mfa`/`block` checks, `no-overly-broad-block`, or
  `break-glass-excluded` (which only considers policies with `mfa`/`block`
  in `grantControls`).
- Exclusions: does not approve any other fixture change; does not waive
  acceptance criterion 5's requirement that no other fixture's pass/fail
  state regresses.

## Decision text

> "Yes, approve the fixture path amendment" — human answer approving the
> `tests/fixtures/strong_tenant.json` scope widening, given in response to
> the round-0 implementation's observed test regression, 2026-07-31.

## Evidence shown to the human

- `project/issues/ISSUE-0016.md` — original allowed paths and acceptance
  criterion 5
- `python3 -m unittest discover -s tests` output before the fixture change:
  `test_strong_tenant_scores_high` and `test_break_glass_evaluable_with_ids`
  fail, `AssertionError: 96 != 100`
- `git diff` of the exact fixture addition (one policy, additive only)
- `project/decisions/DECISION-036-issue-0015-fixture-path-amendment.md` —
  the identical precedent for `ISSUE-0015`

## Consequence

- Permitted next action: keep the fixture addition in the candidate,
  restate `ISSUE-0016.md`'s allowed paths to include
  `tests/fixtures/strong_tenant.json`, run required checks (now passing:
  195 tests), commit, and request the fresh Codex issue review.
- Invalidated approvals/reviews: none (no review has run yet for this
  issue).
- Rollback/recovery expectation: N/A — a single additive fixture entry,
  not a destructive change.

## Notes

Same disposition as `DECISION-036`. This does not retroactively bless
open-ended fixture changes for `ISSUE-0017`/`ISSUE-0018`; `ISSUE-0017`
already anticipates its own fixture entry in `ROADMAP.md`'s issue table,
and each issue's own allowed paths and stop conditions govern separately.
