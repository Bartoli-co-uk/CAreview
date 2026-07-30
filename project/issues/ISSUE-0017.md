# ISSUE-0017: Analyzer rule — admin-scoped sign-in frequency / no persistent browser

**Status:** `PLANNED` — drafted for human review; not yet authorized to start
**Milestone:** `None yet` — requires a new roadmap version/milestone before work may begin (roadmap v5's milestones are all `COMPLETE`; this is new scope)
**Approved roadmap:** `pending` — no roadmap version currently covers this work; `AGENTS.md` requires an approved roadmap before implementation starts
**Dependencies:** `None` (independent of `ISSUE-0015`/`ISSUE-0016`; may be sequenced after them or in parallel once all are authorized)
**Branch:** `ai/ISSUE-0017-admin-signin-frequency-rule` (not yet created)
**Starting SHA:** `not yet created`
**Candidate SHA:** `Not created`

## Objective

Add a new analyzer rule, `admin-signin-frequency`, that checks whether every
built-in admin role (`rules.ADMIN_ROLE_TEMPLATE_IDS`) is covered by an
enabled policy requiring short, periodic re-authentication with no
persistent browser session — matching CIS Microsoft 365 Foundations
Benchmark guidance for privileged-role sessions. Requires two additive
`graph.normalize_policy` fields for data Microsoft Graph already returns on
the same `identity/conditionalAccess/policies` call CAreview already makes.

## In scope

- `graph.py` — `normalize_policy`: add two new top-level keys,
  `signInFrequency` (`{"enabled": bool, "type": "days"|"hours"|"",
  "value": int|None, "frequencyInterval": "timeBased"|"everyTime"|""}`, read
  from `sessionControls.signInFrequency`) and `persistentBrowser`
  (`{"enabled": bool, "mode": "always"|"never"|""}`, read from
  `sessionControls.persistentBrowser`). Both default safely on
  missing/malformed input, following the file's existing pattern (never
  raises). Must not change the existing `sessionControls` key's current
  shape or its test contract (still `[]` on malformed input).
- `rules.py` — new `Rule("admin-signin-frequency", ...)`, medium severity,
  weight 10, plus a `_check_admin_signin_frequency` function reusing
  `ADMIN_ROLE_TEMPLATE_IDS` and the existing full-admin-role-union coverage
  pattern from `_check_mfa_for_admins` (a single narrow policy must not
  overstate admin coverage). **PASS** requires: the union of enabled
  policies scoped to admin roles fully covers `ADMIN_ROLE_TEMPLATE_IDS`, AND
  each covering policy has `signInFrequency.enabled` true with either
  `frequencyInterval == "everyTime"` or (`type == "hours"` and
  `1 <= value <= 4`) — human-confirmed threshold — AND
  `persistentBrowser.mode != "always"`. A day-scale interval, a disabled/
  missing `signInFrequency`, or `persistentBrowser.mode == "always"` all
  FAIL, even if the frequency value looks short.
- `README.md` — one new "What it checks" table row; update rule-count/total-
  weight sentence.
- `tests/test_graph.py` — extend the missing-fields/malformed-nested-objects
  tests for the two new keys' safe defaults, plus one positive-shape test.
- `tests/test_analyzer.py` — at least three cases: (1) admin-scoped enabled
  policy with `signInFrequency` disabled → FAIL; (2) same policy with
  `signInFrequency` enabled at `frequencyInterval: "everyTime"` (or 1–4
  hours) and `persistentBrowser.mode: "never"`, full admin-role union → PASS;
  (3) same as (2) but `persistentBrowser.mode: "always"` → still FAIL (proves
  the persistent-browser half is enforced independently of frequency).
- `tests/fixtures/strong_tenant.json` — one new, narrowly-scoped additive
  policy entry satisfying this rule without perturbing any of the 14 other
  rules' pass/fail state.

## Out of scope

- Any threshold other than the human-confirmed one above (`everyTime` or
  1–4 hours; day-scale intervals always fail) — a different threshold would
  need its own human decision, not a silent choice during implementation.
- The other three proposed rules (`location-restriction-present`,
  `terms-of-use-required`, `phishing-resistant-mfa-admins`) — each is its
  own issue.

## Allowed paths

- `graph.py`, `rules.py`, `README.md`, `tests/test_graph.py`,
  `tests/test_analyzer.py`, `tests/fixtures/strong_tenant.json`

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes, including the new
   `test_graph.py` cases and all three `admin-signin-frequency` analyzer
   cases.
2. `normalize_policy({})` gains exactly the two new top-level keys described
   above, both safely defaulted; no existing normalized field is removed,
   renamed, or reshaped.
3. The rule requires **full** admin-role-union coverage, not a single narrow
   policy — mirroring `mfa-admins`'s existing coverage discipline.
4. `README.md`'s "What it checks" table and rule-count/total-weight sentence
   match `rules.py` exactly.
5. `test_strong_tenant_scores_high` (or equivalent) continues to expect a
   full pass at the new total weight after the one new fixture policy is
   added; no other rule's pass/fail state on any fixture changes.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass, deterministic scores |
| Governance | `python3 scripts/validate_repo.py` | passes |

## Documentation

- `README.md`: new "What it checks" table row; updated rule-count/weight
  sentence in the same section. The rule's rationale text should state the
  exact threshold (everyTime or 1–4 hours) so a reader can reproduce the
  pass/fail decision from the tenant's own policy configuration.

## Security and privacy impact

- Threat-model delta: none — reads fields already present in the same
  already-fetched, already in-memory Graph response; no new Graph call,
  scope, or permission.
- Data/secret impact: none.
- Dependency/supply-chain impact: none; standard library only.
- Protected actions: none.

## Stop conditions

- Any change to the human-confirmed threshold without going back for a
  fresh human decision.
- Any fixture change that perturbs an existing rule's pass/fail state — if
  unavoidable, stop and re-scope rather than silently accepting a
  fixture-driven regression elsewhere.
- Any weakening of the full-admin-role-union coverage requirement to a
  single-policy check (would reopen the same gap Codex previously flagged
  for `mfa-admins`, historically tracked as F-003).

## Not yet started

No branch has been created and no Codex review has run. Per `AGENTS.md`, this
issue may not begin until: (1) a roadmap version/milestone covering it is
drafted and approved by the human, and (2) the human separately authorizes
starting this specific issue.
