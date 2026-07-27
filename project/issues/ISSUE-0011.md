# ISSUE-0011: M2 documentation finalization and dual-mode walkthrough

**Status:** `REVIEWING`
**Milestone:** `M2`
**Approved roadmap:** `ROADMAP.md` version `4` at `9e5ba6d2f6c2b7f7efa81dcfc415e1f787aaa458` (approved by `DECISION-015`)
**Dependencies:** `ISSUE-0007..0010` (all COMPLETE)
**Branch:** `ai/ISSUE-0011-m2-docs`
**Starting SHA:** `4f35275d004265ee152348e7e3d1f7b9f6a62cc6`
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA

## Objective

Bring `README.md` and `docs/security-boundaries.md` up to date with the
complete M2 dual-mode (device-code + app-only) implementation: document
both modes, the exact app-only prerequisite, the trust-boundary delta, and
a walkthrough for each mode with live steps clearly marked as the reader's
own protected action. This is a documentation-only issue — no product
source changes.

## In scope

- `README.md` — dual-mode description, a new "App-only mode (advanced)"
  section (prerequisite, secret lifecycle, rotation/revocation,
  certificate-deferral note), a new "End-to-end walkthrough" section for
  both modes, corrected stale test counts, and updated Security model /
  Known limitations sections.
- `docs/security-boundaries.md` — the app-only trust-boundary delta,
  widened `RISK-002`, the `RISK-006` residual, and the certificate
  deferral, added to "CAreview application boundaries".
- `project/` records for this issue.

## Out of scope

- Any product source change (`server.py`, `auth.py`, `graph.py`, `web/`,
  `tests/`) — a source change here would reopen this as an implementation
  issue per the roadmap's allowed-paths table.
- Live tenant sign-in (protected action; the reader performs it
  themselves per the walkthrough, not this Claude task).

## Allowed paths

- `README.md`, `docs/security-boundaries.md`, `project/` records

## Acceptance criteria

1. README documents both auth modes.
2. README states the exact app-only prerequisite: a user-owned app
   registration with **application** `Policy.Read.All` already consented.
3. README states CAreview never creates an app registration on the
   user's behalf.
4. README states certificate-based auth is unsupported in this release
   and recorded as a deferred future enhancement (would need its own
   dependency-approval decision, e.g. `cryptography`).
5. README states the client secret is session-only with silent renewal.
6. README documents how to rotate/revoke the secret.
7. `docs/security-boundaries.md` records the trust-boundary delta and the
   widened `RISK-002`.
8. A documented end-to-end walkthrough exists for each mode, with the
   live steps marked as protected actions the reader performs themselves.
9. No live run is required to complete this issue.
10. `unittest`, `py_compile`, `validate_repo.py` pass from a clean
    checkout.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | all pass (no source change, so no count change) |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed (includes Markdown link/anchor validation) |
| Documentation walkthrough (non-live) | Started the real server and exercised every pre-live-step path documented in both walkthroughs (`/api/health`, the page's mode-toggle elements, and the sample-analysis path) | matches the documented steps |

## Documentation

This issue *is* the documentation change: `README.md` and
`docs/security-boundaries.md`.

## Security and privacy impact

- Threat-model delta: none — this issue documents the trust-boundary
  delta and residual risks (`RISK-002` widened, `RISK-005`, `RISK-006`)
  that `ISSUE-0008`/`ISSUE-0009`/`ISSUE-0010` already introduced and that
  `DECISION-014` already accepted; it does not introduce a new one.
- Data/secret impact: none — no product code touched, no secret handling
  changed.
- Dependency/supply-chain impact: none.
- Protected actions: none. No live tenant sign-in performed; the
  documentation checks used the real server with the sample-data path and
  static page inspection only.

## Stop conditions

- None encountered. No ambiguity, no path expansion beyond `README.md` /
  `docs/security-boundaries.md` / `project/` records, no protected action
  attempted, no product source touched.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `project/handoffs/ISSUE-0011-handoff.md` | this commit | tests pass; compile clean; validator passed (incl. link/anchor check); documentation walkthrough smoke-checked | pending | pending |

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Not yet complete. Awaiting the fresh Codex issue review and, per the
  workflow, a human advance/merge decision.
