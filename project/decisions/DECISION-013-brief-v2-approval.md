# Human decision: Approve project brief v2 (opt-in app-only auth, secret only)

**Decision ID:** `DECISION-013`
**Type:** `brief approval`
**Decision:** `APPROVE`
**Human approver:** `Jay (jay@bartoli.co.uk), repository owner`
**Decided at:** `2026-07-27`

## Exact binding

- Artifact/action: `project/brief/PROJECT_BRIEF.md` v2 amendment
- Artifact version: `2`
- Commit/candidate SHA: `9ccf835` (full: see `git log --format=%H -1 9ccf835`
  in this branch history)
- Target: `N/A (planning artifact)`
- Scope: approves the brief v2 text as written — lifting the v1 non-goal on
  app registration / non-device-code authentication to add an **opt-in**
  second sign-in mode (OAuth 2.0 client-credentials, **client secret only**)
  beside the unchanged device-code default; trimming delegated `SCOPES` to
  `Policy.Read.All`; certificate-based client assertions recorded as a
  deferred future enhancement, not implemented now.
- Exclusions: does not itself resolve brief v2 Questions 3, 5, and 6 (secret
  retention model, `RISK-002` re-acceptance, client-side tenant validation) —
  those are recorded separately in `DECISION-014`. Does not authorize
  implementation; roadmap v4 must still be drafted, reviewed, and separately
  approved before any M2 issue starts. Does not authorize any live sign-in
  against a real tenant, in either mode.

## Decision text

> "Yes, approve this exact brief v2"

## Evidence shown to the human

- `project/brief/PROJECT_BRIEF.md` (v2 draft, this commit).
- Prior related draft/decision history on `origin/claude/graph-auth-without-cli-8om0zw`
  (brief v2 at `98feea6`, `DECISION-013`/`DECISION-014` there), which was
  explicitly reverted at the human's request before this fresh approval; this
  decision is independent of that earlier, reverted one.

## Consequence

- Permitted next action: draft `ROADMAP.md` v4 (milestone M2, `ISSUE-0007`
  through `ISSUE-0011`) against this approved brief v2.
- Invalidated approvals/reviews: none (v1/`DECISION-001`, v3
  roadmap/`DECISION-003`, and all M1 decisions remain valid and untouched by
  this amendment).
- Rollback/recovery expectation: N/A — no product code exists for this mode
  yet.

## Notes

This is a fresh approval, not a resurrection of the reverted `DECISION-013`
that existed briefly on `claude/graph-auth-without-cli-8om0zw` before the
human asked to cancel and reverse that day's work. The content is similar by
design (the prior analysis was sound) but this decision record, its bound
commit SHA, and the brief text itself are new. Certificate-based auth remains
explicitly out of scope; adding it later requires its own brief amendment and
an explicit decision to accept a third-party dependency (e.g. `cryptography`),
since it cannot be implemented within the stdlib-only constraint.
