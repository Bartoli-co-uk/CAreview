# Human decision: Accept M1 milestone (MVP Conditional Access analyzer)

**Decision ID:** `DECISION-012`
**Type:** `milestone acceptance`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T22:35:18Z`

## Exact binding

- Artifact/action: `project/milestones/M1.md` (round 2, final record)
- Artifact version: round-2 remediation candidate
- Commit/candidate SHA: product code frozen at
  `6311a11a48a0a7e51e83a14ca4081d431cb46698`; milestone record finalized at
  `c780b139902bfe477d46e2a403b4a1b62c960604` (metadata-only since the product
  freeze — verified byte-identical product files across both)
- Target: `Bartoli-co-uk/CAreview`, branch `main`
- Scope: acceptance of the M1 milestone — all six MVP issues
  (`ISSUE-0001`..`ISSUE-0006`), covering local server, device-code auth, Graph
  fetch, analyzer/scoring, UI rendering, and documentation/E2E verification.
- Exclusions: does not constitute a security certification; does not waive the
  documented residual risks below; does not itself authorize any protected
  action (live tenant sign-in remains separately gated).
- Expiry/review date: N/A for the milestone itself; the live-sign-in follow-up
  below has no fixed date, to be revisited when the human's access restrictions
  permit.

## Decision text

> "Accept, but flag live-tenant sign-in as a follow-up" — M1 accepted based on:
> zero critical/high findings across all four milestone reviews; one real bug
> (the `validate_repo.py` self-test) caught by a genuinely independent review
> and fixed mid-gate; both Codex `BLOCKED` outcomes resting solely on the
> review sandbox's inability to execute checks, not a product defect. The human
> separately confirmed they currently cannot perform a live-tenant sign-in test
> due to their own access restrictions, and wants that tracked explicitly
> rather than left as a silent gap.

## Evidence shown to the human

- `project/milestones/M1.md` (full traceability, verification evidence,
  four-review table, findings/remediation history, residual risks)
- `project/reviews/milestones/M1-r2-claude-general.md` (`PASS_WITH_NOTES`)
- `project/reviews/milestones/M1-af6d10b22e3f-codex-general.json` (`BLOCKED`, execution-evidence only)
- `project/reviews/milestones/M1-r2-claude-security.md` (`PASS_WITH_NOTES`)
- `project/reviews/milestones/M1-059b0ae82122-codex-security.json` (`BLOCKED`, execution-evidence only)
- `DECISION-011` (the mid-gate validator fix)

## Consequence

- Permitted next action: mark `project/milestones/M1.md` status `COMPLETE`,
  update `project/status/CURRENT.md`, and record the live-tenant sign-in
  verification as an explicit open follow-up (not a blocker, not silent).
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: N/A (no deployment; local tool).

## Follow-up (tracked, not blocking)

**Live-tenant sign-in verification.** The device-code sign-in and Graph fetch
flow have only been exercised against mocked transports (`tests/test_auth.py`,
`tests/test_graph.py`). Assumption A1 (whether the Microsoft Graph PowerShell
first-party public client can obtain `Policy.Read.All` via device code in a
real tenant) remains unverified. This is a live-tenant sign-in — a protected
action per `AGENTS.md`, requiring separate explicit human approval naming the
tenant before it is attempted. Owner: Jay (@Jay-cli). No fixed date; revisit
when access restrictions permit. If it fails, the documented fallback is a
one-time Entra app registration (currently a non-goal, deferred per `RISK-001`).

## Notes

This is the human's exact milestone-acceptance decision and does not itself
authorize the live-tenant follow-up; that remains separately gated.
