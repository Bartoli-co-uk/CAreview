# Human decision: App-only secret retention model, tenant validation, and RISK-002 acceptance

**Decision ID:** `DECISION-014`
**Type:** `other (brief clarification / risk acceptance)`
**Decision:** `ACCEPT PERMITTED RISK`
**Human approver:** `Jay (jay@bartoli.co.uk), repository owner`
**Decided at:** `2026-07-27`

## Exact binding

- Artifact/action: `project/brief/PROJECT_BRIEF.md` v2 Questions 3, 5, and 6
  (local-server exposure / `RISK-002` given a live client secret; client-side
  tenant validation for app-only mode; secret retention and renewal model).
- Artifact version: brief v2 at commit `9ccf835`, approved by `DECISION-013`.
- Target: `N/A (planning artifact)`.
- Scope:
  1. **Secret retention (Q6):** the client secret is retained in server
     process memory for the app-only session's lifetime and used to silently
     mint a fresh app-only token on expiry, with no re-entry required — the
     same usability the device-code path lacks (it has no refresh token,
     `DECISION-004`).
  2. **`RISK-002` as widened (Q3):** accepted as widened by app-only mode. No
     loopback PIN/token gate is required as a prerequisite to `ISSUE-0008`.
  3. **Tenant validation (Q5):** CAreview validates the tenant value
     client-side (rejecting `organizations`/`common`/`consumers`) in addition
     to the authoritative server-side check, for immediate local feedback.
- Exclusions: does not authorize implementation — `ISSUE-0008` remains
  blocked on drafting, Codex plan review, and human approval of `ROADMAP.md`
  v4. Does not authorize any live sign-in against a real tenant with a real
  secret, in either mode — that remains a separate protected action.

## Decision text

> On secret retention: "Retain for session, silent renewal" — no hourly
> re-entry; the secret stays in memory for the session and is used to
> silently renew the token.
>
> On `RISK-002` as widened: "Accept as widened" — single-user, local-only
> tool; no additional local-auth gate added.
>
> On tenant validation: "Yes, validate client-side too (Recommended)" — in
> addition to the authoritative server-side check.

## Evidence shown to the human

- `project/brief/PROJECT_BRIEF.md` v2 (this commit), Questions 3, 5, 6 and
  the "Data and security" section describing the widened blast radius of a
  retained application secret versus a delegated user token.
- `project/status/CURRENT.md` at the time of this decision (M1 complete,
  no open blockers).

## Consequence

- Permitted next action: `ROADMAP.md` v4 may specify session-lifetime secret
  retention with silent renewal, `RISK-002` re-accepted on that basis, and
  client-side tenant-value rejection mirroring the server, as the M2
  architecture. `ISSUE-0008`'s acceptance criteria are written against this
  retention/renewal model, not per-request discard.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: N/A — no product code exists for this mode
  yet.

## Notes

A secret retained for a whole local session is exposed for materially longer
than one retained only long enough to make a single token request. The
owner's choice trades that longer in-memory retention window for removing the
hourly re-entry friction — a reasonable choice for a genuinely single-user
local tool, accepted as such. This does not change the absolute prohibition
on writing the secret to disk, logs, or any tracked file, which remains a
hard non-goal regardless of retention lifetime.

`RISK-006` (over-broad app-only token, since `.default` returns whatever the
user's app already holds) and `RISK-008` (secret leaking into a test,
fixture, or review report) are unaffected by this decision and remain
separately tracked in `ROADMAP.md` v4's risk table.

This decision is independent of the similarly-numbered, but reverted,
`DECISION-014` that briefly existed on `origin/claude/graph-auth-without-cli-8om0zw`
before the human asked to cancel that day's work; the answers happen to
match because the underlying reasoning holds, not because this record
resurrects that one.
