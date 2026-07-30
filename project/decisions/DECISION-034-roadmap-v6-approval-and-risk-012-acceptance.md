# Human decision: Approve roadmap v6 (M4) and accept RISK-012

**Decision ID:** `DECISION-034`
**Type:** `roadmap approval` / `risk acceptance`
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-30`

## Exact binding

- Artifact/action: `ROADMAP.md` version `6`, adding milestone `M4` (analyzer
  rule-set expansion) and its four issues (`ISSUE-0015`–`ISSUE-0018`); and
  `RISK-012` (the `phishing-resistant-mfa-admins` rule's custom-authentication-
  strength false-negative limitation)
- Artifact version: roadmap v6, round-2 plan-review candidate
  `68655cc7b1e0a63db3d6b37debf834c126bb60e0` (both permitted planning-repair
  rounds used; all 8 findings across both rounds fixed, zero unresolved
  disagreement)
- Commit/candidate SHA: `68655cc7b1e0a63db3d6b37debf834c126bb60e0`
- Target: `Bartoli-co-uk/CAreview`, branch `main`
- Scope: approval of roadmap v6 itself (adds `M4`, four issues, `RISK-012`)
  and acceptance of `RISK-012` as a residual risk. Does **not** itself start
  any issue — `ISSUE-0015`–`ISSUE-0018` remain `PLANNED` and each needs its
  own separate human start authorization, exactly as every prior issue's
  start has (e.g. `ISSUE-0014`'s own start, `DECISION-030`)
- Exclusions: does not constitute a security certification; does not
  authorize any protected action; does not waive any other documented
  residual risk (`RISK-001`–`RISK-011`, all previously accepted at their own
  gates); does not itself constitute M4 milestone acceptance, which remains
  a separate, later gate once the four issues are implemented and the
  milestone's four-review gate runs
- Expiry/review date: `RISK-012` — at `ISSUE-0018`'s implementation, and any
  M4 milestone security review; N/A for the roadmap approval itself

## Decision text

> "Approve v6 from this record" (option 1 of three presented for the roadmap
> decision) — the same disposition `DECISION-015` (v4) and `DECISION-029`
> (v5) each used at their own two-round revision-budget cap: accept the
> round-2 plan-review record as final rather than authorizing a third round.
>
> "Accept as residual" (option 1 of two presented for `RISK-012`) — the same
> disposition already given to `RISK-009`/`RISK-010`/`RISK-011`: a documented,
> non-security-exposure limitation of the analyzer's own accuracy, not a gap
> in the tool's trust boundary, not worth the added scope of a new Graph call
> to resolve custom authentication-strength definitions in this pass.

## Evidence shown to the human

- `ROADMAP.md` (full v6 draft: M4 milestone entry, four-issue sequence,
  per-issue boundaries, `RISK-012` entry, Planning reconciliation rounds 7–8)
- Round 1 (candidate `bb4952d6e6cc…`): `project/reviews/plans/ROADMAP-bb4952d6e6cc-codex.json`
  (`CHANGES_REQUIRED`, 5 findings) and `-claude-response.md` (all 5 fixed)
- Round 2 (candidate `68655cc7b1e0…`): `project/reviews/plans/ROADMAP-68655cc7b1e0-codex.json`
  (`CHANGES_REQUIRED`, 3 required + 1 advisory) and `-claude-response.md`
  (all 4 fixed)
- `project/issues/ISSUE-0015.md`–`ISSUE-0018.md` (the four draft issues M4 binds)
- **Zero unresolved disagreement across both rounds** — every finding in both
  reports was fixed, not merely accepted as residual.

## Consequence

- Permitted next action: `ROADMAP.md`'s top status moves to `APPROVED`
  (v6, binding this commit); `project/status/CURRENT.md`'s `claudex-state`
  stage moves from `ROADMAP_REVIEW` back to `IMPLEMENTATION` (idle — no
  active issue or milestone yet; `M4` is approved but not started); `RISK-012`
  is marked accepted in `ROADMAP.md`; `ISSUE-0018`'s "Out of scope" section
  is updated from "proposed, pending acceptance" to "accepted residual,
  `DECISION-034`." This is corrected in the same commit that records this
  decision, per the `DECISION-012`/`DECISION-023`/`DECISION-032`/`DECISION-033`
  precedent of fixing residual record staleness in the acceptance commit
  itself rather than treating it as a fresh candidate.
- Starting any of `ISSUE-0015`–`ISSUE-0018` still requires its own separate
  human start authorization — this decision approves the roadmap, not the
  start of implementation.
- Invalidated approvals/reviews: none. Roadmap v5 and everything it governs
  (M1, M2, M3, the project-level review) are unaffected.
- Rollback/recovery expectation: standard `git revert` of any single future
  commit if a defect surfaces; this approval itself changes no running code.

## Notes

The two-round plan-review pattern for v6 mirrors v4 and v5 almost exactly:
Codex found real, substantive issues both rounds (not review-sandbox
limitations this time — F-001 through F-005 in round 1 and F-001 through
F-003 in round 2 were all genuine specification gaps, since this is a plan
review of not-yet-implemented work rather than a milestone review of
completed code), every one was fixed, and the human approved directly from
the round-2 record rather than spending a third round chasing a fully clean
report — consistent with how this project has always closed out its
revision-round budget.
