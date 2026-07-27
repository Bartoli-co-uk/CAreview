# Human decision: Approve roadmap v4 (milestone M2 — opt-in app-only auth, secret only)

**Decision ID:** `DECISION-015`
**Type:** `roadmap approval`
**Decision:** `APPROVE`
**Human approver:** `Jay (jay@bartoli.co.uk), repository owner`
**Decided at:** `2026-07-27`

## Exact binding

- Artifact/action: `ROADMAP.md` v4 candidate
- Artifact version: `4`
- Commit/candidate SHA: `9e5ba6d` (full: see `git log --format=%H -1 9e5ba6d`
  in this branch history)
- Target: `N/A (planning artifact)`
- Scope: approves roadmap v4 as written — adds milestone `M2` (least-privilege
  delegated scope trim, plus an opt-in app-only client-credentials sign-in
  mode with a secret only) and its five issues, `ISSUE-0007` through
  `ISSUE-0011`, on top of the already-approved brief v2 (`DECISION-013`) and
  its resolved open questions (`DECISION-014`). Authorizes `ISSUE-0007` to
  start as the first M2 implementation issue, under the same per-issue
  governed workflow (isolated branch, tests + docs in the same change, a
  fresh Codex issue review of the exact base/head, bounded repair rounds)
  used for all six M1 issues.
- Exclusions: does not authorize any live sign-in against a real tenant, in
  either mode — that remains a separate protected action. Does not itself
  constitute the M2 milestone acceptance; that is a separate four-review gate
  (Claude general, Codex general, Claude security, Codex security) after all
  five M2 issues complete, per `AGENTS.md`.

## Decision text

> "Yes, approve this exact roadmap v4"

## Evidence shown to the human

- `ROADMAP.md` at commit `9e5ba6d` (this commit).
- The full four-round review/response record under `project/reviews/plans/`:
  `ROADMAP-71f7ba60b045-*` (round 1, BLOCKED, 5 findings), `ROADMAP-605c282c5c81-*`
  (round 2, BLOCKED, 2 findings + 1 advisory), `ROADMAP-76a09c46a57d-*`
  (confirmatory round, `CHANGES_REQUIRED`, 2 findings), `ROADMAP-faf5ec70bf00-*`
  (confirmatory round, BLOCKED, 3 findings + 1 advisory) — each with a
  corresponding Claude response recording the fix or the out-of-band evidence
  for the recurring review-sandbox limitation (no writable temp directory for
  the governance validator, and socket restrictions for the full unit suite).
- `project/status/CURRENT.md` at the `ROADMAP_REVIEW` stage, naming this as
  the next required action.

## Consequence

- Permitted next action: `ISSUE-0007` (trim delegated `SCOPES` to
  `Policy.Read.All` only) may start in a new top-level Claude issue task, on
  an isolated branch, following the same governed issue workflow as M1.
- Invalidated approvals/reviews: none. v1/`DECISION-001`, v3
  roadmap/`DECISION-003`, and all M1 decisions remain valid and untouched.
- Rollback/recovery expectation: N/A — no M2 product code exists yet; only
  planning documents have changed.

## Notes

The v4 planning loop reached the repository's absolute five-iteration cap
(`AGENTS.md`) across its four review rounds (one BLOCKED initial review, two
`AGENTS.md`-permitted revision rounds, and two further confirmatory rounds run
at the human's explicit direction after the cap was flagged). Every
actionable finding across all four rounds was fixed; the only recurring
blocker was the review sandbox's inability to execute real checks
(`validate_repo.py`, the full `unittest` suite, and `py_compile`'s bytecode
cache), each time addressed with out-of-band evidence showing the checks pass
against the exact reviewed commit. This mirrors the precedent already
recorded for the v3 roadmap's own round-2 review-sandbox limitation. The
human approved directly from this reconciliation record rather than
requesting a further, sixth review round.
