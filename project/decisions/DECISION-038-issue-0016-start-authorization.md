# Human decision: Authorize starting ISSUE-0016

**Decision ID:** `DECISION-038`
**Type:** `issue start authorization`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-31`

## Context

`DECISION-034` approved roadmap v6, which defines `ISSUE-0016` (analyzer
rule `terms-of-use-required`) as an approved `M4` target — `PLANNED`, not
started. Per `AGENTS.md`, roadmap approval alone does not authorize
starting an issue; a separate, explicit human start decision is required,
matching the precedent set by `DECISION-018`, `DECISION-021`, `DECISION-026`,
`DECISION-030`, and `DECISION-035` for prior issues. `ISSUE-0015`
(`M4`'s first issue) is now `COMPLETE` and merged (`DECISION-037`).

## Exact binding

- Artifact/action: start `ISSUE-0016` implementation work on a new branch
- Target: `ai/ISSUE-0016-terms-of-use-rule`, based on `main` at
  `bb01fab` (tip after `ISSUE-0015`'s merge)
- Scope: authorizes starting and implementing `ISSUE-0016` only, within the
  exact scope, allowed paths, and acceptance criteria already recorded in
  `project/issues/ISSUE-0016.md`. Does not pre-approve its advance/merge
  decision or any protected action.

## Decision text

> "yes, authorize starting ISSUE-0016"

## Evidence shown to the human

- `project/issues/ISSUE-0016.md` — full scope, acceptance criteria, required
  checks, and stop conditions
- `ROADMAP.md`'s `M4` issue sequence, row 16
- `project/status/CURRENT.md`'s "Next required actor" / "Next permitted
  action" rows naming `ISSUE-0016` as the recommended next `M4` issue

## Consequence

- Permitted next action: implement `ISSUE-0016` under the normal governed
  per-issue workflow (isolated branch, real checks, fresh Codex issue
  review of the exact base/head, bounded repair up to 2 rounds, human
  advance/merge decision). This decision does **not** itself complete or
  approve `ISSUE-0016` — only its start.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: N/A — a new branch and additive analyzer
  rule; no destructive action.

## Notes

`ISSUE-0016` is the first of the three `M4` rules needing a `normalize_policy`
extension (`grantControls.termsOfUse`), and its own round-1 plan review
already flagged and fixed a false-pass nuance (F-003, the `operator: "OR"`
case) — the issue file's acceptance criteria and stop conditions already
encode that fix; this decision does not reopen or change it.
