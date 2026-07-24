# Human decision: Approve project brief v1

**Decision ID:** `DECISION-001`
**Type:** `brief approval`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli, jay@bartoli.co.uk), repository owner`
**Decided at:** `2026-07-24T10:29:45Z`

## Exact binding

- Artifact/action: `project/brief/PROJECT_BRIEF.md`
- Artifact version: `1`
- Commit/candidate SHA: `179a02354aecbafa2c9d5aa34f9c9a5a04bbc79a`
- Target: `N/A (planning artifact)`
- Scope: Approval of the exact brief above; authorizes roadmap drafting only.
- Exclusions: Does not authorize implementation, protected actions, or roadmap approval.
- Expiry/review date: `N/A — a change to the brief requires a fresh approval`

## Decision text

> Brief approval: "Approve as-is".
> Auth risk (brief A1/Q1–Q2): "Proceed public-client, defer fallback" — build on
> the Microsoft Graph PowerShell first-party public client with `organizations`
> authority; if a tenant returns 403 on policy read, add the one-time
> app-registration fallback as a later issue.
> Local exposure (brief A4/Q3): "Localhost only, no extra auth" — bind to
> 127.0.0.1 with no login of its own for the MVP.

(Captured from the owner's answers to the approval questions on 2026-07-24.)

## Evidence shown to the human

- `project/brief/PROJECT_BRIEF.md` v1 at `179a02354aecbafa2c9d5aa34f9c9a5a04bbc79a`
- Summary of assumptions A1–A5 and the four brief questions.

## Consequence

- Permitted next action: a fresh Claude planning task drafts `ROADMAP.md` and the
  dependency-ordered issue records, then requests a Codex plan review.
- Invalidated approvals/reviews: none.
- Rollback/recovery expectation: N/A (no code changed).

## Notes

Two design directives from the owner constrain the roadmap and must be reflected
in it:

1. **Auth:** first-party public client (Graph PowerShell) + device-code +
   `organizations` authority for the MVP; app-registration fallback is a
   deferred, out-of-MVP issue triggered only if the tenant blocks first-party
   device-code (brief assumption A1).
2. **Local API protection:** localhost binding only, no additional local
   authentication in the MVP (brief assumption A4). Residual risk RISK: another
   local process/user could reach the loopback API while a token is in memory —
   accepted for a trusted single-user machine.

Approval does not expand beyond the exact binding above.
