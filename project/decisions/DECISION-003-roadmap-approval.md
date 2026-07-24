# Human decision: Approve roadmap v3

**Decision ID:** `DECISION-003`
**Type:** `roadmap approval`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T11:27:22Z`

## Exact binding

- Artifact/action: `ROADMAP.md`
- Artifact version: `3`
- Commit/candidate SHA: `125d74f6d4bfe85f1a727293064d0887f2d121c7`
- Target: `N/A (planning artifact)`
- Scope: Approval of the exact roadmap v3 above; authorizes implementation of the
  six planned issues (ISSUE-0001..0006) sequentially under the normal issue gates.
- Exclusions: does not approve any protected action (live tenant auth/fetch,
  network exposure, installs, publishing) or milestone/final acceptance.
- Expiry/review date: `N/A — a roadmap change requires a new version and approval`

## Decision text

> Roadmap approval question answered "Approve roadmap v3 — start building",
> accepting the F-004 review-sandbox evidence gap. Push authorized ("Push now").

## Evidence shown to the human

- `ROADMAP.md` v3 at `125d74f6d4bfe85f1a727293064d0887f2d121c7`.
- Codex plan reviews round 1 (`ROADMAP-691b1427de57-codex.json`) and round 2
  (`ROADMAP-4daf03ca5be5-codex.json`), both `BLOCKED`, with Claude responses.
- Out-of-band `validate_repo.py` evidence (passes except the known wrong-stage
  self-test artifact).

## Consequence

- Permitted next action: begin `ISSUE-0001` on branch `ai/ISSUE-0001-server-shell`
  in a fresh issue task; implement, run real checks, commit, and run the mandatory
  Codex issue review.
- Accepted residual (F-004): the Codex review sandbox cannot run the governance
  validator (no writable temp dir), so plan/issue reviews may report a governance
  evidence limitation. The human accepts this as an environment limitation,
  mitigated by running `validate_repo.py` out-of-band and recording the result.
- Invalidated approvals/reviews: none.

## Notes

Two non-blocking follow-ups remain (not part of this approval):
- The validator's wrong-stage self-test bug (`scripts/validate_repo.py`).
- The identical launcher schema bug still present upstream in
  `Bartoli-co-uk/ClaudexCodexSetUp` (fixed here via `DECISION-002`).
