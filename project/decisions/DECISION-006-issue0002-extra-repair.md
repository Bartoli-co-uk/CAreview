# Human decision: Authorize one extra repair round for ISSUE-0002

**Decision ID:** `DECISION-006`
**Type:** `issue advance (repair-limit / iteration-cap override)`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T14:26:45Z`

## Exact binding

- Scope: ISSUE-0002 only — authorize one repair round beyond the default two, and
  the corresponding extra review iteration beyond the absolute five-iteration cap,
  to resolve Codex finding F-001 (immediate single-concurrency supersession) and
  the F-002 README advisory on candidate `752cd75a87708724b1b131845c256706da97ef0b`.
- Exclusions: does not change the standing limits for any other issue; does not
  authorize protected actions.

## Decision text

> "Authorize one more fix, then merge" — for ISSUE-0002's final BLOCKED review.

## Consequence

- Apply the small fix (a new `start()` clears the old session/token immediately,
  before its device-code request) and the README wording, run one final Codex
  review, and — per DECISION-004/005 — merge if it is BLOCKED only on the
  execution-evidence limitation with no substantive finding.

## Notes

The finding was legitimate but low-risk on a single-user local tool; the human
judged the small correctness fix worth one bounded extra round rather than
accepting the residual.
