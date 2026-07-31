# ISSUE-0015: Analyzer rule — location-restriction presence

**Status:** `COMPLETE` (merged, with an accepted sandbox execution-evidence
residual) — the human reviewed the round-1 zero-finding `BLOCKED` outcome
(see round history below) and chose to accept the sandbox residual and
merge (`DECISION-037`)
**Milestone:** `M4` — bound by roadmap v6 (analyzer rule-set expansion); `M4` itself is `PLANNED`, not started
**Approved roadmap:** `ROADMAP.md` version `6`, `APPROVED` (`DECISION-034`, binds `68655cc7b1e0a63db3d6b37debf834c126bb60e0`) — binds this issue to `M4`
**Start authorization:** `DECISION-035` (retroactive, recorded after the round-0 review's F-003 finding)
**Dependencies:** `None`
**Branch:** `ai/ISSUE-0015-location-restriction-rule`
**Starting SHA:** `ee29aa91346c5246d75ae48cdfdcf39137de0858`
**Candidate SHA:** round 1 is this commit — the launcher records the full HEAD SHA at review time; see the round table below for each round's exact reviewed SHA

## Objective

Add a new analyzer rule, `location-restriction-present`, that checks whether
at least one enabled Conditional Access policy conditions on a named location
(rather than leaving `includeLocations`/`excludeLocations` at the default
`All`/`AllTrusted`). This is the simplest of four proposed rule additions
(see `ISSUE-0016`–`ISSUE-0018`) — it needs no `graph.py` change, since
`normalize_policy` already captures `conditions.includeLocations`/
`excludeLocations` in full.

## In scope

- `rules.py` — new `Rule("location-restriction-present", ...)`, medium
  severity, weight 10, plus a `_check_location_restriction` function reusing
  existing helpers (`_enabled`, `_cond`, `_names`, `_any`). PASS if any enabled
  policy's `includeLocations ∪ excludeLocations` (case-insensitive) minus
  `{"all", "alltrusted"}` is non-empty.
- `README.md` — one new row in the "What it checks" table; update the rule
  count/total-weight sentence.
- `tests/test_analyzer.py` — one fail-trip case (all-users policy with
  `includeLocations: ["All"]` only) and one pass case (same policy plus a
  named-location GUID in `includeLocations` or `excludeLocations`).

## Out of scope

- Resolving named-location GUIDs to friendly names or countries (would need
  the separate `identity/conditionalAccess/namedLocations` Graph endpoint —
  a recorded non-goal for this MVP, see `README.md`'s design-goals section).
- The other three proposed rules (`terms-of-use-required`,
  `admin-signin-frequency`, `phishing-resistant-mfa-admins`) — each is its
  own issue.

## Allowed paths

- `rules.py`, `README.md`, `tests/test_analyzer.py`
- `tests/fixtures/strong_tenant.json` — added by scope amendment
  `DECISION-036`, scoped to exactly one additive policy (see below)

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes, including the two new
   `location-restriction-present` cases.
2. The rule is present in `rules.RULES` with documented severity, weight,
   rationale, remediation, and `requires` fields (covered automatically by
   the existing `test_every_rule_has_metadata` contract test).
3. `README.md`'s "What it checks" table and rule-count/total-weight sentence
   are updated to match `rules.py` exactly.
4. The rule does not regress any pre-existing rule's pass/fail state on the
   existing `strong_tenant.json`/`weak_tenant.json`/`incomplete_tenant.json`
   fixtures, **except** the one additive `strong_tenant.json` policy
   approved by `DECISION-036` (added because the new rule would otherwise
   newly fire against `strong_tenant.json`, regressing
   `test_strong_tenant_scores_high`). No other fixture change is in scope.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Governance | `python3 scripts/validate_repo.py` | passes |

## Documentation

- `README.md`: new "What it checks" table row; updated rule-count/weight
  sentence in the same section.

## Security and privacy impact

- Threat-model delta: none — read-only analysis of already-fetched, already
  in-memory policy data; no new Graph call, scope, or permission.
- Data/secret impact: none — no new data leaves the process; location GUIDs
  are not resolved to any external identifier.
- Dependency/supply-chain impact: none; standard library only, no new
  third-party dependency.
- Protected actions: none.

## Stop conditions

- Any temptation to resolve named-location GUIDs to friendly
  names/countries — that requires a new Graph endpoint and is explicitly out
  of scope for this issue.
- Any fixture change that would perturb an existing rule's pass/fail state —
  if that seems unavoidable, stop and re-scope rather than silently accepting
  a fixture-driven regression elsewhere. **Triggered once**: the round-0
  candidate's `strong_tenant.json` addition did exactly this without first
  stopping; resolved after the fact by `DECISION-036` rather than reverted,
  per the human's explicit choice on the round-0 finding.

## Round history

| Round | Reviewed SHA | Outcome | Findings |
|---|---|---|---|
| 0 | `1ff0b987d2f75377589e6c4875724b94aef81591` | `BLOCKED` | F-001 (medium: candidate-identity mismatch between issue/handoff and reviewed HEAD); F-002 (medium: `strong_tenant.json` changed outside allowed paths); F-003 (high: no durable ISSUE-0015 start-authorization record) — see `project/reviews/issues/ISSUE-0015-1ff0b987d2f7-codex.json` |
| 1 | `31c94a824cc7ae85e0baadc926f9cd94faaab8fc` | `BLOCKED` | Zero content findings (`findings: []`). Blocked solely because the review sandbox could not independently reproduce the three required checks: `py_compile` denied `__pycache__` write, `unittest discover` had 76 `test_server.py` setup errors from denied loopback socket binding, and `validate_repo.py` had no writable temp directory. Same failure class as `ISSUE-0014`'s accepted round-2 residual. All three required checks were independently run in this task's own environment with real, non-sandboxed results: compile exit 0, `python3 -m unittest discover -s tests` → 190 passed, `python3 scripts/validate_repo.py` → passed (67 required files) — see the "Verification evidence" section of `project/handoffs/ISSUE-0015-handoff.md`. See `project/reviews/issues/ISSUE-0015-31c94a824cc7-codex.json` |

Round 0's F-001 and F-002 were repaired in the round-1 commit; F-003 was
resolved by `DECISION-035`. Round 1's sole blocker is the sandbox
execution-evidence limitation, presented to the human for an advance/merge
decision rather than treated as a passing outcome on its own.

## Advance/merge decision

The human reviewed round 1's zero-finding `BLOCKED` outcome and the real,
independently-run check results and chose to accept the sandbox
execution-evidence residual and merge, the same disposition used
repeatedly for this class of finding elsewhere in this project (most
recently `ISSUE-0014`, `DECISION-031`). `DECISION-037` records the exact
binding. `ai/ISSUE-0015-location-restriction-rule` is merged to `main`.
