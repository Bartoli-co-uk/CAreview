# ISSUE-0016: Analyzer rule — Terms of Use requirement present

**Status:** `REVIEWING`
**Milestone:** `M4` — bound by roadmap v6 (analyzer rule-set expansion); `M4` itself is `PLANNED`, not started
**Approved roadmap:** `ROADMAP.md` version `6`, `APPROVED` (`DECISION-034`, binds `68655cc7b1e0a63db3d6b37debf834c126bb60e0`) — binds this issue to `M4`
**Start authorization:** `DECISION-038`
**Dependencies:** `None` (independent of `ISSUE-0015`; sequenced after it as the second `M4` issue delivered)
**Branch:** `ai/ISSUE-0016-terms-of-use-rule`
**Starting SHA:** `bb01fabd6e6984ee89bc3b56ab56ed2f81000c5e`
**Candidate SHA:** round 0 is this commit — the launcher records the full HEAD SHA

## Objective

Add a new analyzer rule, `terms-of-use-required`, that checks whether at
least one enabled, meaningfully-scoped Conditional Access policy requires
acceptance of a Terms of Use agreement as a grant control. Requires a small,
additive change to `graph.normalize_policy` to stop dropping
`grantControls.termsOfUse`, which Microsoft Graph already returns on the same
`identity/conditionalAccess/policies` call CAreview already makes.

## In scope

- `graph.py` — `normalize_policy`: add `termsOfUse` (list[str] of agreement
  GUIDs) inside the existing `grantControls` dict, read from
  `grantControls.termsOfUse` on the raw policy. Defaults to `[]` on
  missing/malformed input, following the file's existing pattern (never
  raises). Must not change the existing `grantControls.operator`/
  `builtInControls` keys or any other normalized field.
- `rules.py` — new `Rule("terms-of-use-required", ...)`, low severity, weight
  5, plus a `_check_terms_of_use` function. **PASS** requires ALL of:
  (1) the policy is enabled; (2) its scope is "meaningfully broad" —
  `includeUsers` contains `"All"` with no `excludeGroups`/`excludeRoles`
  (mirroring `mfa-all-users`'s existing exclusion discipline — individual-user
  exclusions like break-glass are tolerated, a whole excluded group/role is
  not), OR `includeRoles` intersects `ADMIN_ROLE_TEMPLATE_IDS` with none of
  those specific roles present in `excludeRoles`; (3) `grantControls.termsOfUse`
  is non-empty; **(4) `grantControls.operator == "AND"` whenever
  `builtInControls` is also non-empty** — Graph's grant-control operator is
  `"AND"` (all controls required) or `"OR"` (any one control satisfies the
  policy); if the operator is `"OR"`, Terms of Use is one *alternative* among
  several, not a requirement, and must not count as PASS. A `termsOfUse`-only
  policy (empty `builtInControls`) has no operator ambiguity and passes
  regardless of the `operator` value.
- `README.md` — one new "What it checks" table row; update rule-count/total-
  weight sentence.
- `tests/test_graph.py` — extend the missing-fields/malformed-nested-objects
  tests to assert `grantControls["termsOfUse"] == []` on missing/malformed
  input, plus one positive-shape test asserting a populated `termsOfUse` list
  round-trips correctly.
- `tests/test_analyzer.py` — at least four cases: (1) fail-trip, enabled
  all-users policy with no `termsOfUse` → FAIL; (2) pass, same policy with a
  non-empty `termsOfUse` and `operator: "AND"` (or empty `builtInControls`)
  → PASS; (3) same as (2) but `operator: "OR"` with a non-empty
  `builtInControls` → still FAIL (Terms of Use is only an alternative, not
  required — this is the false-pass Codex's round-1 plan review flagged,
  F-003); (4) an otherwise-qualifying all-users policy that also sets
  `excludeGroups`/`excludeRoles` → FAIL (not meaningfully scoped, mirroring
  `mfa-all-users`'s existing test for the same nuance).

## Out of scope

- Resolving Terms of Use GUIDs to agreement names/content (would need the
  separate `identityGovernance/termsOfUse/agreements` Graph endpoint — a
  recorded non-goal for this MVP).
- The other three proposed rules (`location-restriction-present`,
  `admin-signin-frequency`, `phishing-resistant-mfa-admins`) — each is its
  own issue.

## Allowed paths

- `graph.py`, `rules.py`, `README.md`, `tests/test_graph.py`,
  `tests/test_analyzer.py`
- `tests/fixtures/strong_tenant.json` — added by scope amendment
  `DECISION-039`, scoped to exactly one additive policy (see below)

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes, including the new
   `test_graph.py` default/round-trip cases and all four new
   `terms-of-use-required` analyzer cases, including the OR-operator
   false-pass case and the excluded-scope case.
2. `normalize_policy({})`'s `grantControls` still contains exactly
   `operator`, `builtInControls`, and the new `termsOfUse` key — no other
   normalized field is removed, renamed, or reshaped.
3. The rule is present in `rules.RULES` with documented severity, weight,
   rationale, remediation, and `requires` fields (covered automatically by
   `test_every_rule_has_metadata`).
4. `README.md`'s "What it checks" table and rule-count/total-weight sentence
   match `rules.py` exactly.
5. No existing rule's pass/fail state changes on the current fixtures,
   **except** the one additive `strong_tenant.json` policy approved by
   `DECISION-039` (added because the new rule would otherwise newly fire
   against `strong_tenant.json`, regressing `test_strong_tenant_scores_high`
   and `test_break_glass_evaluable_with_ids`). No other fixture change is
   in scope.

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

- Threat-model delta: none — reads a field already present in the same
  already-fetched, already in-memory Graph response; no new Graph call,
  scope, or permission.
- Data/secret impact: none — Terms of Use GUIDs are opaque identifiers, not
  resolved to agreement content, and are not persisted or logged.
- Dependency/supply-chain impact: none; standard library only.
- Protected actions: none.

## Stop conditions

- Any temptation to resolve Terms of Use GUIDs to agreement names/content —
  out of scope, needs a new Graph endpoint decision.
- Any change to an existing `grantControls` key's shape or default —
  `termsOfUse` must be strictly additive.
- Passing an `operator: "OR"` policy where Terms of Use is merely one
  alternative control among several — this is the exact false-pass Codex's
  round-1 plan review identified (F-003) and must not regress. **Verified**:
  `test_terms_of_use_flagged_when_only_an_or_alternative` directly covers
  this case.
- Any fixture change that would perturb an existing rule's pass/fail state —
  triggered once (same class as `ISSUE-0015`'s round-0 finding), resolved
  before implementation was committed via `DECISION-039` rather than
  silently made.

## Round history

| Round | Reviewed SHA | Outcome | Findings |
|---|---|---|---|
| 0 | `bfa12f76053b4816e66c36541f3ac578b8f2509e` | `BLOCKED` | F-001 (medium, sandbox-only: all three required checks failed to complete in the review sandbox — denied `__pycache__`/socket/tempdir access; the focused 38 graph/analyzer tests passed and no implementation defect was found); F-002 (low, advisory: `README.md`'s usage-section test count was stale at 188, fixed in round 1 to 195) — see `project/reviews/issues/ISSUE-0016-bfa12f76053b-codex.json` |

Round 0's F-002 is fixed in round 1 (README count corrected). F-001 is the
same sandbox execution-evidence class already accepted repeatedly in this
project (most recently `ISSUE-0015`, `DECISION-037`); all three required
checks were independently run in this task's own environment with real
passing results (see `project/handoffs/ISSUE-0016-handoff.md`).
