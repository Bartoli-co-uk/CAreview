# Human decision: Approve project brief v2 amendment (opt-in app-only auth)

**Decision ID:** `DECISION-013`
**Type:** `brief approval`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli, jay@bartoli.co.uk), repository owner`
**Decided at:** `2026-07-27` (exact time not captured; chat-session decision)

## Exact binding

- Artifact/action: `project/brief/PROJECT_BRIEF.md`
- Artifact version: `2`
- Commit/candidate SHA: `98feea68b840bc2c92eda1cd46af8217555daeb5`
- Target: `N/A (planning artifact)`
- Scope: Approval of the exact v2 amendment above — adding an opt-in
  client-credentials (application/app-only) sign-in mode alongside the
  unchanged default device-code flow, and trimming the delegated `SCOPES`
  request to `Policy.Read.All`. Authorizes roadmap drafting only.
- Exclusions: Does not authorize implementation, protected actions, or
  roadmap approval. Does not itself resolve brief v2's open Questions 3, 5,
  and 6 (loopback auth gate given widened RISK-002; tenant-value validation
  for app-only mode; acceptability of hourly secret re-entry) — see Notes.

## Decision text

> "I have commited it go ahead and start the work" (verbatim, chat session,
> following the human merging PR #2 — which carried the v2 brief amendment —
> into `main` at `a676f351ab5428e8c99b2fe48145f8be49cef814`).
>
> Earlier in the same session, on the UI-field-vs-env-var question for the
> app-only secret, the human selected: "UI form field" over an environment
> variable, i.e. tenant ID, client ID, and secret are all entered through the
> sign-in card.

## Evidence shown to the human

- `project/brief/PROJECT_BRIEF.md` v2 amendment at `98feea6`, including the
  "v2 amendment summary", the revised Non-goals, and the new/revised
  "Data and security" section naming the widened RISK-002.
- The human independently created and merged PR #2
  (`https://github.com/Bartoli-co-uk/CAreview/pull/2`) carrying this exact
  commit into `main`, then explicitly directed proceeding with the work.

## Consequence

- Permitted next action: draft a `ROADMAP.md` amendment (new `M2` milestone
  and its issues) covering this brief, then request a fresh Codex plan
  review of that exact roadmap candidate before it can be approved. No
  implementation may begin before that roadmap is approved, per `AGENTS.md`.
- Invalidated approvals/reviews: none. Roadmap v3 / `DECISION-003` remain
  valid for the M1 scope they cover; this decision does not reopen M1.
- Rollback/recovery expectation: N/A (no product code changed by this
  decision).

## Notes

The human's approval was a direct "go ahead and start the work" rather than
point-by-point answers to brief v2's five open sub-questions. Per
`AGENTS.md`, this record must not invent or paraphrase answers the human did
not give. Treating "go ahead" as approval of the brief's stated goals and
non-goals as written is a reasonable reading and is what this decision binds.
It is **not** a substitute for resolving Questions 3, 5, and 6: those affect
issue-level design choices (whether a loopback auth gate is added, how
invalid-tenant input is handled, and whether hourly secret re-entry is
acceptable UX) and will be carried into the roadmap draft with an explicit
default noted, subject to change at roadmap review or issue review.

This decision does not waive the mandatory fresh Codex review of the roadmap
or of each implementation issue. `AGENTS.md` rule 13 is explicit that a
missing or unavailable Codex tool blocks the issue rather than permitting the
gate to be skipped; that constraint is unaffected by this approval.

Approval does not expand beyond the exact binding above.
