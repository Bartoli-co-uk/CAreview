# Human decision: Adopt a React/Vite frontend, accepting a Node.js build-step exception

**Decision ID:** `DECISION-024`
**Type:** `other` (constraint exception — Node.js/npm build toolchain for the UI only)
**Decision:** `APPROVE`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-28`

## Exact binding

- Artifact/action: replace the vanilla-JS/HTML/CSS UI in `web/` with a React +
  TypeScript dashboard built by Vite, sourced in `frontend/`, compiled into
  `web/index.html`/`index.js`/`index.css` via `npm run build`.
- Artifact version: initial introduction (this issue).
- Commit/candidate SHA: recorded at the handoff for this issue (see
  `project/status/CURRENT.md` at close of this work).
- Target: `Bartoli-co-uk/CAreview`, branch `ai/react-dashboard-frontend`.
- Scope: permits a Node.js/npm build toolchain **for the frontend only**
  (`frontend/`, building into `web/`). Does not permit any third-party
  runtime dependency in the Python backend (`server.py`, `auth.py`,
  `graph.py`, `analyzer.py`, `rules.py`), which remains stdlib-only. Does not
  authorize any other constraint relaxation (persistence, hosting beyond
  loopback, CSP relaxation, new Microsoft Graph scopes).
- Exclusions: does not itself authorize CI changes (the two new `npm`
  commands are not yet wired into `.github/workflows/validate.yml` — tracked
  as follow-up below); does not waive the normal issue/review workflow for
  future changes to `frontend/`.
- Expiry/review date: N/A — durable constraint exception, reviewable like any
  other roadmap constraint.

## Decision text

> Requested a dashboard rebuild of CAreview modeled on a reviewed mockup
> ("AccessGuard"), and, when asked to choose a technical approach, selected
> **"Modern framework build (React/Vite, npm)"** over the stdlib-compatible
> vanilla-JS alternative — explicitly accepting that this "requires relaxing
> the CSP... adding a Node build step, and goes against the project's stated
> 'no build step by default' design goal." Separately, when asked how to
> reconcile this with `AGENTS.md`'s requirement that implementation wait on an
> approved brief/roadmap and a Codex review, selected **"Direct override —
> build it now, record the decision after,"** described as: "Treat your
> instruction in this chat as the explicit human approval AGENTS.md allows to
> take priority. I'll implement directly, then write up a DECISION-0NN entry
> and update ROADMAP.md/README.md afterward to keep the repo's records
> honest — skipping the formal Codex pre-review gate for this piece of
> work."

## Evidence shown to the human

- A comparison of the vanilla-JS/no-build approach against React/Vite,
  including the specific CSP/build-step tradeoffs, presented via the
  assistant's plan-mode analysis before this decision was made.
- The exact `AGENTS.md`/`ROADMAP.md`/`project/intake/PROJECT_DESCRIPTION.md`
  constraint language this decision creates an exception to, quoted back to
  the human before the override was chosen.

## Consequence

- Permitted next action: implement the React/Vite frontend under this
  exception; correct `ROADMAP.md`'s stdlib-only/no-build-step constraint
  language and `README.md`'s "zero build by default" claims to reflect this
  exception (done in the same change as this decision); update
  `project/status/CURRENT.md` accordingly.
- Invalidated approvals/reviews: none — no prior brief/roadmap/Codex review
  existed to invalidate; this decision explicitly substitutes for the
  pre-implementation Codex review `AGENTS.md` would otherwise require.
- Rollback/recovery expectation: the previous vanilla UI remains available in
  Git history (tag or commit prior to this change) if this exception is
  later revoked.

## Follow-up (tracked, not blocking)

- **CI does not yet run the frontend build or its test suite.**
  `.github/workflows/validate.yml` still only runs the three Python commands.
  Owner: Jay. No fixed date.
- **No Codex pre-implementation review was performed for this issue**, per
  the direct-override decision above. A future Codex review of this diff
  remains available if the human later wants one; it was not required to
  proceed.
- **`web/index.html`/`index.js`/`index.css` are now generated, gitignored
  build output**, not committed source — a change from the project's
  previous "clone and run" experience. `README.md`'s Quick Start now
  documents the required `npm install && npm run build` step.

## Notes

This decision narrowly authorizes a Node.js/npm build toolchain for the UI
alone. It does not reopen or relax any other recorded constraint (backend
stdlib-only, no persistence, loopback-only, CSP `default-src 'self'`), all of
which remain enforced in the new frontend exactly as before.
