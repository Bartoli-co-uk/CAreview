# Human decision: Authorize starting ISSUE-0013

**Decision ID:** `DECISION-026`
**Type:** `issue start authorization`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-28`

## Context

`DECISION-025` (ISSUE-0012 advance and merge) accepted the round-2
`CHANGES_REQUIRED` residual (F-001: an unawaited, unconditional/unscoped
compensating logout after a stale successful device-code poll) as tracked
risk, and combined that with an explicit instruction to open a new issue,
with its own fresh repair budget, to fix the underlying server-session-
scoping gap properly. This decision records that start authorization as a
durable repository record, matching the precedent set by `DECISION-018`
and `DECISION-021` for prior issues in this project.

## Exact binding

- Artifact/action: start `ISSUE-0013` implementation work on a new branch
- Target: `ai/ISSUE-0013-scoped-device-code-abandon`, based on `main` at
  `959fbcf` (`main`'s tip after the `ISSUE-0012` merge)
- Scope: authorizes starting and implementing `ISSUE-0013` only — does not
  pre-approve its advance/merge decision or any protected action. Like
  `ISSUE-0012`, this is out-of-band relative to `ROADMAP.md` v4 (no
  roadmap version covers either); it fixes a residual from out-of-band
  work rather than delivering a roadmap-planned M1/M2 issue.

## Decision text

> "then open a new issue, make sure to follow governance set in place to
> use it" (in the same instruction as `DECISION-025`'s merge authorization)

## Evidence shown to the human

- `project/issues/ISSUE-0012.md`'s "Human decision required" section —
  the exact F-001 finding and three presented options
- `project/reviews/issues/ISSUE-0012-195bd8e74688-codex.json` — the
  round-2 `CHANGES_REQUIRED` report naming the finding and its suggested
  remediation (a server API that conditionally clears only the named
  device attempt, rather than an unconditional logout)

## Consequence

- Permitted next action: implement `ISSUE-0013` under the normal governed
  per-issue workflow (issue record, implementation, real checks, fresh
  Codex review, bounded repair up to 2 rounds, human advance/merge
  decision). This decision does **not** itself complete or approve
  `ISSUE-0013`, and does not authorize merging it without a separate
  advance/merge decision.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: none — no protected action taken yet.

## Notes

Unlike most prior issues in this repository, `ISSUE-0013` is not itself
governed by an approved `ROADMAP.md` version — it exists to remediate a
residual from `ISSUE-0012`, which was itself out-of-band per
`DECISION-024`. The same per-issue review gate (implementation, real
checks, fresh Codex review, bounded repair) still applies in full; only
the roadmap-governance layer above the issue level is absent, exactly as
it was for `ISSUE-0012`.
