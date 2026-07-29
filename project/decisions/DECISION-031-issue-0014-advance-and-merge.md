# Human decision: Advance and merge ISSUE-0014 (frontend build/tests into CI)

**Decision ID:** `DECISION-031`
**Type:** `issue advance`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-29`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0014-frontend-ci` into `main`
- Artifact version: `ISSUE-0014` round-2 (final) candidate
- Commit/candidate SHA: `f63a0dadae917f35b328b60b1a562aa535d97d10` (product
  candidate reviewed by Codex); `4d541b4` (metadata-only follow-up
  recording the round-2 outcome, not itself re-reviewed)
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: `ISSUE-0014` only — `.github/workflows/validate.yml`,
  `README.md`, `CONTRIBUTING.md` (CI-status wording), and its own
  review/status/decision records
- Exclusions: no other pending change; does not initiate M3's milestone
  gate (four fresh reviews against a frozen candidate); does not accept
  `RISK-009` beyond what `DECISION-028` already accepted; does not
  authorize any product source change

## Decision text

> "Accept the sandbox residual and merge" (selected from three presented
> options in `project/issues/ISSUE-0014.md`'s "Human decision required")

## Evidence shown to the human

- `project/reviews/issues/ISSUE-0014-c4cb4d28f9b7-codex.json` — round 0,
  `BLOCKED` (F-001: stale `CURRENT.md` rows; fixed in repair round 1)
- `project/reviews/issues/ISSUE-0014-d72dbd9a5481-codex.json` — round 1,
  `BLOCKED` again, same F-001 narrower (round-1 repair fixed only 3 of 9
  stale rows; fixed fully in repair round 2)
- `project/reviews/issues/ISSUE-0014-f63a0dadae91-codex.json` — round 2
  (final), `BLOCKED` with **zero content findings**; sole blocker is the
  review sandbox's own execution-evidence limitations (no writable temp
  directory, no loopback sockets, no network access)
- `project/issues/ISSUE-0014.md` — full round table, real local check
  results at the round-2 candidate (188 backend tests, `py_compile` clean,
  `validate_repo.py` clean, frontend build producing all three output
  files, 91 frontend tests, and the negative-CI local-fallback proof)
- `project/decisions/DECISION-030-issue-0014-start-authorization.md` — the
  durable record of authorization to start this issue
- Precedent: `DECISION-010` (ISSUE-0006), `DECISION-016` (ISSUE-0007),
  `DECISION-017` (ISSUE-0008), `DECISION-019` (ISSUE-0009), `DECISION-020`
  (ISSUE-0010), `DECISION-022` (ISSUE-0011) — same sandbox-only-blocker
  pattern, each previously accepted the same way

## Consequence

- Permitted next action: merge `ai/ISSUE-0014-frontend-ci`
  (`f63a0dadae917f35b328b60b1a562aa535d97d10`..`4d541b4`) into `main`; mark
  `ISSUE-0014` `COMPLETE` in `ROADMAP.md`'s M3 table and
  `project/issues/ISSUE-0014.md`; update `project/status/CURRENT.md`;
  push the resulting `main` to GitHub. CI now builds and tests the
  frontend on every push and pull request. This completes M3's currently
  planned issue set (`ISSUE-0012`, `ISSUE-0013`, `ISSUE-0014`), but M3's
  milestone acceptance gate itself (four fresh general/security reviews
  against one frozen candidate) remains a separate, later human-initiated
  step, not authorized by this decision.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of the merge commit
  if a defect surfaces post-merge; no destructive history rewrite.

## Notes

Both permitted issue repair rounds were used — round 1 for a narrower form
of the same governance-record finding round 0 raised, round 2 for the
sandbox-only residual. The round-2 candidate is clean of every actionable
finding; the residual `BLOCKED` outcome comes entirely from the review
sandbox's inability to write a temp directory, bind a loopback socket, or
reach the network in this environment — a structural limitation already
accepted repeatedly for other issues in this project, not a product or
documentation defect.
