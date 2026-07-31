# Claude handoff: ISSUE-0017

**Claude issue task:** `ISSUE-0017 admin-signin-frequency-rule implementation`
**Approved issue:** `project/issues/ISSUE-0017.md` at this commit (bound to `M4`, roadmap v6, `DECISION-034`; start authorized by `DECISION-041`)
**Starting SHA:** `48129547a68239e8f733ce6b50b6a63407a35256` (tip after `ISSUE-0016`'s merge)
**Candidate SHA:** this commit — the launcher records the full HEAD SHA at review time
**Created at:** `2026-07-31`

## Outcome

Implemented in full. Adds the `admin-signin-frequency` analyzer rule exactly
as specified in `ISSUE-0017.md`, using the effective-coverage algorithm
(union of qualifying policies' coverage; all-users-minus-`excludeRoles`;
`persistentBrowser.mode == "never"` exactly, not merely `!= "always"`) rather
than a verbatim copy of `mfa-admins`'s simpler single-condition pattern.
`graph.normalize_policy` gained two strictly additive top-level keys.

## Changed files

| Path | Change and reason |
|---|---|
| `graph.py` | `normalize_policy` gains `signInFrequency` (`{"enabled", "type", "value", "frequencyInterval"}`) and `persistentBrowser` (`{"enabled", "mode"}`), both read from `sessionControls` and safely defaulted (`enabled` uses the same `_control_enabled` pattern already used for the `sessionControls` list; enum fields fall back to `""` on any value outside the documented set; `value` falls back to `None` on any non-`int`/bool input). `sessionControls`'s existing shape and test contract are unchanged. |
| `rules.py` | New `_qualifies_for_admin_signin_frequency` and `_effectively_covered_admin_roles` helpers plus `_check_admin_signin_frequency` and a new `Rule("admin-signin-frequency", ...)` entry (medium, weight 10). Qualifying = enabled, `frequencyInterval == "everyTime"` or (`type == "hours"` and `1 <= value <= 4`), AND `persistentBrowser.mode == "never"` exactly. Coverage per qualifying policy = `ADMIN_ROLE_TEMPLATE_IDS` minus `excludeRoles` when `"All" in includeUsers`, else `(includeRoles ∩ ADMIN_ROLE_TEMPLATE_IDS)` minus `excludeRoles`. PASS iff the union across all qualifying policies equals `ADMIN_ROLE_TEMPLATE_IDS`; non-qualifying policies are excluded from the union and never subtract established coverage. |
| `README.md` | "What it checks" table gains one row; rule-count/total-weight sentence updated (12 → 13 rules, 135 → 145 weight); the `rules.py` file-list row's count updated too. |
| `tests/test_graph.py` | Extended the malformed/missing-fields tests to assert both new keys' safe defaults, plus a new positive round-trip test (`test_normalize_round_trips_signin_frequency_and_persistent_browser`). |
| `tests/test_analyzer.py` | New `AdminSignInFrequencyTests` class with nine cases: frequency disabled → FAIL; `everyTime` + `never` full coverage → PASS; `1-4 hours` + `never` full coverage → PASS; `persistentBrowser.mode: "always"` → FAIL; `persistentBrowser` absent → FAIL; `persistentBrowser.mode: ""` → FAIL (these three together prove `mode == "never"` is required exactly, per Codex round-2 F-001); an `includeUsers: ["All"]` policy excluding one admin role, uncovered elsewhere → FAIL; a qualifying full-coverage policy plus a second, non-qualifying overlapping policy → still PASS; two qualifying policies whose role sets only jointly cover all admin roles → PASS. |
| `tests/fixtures/strong_tenant.json` | One new, narrowly-scoped additive policy (`...0010`, "Frequent re-auth for administrators, no persistent browser": admin-role scope, `signInFrequency.frequencyInterval: "everyTime"`, `persistentBrowser.mode: "never"`, no `grantControls`) satisfying only this rule — carries no `mfa`/`block`/`termsOfUse` control, so it cannot affect any other rule's evaluation. Verified the full suite stays at 100/no findings before committing. |

## Decisions and assumptions

- No assumptions beyond what `ISSUE-0017.md` specified for the rule logic.
  The `requires` list documents `conditions.includeUsers`,
  `conditions.includeRoles`, `conditions.excludeRoles`, `signInFrequency`,
  and `persistentBrowser`, all guaranteed top-level/nested keys in the
  normalized policy shape (`_field_declared_in_contract` confirms this via
  `test_requires_policy_fields_are_never_missing`, which runs generically
  over every rule in `rules.RULES` including this one).
- Unlike `ISSUE-0015`/`ISSUE-0016`, the issue file's own "Allowed paths"
  and acceptance criteria already anticipated the `strong_tenant.json`
  fixture addition (item 5 explicitly describes "one new, narrowly-scoped
  additive policy entry"), so no separate fixture-scope-amendment decision
  (the `DECISION-036`/`DECISION-039` pattern) was needed this time.
- `value`'s malformed-input handling treats Python `bool` as non-`int` for
  this field (i.e. `True`/`False` are not accepted as a frequency value)
  since Graph's own schema never sends a boolean there and accepting it
  would let a malformed `value: true` silently satisfy `1 <= value <= 4`
  (`True == 1` in Python) — a defensive choice, not called out in the issue
  text but consistent with "never raises" and "safely defaulted."

## Acceptance-criteria mapping

| Criterion (from `ISSUE-0017.md`) | Implementation evidence | Status |
|---|---|---|
| 1. Tests pass, including new `test_graph.py` and nine `admin-signin-frequency` cases | `python3 -m unittest discover -s tests` → 205 passed | Met |
| 2. `normalize_policy({})` gains exactly the two new keys, safely defaulted; no existing field removed/renamed/reshaped | `test_normalize_handles_missing_fields`'s new assertions; `sessionControls`'s own assertions unchanged | Met |
| 3. Effective-coverage algorithm implemented exactly (all-users-minus-`excludeRoles`; union across qualifying policies only; non-qualifying policies never subtract) | `_check_admin_signin_frequency`/`_effectively_covered_admin_roles`; `test_non_qualifying_overlapping_policy_does_not_subtract_coverage`, `test_union_of_two_qualifying_policies_covers_all_roles`, `test_all_users_policy_excluding_one_admin_role_fails_for_that_role` | Met |
| 4. README table/weight sentence match `rules.py` | Manual diff, both updated in this commit | Met |
| 5. `test_strong_tenant_scores_high` (or equivalent) still expects a full pass at the new total weight; no other rule's pass/fail state changes | Full suite green; `analyzer.analyze` on `strong_tenant.json` manually confirmed `score == 100`, `findings == []` before commit | Met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 205 passed, exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files checked) | none |

The reviewer or CI must independently confirm required checks; this
handoff is not test authority.

## Documentation

- `README.md`'s "What it checks" table and rule-count/weight sentence
  updated in this same change (both required by the issue's acceptance
  criteria).

## Security and residual risk

- Threat-model change: none — reads fields already present in the same
  already-fetched, already in-memory Graph response; no new Graph call,
  scope, or permission.
- Residual risk/uncertainty: none identified beyond the issue's own
  documented out-of-scope items (no threshold other than `everyTime`/1-4
  hours; the other three proposed `M4` rules are separate issues).
- Protected action attempted: No.

## Review request

- Base SHA: `48129547a68239e8f733ce6b50b6a63407a35256`
- Head SHA: this commit (the launcher records the full HEAD SHA)
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0017 48129547a68239e8f733ce6b50b6a63407a35256 <HEAD-SHA>`
- PowerShell: `.\scripts\run-codex-review.ps1 issue ISSUE-0017 48129547a68239e8f733ce6b50b6a63407a35256 <HEAD-SHA>`
- Areas needing special attention: the `persistentBrowser.mode == "never"`
  exactness (not `!= "always"`) and the all-users-minus-`excludeRoles`
  union-coverage computation are the two places most likely to hide a
  subtle logic error — a reviewer should re-derive both from `rules.py`
  rather than trust this handoff's claim.

## Round 1 repair

Round 0's fresh Codex issue review
(`project/reviews/issues/ISSUE-0017-079f5c72cb27-codex.json`) returned
`CHANGES_REQUIRED` with one real, medium-severity defect:

- **F-001**: `_qualifies_for_admin_signin_frequency` checked only
  `persistentBrowser.mode == "never"` and ignored
  `persistentBrowser.enabled`. A policy whose `persistentBrowser` control
  was explicitly disabled (`isEnabled: false`) but carried a stale
  `mode: "never"` from a prior configuration falsely qualified — contrary
  to `ISSUE-0017.md`'s own requirement that a disabled control disqualifies
  a policy "even if some other part of it looks compliant." Fixed by
  requiring `pb.get("enabled") is True and pb.get("mode") == "never"`
  (`rules.py`), with a new regression test
  (`test_persistent_browser_disabled_with_stale_never_mode_still_fails`)
  asserting the disabled/stale-`"never"` case still fails.

The review's other observations (76 `test_server.py` errors from the
sandbox denying loopback socket binding; `py_compile`/governance-validation
unavailable without a writable temp directory) are the same sandbox
execution-evidence limitation class already accepted repeatedly in this
project (most recently `ISSUE-0016`, `DECISION-040`), not a repair item —
all three required checks were independently run in this task's own
environment with real passing results below.

### Round 1 verification (real, run in this task's environment)

| Check | Exact command | Actual result/exit |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | 206 passed, exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files checked) |
