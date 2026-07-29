# Human decision: Accept RISK-009 (npm build-time supply chain) as residual

**Decision ID:** `DECISION-028`
**Type:** `roadmap approval` / risk acceptance
**Decision:** `ACCEPT PERMITTED RISK`
**Human approver:** `Jay, repository owner`
**Decided at:** `2026-07-29`

## Exact binding

- Artifact/action: `RISK-009` as recorded in `ROADMAP.md` v5 and
  `project/milestones/M3.md`
- Artifact version: roadmap v5 candidate `441b4da0d3ba0d9d13dcf0d710bdae5a1c0685ab`
  plus its round-1 repair commit `a276e83` (neither yet fully approved as a
  roadmap version — this decision accepts the risk itself, not the roadmap)
- Commit/candidate SHA: `a276e83` (current `main` tip at decision time)
- Target: `Bartoli-co-uk/CAreview` repository, `frontend/` build toolchain
  (`frontend/package-lock.json` and its transitive dependency graph)
- Scope: the npm build-time supply-chain exposure as currently documented —
  no lockfile pinning/auditing beyond what is committed today, no `npm audit`
  step anywhere, CI does not yet build the frontend at all
- Exclusions: does not accept any *future* widening of this risk (e.g. adding
  new dependencies, loosening the lockfile, or fetching build-time content
  from a network source); does not substitute for `ISSUE-0014` or any
  dependency-audit work; does not itself approve roadmap v5 as a whole —
  `F-004`'s resolution unblocks that gate, it is not the gate itself

## Risk being accepted

- **Finding:** `RISK-009` (`ROADMAP.md`, `project/milestones/M3.md`) — the
  React frontend build introduced a transitive npm dependency graph that the
  previously dependency-free, stdlib-only backend never had. A compromised or
  typosquatted transitive package executes with the developer's own
  privileges at `npm install`/`npm run build` time and could write arbitrary
  content into the `web/index.js` the server then serves. Nothing pins or
  audits transitive versions beyond the committed lockfile, `npm audit` runs
  nowhere, and CI does not build the frontend at all yet (`ISSUE-0014`,
  `PLANNED`, not started).
- **Existing partial mitigations, not chosen for this purpose:** the lockfile
  is committed, so builds are reproducible and a dependency change is visible
  in a reviewable diff; the served page keeps `default-src 'self'` and loads
  no external asset at runtime, so any compromise must arrive through the
  build rather than at runtime; no dependency reaches the Python backend,
  which still handles every token and secret.
- **Potential impact if it occurs:** a malicious build-time dependency could
  inject arbitrary JavaScript into the served dashboard, executing in the
  browser context of whoever opens `http://127.0.0.1:8765` — the same
  loopback-only, single-user exposure class the project already accepts
  elsewhere (`RISK-002`), not a new capability beyond that boundary, but a new
  *path* to reach it (a supply-chain compromise rather than a local-process
  compromise).

## Decision text

> "Accept as-is for now" — for a low-traffic, single-user personal tool, with
> the committed lockfile keeping dependency changes visible in diffs and no
> external asset loaded at runtime; revisit if the project's scope or user
> base grows.

## Evidence shown to the human

- `ROADMAP.md` `RISK-009` entry
- `project/milestones/M3.md` residual-risks table and "Open questions for the
  human" section
- `project/reviews/plans/ROADMAP-441b4da0d3ba-codex.json` finding `F-004`,
  which required this exact decision before roadmap v5 could be approved

## Consequence

- Permitted next action: `F-004` from the round-1 plan review is resolved.
  A further fresh Codex plan review of roadmap v5 (round 2, within the
  two-round planning-repair limit) may now run against a candidate that
  records this acceptance; if it clears, the human still separately approves
  the exact roadmap v5 version and commit before it becomes the governing
  artifact.
- Invalidated approvals/reviews: none. This does not itself approve roadmap
  v5 or open/authorize `ISSUE-0014`.
- Rollback/recovery expectation: if this acceptance is revisited (e.g. after
  `ISSUE-0014` adds `npm audit` to CI), record a new decision rather than
  editing this one.

## Notes

This narrows `RISK-009` from "undecided" to "accepted as documented," on the
same low-traffic/single-user reasoning the project has already applied to
`RISK-002`. It does not reduce the actual mitigations in place — `ISSUE-0014`
remains the recommended next step for tightening this boundary (running the
build/tests in CI at minimum), and an `npm audit` step remains available as
future work without needing to reopen this decision.
