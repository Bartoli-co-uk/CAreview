# ISSUE-0017: Analyzer rule — admin-scoped sign-in frequency / no persistent browser

**Status:** `REVIEWING`
**Milestone:** `M4` — bound by roadmap v6 (analyzer rule-set expansion); `M4` itself is `PLANNED`, not started
**Approved roadmap:** `ROADMAP.md` version `6`, `APPROVED` (`DECISION-034`, binds `68655cc7b1e0a63db3d6b37debf834c126bb60e0`) — binds this issue to `M4`
**Start authorization:** `DECISION-041`
**Dependencies:** `None` (independent of `ISSUE-0015`/`ISSUE-0016`; sequenced after them as the third `M4` issue delivered)
**Branch:** `ai/ISSUE-0017-admin-signin-frequency-rule`
**Starting SHA:** `4812954` (tip after `ISSUE-0016`'s merge)
**Candidate SHA:** round 0 is this commit — the launcher records the full HEAD SHA

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
  weight 10, plus a `_check_admin_signin_frequency` function using the
  **effective-coverage algorithm** below (deliberately more precise than
  `_check_mfa_for_admins`'s existing pattern, which ignores `excludeRoles`
  and doesn't handle an `includeUsers: ["All"]` policy contributing role
  coverage — Codex's round-1 plan review, F-004, flagged that copying it
  verbatim would carry the same ambiguity into this new rule; the existing,
  already-accepted `mfa-admins` rule itself is unchanged by this issue):

  1. **Qualifying policies**: enabled policies where `signInFrequency.enabled`
     is true with either `frequencyInterval == "everyTime"` or (`type ==
     "hours"` and `1 <= value <= 4` — human-confirmed threshold), AND
     `persistentBrowser.mode == "never"` **exactly** — not merely
     `!= "always"` (Codex's round-2 plan review, F-001: the rule's own stated
     requirement is "no persistent browser session," and a missing/disabled/
     empty-string `persistentBrowser.mode` is not evidence that persistence
     is prohibited, only that it wasn't configured either way). A day-scale
     interval, a disabled/missing `signInFrequency`, or any
     `persistentBrowser.mode` other than exactly `"never"` (including
     `"always"`, empty, or absent) all disqualify a policy, even if some
     other part of it looks compliant.
  2. **Effectively covered roles, per qualifying policy**: if `"All"` is in
     `includeUsers`, the policy covers `ADMIN_ROLE_TEMPLATE_IDS` **minus**
     any of those role IDs present in `excludeRoles` (an all-users policy
     that excludes a specific admin role does not cover that role).
     Otherwise, the policy covers `(includeRoles ∩ ADMIN_ROLE_TEMPLATE_IDS)
     minus excludeRoles`.
  3. **PASS** iff the union of effectively-covered-roles across *all*
     qualifying policies equals `ADMIN_ROLE_TEMPLATE_IDS`. Non-qualifying
     policies (e.g. admin-scoped but with too-long a frequency) are simply
     excluded from the union — they never subtract from or block coverage
     a qualifying policy already established for the same role; this is
     the direct fix for F-004's "overlapping compliant/non-compliant
     policies" ambiguity.
- `README.md` — one new "What it checks" table row; update rule-count/total-
  weight sentence.
- `tests/test_graph.py` — extend the missing-fields/malformed-nested-objects
  tests for the two new keys' safe defaults, plus one positive-shape test.
- `tests/test_analyzer.py` — at least nine cases: (1) admin-scoped enabled
  policy with `signInFrequency` disabled → FAIL; (2) same policy with
  `signInFrequency` enabled at `frequencyInterval: "everyTime"` (or 1–4
  hours) and `persistentBrowser.mode: "never"`, full admin-role union → PASS;
  (3) same as (2) but `persistentBrowser.mode: "always"` → still FAIL;
  (3a) same as (2) but `persistentBrowser` entirely absent/disabled → still
  FAIL; (3b) same as (2) but `persistentBrowser.mode: ""` (present but no
  mode set) → still FAIL — (3), (3a), and (3b) together prove
  `mode == "never"` is required exactly, not merely "not always" (Codex's
  round-2 plan review, F-001); (4) a qualifying `includeUsers: ["All"]`
  policy that also `excludeRoles` one admin role, with no other policy
  covering that role → FAIL (proves the all-users-minus-exclusion
  computation); (5) a qualifying policy covering all admin roles, PLUS a
  second, non-qualifying policy (frequency disabled) also scoped to one of
  those roles → still PASS (proves a non-qualifying overlapping policy
  doesn't subtract established coverage);
  (6) two qualifying policies whose role sets only jointly cover
  `ADMIN_ROLE_TEMPLATE_IDS` (neither alone does) → PASS (proves the union,
  not a single-policy check).
- `tests/fixtures/strong_tenant.json` — one new, narrowly-scoped additive
  policy entry satisfying this rule without perturbing any pre-existing
  rule's pass/fail state (12 rules will pre-exist at this issue's baseline,
  assuming `ISSUE-0015` and `ISSUE-0016` land first per the sequencing
  above — the exact count is whatever `rules.RULES` holds at the actual
  implementation baseline, not a number fixed by this document).

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
   `test_graph.py` cases and all nine `admin-signin-frequency` analyzer
   cases.
2. `normalize_policy({})` gains exactly the two new top-level keys described
   above, both safely defaulted; no existing normalized field is removed,
   renamed, or reshaped.
3. The rule implements the effective-coverage algorithm exactly as specified
   (role coverage computed per qualifying policy, including the
   all-users-minus-`excludeRoles` case; union across qualifying policies
   only; non-qualifying policies never subtract established coverage) —
   not a single narrow-policy check, and not a verbatim copy of
   `mfa-admins`'s simpler pattern.
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

## Round history

| Round | Reviewed SHA | Outcome | Findings |
|---|---|---|---|

Round 0 not yet reviewed by Codex.
