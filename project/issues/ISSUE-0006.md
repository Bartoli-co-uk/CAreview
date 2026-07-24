# ISSUE-0006: Documentation finalization and end-to-end verification

**Status:** `REPAIRING`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `3` at `125d74f6d4bfe85f1a727293064d0887f2d121c7`
**Dependencies:** `ISSUE-0001`, `ISSUE-0002`, `ISSUE-0003`, `ISSUE-0004`, `ISSUE-0005`
**Branch:** `ai/ISSUE-0006-docs-verification`
**Starting SHA:** `4e8e999ef2204ee7089726b205f5895dc73b38b0`
**Candidate SHA:** `this commit (branch HEAD); launcher binds the exact SHA`

## Objective

Finalize user-facing documentation and record a clean-checkout, end-to-end
verification of the MVP, and ensure lint/tests are green, so the milestone can
be frozen for its four reviews.

## In scope

- `README.md` — accurate run/verify steps and a concise end-to-end walkthrough
  (sign in → fetch → score/findings → cards), plus the known-limitations note
  (RISK-001/002/004).
- `docs/` — only if a threat-model note needs updating.
- Small test/lint fixes surfaced by the clean-checkout pass (no new features).

## Out of scope

- New product features or new rules.

## Allowed paths

- `README.md`, `docs/**`, `tests/**`, and minimal fixes within existing modules
  strictly to keep checks green.

## Acceptance criteria

1. From a fresh clone, README steps run the app and tests with no third-party installs.
2. `python3 -m py_compile $(git ls-files '*.py')` and
   `python3 -m unittest discover -s tests` are clean.
3. A documented end-to-end walkthrough exists and matches actual behaviour.
4. Known limitations and the heuristic-score caveat are documented.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Clean checkout | Fresh clone → follow README | app runs, tests pass |
| Governance | `python3 scripts/validate_repo.py` | passes |

## Documentation

- This issue is primarily documentation; it completes the M1 documentation plan.

## Security and privacy impact

- Threat-model delta: none.
- Data/secret impact: ensure no tokens/tenant data appear in docs or examples.
- Dependency/supply-chain impact: none.
- Protected actions: none.

## Stop conditions

- Any documentation that would require committing sensitive tenant data or a
  screenshot containing real policy detail.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `ISSUE-0006-handoff.md` | `30a75c425bf1…` | py_compile 0; 80 tests pass; validator pass | `ISSUE-0006-30a75c425bf1-codex.json` | BLOCKED (F-002 port URL, F-003 disk-write claim, F-004 status) |
| 1 (repair) | `ISSUE-0006-handoff.md` | `cc98f4e616af…` | py_compile 0; 80 tests pass; validator pass | `ISSUE-0006-cc98f4e616af-codex.json` | BLOCKED (F-002 status staleness, F-003 README overclaim) |
| 2 (repair, DECISION-007) | `ISSUE-0006-handoff.md` | repair-2 candidate (launcher binds SHA) | py_compile 0; 80 tests pass; validator pass | pending final review | pending |

Maximum two repair rounds; every Codex review is a fresh ephemeral read-only
process against the named SHA.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
