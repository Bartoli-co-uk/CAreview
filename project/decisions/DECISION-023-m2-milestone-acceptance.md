# Human decision: Accept M2 milestone (dual-mode authentication)

**Decision ID:** `DECISION-023`
**Type:** `milestone acceptance`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-28`

## Exact binding

- Artifact/action: `project/milestones/M2.md` (round 1, final record)
- Artifact version: round-1 candidate (round 0 superseded per its own
  evidence-binding defect, fixed to produce round 1)
- Commit/candidate SHA: product code frozen at
  `98be0bc562de8f7cf52e3019715bc4cff571ad91` (the `ISSUE-0011` closeout
  commit); milestone record's reviewed candidate is
  `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` (metadata-only since the
  product freeze — verified byte-identical product files across both by
  both Claude general and Codex general independently)
- Target: `Bartoli-co-uk/CAreview`, branch `main`
- Scope: acceptance of the M2 milestone — all five dual-mode-auth issues
  (`ISSUE-0007`..`ISSUE-0011`), covering delegated-scope trim, app-only
  token acquisition, the `/api/auth/app` endpoint, the sign-in UI toggle,
  and M2 documentation finalization.
- Exclusions: does not constitute a security certification; does not
  waive the documented residual risks below; does not itself authorize
  any protected action (live tenant sign-in, either mode, remains
  separately gated).
- Expiry/review date: N/A for the milestone itself; the live-sign-in
  follow-up (both modes) has no fixed date, to be revisited when the
  human's access restrictions permit.

## Decision text

> "Approve M2 now" — in response to option 1 of three presented in
> `project/milestones/M2.md`'s "Human decision" section: accept M2 with
> the `ROADMAP.md`/`CURRENT.md` staleness and the exhausted
> general-remediation-cycle finding treated as ordinary record-hygiene
> follow-up, not a blocker requiring a new milestone candidate — the same
> disposition `DECISION-012` gave M1's sandbox-only `BLOCKED` outcomes.

## Evidence shown to the human

- `project/milestones/M2.md` (full traceability, verification evidence,
  four-review table, findings/remediation history, residual risks, and
  the three options presented for this decision)
- `project/reviews/milestones/M2-9c01749b221d-claude-general.md`
  (`CHANGES_REQUIRED` — 3 blocking findings, all governance-record
  defects, zero product defects)
- `project/reviews/milestones/M2-9c01749b221d-codex-general.json`
  (`BLOCKED` — F-001 stale `CURRENT.md`; F-002 general-remediation cycle
  already consumed, explicitly directing a human decision)
- `project/reviews/milestones/M2-9c01749b221d-claude-security.md`
  (`PASS_WITH_NOTES` — zero critical/high; 7 low/info findings, most
  notably SEC-001 and SEC-003, tracked as follow-up below)
- `project/reviews/milestones/M2-9c01749b221d-codex-security.json`
  (`BLOCKED` — sole finding is the sandbox execution-evidence residual,
  no product finding)
- Superseded round-0 evidence retained for the record:
  `project/reviews/milestones/M2-b55bf97ff4a4-codex-general.json`,
  `project/reviews/milestones/M2-b55bf97ff4a4-claude-general.md`
- Precedent: `DECISION-012` (M1 acceptance despite both Codex reviews
  `BLOCKED` solely on the same sandbox limitation)

## Consequence

- Permitted next action: mark `project/milestones/M2.md` status
  `COMPLETE`; correct `ROADMAP.md`'s residual pre-`DECISION-015`
  "PLANNED (unapproved)" language as the ordinary follow-up this decision
  authorizes (not a new milestone candidate — no re-review required);
  update `project/status/CURRENT.md`; push the resulting `main` to
  GitHub.
- Invalidated approvals/reviews: none. This decision does not reopen or
  invalidate any of the four round-1 reviews.
- Rollback/recovery expectation: N/A (no deployment; local tool;
  documentation-only follow-up commit).

## Follow-up (tracked, not blocking)

- **`ROADMAP.md` stale approval-status language** (Claude general F-001):
  corrected in the same commit that records this decision, per the
  consequence above.
- **Live-tenant sign-in verification, both modes.** Device-code and
  app-only sign-in and Graph fetch have only been exercised against
  mocked transports. This remains a protected action requiring separate
  explicit human approval naming the tenant before it is attempted.
  Owner: Jay (@Jay-cli). No fixed date.
- **SEC-001 (Claude security, low):** `_renew_app_only()` has no failure
  counter/backoff and does not clear the retained secret on a renewal
  failure, so a rotated/revoked app-only secret keeps being replayed to
  Microsoft's token endpoint on every `/api/policies`/`/api/analysis`
  call until an explicit sign-out, even though the UI's visible state
  doesn't communicate that the secret is still held. Owner: Jay
  (@Jay-cli). No fixed date; candidate for a future issue if prioritized.
- **SEC-003 (Claude security, low, risk-candidate):** `/api/auth/app` is
  an unauthenticated (loopback-scoped) credential-validation oracle and a
  session-supersession primitive not explicitly named in the `RISK-002`
  text already accepted by `DECISION-014`. Not accepted as a formal risk
  by this decision; tracked for the human to decide whether it needs its
  own documentation update or mitigation.

## Notes

This is the human's exact milestone-acceptance decision and does not
itself authorize any live-tenant follow-up or the SEC-001/SEC-003
remediation; those remain separately gated/tracked. The general-
remediation cycle exhaustion both round-1 general reviews identified is
resolved by this decision, not overridden — the human, not Claude,
chose to accept M2 with the residuals named above rather than direct
another candidate.
