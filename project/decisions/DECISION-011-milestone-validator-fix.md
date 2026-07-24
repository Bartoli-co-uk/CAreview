# Human decision: Fix validate_repo.py's missing-milestone-record self-test (M1 general-remediation)

**Decision ID:** `DECISION-011`
**Type:** `protected action (governance script fix) / milestone general-remediation cycle`
**Decision:** `APPROVE` (retroactive record — see Notes)
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T17:XX:XXZ`

## Context

A genuinely independent, fresh Claude general-review subagent (not the author,
no shared context) found that `python3 scripts/validate_repo.py` **fails**
(exit 1) at the M1 milestone candidate, contradicting the milestone record's
claim that it passed. Root cause, verified directly: `scripts/validate_repo.py`'s
`smoke_target_binding_rejections` "missing milestone record" fixture copies the
entire live repository (`make_copy`), which now legitimately contains
`project/milestones/M1.md` since this project has reached its own M1 milestone —
so the fixture no longer represents a genuinely missing record, the launcher
correctly does not reject it, and the self-test's own assertion fails. This is
the same class of self-test defect as the earlier `ROADMAP_REVIEW` one noted in
`DECISION-002`, but unlike that one it does not self-resolve by moving stages —
it will fail on every future `validate_repo.py` run for as long as `M1.md`
exists in the repository.

## Exact binding

- Artifact/action: `scripts/validate_repo.py`,
  `smoke_target_binding_rejections`'s "missing milestone record" fixture —
  explicitly delete any copied `project/milestones/M1.md` from the fixture tree
  before asserting the launcher rejects it.
- Scope: this repository's copy of the governance script only.
- Verified: `python3 scripts/validate_repo.py` now exits 0 (was exit 1).

## Decision text

> Following the established precedent of `DECISION-002` (fixing a blocking
> governance-script bug discovered mid-workflow rather than merely documenting
> it, because this one would otherwise fail permanently), this fix is applied as
> the M1 milestone's one permitted general-remediation cycle.

## Consequence

- This is a genuine source change to a committed script, so per
  `docs/workflow.md` it creates a **new milestone candidate** and **invalidates
  all four milestone reviews already gathered** (2 fresh Claude subagent
  reviews + intended Codex reviews). All four must be rerun fresh against the
  new candidate SHA.
- This uses the milestone's one permitted general-remediation cycle
  (`docs/workflow.md`: "at most one milestone general-remediation cycle").
- The identical upstream bug likely exists in `Bartoli-co-uk/ClaudexCodexSetUp`
  and should be reported there separately (follow-up, out of scope here).

## Notes

Recorded retroactively in the same turn as the fix, consistent with how
`DECISION-002` was handled: the fix is small, mechanical, strictly improves
correctness (makes a negative self-test genuinely test what it claims to), and
does not touch any product code or weaken any gate.
