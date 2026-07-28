# Human decision: Accept ISSUE-0013's residual risk and merge

**Decision ID:** `DECISION-027`
**Type:** `issue advance` / risk acceptance
**Decision:** `APPROVE` / `ACCEPT PERMITTED RISK`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-28`

## Exact binding

- Artifact/action: merge `ai/ISSUE-0013-scoped-device-code-abandon` into `main`
- Artifact version: `ISSUE-0013` round-2 (final attempted) candidate
- Commit/candidate SHA: `8858858a2090aa72d8d0b14a6de64a17a447c120` (product
  candidate reviewed by Codex); `9169eb6` and `80156d3` (metadata-only
  follow-ups recording the round-2 outcome and README updates, not
  themselves re-reviewed)
- Target: `Bartoli-co-uk/CAreview` repository, `main` branch
- Scope: all of `ISSUE-0013` (scoped device-code session abandonment) and
  its own review/status/decision records
- Exclusions: does not authorize any further code change to the
  abandon/retry mechanism without a new issue; does not open or approve an
  M3 milestone; does not retroactively change the severity classification
  Codex assigned the underlying finding

## Risk being accepted

- **Finding:** round-2 Codex issue review F-001 (high, blocking):
  `abandonWithRetry()` retries a failed `/api/auth/abandon` delivery every
  3 seconds for ~16 minutes, but if every attempt in that window fails, it
  gives up silently — there is no observable "cleanup still pending" state,
  and the abandoned device-code attempt's token could remain installed
  server-side for the remainder of its own natural session lifetime if
  that lifetime outlasts the retry window.
- **Preconditions for actual impact:** all of the following must hold
  simultaneously: (1) a device-code sign-in was actually approved by the
  user in the external Microsoft flow, (2) the CAreview browser tab had
  separately abandoned that attempt (e.g. clicked "view sample data")
  before the poll resolved, and (3) the loopback `POST /api/auth/abandon`
  call fails on every retry for the full ~16-minute window — which,
  because this call never leaves the local machine, would require the
  CAreview server process itself to be in a persistently broken state
  (in which case its in-memory token state is equally fragile and not
  reliably exploitable either) or the browser tab to close before any
  attempt succeeds.
- **Potential impact if it occurs:** a Conditional Access read-only Graph
  token remains valid in the local CAreview process's memory, reachable
  only from the same machine via the loopback API, for up to the token's
  own remaining lifetime (Microsoft-issued, typically on the order of an
  hour) or until the process restarts. This is strictly narrower than the
  project's already-accepted `RISK-002` (no authentication beyond loopback
  binding) — it does not grant a new capability, only extends how long an
  already-accepted class of exposure can persist in an already-narrow
  scenario.

## Decision text

> "Accept the documented residual and merge ISSUE-0013"

## Evidence shown to the human

- `project/issues/ISSUE-0013.md`'s "Human decision required" section
  (three options presented; option 1 selected)
- `project/reviews/issues/ISSUE-0013-8858858a2090-codex.json` (round 2,
  final permitted repair round, `BLOCKED` on the finding described above)
- `project/reviews/issues/ISSUE-0013-8c273e194622-codex.json` (round 1),
  `project/reviews/issues/ISSUE-0013-d3866851c7d6-codex.json` (round 0) —
  full history showing two real defects already fixed (client-side race,
  fire-and-forget delivery) before this final, narrower residual
- `project/handoffs/ISSUE-0013-handoff.md` (rounds 0-2) — real command
  output for all required checks at every round
- `docs/security-boundaries.md`'s "Scoped device-code abandonment" bullet
  — the accepted-residual rationale in its permanent form

## Consequence

- Permitted next action: fast-forward merge
  `ai/ISSUE-0013-scoped-device-code-abandon` into `main`; mark
  `ISSUE-0013` `COMPLETE (merged, with accepted residual)` in
  `project/issues/ISSUE-0013.md`; update `project/status/CURRENT.md`; push
  the resulting `main` to GitHub.
- Invalidated approvals/reviews: none. This decision does not overturn or
  mark the round-2 finding resolved — it accepts the residual as
  documented and authorizes proceeding with it open.
- Rollback/recovery expectation: standard `git revert` of the merge (a
  fast-forward, so reverting means resetting `main` back to its pre-merge
  tip) if a defect surfaces post-merge; no destructive history rewrite.
- Reopening triggers: the affected scope, preconditions, or exposure
  described above changes; a future finding shows the loopback delivery
  failure mode is more likely than assessed here; or the human later
  decides to open a follow-up issue to build an observable cleanup-pending
  state (option 2 from `ISSUE-0013.md`, not chosen now but not foreclosed).

## Notes

This is the second issue in this project accepted with an open, non-`PASS`
Codex outcome rather than a clean result (see `DECISION-025` for
`ISSUE-0012`). In both cases the residual is a narrow, low-likelihood
timing/reliability gap in a defense-in-depth mechanism, not a defect in
the primary security boundary (loopback binding, Host/Origin checks,
in-memory-only token storage), and in both cases the human reviewed the
exact finding and its evidence before deciding to proceed.
