# Human decision: Authorize starting ISSUE-0011

**Decision ID:** `DECISION-021`
**Type:** `issue start authorization`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-28`

## Context

`DECISION-020` (ISSUE-0010 advance and merge) scopes itself to `ISSUE-0010`
only and states it does not authorize starting `ISSUE-0011` — standard
scoping language, not an active deferral instruction (contrast
`DECISION-017`, which explicitly said "don't begin 0009 yet"). In a new
top-level task, the human directly instructed Claude: "begin ISSUE-0011".
The round-0 Codex review of `ISSUE-0011`
(`project/reviews/issues/ISSUE-0011-b0b91742ec6c-codex.json`, finding
F-002) correctly noted that this authorization existed only in chat at
that point, not as a durable repository record, per `AGENTS.md`'s
default-manual autonomy rule and its instruction that chat history is not
authoritative. This decision records it.

## Exact binding

- Artifact/action: start `ISSUE-0011` implementation work on a new branch,
  per `ROADMAP.md`'s `ISSUE-0011` row and `project/issues/ISSUE-0011.md`
- Target: `ai/ISSUE-0011-m2-docs`, based on `main` at
  `4f35275d004265ee152348e7e3d1f7b9f6a62cc6` (`main`'s tip when the branch
  was created — the `ISSUE-0010` closeout commit)
- Scope: authorizes starting and implementing `ISSUE-0011` only — does not
  pre-approve its advance/merge decision or any protected action

## Decision text

> "begin ISSUE-0011"

## Evidence shown to the human

- `project/status/CURRENT.md` (pre-change) — showed `ISSUE-0011` as the
  next, un-deferred M2 roadmap item
- `ROADMAP.md`'s `ISSUE-0011` row — documentation-only scope, no product
  source change permitted

## Consequence

- Permitted next action: implement `ISSUE-0011` under the normal governed
  per-issue workflow (issue record, implementation, real checks, fresh
  Codex review, bounded repair, human advance/merge decision) — the same
  as every prior M2 issue. This decision does **not** itself complete or
  approve `ISSUE-0011`.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: none — no protected action taken.

## Notes

This decision exists specifically to close the gap the round-0 Codex
review correctly identified: the repository's own records must durably
show the human's authorization for a start, not rely on unrecorded chat
context, matching the precedent set by `DECISION-018` for `ISSUE-0009`.
