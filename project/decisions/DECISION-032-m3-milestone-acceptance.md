# Human decision: Accept M3 milestone (React/TypeScript dashboard UI)

**Decision ID:** `DECISION-032`
**Type:** `milestone acceptance`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-29`

## Exact binding

- Artifact/action: `project/milestones/M3.md` (round 2, final record)
- Artifact version: round-2 candidate (round 1 superseded per its own
  verification-table-binding and stale-prose defects, fixed to produce
  round 2)
- Commit/candidate SHA: product/CI-config code frozen at `861f401` (the
  `ISSUE-0014` CI step-order fix); milestone record's reviewed candidates
  are round 1 `61d76c57ff2d70fe95988497e6eaafd0b1649a41` and round 2
  `e9f574da95679b7701db52042d91429068d54206` (both metadata-only since the
  product/CI-config freeze — no product or CI file differs from `861f401`
  in either)
- Target: `Bartoli-co-uk/CAreview`, branch `main`
- Scope: acceptance of the M3 milestone — all three delivered issues
  (`ISSUE-0012`: React/TypeScript dashboard; `ISSUE-0013`: scoped
  device-code session abandonment; `ISSUE-0014`: frontend build/tests
  wired into CI), covering the dashboard replacing the vanilla-JS UI,
  the scoped-abandon endpoint, and CI now building/testing the frontend
- Exclusions: does not constitute a security certification; does not
  waive the documented residual risks below; does not itself authorize
  any protected action (live tenant sign-in, either mode, remains
  separately gated); does not retroactively supply the pre-implementation
  brief/roadmap cycle `ISSUE-0012`/`ISSUE-0013` skipped under
  `DECISION-024`'s direct override — this acceptance is of the delivered,
  reviewed, merged work, not a claim that the skipped planning gate was
  supplied after the fact
- Expiry/review date: N/A for the milestone itself; the live-sign-in
  follow-up (both modes) has no fixed date, unchanged from M1/M2

## Decision text

> "Accept and approve M3" — in response to option 1 of three presented in
> `project/milestones/M3.md`'s "Human decision required" section: accept
> M3 with round 2's residual `ROADMAP.md`/`CURRENT.md` staleness and the
> exhausted general-remediation-cycle finding treated as ordinary
> record-hygiene follow-up, not a blocker requiring a third review round —
> the same disposition `DECISION-012` (M1) and `DECISION-023` (M2) each
> gave their own milestone gates at the same kind of finding.

## Evidence shown to the human

- `project/milestones/M3.md` (full traceability, verification evidence,
  two-round four-review table, findings/remediation history, residual
  risks, and the three options presented for this decision)
- Round 1 (candidate `61d76c57ff2d…`): `project/reviews/milestones/M3-61d76c57ff2d-claude-general.md`
  (`CHANGES_REQUIRED`, 4 findings, all governance-record staleness);
  `-codex-general.json` (`BLOCKED`, 1 finding, verification-table binding);
  `-claude-security.md` (`PASS_WITH_NOTES`, zero critical/high); `-codex-security.json`
  (`INCONCLUSIVE`, sandbox execution-evidence class plus the same
  verification-table finding)
- Round 2 (candidate `e9f574da9567…`, the round-1 repair):
  `project/reviews/milestones/M3-e9f574da9567-claude-general.md`
  (`CHANGES_REQUIRED`, 1 finding — a stale `ROADMAP.md` line missed by the
  round-1 repair); `-codex-general.json` (`BLOCKED`, 1 finding — same line
  plus five un-synchronized `CURRENT.md` rows); `-claude-security.md`
  (`PASS_WITH_NOTES`, unchanged from round 1); `-codex-security.json`
  (`INCONCLUSIVE`, recurring sandbox execution-evidence class)
- **Zero critical or high findings, and zero product-code correctness or
  security defects, across both rounds and all eight reports.**

## Consequence

- Permitted next action: `project/milestones/M3.md` moves to `COMPLETE`;
  `ROADMAP.md`'s M3 milestone-table row moves from "ISSUES DELIVERED —
  milestone gate not run" to `COMPLETE`; the residual staleness round 2
  found (`ROADMAP.md`'s Delivery-status line, and `CURRENT.md`'s Open
  blockers/Tracked follow-up/Next required actor/Next permitted
  action/Actions not yet permitted rows) is corrected in this same
  commit, per the `DECISION-023` precedent, rather than treated as a
  fresh milestone candidate. `docs/security-boundaries.md`'s residuals
  (`RISK-009`, `RISK-011`) remain tracked exactly as already accepted
  (`DECISION-028`, `DECISION-027`) — this decision does not reopen or
  re-decide them.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: standard `git revert` of any single
  future commit if a defect surfaces; the M3 acceptance itself changes no
  running code and needs no rollback path of its own.

## Notes

Both milestone-review rounds converged on the same lesson M1 and M2 each
taught separately: this project's governance-record discipline (keeping
`ROADMAP.md`/`CURRENT.md`/the milestone record itself in sync with fast-
moving implementation work) is harder to get right than the product code
it's tracking. Every one of the roughly ten findings across M1, M2, and
M3's milestone gates has been this same class of defect; none has ever
been a product-code correctness or security defect. That pattern is
itself informative for how much weight future milestone gates should put
on record-freshness checks versus code review — worth the human's own
consideration, not a conclusion this record presumes to draw.
