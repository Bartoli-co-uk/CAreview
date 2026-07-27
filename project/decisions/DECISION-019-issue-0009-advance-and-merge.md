# Human decision: Advance and merge ISSUE-0009 (app-only endpoint)

**Decision ID:** `DECISION-019`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-27`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0009-app-only-endpoint` into `main`
- Artifact version: `ISSUE-0009` round-1 candidate
- Commit/candidate SHA: `7b0600f0831f68f8933b68ca0bba34f58a00b0cc`
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0009` only — `POST /api/auth/app` endpoint in `server.py`,
  its tests, README documentation, and its own review/status records
- Exclusions: no other pending change; does not pre-approve `ISSUE-0010` or
  any later M2 issue; does not authorize starting `ISSUE-0010`

## Decision text

> "Approve and merge ISSUE-0009 into main"

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0009-c029199c5671-codex.json` — round 0, `BLOCKED` (3 findings: F-001 missing start-authorization record + stale base SHA, F-002 incomplete renewal tests, F-003 incomplete secret-scan coverage; all fixed in repair round 1)
- `project/reviews/issues/ISSUE-0009-7b0600f0831f-codex.json` — round 1 (final), `BLOCKED` with **zero findings**; sole blocker is the accepted sandbox execution-evidence residual (`DECISION-015`)
- `project/handoffs/ISSUE-0009-handoff.md` — real local check results at the round-1 candidate: 162 tests OK, `py_compile` clean, `validate_repo.py` clean
- `project/issues/ISSUE-0009.md` — full round table and acceptance-criteria mapping
- `project/decisions/DECISION-018-issue-0009-start-authorization.md` — the durable record of authorization to start this issue
- Precedent: `DECISION-010` (ISSUE-0006), `DECISION-016` (ISSUE-0007), `DECISION-017` (ISSUE-0008) — same sandbox-only-blocker pattern

## Consequence

- Permitted next action: merge `ai/ISSUE-0009-app-only-endpoint`
  (`7b0600f0831f68f8933b68ca0bba34f58a00b0cc`) into `main`; mark
  `ISSUE-0009` `COMPLETE` in `ROADMAP.md`'s M2 table and
  `project/issues/ISSUE-0009.md`; update `project/status/CURRENT.md`; push
  the resulting `main` to GitHub. `ISSUE-0010` does **not** start as part
  of this decision.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit
  if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Only 1 of 2 permitted issue repair rounds was needed. The round-1
candidate is clean of every actionable finding; the residual `BLOCKED`
outcome comes entirely from the review sandbox's known inability to bind
loopback sockets, write `__pycache__`, or create a writable temp
directory — a structural limitation accepted in `DECISION-015`, not a
product defect.
