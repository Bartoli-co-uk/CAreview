# Human decision: Advance and merge ISSUE-0017 (admin-signin-frequency analyzer rule)

**Decision ID:** `DECISION-042`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0017-admin-signin-frequency-rule` into
  `main`, plus a metadata-only follow-up correcting `ROADMAP.md`'s stale
  `M4` status prose and `README.md`'s stale test count
- Artifact version: `ISSUE-0017` round-2 (final) candidate
- Commit/candidate SHA: `2a55a56ce2551260102104c3718429f8ce6b2e62` (product/
  documentation candidate reviewed by Codex); `cadc728` (metadata-only
  follow-up recording the round-2 outcome, not itself re-reviewed)
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0017` only — `graph.py`, `rules.py`, `README.md`,
  `tests/test_graph.py`, `tests/test_analyzer.py`,
  `tests/fixtures/strong_tenant.json` (already in the issue's own
  originally-approved allowed paths, no scope amendment needed), plus the
  metadata-only correction to `ROADMAP.md`'s `M4` delivery-status prose
  (F-002) and `README.md`'s stale test count (F-003), and this issue's own
  handoff/review/status/decision records
- Exclusions: no other pending change; does not start `ISSUE-0018`; does
  not open `M4`'s milestone gate; does not accept any risk beyond the
  sandbox execution-evidence residual described below

## Decision text

> "Accept and merge (recommended)" (selected from the options presented
> after the round-2 fresh Codex review, which itself offered: accept and
> merge with a metadata-only follow-up; hold and specify a different
> disposition; or get independent re-verification first)

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0017-079f5c72cb27-codex.json` — round 0,
  `CHANGES_REQUIRED` (F-001, medium, real: `persistentBrowser.enabled` not
  checked alongside `mode == "never"` — fixed in round 1)
- `project/reviews/issues/ISSUE-0017-72910d8b22dd-codex.json` — round 1,
  `BLOCKED` (F-001 sandbox-only; F-002 medium/real: issue/handoff records
  left internally contradictory after the round-1 source fix — fixed in
  round 2)
- `project/reviews/issues/ISSUE-0017-2a55a56ce255-codex.json` — round 2
  (final), `BLOCKED` with no product-code defect: F-001 (sandbox-only,
  same accepted class as `ISSUE-0014`–`ISSUE-0016`), F-002 (medium, real,
  unresolved at the time of review: `ROADMAP.md`'s `M4` status prose never
  updated past round 0), F-003 (low, advisory, pre-existing: `README.md`
  stale test count)
- `project/issues/ISSUE-0017.md` — full round table, "Human decision
  required" section, real local check results at every round (206 tests
  passed, `py_compile` clean, `validate_repo.py` clean)
- `project/decisions/DECISION-041-issue-0017-start-authorization.md` — the
  durable record of authorization to start this issue
- Precedent: `DECISION-040` (`ISSUE-0016`), `DECISION-037` (`ISSUE-0015`),
  and `DECISION-031` (`ISSUE-0014`) — the same sandbox-only-blocker pattern,
  each previously accepted the same way

## Consequence

- Permitted next action: apply the metadata-only follow-up (`ROADMAP.md`
  F-002, `README.md` F-003) on `ai/ISSUE-0017-admin-signin-frequency-rule`;
  merge the branch into `main`; mark `ISSUE-0017` `COMPLETE` in
  `project/issues/ISSUE-0017.md` and `ROADMAP.md`'s `M4` issue table;
  update `project/status/CURRENT.md`. `M4`'s next issue (`ISSUE-0018`)
  remains unauthorized to start without its own separate human start
  decision.
- Invalidated approvals/reviews: none — the metadata-only follow-up
  touches no product source (`graph.py`, `rules.py`, tests, fixtures) so
  the round-2 Codex review of the product candidate remains valid for that
  candidate.
- Rollback/recovery expectation: standard `git revert` of the merge commit
  if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Both permitted issue repair rounds were used: round 1 fixed a real
product-code defect (F-001, the `persistentBrowser.enabled` gap); round 2
fixed a real governance-record staleness defect (F-002, stale
candidate-SHA/handoff sections) that round 1's own review surfaced. The
round-2 candidate's own fresh review is clean of every actionable
*product* finding — its residual `BLOCKED` outcome is the sandbox
execution-evidence limitation (F-001, structural, already accepted
repeatedly) plus one real-but-minor governance-record gap (F-002,
`ROADMAP.md` prose that fell behind its own repair rounds — ordinary
record hygiene, not a defect in the rule logic) and one pre-existing,
unrelated advisory (F-003). None of these reopen or weaken the rule's
effective-coverage algorithm, its `persistentBrowser.mode == "never"`
exactness, or any other acceptance criterion.
