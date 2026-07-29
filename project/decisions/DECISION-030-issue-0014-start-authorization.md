# Human decision: Authorize starting ISSUE-0014

**Decision ID:** `DECISION-030`
**Type:** `issue start authorization`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-29`

## Context

`DECISION-029` approved roadmap v5, which defines `ISSUE-0014` (wire the
frontend build and test suite into CI) as an approved target — `PLANNED`,
not started. Per `AGENTS.md`, roadmap approval alone does not authorize
starting an issue; a separate, explicit human start decision is required.
This decision records that authorization, matching the precedent set by
`DECISION-018`, `DECISION-021`, and `DECISION-026` for prior issues.

## Exact binding

- Artifact/action: start `ISSUE-0014` implementation work on a new branch
- Target: `ai/ISSUE-0014-frontend-ci`, based on `main` at `8e864a3`
  (`main`'s tip after roadmap v5's approval, `DECISION-029`)
- Scope: authorizes starting and implementing `ISSUE-0014` only, within the
  exact scope, allowed paths, and acceptance criteria already recorded in
  `project/issues/ISSUE-0014.md`. Does not pre-approve its advance/merge
  decision or any protected action. Does not authorize pushing a
  deliberately failing commit to a live GitHub Actions run — `ISSUE-0014`'s
  own stop conditions and acceptance criterion 2 require local verification
  instead, per `DECISION-029`'s accepted F-001 residual on that point.

## Decision text

> "start ISSUE-0014"

## Evidence shown to the human

- `project/issues/ISSUE-0014.md` — full scope, acceptance criteria, required
  checks, and stop conditions
- `ROADMAP.md`'s M3 issue sequence, row 14
- `project/status/CURRENT.md`'s "Next required actor" / "Next permitted
  action" rows, naming this as the open next step

## Consequence

- Permitted next action: implement `ISSUE-0014` under the normal governed
  per-issue workflow (isolated branch, real checks, fresh Codex issue
  review of the exact base/head, bounded repair up to 2 rounds, human
  advance/merge decision). This decision does **not** itself complete or
  approve `ISSUE-0014` — only its start.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: N/A — a new branch and CI-only change; no
  destructive action.

## Notes

`ISSUE-0014`'s scope is narrow and low-risk (a CI workflow step plus two
documentation caveats), with no product source path in its allowed-paths
list. The two residuals `DECISION-029` already accepted for this issue
(the negative-CI fallback-proof limitation, and `RISK-010`) remain accepted
as-is; this decision does not reopen them.
