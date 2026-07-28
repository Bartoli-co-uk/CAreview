# Human decision: Advance and merge ISSUE-0011 (M2 documentation finalization)

**Decision ID:** `DECISION-022`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-28`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0011-m2-docs` into `main`
- Artifact version: `ISSUE-0011` round-1 (final) candidate
- Commit/candidate SHA: `e878cdcd979b7be87ff20cc986cb16d0d457dfe0`
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0011` only — `README.md` and `docs/security-boundaries.md`
  documentation, and its own review/status records
- Exclusions: no other pending change; does not initiate the M2 milestone
  gate (four fresh reviews against a frozen candidate); does not
  pre-approve any M3+ work

## Decision text

> "Approve and merge ISSUE-0011 into main"

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0011-b0b91742ec6c-codex.json` — round 0, `BLOCKED` (2 findings: F-001 inaccurate secret-transmission wording, F-002 missing start-authorization record; both fixed in repair round 1)
- `project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json` — round 1 (final), `BLOCKED` with **zero findings**; sole blocker is the accepted sandbox execution-evidence residual (`DECISION-015`)
- `project/handoffs/ISSUE-0011-handoff.md` — real local check results at the round-1 candidate: 173 tests OK, `py_compile` clean, `validate_repo.py` clean, plus a non-live documentation walkthrough
- `project/issues/ISSUE-0011.md` — full round table and acceptance-criteria mapping
- `project/decisions/DECISION-021-issue-0011-start-authorization.md` — the durable record of authorization to start this issue
- Precedent: `DECISION-010` (ISSUE-0006), `DECISION-016` (ISSUE-0007), `DECISION-017` (ISSUE-0008), `DECISION-019` (ISSUE-0009), `DECISION-020` (ISSUE-0010) — same sandbox-only-blocker pattern

## Consequence

- Permitted next action: merge `ai/ISSUE-0011-m2-docs`
  (`e878cdcd979b7be87ff20cc986cb16d0d457dfe0`) into `main`; mark
  `ISSUE-0011` `COMPLETE` in `ROADMAP.md`'s M2 table and
  `project/issues/ISSUE-0011.md`; update `project/status/CURRENT.md`; push
  the resulting `main` to GitHub. This completes M2's planned issue set
  (`ISSUE-0007..0011`), but the M2 milestone acceptance gate itself (four
  fresh general/security reviews against one frozen candidate) is a
  separate, later human-initiated step, not authorized by this decision.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit
  if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Only 1 of 2 permitted issue repair rounds was needed. The round-1
candidate is clean of every actionable finding; the residual `BLOCKED`
outcome comes entirely from the review sandbox's known inability to bind
loopback sockets, write `__pycache__`, or create a writable temp
directory — a structural limitation accepted in `DECISION-015`, not a
product or documentation defect.
