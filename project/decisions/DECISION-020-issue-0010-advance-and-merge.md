# Human decision: Advance and merge ISSUE-0010 (sign-in card mode toggle and app-only form)

**Decision ID:** `DECISION-020`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-27`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0010-app-only-ui` into `main`
- Artifact version: `ISSUE-0010` round-2 (final) candidate
- Commit/candidate SHA: `2a2d0b73e94d2635a645728e5b78f7f500c0a6b2`
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0010` only — sign-in card mode toggle and app-only form in
  `web/index.html`/`web/app.js`/`web/style.css`, its tests, README
  documentation, and its own review/status records
- Exclusions: no other pending change; does not pre-approve `ISSUE-0011`;
  does not authorize starting `ISSUE-0011`

## Decision text

> "Approve and merge ISSUE-0010 into main"

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0010-1d557b3840f7-codex.json` — round 0, `BLOCKED` (2 findings: F-001 secret not cleared on a rejected fetch, F-002 missing successful-submit browser evidence; both fixed in repair round 1)
- `project/reviews/issues/ISSUE-0010-451dbe236769-codex.json` — round 1, `BLOCKED` (1 metadata finding: stale `CURRENT.md`; fixed in repair round 2)
- `project/reviews/issues/ISSUE-0010-2a2d0b73e94d-codex.json` — round 2 (final), `BLOCKED` with **zero findings**; sole blocker is the accepted sandbox execution-evidence residual (`DECISION-015`)
- `project/handoffs/ISSUE-0010-handoff.md` — real local check results at the round-2 candidate: 173 tests OK, `py_compile` clean, `validate_repo.py` clean, plus the full human-performed manual browser walkthrough (all five required checkpoints, including a successful submit verified against a local-only mock-success server)
- `project/issues/ISSUE-0010.md` — full round table and acceptance-criteria mapping
- Precedent: `DECISION-010` (ISSUE-0006), `DECISION-016` (ISSUE-0007), `DECISION-017` (ISSUE-0008), `DECISION-019` (ISSUE-0009) — same sandbox-only-blocker pattern

## Consequence

- Permitted next action: merge `ai/ISSUE-0010-app-only-ui`
  (`2a2d0b73e94d2635a645728e5b78f7f500c0a6b2`) into `main`; mark
  `ISSUE-0010` `COMPLETE` in `ROADMAP.md`'s M2 table and
  `project/issues/ISSUE-0010.md`; update `project/status/CURRENT.md`; push
  the resulting `main` to GitHub. `ISSUE-0011` does **not** start as part
  of this decision.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit
  if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Both of 2 permitted issue repair rounds were used. The round-2 candidate
is clean of every actionable finding; the residual `BLOCKED` outcome comes
entirely from the review sandbox's known inability to bind loopback
sockets, write `__pycache__`, or create a writable temp directory — a
structural limitation accepted in `DECISION-015`, not a product defect.
