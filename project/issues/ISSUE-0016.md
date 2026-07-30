# ISSUE-0016: Analyzer rule — Terms of Use requirement present

**Status:** `PLANNED` — drafted for human review; not yet authorized to start
**Milestone:** `None yet` — requires a new roadmap version/milestone before work may begin (roadmap v5's milestones are all `COMPLETE`; this is new scope)
**Approved roadmap:** `pending` — no roadmap version currently covers this work; `AGENTS.md` requires an approved roadmap before implementation starts
**Dependencies:** `None` (independent of `ISSUE-0015`; may be sequenced after it or in parallel once both are authorized)
**Branch:** `ai/ISSUE-0016-terms-of-use-rule` (not yet created)
**Starting SHA:** `not yet created`
**Candidate SHA:** `Not created`

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
  5, plus a `_check_terms_of_use` function. PASS if an enabled policy scoped
  to `includeUsers: ["All"]` or intersecting `ADMIN_ROLE_TEMPLATE_IDS` has a
  non-empty `grantControls.termsOfUse`.
- `README.md` — one new "What it checks" table row; update rule-count/total-
  weight sentence.
- `tests/test_graph.py` — extend the missing-fields/malformed-nested-objects
  tests to assert `grantControls["termsOfUse"] == []` on missing/malformed
  input, plus one positive-shape test asserting a populated `termsOfUse` list
  round-trips correctly.
- `tests/test_analyzer.py` — one fail-trip case (enabled all-users policy,
  no `termsOfUse`) and one pass case (same policy with a non-empty
  `termsOfUse` list).

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

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes, including the new
   `test_graph.py` default/round-trip cases and the two new
   `terms-of-use-required` analyzer cases.
2. `normalize_policy({})`'s `grantControls` still contains exactly
   `operator`, `builtInControls`, and the new `termsOfUse` key — no other
   normalized field is removed, renamed, or reshaped.
3. The rule is present in `rules.RULES` with documented severity, weight,
   rationale, remediation, and `requires` fields (covered automatically by
   `test_every_rule_has_metadata`).
4. `README.md`'s "What it checks" table and rule-count/total-weight sentence
   match `rules.py` exactly.
5. No existing rule's pass/fail state changes on the current fixtures (no
   fixture file changes are needed for this issue).

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

## Not yet started

No branch has been created and no Codex review has run. Per `AGENTS.md`, this
issue may not begin until: (1) a roadmap version/milestone covering it is
drafted and approved by the human, and (2) the human separately authorizes
starting this specific issue.
