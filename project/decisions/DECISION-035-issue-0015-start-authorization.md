# Human decision: Authorize starting ISSUE-0015

**Decision ID:** `DECISION-035`
**Type:** `issue start authorization`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Context

`DECISION-034` approved roadmap v6, which defines `ISSUE-0015` (analyzer rule
`location-restriction-present`) as an approved `M4` target — `PLANNED`, not
started. Per `AGENTS.md`, roadmap approval alone does not authorize starting
an issue; a separate, explicit human start decision is required, matching
the precedent set by `DECISION-018`, `DECISION-021`, `DECISION-026`, and
`DECISION-030` for prior issues.

Implementation of `ISSUE-0015` (branch `ai/ISSUE-0015-location-restriction-rule`,
candidate `bcfeacdb0e264db42badf4a6a945acb94f3fc3ff`) had already been
committed before this record was created. The round-0 fresh Codex issue
review (`project/reviews/issues/ISSUE-0015-1ff0b987d2f7-codex.json`,
`BLOCKED`) correctly flagged (F-003) that no durable start-authorization
record existed for this specific issue. This decision closes that gap by
recording, after the fact, that the human did separately authorize starting
`ISSUE-0015`.

## Exact binding

- Artifact/action: start `ISSUE-0015` implementation work on a new branch
- Target: `ai/ISSUE-0015-location-restriction-rule`, based on `main` at
  `ee29aa91346c5246d75ae48cdfdcf39137de0858`
- Scope: authorizes starting and implementing `ISSUE-0015` only, within the
  scope, allowed paths, and acceptance criteria recorded in
  `project/issues/ISSUE-0015.md` (as amended by `DECISION-036` for the
  fixture-path addition). Does not pre-approve its advance/merge decision or
  any protected action.

## Decision text

> "Yes, I authorized it" — human answer confirming ISSUE-0015 start
> authorization, given in response to the round-0 Codex review's F-003
> finding, 2026-07-31.

## Evidence shown to the human

- `project/issues/ISSUE-0015.md` — full scope, acceptance criteria, required
  checks, and stop conditions
- `project/reviews/issues/ISSUE-0015-1ff0b987d2f7-codex.json` — round-0
  `BLOCKED` review naming F-003 (missing start-authorization record)
- `ROADMAP.md`'s `M4` issue sequence
- `project/status/CURRENT.md`'s "Next required actor" / "Next permitted
  action" rows naming `ISSUE-0015` as the recommended first `M4` issue

## Consequence

- Permitted next action: continue `ISSUE-0015`'s repair round 1 (fix F-001,
  F-002, F-003 from the round-0 review) under the normal governed per-issue
  workflow, then rerun the fresh Codex issue review against the new
  candidate SHA.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: N/A — retroactive documentation only; no
  destructive action.

## Notes

This decision is retroactive: it documents an authorization the human
already gave to start this work, rather than authorizing work not yet
begun. It does not retroactively supply any other missing gate, and it does
not itself resolve F-001 or F-002 from the round-0 review — those are
handled separately (`DECISION-036` for F-002; a mechanical record fix for
F-001).
