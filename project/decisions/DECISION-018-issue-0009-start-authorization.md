# Human decision: Authorize starting ISSUE-0009

**Decision ID:** `DECISION-018`
**Type:** `issue start authorization`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-27`

## Context

`DECISION-017` explicitly withheld authorization to start `ISSUE-0009`
("merge but don't begin 0009 yet") and `project/status/CURRENT.md` recorded
a process blocker requiring a further explicit human go-ahead before any
`ISSUE-0009` work could begin. The human opened a new task instructing
Claude to "begin ISSUE-0009 on project careview." Because that instruction
alone is exactly the kind of "next roadmap item in sequence" framing
`DECISION-017` said was **not** sufficient on its own, Claude asked a direct
confirmation question before doing any product work: "Is this message that
go-ahead?" The human selected "Yes, proceed now."

## Exact binding

- Artifact/action: start `ISSUE-0009` implementation work on a new branch,
  per `ROADMAP.md`'s `ISSUE-0009` row and `project/issues/ISSUE-0009.md`
- Target: `ai/ISSUE-0009-app-only-endpoint`, based on `main` at
  `4fdfa9f65b1e32bc0992dc3b7bd7d2357c3a8339` (main's tip when the branch was
  created; `04e68ee930c44a6c6dc438dfab39c381b6105e6d` is the earlier
  `ISSUE-0008` merge commit it descends from)
- Scope: authorizes starting and implementing `ISSUE-0009` only — does not
  pre-approve its advance/merge decision, any later M2 issue, or any
  protected action

## Decision text

> "Yes, proceed now" — in answer to: "CURRENT.md records that ISSUE-0009 was
> deliberately paused — the human said not to start it without a further
> explicit go-ahead beyond just being next in the roadmap. Is this message
> that go-ahead?"

## Evidence shown to the human

- `project/status/CURRENT.md` (pre-change) — the recorded process blocker
  and its exact wording
- `project/decisions/DECISION-017-issue-0008-advance-and-merge.md` — the
  prior exclusion this decision authorizes moving past

## Consequence

- Permitted next action: implement `ISSUE-0009` under the normal governed
  per-issue workflow (issue record, implementation, real checks, fresh
  Codex review, bounded repair, human advance/merge decision) — the same as
  every prior M2 issue. This decision does **not** itself complete or
  approve `ISSUE-0009`.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: none — no protected action taken.

## Notes

This decision exists specifically to close the gap the round-0 Codex review
(`project/reviews/issues/ISSUE-0009-c029199c5671-codex.json`, finding
F-001) correctly identified: the repository's own records must durably show
the human authorization for a start, not rely on unrecorded chat context.
