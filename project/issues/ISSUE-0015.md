# ISSUE-0015: Analyzer rule — location-restriction presence

**Status:** `REVIEWING`
**Milestone:** `M4` — bound by roadmap v6 (analyzer rule-set expansion); `M4` itself is `PLANNED`, not started
**Approved roadmap:** `ROADMAP.md` version `6`, `APPROVED` (`DECISION-034`, binds `68655cc7b1e0a63db3d6b37debf834c126bb60e0`) — binds this issue to `M4`
**Dependencies:** `None`
**Branch:** `ai/ISSUE-0015-location-restriction-rule`
**Starting SHA:** `ee29aa91346c5246d75ae48cdfdcf39137de0858`
**Candidate SHA:** `bcfeacdb0e264db42badf4a6a945acb94f3fc3ff`

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

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes, including the two new
   `location-restriction-present` cases.
2. The rule is present in `rules.RULES` with documented severity, weight,
   rationale, remediation, and `requires` fields (covered automatically by
   the existing `test_every_rule_has_metadata` contract test).
3. `README.md`'s "What it checks" table and rule-count/total-weight sentence
   are updated to match `rules.py` exactly.
4. The rule does not regress any pre-existing rule's pass/fail state on
   the existing `strong_tenant.json`/`weak_tenant.json`/`incomplete_tenant.json`
   fixtures (no fixture changes are needed for this issue).

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
  a fixture-driven regression elsewhere.

## Not yet started

No branch has been created and no Codex review has run. Per `AGENTS.md`, this
issue may not begin until: (1) a roadmap version/milestone covering it is
drafted and approved by the human, and (2) the human separately authorizes
starting this specific issue.
