# Claude security review: milestone M3 — React/TypeScript dashboard UI (round 2)

**Outcome:** `PASS_WITH_NOTES`
**Reviewer role:** `Milestone security reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-sonnet-5 (Claude Code harness)`
**Fresh session/task ID:** `same top-level session; conducted as an independent read-only review task per the milestone-security prompt, with the round-2 Codex reports (launched moments earlier) deliberately not consulted before writing this report`
**Reviewed artifact:** whole repository tree at the round-2 candidate, with emphasis on what changed since round 1
**Reviewed SHA:** `e9f574da95679b7701db52042d91429068d54206`
**Base SHA:** `61d76c57ff2d70fe95988497e6eaafd0b1649a41` (round-1 candidate)
**Created at:** `2026-07-29T19:52:00Z`

This report states only that the review passed within its documented scope
and evidence. It is not a security certification.

## Scope and inputs

- `git diff --name-only 61d76c57 e9f574d`: `ROADMAP.md`, `project/milestones/M3.md`,
  `project/status/CURRENT.md` — all three governance-record-only changes,
  correcting stale prose. **No product source, no CI workflow, no
  dependency manifest changed.** This is the decisive fact for a round-2
  security re-review: nothing in the actual attack surface moved.
- Re-read round 1's security findings
  (`project/reviews/milestones/M3-61d76c57ff2d-claude-security.md`,
  `-codex-security.json`) to confirm the repair didn't touch anything they
  covered.
- Independently re-executed at the reviewed SHA: `python3 -m unittest
  discover -s tests` (188 passed), `cd frontend && npm run build && npm
  test` (build succeeded, 91 passed) — identical to round 1, as expected.
- Peer report withheld for blind review: `yes` — round 2's Codex security
  review was launched before this report and not read before writing it.

## Findings

No new security-relevant finding. Every property verified in round 1's
Claude security review (JSX rendering safety, the scoped-abandon
endpoint's origin/type checks and handle scoping, CI's least-privilege
permissions and SHA-pinned actions, `RISK-009`/`RISK-010`/`RISK-011`
accurately documented as already-accepted residuals) is unchanged, because
no file in scope of that assessment changed between round 1 and round 2.

Round 2's own Claude general review (companion report, this candidate)
found one low-severity governance-record staleness item (`ROADMAP.md`'s
Delivery-status line not yet updated to reflect that round 1 ran). That
finding has no security content — it is a documentation-accuracy issue
about milestone-review bookkeeping, not about the product's security
posture, and is out of this security review's scope to remediate or
re-litigate.

## Residual risks

Unchanged from round 1:

| Risk | Severity | Treatment | Owner/review date |
|---|---|---|---|
| `RISK-009` (npm build-time supply chain) | Medium | Accepted (`DECISION-028`) | Jay / if scope or user base grows |
| `RISK-010` (onboarding regression) | Low | Accepted (`DECISION-029`) | Jay / on build-arrangement change |
| `RISK-011` (abandon-retry fails open after ~16 min) | Low–medium | Accepted (`DECISION-027`) | Jay / if abandon is revisited |

## Evidence gaps

Unchanged from round 1: no real npm-registry `npm audit` run this session;
no live-tenant end-to-end test; no dynamic/fuzz testing beyond the
committed suites.

## Disposition

`PASS_WITH_NOTES`, same as round 1 and for the same reasons — this
round's repair touched only governance-record prose, not anything within
this review's security scope, so re-verifying that scope reproduces round
1's clean result. No critical or high finding in either round.
