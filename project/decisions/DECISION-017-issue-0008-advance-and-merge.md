# Human decision: Advance and merge ISSUE-0008 (app-only token acquisition)

**Decision ID:** `DECISION-017`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-27`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0008-app-only-token` into `main`
- Artifact version: `ISSUE-0008` round-1 candidate
- Commit/candidate SHA: `205125474389932f02e7c484dd59ad612892ac4b`
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0008` only — app-only client-credentials token acquisition
  inside `auth.py`, its tests, and its own review/status records
- Exclusions: no other pending change; does not pre-approve `ISSUE-0009` or
  any later M2 issue; does not authorize starting `ISSUE-0009` in this task
  or any task — the human has explicitly deferred that start

## Decision text

> "merge but don't begin 0009 yet"

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0008-88a4a6d355eb-codex.json` — round 0, `BLOCKED` (2 findings: F-001 scope-override, F-002 missing race tests; both fixed in repair round 1)
- `project/reviews/issues/ISSUE-0008-205125474389-codex.json` — round 1 (final), `BLOCKED` with **zero findings**; sole blocker is the accepted sandbox execution-evidence residual (`DECISION-015`)
- `project/handoffs/ISSUE-0008-handoff.md` — real local check results at the round-1 candidate: 116 tests OK, `py_compile` clean, `validate_repo.py` clean
- `project/issues/ISSUE-0008.md` — full round table and acceptance-criteria mapping
- Precedent: `DECISION-010` (ISSUE-0006), `DECISION-016` (ISSUE-0007) — same sandbox-only-blocker pattern

## Consequence

- Permitted next action: merge `ai/ISSUE-0008-app-only-token` (`205125474389932f02e7c484dd59ad612892ac4b`) into `main`; mark `ISSUE-0008` `COMPLETE` in `ROADMAP.md`'s M2 table and `project/issues/ISSUE-0008.md`; update `project/status/CURRENT.md`; push the resulting `main` to GitHub. `ISSUE-0009` explicitly does **not** start as part of this decision — `CURRENT.md`'s resting state must show `active_issue: none` with `ISSUE-0009` named as the next permitted (not started) action.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Only 1 of 2 permitted issue repair rounds was needed. The round-1 candidate
is clean of every actionable finding; the residual `BLOCKED` outcome comes
entirely from the review sandbox's known inability to bind loopback
sockets, write `__pycache__`, or create a writable temp directory — a
structural limitation accepted in `DECISION-015`, not a product defect.
