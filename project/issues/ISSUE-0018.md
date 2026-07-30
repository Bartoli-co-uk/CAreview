# ISSUE-0018: Analyzer rule — phishing-resistant authentication strength for admins

**Status:** `PLANNED` — drafted for human review; not yet authorized to start
**Milestone:** `None yet` — requires a new roadmap version/milestone before work may begin (roadmap v5's milestones are all `COMPLETE`; this is new scope)
**Approved roadmap:** `pending` — no roadmap version currently covers this work; `AGENTS.md` requires an approved roadmap before implementation starts
**Dependencies:** `None` (independent of `ISSUE-0015`/`ISSUE-0016`/`ISSUE-0017`; may be sequenced after them or in parallel once all are authorized)
**Branch:** `ai/ISSUE-0018-phishing-resistant-mfa-rule` (not yet created)
**Starting SHA:** `not yet created`
**Candidate SHA:** `Not created`

## Objective

Add a new analyzer rule, `phishing-resistant-mfa-admins`, that checks
whether every built-in admin role (`rules.ADMIN_ROLE_TEMPLATE_IDS`) is
covered by an enabled policy requiring Microsoft's built-in
**phishing-resistant** authentication strength grant control — a materially
stronger bar than the existing `mfa-admins` rule, which only checks for the
`mfa` built-in control (satisfiable by SMS/push, both bypassable by
adversary-in-the-middle phishing). Requires one additive
`graph.normalize_policy` field for data Microsoft Graph already returns on
the same `identity/conditionalAccess/policies` call CAreview already makes.

## Verified external fact (must not be re-derived by guesswork during implementation)

Microsoft's built-in `authenticationStrengthPolicy` IDs are stable and
documented on Microsoft Learn's `authenticationStrengthPolicies`
list-policies page:
- `00000000-0000-0000-0000-000000000002` — "Multifactor authentication"
- `00000000-0000-0000-0000-000000000003` — "Passwordless MFA"
- `00000000-0000-0000-0000-000000000004` — **"Phishing resistant MFA"** ← this rule's target

The implementer must re-confirm this against the current Microsoft Learn
page (or a live tenant response) before hardcoding it, rather than trusting
this issue file as the sole source — treat it as a strong lead, not
unverifiable fact, per `AGENTS.md`'s evidence discipline.

## In scope

- `graph.py` — `normalize_policy`: inside the existing `grantControls` dict,
  add `authenticationStrengthId` (str, read from
  `grantControls.authenticationStrength.id`), defaulting to `""` on
  missing/malformed input. Must not change the existing
  `grantControls.operator`/`builtInControls` keys or any other normalized
  field.
- `rules.py` — a module-level constant
  `PHISHING_RESISTANT_STRENGTH_ID = "00000000-0000-0000-0000-000000000004"`
  with a comment citing the source above; new
  `Rule("phishing-resistant-mfa-admins", ...)`, high severity, weight 15,
  plus a `_check_phishing_resistant_mfa_admins` function reusing
  `ADMIN_ROLE_TEMPLATE_IDS` and the same full-admin-role-union coverage
  pattern as `_check_mfa_for_admins`. PASS requires the union of enabled
  policies scoped to admin roles to fully cover `ADMIN_ROLE_TEMPLATE_IDS`,
  each with `grantControls.authenticationStrengthId ==
  PHISHING_RESISTANT_STRENGTH_ID`.
- `README.md` — one new "What it checks" table row (rationale must state the
  documented limitation below, not bury it in code comments only); update
  rule-count/total-weight sentence.
- `tests/test_graph.py` — extend the missing-fields/malformed-nested-objects
  tests to assert `grantControls["authenticationStrengthId"] == ""` on
  missing/malformed input, plus one positive-shape test.
- `tests/test_analyzer.py` — at least three cases: (1) admin-scoped enabled
  policy with `builtInControls: ["mfa"]` only, no authentication strength →
  FAIL; (2) same policy with `authenticationStrengthId` set to the
  phishing-resistant ID, full admin-role union → PASS; (3) same as (2) but
  with the *plain* MFA strength ID (`...002`) instead → still FAIL (proves
  the check is strength-specific, not "any strength configured").

## Out of scope

- Recognizing tenant-defined **custom** authentication strengths that
  happen to be restricted to phishing-resistant methods (FIDO2/certificate/
  Windows Hello) — this rule only recognizes Microsoft's built-in
  phishing-resistant strength by ID. This is an accepted MVP limitation and
  must be stated explicitly in the rule's rationale and the README row, not
  silently hidden.
- The other three proposed rules (`location-restriction-present`,
  `terms-of-use-required`, `admin-signin-frequency`) — each is its own
  issue.

## Allowed paths

- `graph.py`, `rules.py`, `README.md`, `tests/test_graph.py`,
  `tests/test_analyzer.py`

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes, including the new
   `test_graph.py` cases and all three `phishing-resistant-mfa-admins`
   analyzer cases.
2. The hardcoded `PHISHING_RESISTANT_STRENGTH_ID` is re-verified against a
   current, cited source at implementation time (not copy-pasted from this
   issue file without a fresh check) and the source is cited in a code
   comment, mirroring how `ADMIN_ROLE_TEMPLATE_IDS` cites its source.
3. The rule requires full admin-role-union coverage, not a single narrow
   policy.
4. The custom-authentication-strength limitation is documented in both
   `rules.py`'s rationale string and the `README.md` table row.
5. `README.md`'s "What it checks" table and rule-count/total-weight sentence
   match `rules.py` exactly.
6. No existing rule's pass/fail state changes on the current fixtures.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Governance | `python3 scripts/validate_repo.py` | passes |

## Documentation

- `README.md`: new "What it checks" table row, including the documented
  custom-authentication-strength limitation; updated rule-count/weight
  sentence in the same section.

## Security and privacy impact

- Threat-model delta: none new — reads a field already present in the same
  already-fetched, already in-memory Graph response; no new Graph call,
  scope, or permission.
- Data/secret impact: none.
- Dependency/supply-chain impact: none; standard library only.
- Protected actions: none.

## Stop conditions

- Hardcoding the phishing-resistant strength ID without re-verifying it
  against a current, cited Microsoft source at implementation time.
- Silently expanding the rule to attempt custom-authentication-strength
  recognition — that is explicitly out of scope and would require its own
  design decision (likely a new Graph call to resolve the custom strength's
  allowed methods).
- Any weakening of the full-admin-role-union coverage requirement.

## Not yet started

No branch has been created and no Codex review has run. Per `AGENTS.md`, this
issue may not begin until: (1) a roadmap version/milestone covering it is
drafted and approved by the human, and (2) the human separately authorizes
starting this specific issue.
