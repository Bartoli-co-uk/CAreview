# Human decision: Raised repair budget for small fixes (ISSUE-0003 onward)

**Decision ID:** `DECISION-007`
**Type:** `review-gate policy (repair budget)`
**Decision:** `APPROVE` (standing policy for the M1 build)
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T14:33:54Z`

## Exact binding

- Scope: ISSUE-0003 (finish) and the remaining MVP issues (ISSUE-0004..0006).
- Grant: Claude may apply **small, low-risk, clearly-correct** fixes beyond the
  default two repair rounds — up to about **four repair rounds per issue** — and
  continue, running a fresh Codex review after each, then merge under DECISION-004
  when a review is BLOCKED only on the execution-evidence limitation with no
  substantive finding.
- Still STOP for the human on: any high-severity or security finding not cleanly
  resolved, a design-level or ambiguous finding, a protected action, or an issue
  that is not converging (findings not shrinking round over round).

## Decision text

> Repair-budget question answered "Raise the budget for small fixes".

## Consequence

- Supersedes the default two-round limit for these issues only. The absolute
  intent of the workflow (independent review each round, no downgrading findings)
  is unchanged; only the number of permitted small-fix rounds is raised.

## Notes

Reviews have been converging: the security-critical findings (e.g. ISSUE-0003
token-exfiltration) were resolved early, and later rounds surface progressively
smaller, peripheral fixes. This decision avoids a human round-trip for each such
fix while preserving the stop conditions above.
