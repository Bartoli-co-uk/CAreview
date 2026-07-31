# Human decision: Authorize starting ISSUE-0017

**Decision ID:** `DECISION-041`
**Type:** `issue start authorization`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Context

`DECISION-034` approved roadmap v6, which defines `ISSUE-0017` (analyzer
rule `admin-signin-frequency`) as an approved `M4` target — `PLANNED`, not
started. Per `AGENTS.md`, roadmap approval alone does not authorize
starting an issue; a separate, explicit human start decision is required,
matching the precedent set by `DECISION-018`, `DECISION-021`,
`DECISION-026`, `DECISION-030`, `DECISION-035`, and `DECISION-038` for
prior issues. `ISSUE-0016` (`M4`'s second issue) is now `COMPLETE` and
merged (`DECISION-040`).

## Exact binding

- Artifact/action: start `ISSUE-0017` implementation work on a new branch
- Target: `ai/ISSUE-0017-admin-signin-frequency-rule`, based on `main` at
  `48129547a68239e8f733ce6b50b6a63407a35256` (tip after `ISSUE-0016`'s merge)
- Scope: authorizes starting and implementing `ISSUE-0017` only, within the
  exact scope, allowed paths, and acceptance criteria already recorded in
  `project/issues/ISSUE-0017.md`. Does not pre-approve its advance/merge
  decision or any protected action.

## Decision text

> "begin issue 17 in careview"

## Evidence shown to the human

- `project/issues/ISSUE-0017.md` — full scope, acceptance criteria, required
  checks, and stop conditions
- `ROADMAP.md`'s `M4` issue sequence, row 17
- `project/status/CURRENT.md`'s "Next required actor" / "Next permitted
  action" rows naming `ISSUE-0017` as the recommended next `M4` issue

## Consequence

- Permitted next action: implement `ISSUE-0017` under the normal governed
  per-issue workflow (isolated branch, real checks, fresh Codex issue
  review of the exact base/head, bounded repair up to 2 rounds, human
  advance/merge decision). This decision does **not** itself complete or
  approve `ISSUE-0017` — only its start.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: N/A — a new branch and additive analyzer
  rule; no destructive action.

## Notes

`ISSUE-0017` deliberately does not reuse `mfa-admins`'s simpler coverage
pattern verbatim — its own plan review (Codex round-1 F-004, round-2
F-001) required the more precise effective-coverage algorithm already
encoded in the issue file's acceptance criteria and stop conditions. This
decision does not reopen or change that algorithm.
