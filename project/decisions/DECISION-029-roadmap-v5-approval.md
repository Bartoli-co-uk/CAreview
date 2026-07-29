# Human decision: Approve roadmap v5 (M3 — React/TypeScript dashboard UI)

**Decision ID:** `DECISION-029`
**Type:** `roadmap approval`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-29`

## Exact binding

- Artifact/action: `ROADMAP.md` v5 candidate
- Artifact version: `5`
- Commit/candidate SHA: `8ea41ee` (full: see `git log --format=%H -1 8ea41ee`
  in this branch history) — the commit recording the round-2 plan review
- Target: `N/A (planning artifact)`
- Scope: approves roadmap v5 as written — adds milestone `M3` (React/
  TypeScript dashboard UI), its issue sequence retroactively binding
  `ISSUE-0012` and `ISSUE-0013` (both already merged, `DECISION-025`/
  `DECISION-027`), and `ISSUE-0014` (`PLANNED`, CI wiring, not started);
  records `RISK-009` (accepted, `DECISION-028`), `RISK-010`, and `RISK-011`
  (already accepted, `DECISION-027`); states the exact bounds of the
  `DECISION-024` build-step exception. Authorizes `ISSUE-0014` to be
  *approved as a target* under this roadmap; starting it still requires its
  own separate human start decision, per `AGENTS.md`.
- Exclusions: does not itself start `ISSUE-0014` or any other issue. Does not
  constitute the M3 milestone acceptance — that is a separate four-review gate
  (Claude general, Codex general, Claude security, Codex security) against a
  frozen candidate, not yet run, and whether to run it at all remains an open
  question (`project/milestones/M3.md`). Does not retroactively supply the
  brief/roadmap cycle `ISSUE-0012`/`ISSUE-0013` skipped under `DECISION-024`'s
  direct override — this roadmap records that fact rather than curing it.
  Does not authorize any live-tenant action, publication, or other protected
  action.

## Decision text

> "Approve from record, accept both as residuals" — approving roadmap v5 at
> its round-2 reviewed commit, treating the two round-2 findings below as
> accepted residuals rather than blockers, the same disposition
> `DECISION-015` used for roadmap v4 at its own iteration cap.

## Evidence shown to the human

- `ROADMAP.md` at commit `8ea41ee` (this commit).
- Round 1: `project/reviews/plans/ROADMAP-441b4da0d3ba-codex.json`
  (`CHANGES_REQUIRED`, four findings — all repaired, including `RISK-009`'s
  acceptance at `DECISION-028`).
- Round 2: `project/reviews/plans/ROADMAP-9bd2c0f8f6fb-codex.json`
  (`CHANGES_REQUIRED`, two findings, accepted here rather than repaired
  further — see below).
- `project/status/CURRENT.md` at the `ROADMAP_REVIEW` stage, presenting both
  round-2 findings and the three options for proceeding.

## Residuals accepted by this decision

- **F-001** (medium, `project/issues/ISSUE-0014.md`, `ROADMAP.md:312`):
  `ISSUE-0014`'s specified negative-CI fallback (a bare local `npm test` run
  with one test edited to fail) proves Vitest itself can fail; it does not
  prove the *modified GitHub Actions workflow* propagates that failure to a
  red job. This is a gap in a not-yet-started issue's planned verification
  rigor, not a defect in any merged code or currently running check. Accepted
  as a residual on the issue record itself — whoever implements `ISSUE-0014`
  should tighten this to genuine workflow-level proof (a local Actions
  runner, or an equivalent workflow-aware validator) if one becomes available
  in that task's environment, but a documented, honest fallback is acceptable
  to plan against in the meantime.
- **F-002** (medium, `ROADMAP.md:422`/`430`, `project/status/CURRENT.md`):
  `RISK-010` (onboarding regression — fresh clone no longer serves a UI
  without a build) was described inconsistently: one line called it
  "accepted implicitly" by `DECISION-024`, another called it "new and
  undecided." Resolved by this decision: `RISK-010` **is accepted**, on the
  same basis `ROADMAP.md:422` already gave — it is a low-severity,
  documentation-shaped consequence of `DECISION-024` (the build-step
  exception), already mitigated by documentation in three places (`README.md`
  Quick Start, `frontend/README.md`, `CONTRIBUTING.md`), with no security
  impact. `DECISION-024` predates this project's practice of naming risks
  individually, which is why it never cites `RISK-010` by ID; that gap in
  cross-referencing does not change the substance already recorded there.

## Consequence

- Permitted next action: `ISSUE-0014` (wire the frontend build and test suite
  into CI) is now an approved roadmap target and may be **proposed** to start;
  starting it still requires its own separate human decision, per `AGENTS.md`,
  the same way `DECISION-018`/`DECISION-021`/`DECISION-026` separately
  authorized starting `ISSUE-0009`/`ISSUE-0011`/`ISSUE-0013`. Whether to run
  M3's four-review milestone gate, and when, remains open per
  `project/milestones/M3.md`.
- Invalidated approvals/reviews: none. v1–v4 and all prior milestone/issue
  decisions remain valid and untouched. `DECISION-025`, `DECISION-026`,
  `DECISION-027`, `DECISION-028` are unaffected.
- Rollback/recovery expectation: N/A — no new product code exists yet from
  this decision; only planning documents changed.
- `ROADMAP.md`'s header status must be updated from `DRAFT` to `APPROVED` at
  the next commit that touches it, citing this decision and its exact bound
  SHA, consistent with how `DECISION-015` is cited for v4.

## Notes

The v5 planning loop used both `AGENTS.md`-permitted revision rounds (round 1:
four findings, all repaired; round 2: two findings, accepted here). Round 2's
two findings are both about documentation/verification precision in an
unstarted issue and a risk-register wording gap — neither is a defect in
running code, a security finding, or a claim that something works when it
does not. The human approved directly from this record rather than
authorizing a third repair round, mirroring `DECISION-015`'s handling of
roadmap v4 at its own iteration cap.
