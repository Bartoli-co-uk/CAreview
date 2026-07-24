# ISSUE-0004: Analyzer engine, rule set, and scoring

**Status:** `COMPLETE`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `3` at `125d74f6d4bfe85f1a727293064d0887f2d121c7`
**Dependencies:** `ISSUE-0003`
**Branch:** `ai/ISSUE-0004-analyzer`
**Starting SHA:** `e94ef5abad6e95ec899a7bca04e30e9dc3dbea81`
**Candidate SHA:** `this commit (branch HEAD); launcher binds the exact SHA`

## Objective

Implement the data-driven analyzer that turns normalized CA policies into a
0–100 security score and a severity-sorted list of best-practice / vulnerability
findings, fully unit-tested against committed sanitized fixtures.

## In scope

- `rules.py` — declarative starter rule set with documented weights: block legacy
  auth; MFA for admins; MFA for all users; device compliance/hybrid join;
  sign-in/user risk policy present; break-glass excluded but scoped;
  report-only vs enabled; overly broad "all users + all apps" grant; missing
  session controls. Each rule declares the **data-contract fields it requires**
  (Codex F-003); a rule whose required fields are absent is **not evaluable** and
  is excluded from scoring, never counted as pass or fail. The break-glass rule
  specifically requires the user-supplied break-glass ID input from ISSUE-0003's
  contract (Codex F-002); without it the rule is *not evaluable*, not a failure.
- `analyzer.py` — evaluate rules over the normalized policy set, compute the
  weighted 0–100 score, and emit findings (id, title, severity, rationale,
  affected policies, remediation).
- `server.py` — `/api/analysis` returns score + findings for the current policies.
- `tests/` + `tests/fixtures/` — sanitized "strong", "weak", and "incomplete"
  tenant fixtures with expected deterministic scores and findings, where
  "incomplete" exercises the *not evaluable* path.

## Out of scope

- UI rendering (ISSUE-0005). CIS/FOCI/persona rule packs (non-goals).

## Allowed paths

- `analyzer.py`, `rules.py`, `server.py`, `tests/**`

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes.
2. A strong-baseline fixture scores high and a weak fixture scores low, with
   deterministic, documented numbers.
3. Each rule's weight, required data-contract fields, and finding severity are
   documented in `rules.py`.
4. Findings are returned severity-sorted (critical → info).
5. The score is labeled a heuristic (RISK-004), not a compliance measure.
6. A rule lacking its required evidence is reported *not evaluable* and excluded
   from the score (never pass/fail); the "incomplete" fixture proves this.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass, deterministic scores |

## Documentation

- README/verify: describe the offline analyzer test and what the score means.
- `rules.py`: inline documentation of each rule and weight.

## Security and privacy impact

- Threat-model delta: none new; operates on already-fetched in-memory data.
- Data/secret impact: fixtures must be sanitized (no real tenant data/IDs).
- Dependency/supply-chain impact: none; standard library only.
- Protected actions: none.

## Stop conditions

- Any temptation to embed real tenant data as a fixture; scope creep into
  non-goal rule packs.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `ISSUE-0004-handoff.md` | `f211f62ab4d9…` | py_compile 0; 62 tests pass; validator pass | `ISSUE-0004-f211f62ab4d9-codex.json` | BLOCKED (F-001 evaluability, F-002 overly-broad rule, F-003 API input, F-004 break-glass, F-005 docs) |
| 1 (repair) | `ISSUE-0004-handoff.md` | `5065a80db86a…` | py_compile 0; 67 tests pass; validator pass | `ISSUE-0004-5065a80db86a-codex.json` | BLOCKED (F-001 execution, F-002 evaluability, F-003 status) |
| 2 (repair, DECISION-007) | `ISSUE-0004-handoff.md` | `fbb416403d6e…` | py_compile 0; 68 tests pass; validator pass | `ISSUE-0004-fbb416403d6e-codex.json` | BLOCKED (F-002 evaluability re-raised, F-003 MFA coverage gap, F-004 status) |
| 3 (repair, DECISION-007) | `ISSUE-0004-handoff.md` | `6cc54832…` | py_compile 0; 71 tests pass; validator pass | `ISSUE-0004-a7ec63010bd5-codex.json` (against round-4 candidate) | see round 4 |
| 4 (repair, DECISION-008) | `ISSUE-0004-handoff.md` | `a7ec63010bd5…` | py_compile 0; 73 tests pass; validator pass | `ISSUE-0004-a7ec63010bd5-codex.json` | BLOCKED (F-002 nested-path gap, F-001/F-003/F-004 process+records) |
| 5 (repair, DECISION-007/008) | `ISSUE-0004-handoff.md` | `80a87704…` | py_compile 0; 73 tests pass; validator pass | (superseded by final round) | round-cap reached; human decision requested |
| 6 (final, DECISION-009) | `ISSUE-0004-handoff.md` | `9f3885bb80ca…` | py_compile 0; 73 tests pass; validator pass | `ISSUE-0004-9f3885bb80ca-codex.json` | BLOCKED — no additional substantive analyzer defect; SHA/record sync (fixed) + execution evidence only (merged) |

Default is two repair rounds; `DECISION-007` raised the budget for small fixes,
`DECISION-008` resolved a recurring design disagreement, and `DECISION-009`
authorized the final confirming round past even that raised budget. Every Codex
review is a fresh ephemeral read-only process against the named SHA.

## Completion

- Final reviewed product SHA: `9f3885bb80ca4c65912f5872785e0980e52747c5`
- Human advance/merge decision: `DECISION-005`, `DECISION-007`, `DECISION-008`, `DECISION-009`
- Merge/result SHA: merged into `main` (see merge commit)
- Residual risks or follow-up: score is a documented heuristic (RISK-004); live Graph fetch not exercised (protected action, unchanged from ISSUE-0003)
- Status record updated: this commit + `project/status/CURRENT.md`
