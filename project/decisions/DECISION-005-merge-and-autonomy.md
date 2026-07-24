# Human decision: Merge ISSUE-0001 and autonomous cadence to the M1 milestone

**Decision ID:** `DECISION-005`
**Type:** `issue advance / merge + autonomy cadence`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T12:46:57Z`

## Exact binding

- Merge: `ai/ISSUE-0001-server-shell` (reviewed product SHA
  `39cff76bef15e787b1776a965d139671b081d8ac`) into `main`.
- Cadence: authorize Claude to implement, review, and merge the remaining
  MVP issues (ISSUE-0002..0006) autonomously under the DECISION-004 gate policy,
  checking in at the M1 milestone gate.
- Exclusions: does not authorize any protected action. Claude must still STOP for
  the human on: a substantive Codex code/security finding it cannot cleanly
  resolve within two repair rounds; any protected action (notably the live
  device-code sign-in / Graph fetch); material ambiguity; or exhausted loops.

## Decision text

> "Merge it" (ISSUE-0001) and "Autonomous to the M1 milestone".

## Consequence

- ISSUE-0001 is merged and marked COMPLETE.
- Claude proceeds to ISSUE-0002 (device-code auth) and onward, each on its own
  branch with the mandatory Codex review and, per DECISION-004, author out-of-band
  evidence; a review that is BLOCKED only on the execution-evidence limitation
  with no substantive finding is merged under this authorization.
- Claude presents the frozen M1 candidate for the four blind milestone reviews and
  the human's milestone acceptance.

## Notes

Live-tenant authentication and Graph access remain protected actions requiring a
separate, explicit approval naming the tenant (ISSUE-0002/0003); the MVP completes
on mocked evidence with live behaviour as a residual gap the human accepts at M1.
