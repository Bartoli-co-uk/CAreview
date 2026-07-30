# Claude security review: project-level final review — CAreview (round 2)

**Outcome:** `PASS_WITH_NOTES`
**Reviewer role:** `Project security reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-sonnet-5 (Claude Code harness)`
**Fresh session/task ID:** `same top-level session; conducted as an independent read-only review task per the milestone-security prompt (reused for project scope), with the round-2 Codex reports (launched moments earlier) deliberately not consulted before writing this report`
**Candidate SHA:** `917764a46cea280480f4bc40f2fbc7478dde5f9b`
**Tree identity:** clean; product/backend/frontend/CI-config content unchanged since `861f401`
**Threat model:** `docs/security-boundaries.md`, project-wide
**Created at:** `2026-07-29T20:24:00Z`
**Peer conclusion withheld:** `yes`

This report states only that the review passed within its documented scope
and evidence. It is not a security certification.

## Scope and evidence

- `git diff --name-only 5ce5108 917764a`: `README.md`,
  `project/milestones/PROJECT.md` — both governance/disclosure prose, no
  product source, no CI workflow, no dependency manifest.
- Re-read round 1's security findings
  (`project/reviews/milestones/PROJECT-5ce510871a17-claude-security.md`,
  `-codex-security.json`) to confirm the repair resolves both without
  touching anything outside their scope.
- Independently re-executed at the reviewed SHA: `python3 -m unittest
  discover -s tests` (188 passed), `cd frontend && npm run build && npm
  test` (build succeeded, 91 passed) — identical to round 1.
- Peer report withheld for blind review: `yes`.

## Findings

None. **SEC-001** (candidate-binding mismatch) is resolved: `git
rev-parse HEAD` at this candidate exactly matches `PROJECT.md`'s claimed
reviewed SHA for round 1, and this round's own header/table are
internally consistent with `git rev-parse HEAD` at round 2. **SEC-002**
(`README.md` risk-disclosure staleness) is resolved: the table now
accurately reflects `RISK-009`/`RISK-010`/`RISK-011`'s accepted status,
independently confirmed against `ROADMAP.md`'s risk register.

No new security-relevant finding — nothing in this repair's diff touches
any file within this review's actual security scope (auth, secrets,
CSP, dependencies, CI permissions), so re-verification of that scope
reproduces round 1's clean result there.

## Residual risks

Project-wide, unchanged from `M3`'s own acceptance and round 1 of this
review:

| Risk | Severity | Treatment | Owner/review date |
|---|---|---|---|
| `RISK-001` (device-code may be blocked by tenant) | Medium | Accepted `DECISION-001` | Jay |
| `RISK-002` (no local auth beyond loopback; widened for app-only) | Medium–high | Accepted as widened `DECISION-014` | Jay |
| `RISK-004` (heuristic score) | Low | Documented, `DECISION-001` | Jay |
| `RISK-005` (client secret exposed browser-side during entry) | Medium–high | Accepted, roadmap v4 | Jay |
| `RISK-006` (app-only token over-broad) | Medium | Documentation + UI caution only | Jay |
| `RISK-009` (npm build-time supply chain) | Medium | Accepted `DECISION-028` | Jay / if scope or user base grows |
| `RISK-010` (onboarding regression) | Low | Accepted `DECISION-029` | Jay / on build-arrangement change |
| `RISK-011` (abandon-retry fails open) | Low–medium | Accepted `DECISION-027` | Jay / if abandon is revisited |
| SEC-001/SEC-003 (M2, tracked non-blocking) | Low | Tracked, `DECISION-023` | Jay |

## Evidence gaps

Unchanged from round 1: no real npm-registry `npm audit` this session
(`RISK-009`'s already-disclosed gap); no live-tenant end-to-end test
(protected action); no dynamic/fuzz testing beyond committed suites.

## Disposition

`PASS_WITH_NOTES`: both round-1 findings resolved, no critical or high
finding in either round, no new finding this round. This report does not
itself accept or re-accept any residual risk — each was already accepted
by the human at its own respective milestone decision, prior to and
independent of this project-level review.
