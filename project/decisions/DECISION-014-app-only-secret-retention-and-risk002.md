# Human decision: App-only secret retention model, and RISK-002 re-acceptance

**Decision ID:** `DECISION-014`
**Type:** `other (brief clarification / risk acceptance)`
**Decision:** `ACCEPT PERMITTED RISK`
**Human approver:** `Jay (@Jay-cli, jay@bartoli.co.uk), repository owner`
**Decided at:** `2026-07-27` (exact time not captured; chat-session decision)

## Exact binding

- Artifact/action: `project/brief/PROJECT_BRIEF.md` v2 Question 6 (secret
  retention / re-entry) and Question 3 (local-server exposure given the
  widened `RISK-002`); `ROADMAP.md` v4's `RISK-002` entry and its "Open
  questions that must be answered before `ISSUE-0008` starts" list.
- Artifact version: brief v2 at `98feea68b840bc2c92eda1cd46af8217555daeb5`;
  roadmap v4 draft at `f3bfeb16ec63eddf8b58321267540e56183eae05`.
- Target: `N/A (planning artifact)`.
- Scope: resolves brief v2 Q6 in favor of **session-lifetime secret
  retention** (the client secret is held in server process memory for as
  long as the app-only session is active — the same lifetime the delegated
  flow already gives its access token — rather than being discarded
  immediately after each token request); and re-accepts `RISK-002` as
  widened by app-only mode, on that exact basis.
- Exclusions: does not resolve brief v2 Q5 (tenant-value validation UX),
  which remains open. Does not authorize implementation — `ISSUE-0008` is
  still blocked on the mandatory Codex plan review of roadmap v4 (see
  `project/status/CURRENT.md`). Does not authorize any live sign-in against
  a real tenant, in either mode — that remains a separate protected action.

## Decision text

> On secret retention (brief v2 Q6): "don't have them reenter as it is
> hosted locally so the information can stay there" — the secret is kept in
> memory for the session rather than requiring re-entry on every hourly
> token expiry.
>
> On RISK-002 as widened (brief v2 Q3 / roadmap v4 `RISK-002`): "accept it".

## Evidence shown to the human

- `project/status/CURRENT.md` at the time of this decision, naming brief v2
  Q3/Q5/Q6 as open and `RISK-002` as requiring explicit re-acceptance before
  `ISSUE-0008`.
- `ROADMAP.md` v4's `RISK-002`, `RISK-005`, and `RISK-007` entries, and the
  "Open judgement calls" note from the roadmap-drafting task naming the
  brief's internal tension between "held ... for the session's lifetime"
  and "re-submitting ... each time".

## Consequence

- Permitted next action: `ROADMAP.md` v4 and its risk table are updated to
  record this resolution (session-lifetime retention; `RISK-002` accepted
  on that basis; `RISK-007`'s hourly-re-entry framing superseded — silent
  renewal from the retained secret replaces it, and the exposure window
  described in `RISK-005`/`RISK-002` is now "for the session", not "per
  token request"). `ISSUE-0008`'s acceptance criteria are updated to specify
  silent app-only token renewal from the retained secret, with no
  re-submission required.
- Invalidated approvals/reviews: none (roadmap v4 was never reviewed or
  approved to begin with).
- Rollback/recovery expectation: N/A — no product code exists yet for this
  mode.

## Notes

This decision changes the shape of the risk, not just its acceptance: a
secret retained for a whole local session is exposed for materially longer
than one retained only long enough to make a single token request. The
owner's stated rationale — "it is hosted locally so the information can
stay there" — trades that longer in-memory retention window for removing
the hourly re-entry friction. This is a reasonable choice for a genuinely
single-user local tool and is accepted as such; it does not change the
absolute prohibition on writing the secret to disk, logs, or any tracked
file, which remains a hard non-goal regardless of retention lifetime.

`RISK-006` (over-broad app-only token, since `.default` returns whatever the
user's app already holds) and `RISK-008` (secret leaking into a test,
fixture, or review report) are unaffected by this decision and remain
separately tracked.

Brief v2 Q5 (whether to reject `organizations`/`common`/`consumers`
client-side as well as server-side) remains unanswered and is not resolved
by this decision.

Approval does not expand beyond the exact binding above.
