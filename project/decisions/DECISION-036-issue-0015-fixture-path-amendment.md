# Human decision: Amend ISSUE-0015 allowed paths to include the strong-tenant fixture

**Decision ID:** `DECISION-036`
**Type:** `issue scope amendment`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Context

`ISSUE-0015`'s original allowed paths were `rules.py`, `README.md`, and
`tests/test_analyzer.py`, and acceptance criterion 4 stated no fixture
changes were needed. The round-0 fresh Codex issue review
(`project/reviews/issues/ISSUE-0015-1ff0b987d2f7-codex.json`, `BLOCKED`)
found (F-002) that the candidate added a new policy to
`tests/fixtures/strong_tenant.json` outside that allowed-paths list.

Investigation confirms the change was necessary, not incidental: the new
`location-restriction-present` rule fails any enabled policy that leaves
`includeLocations`/`excludeLocations` at the default `All`/`AllTrusted`, and
`strong_tenant.json` (the fixture representing a fully compliant tenant)
had no policy that restricted by named location. Without the added policy,
the pre-existing `test_strong_tenant_scores_high` assertion (`score == 100`,
`findings == []`) would regress — the new rule would newly fire against the
"strong" fixture. `ISSUE-0015`'s own stop conditions anticipated exactly
this case and required stopping to re-scope rather than silently making the
change, which is what this decision now does after the fact.

## Exact binding

- Artifact/action: amend `project/issues/ISSUE-0015.md`'s allowed paths
- Artifact version: `ISSUE-0015.md` as committed at
  `bcfeacdb0e264db42badf4a6a945acb94f3fc3ff` / `1ff0b987d2f75377589e6c4875724b94aef81591`
- Commit/candidate SHA: `1ff0b987d2f75377589e6c4875724b94aef81591` (repair
  round 1 will restate the amended allowed paths and produce a new candidate
  SHA)
- Target: `project/issues/ISSUE-0015.md`'s "Allowed paths" and "Out of
  scope"/acceptance-criterion-4 sections
- Scope: adds exactly one path, `tests/fixtures/strong_tenant.json`, to
  `ISSUE-0015`'s allowed paths, solely to add the one new policy already
  present in the candidate diff (`ee29aa9..1ff0b98`, lines adding policy
  `00000000-0000-0000-0000-000000000008`, "Restrict finance app access by
  location") so that `test_strong_tenant_scores_high` continues to pass.
- Exclusions: does not approve any other fixture change; does not approve
  changing `weak_tenant.json` or `incomplete_tenant.json`; does not waive
  acceptance criterion 4's requirement that no *other* fixture's pass/fail
  state regresses.

## Decision text

> "Yes, approve the fixture path amendment" — human answer approving the
> `tests/fixtures/strong_tenant.json` scope widening, given in response to
> the round-0 Codex review's F-002 finding, 2026-07-31.

## Evidence shown to the human

- `project/issues/ISSUE-0015.md` — original allowed paths and acceptance
  criterion 4
- `project/reviews/issues/ISSUE-0015-1ff0b987d2f7-codex.json` — F-002
  finding and evidence
- `git diff ee29aa9..1ff0b98 -- tests/fixtures/strong_tenant.json` — the
  exact fixture change
- `tests/test_analyzer.py::test_strong_tenant_scores_high` — the
  pre-existing assertion that would regress without the fixture change

## Consequence

- Permitted next action: repair round 1 restates `ISSUE-0015.md`'s allowed
  paths to include `tests/fixtures/strong_tenant.json`, keeps the existing
  fixture addition, reruns required checks, and requests a fresh Codex
  re-review.
- Invalidated approvals/reviews: none beyond the round-0 review already
  being superseded by the repair.
- Rollback/recovery expectation: N/A — a single additive fixture entry, not
  a destructive change.

## Notes

This does not retroactively bless open-ended fixture changes for
`ISSUE-0016`–`ISSUE-0018`; each of those issues' own allowed paths and stop
conditions govern separately.
