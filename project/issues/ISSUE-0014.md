# ISSUE-0014: Wire the frontend build and test suite into CI

**Status:** `REPAIRING`
**Milestone:** `M3`
**Approved roadmap:** `ROADMAP.md` version `5`, `APPROVED` (`DECISION-029`, binds `8ea41ee`).
**Dependencies:** `ISSUE-0012` (frontend exists to build/test)
**Branch:** `ai/ISSUE-0014-frontend-ci`
**Starting SHA:** `8e864a38e03d0df90c79a469c0e1fdf740da7904`
**Candidate SHA:** round 0 `c4cb4d28f9b710e4f24366ec6fbb61e810246d96` (`BLOCKED`,
F-001: stale `CURRENT.md` rows — repair missed six of nine stale rows);
round 1 `d72dbd9a5481ec8dc69143fb31aef7a15fc0445b` (`BLOCKED` again, same
F-001, narrower); round 2 candidate is this commit — the launcher records
the full HEAD SHA. This is the last repair round `AGENTS.md` permits for
an issue.

## Objective

`.github/workflows/validate.yml` currently runs three Python checks only. The
91 Vitest tests (including the hostile-markup and dangerous-sink checks the
project relies on to argue the React UI is XSS-safe) and the frontend build
have never run in CI — only on whoever's laptop ran them locally before
pushing. Add a CI step that builds and tests the frontend from the committed
lockfile, so a broken build or a red test blocks the workflow the same way a
broken Python check already does.

## In scope

- A new job/step in `.github/workflows/validate.yml` that runs, in order:
  `npm ci` (not `npm install` — must build from the committed lockfile,
  never resolve fresh versions in CI), `npm run build`, `npm test`, all
  inside `frontend/`.
- Pinning the Node version used by that step and SHA-pinning any new
  GitHub Action the same way the existing `actions/checkout` step is pinned.
- Updating `README.md`/`CONTRIBUTING.md` to say CI now covers the frontend,
  removing the "CI does not run either of these yet" caveat those files
  currently carry.

## Out of scope

- Any product source change (backend or frontend).
- Any change to the frontend's test content in order to make CI pass.
- Loosening or skipping a check to get a green run.
- Any dependency-audit or supply-chain-pinning work beyond what the
  committed lockfile already provides (that is `RISK-009`'s separate,
  still-undecided treatment, not this issue's scope).

## Allowed paths

- `.github/workflows/validate.yml`
- `CONTRIBUTING.md`, `README.md` (CI-status wording only)
- `project/` records for this issue

## Acceptance criteria

1. The workflow runs `npm ci`, `npm run build`, and `npm test` in `frontend/`
   on every push and pull request, alongside the existing three Python steps.
2. A deliberately broken frontend candidate fails the workflow. **Verified
   locally, not by a live GitHub Actions run** (pushing a deliberately red
   commit and exercising branch/workflow cleanup is a protected action this
   issue does not authorize on its own): use `act` or an equivalent local
   GitHub Actions runner against the modified `validate.yml` on a disposable
   worktree, with one Vitest test edited to fail; capture the runner's real
   exit status and output showing the job fails, then discard that disposable
   change. If no local runner is available in the environment, the fallback
   is a same-effect substitute check documented in the handoff (e.g. running
   the exact composed shell command the workflow step will run, with the
   same red test, and showing a non-zero exit) — not a claim that GitHub
   Actions was exercised.
3. The three existing Python steps keep passing unmodified.
4. No new backend dependency and no expansion of the Node toolchain beyond
   what `DECISION-024` already permits.
5. `README.md` and `CONTRIBUTING.md` no longer say CI skips the frontend.

## Required checks

| Check | Command or method | Result (round 0) |
|---|---|---|
| Backend tests | `python3 -m unittest discover -s tests` | 188 passed |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files) |
| Frontend build | `cd frontend && npm ci && npm run build` | exit 0; produced `web/index.html` (0.54 kB), `index.css` (6.56 kB), `index.js` (237.09 kB) |
| Frontend tests | `cd frontend && npm test` | 91 passed, 7 test files, exit 0 |
| Negative-CI proof | Per acceptance criterion 2 — **local fallback used, `act` was not available in this environment** | A temporary `expect(1).toBe(2)` test was added to `src/test/hostileMarkup.test.tsx`, then the exact composed commands the new workflow steps run (`npm ci`; `npm run build`; `npm test`, all from `frontend/`) were run in order: `npm ci` exit 0, `npm run build` exit 0, `npm test` **exit 1** — Vitest reported `1 failed, 91 passed`, the added test failing with `AssertionError: expected 1 to be 2`. The temporary test was then reverted; `npm test` returned to 91 passed, exit 0. This proves the composed command fails non-zero on a red test, which is what fails a GitHub Actions `run:` step — it does not exercise the YAML parser or the actual hosted runner, the residual `DECISION-029` already accepted for this criterion |

## Documentation

- `README.md`: remove the "CI does not run the frontend" caveat; state what CI now covers.
- `CONTRIBUTING.md`: same, in the "If you touch the UI" section added with roadmap v5.
- `project/status/CURRENT.md`: record the new CI coverage and the exact candidate SHA once merged.

## Security and privacy impact

- Threat-model delta: none to runtime behavior. Reduces the evidence gap
  `RISK-009` and `docs/security-boundaries.md`'s build-time dependency
  boundary both flag — a dependency change reaching `main` will now be
  caught by an automated build/test run, not only a human reading a
  lockfile diff.
- Data/secret impact: none. CI needs no new secret; `npm ci`/`npm run
  build`/`npm test` use only the committed lockfile and source.
- Dependency/supply-chain impact: none beyond the Node toolchain
  `DECISION-024` already permits. Does **not** add `npm audit`, pinning, or
  any other `RISK-009` mitigation beyond what CI executing the existing
  lockfile-bound build already provides as a side effect.
- Protected actions: pushing a deliberately failing commit to a real GitHub
  Actions run, or any branch/workflow-run cleanup that would follow, is a
  protected action and is explicitly **not** authorized by this record —
  see acceptance criterion 2's local-verification requirement instead.

## Stop conditions

- No local GitHub Actions runner is available and no equivalent substitute
  check can honestly demonstrate the negative-CI property.
- Any attempt to satisfy criterion 2 that would require pushing to GitHub
  or running a live Actions workflow without a separate, explicit human
  approval naming that exact action.
- Any temptation to expand scope into `RISK-009`'s dependency-audit
  question — that remains a separate, undecided human treatment decision.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | This record's Required checks table | `c4cb4d28f9b710e4f24366ec6fbb61e810246d96` | 188 backend tests, py_compile, validate_repo.py, frontend build, 91 frontend tests, negative-CI local fallback — all recorded above | `project/reviews/issues/ISSUE-0014-c4cb4d28f9b7-codex.json` | `BLOCKED` — F-001 (medium): `CURRENT.md` contained stale rows contradicting this candidate |
| 1 | Round-0 checks unchanged; no product/CI file touched | `d72dbd9a5481ec8dc69143fb31aef7a15fc0445b` | Unchanged from round 0 (backend tests, py_compile, validate_repo.py all re-run and passing) | `project/reviews/issues/ISSUE-0014-d72dbd9a5481-codex.json` | `BLOCKED` again — F-001 (medium, narrower): the round-1 repair fixed 3 of 9 stale `CURRENT.md` rows and missed the other 6 |
| 2 | Round-0 checks unchanged; no product/CI file touched | *this commit* | Unchanged from round 0 | *pending* | *pending* |

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Final reviewed product SHA: `N/A — not started`
- Human advance/merge decision: `N/A`
- Merge/result SHA: `N/A`
- Residual risks or follow-up: `N/A`
- Status record updated: `N/A`
