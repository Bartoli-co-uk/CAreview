# Claude handoff: ISSUE-0016

**Claude issue task:** `ISSUE-0016 terms-of-use-rule implementation`
**Approved issue:** `project/issues/ISSUE-0016.md` at this commit (bound to `M4`, roadmap v6, `DECISION-034`; start authorized by `DECISION-038`)
**Starting SHA:** `bb01fabd6e6984ee89bc3b56ab56ed2f81000c5e`
**Candidate SHA:** this commit — the launcher records the full HEAD SHA at review time
**Created at:** `2026-07-31`

## Outcome

Implemented in full. Adds the `terms-of-use-required` analyzer rule exactly
as specified in `ISSUE-0016.md`, including the `operator: "OR"` false-pass
guard (F-003) its own round-1 plan review flagged. `graph.normalize_policy`
gained a strictly additive `grantControls.termsOfUse` field.

## Changed files

| Path | Change and reason |
|---|---|
| `graph.py` | `normalize_policy`: `grantControls` gains `termsOfUse` (`_str_list(grant.get("termsOfUse"))`), defaulting to `[]`. `operator`/`builtInControls` unchanged. |
| `rules.py` | New `_check_terms_of_use` helper and `Rule("terms-of-use-required", ...)` entry (low, weight 5). PASS requires: enabled; meaningfully scoped (all-users with no excluded group/role, or admin-role scope with none of those specific roles excluded — mirrors `mfa-all-users`/`mfa-admins`'s exclusion discipline); `termsOfUse` non-empty; and, when `builtInControls` is also non-empty, `operator == "AND"` (an `"OR"` policy makes Terms of Use only an alternative, not a requirement). |
| `README.md` | "What it checks" table gains one row; rule-count/total-weight sentence updated (11 → 12 rules, 130 → 135 weight); the `rules.py` file-list row's count updated too. |
| `tests/test_graph.py` | Extended the malformed/missing-fields tests to assert `grantControls["termsOfUse"] == []`, plus a new positive round-trip test and an assertion that `grantControls` has exactly the three expected keys. |
| `tests/test_analyzer.py` | Four new cases: fail-trip (no `termsOfUse`), pass (`termsOfUse` + `operator: "AND"` alongside `mfa`), fail (`termsOfUse` present but `operator: "OR"` alongside `mfa` — the F-003 false-pass guard), fail (`termsOfUse`-only policy but scope excludes a group — the exclusion-discipline nuance). |
| `tests/fixtures/strong_tenant.json` | One new, narrowly-scoped policy (`...0009`, "Require Terms of Use for all users": all-users, `operator: "AND"`, `termsOfUse` only, no `builtInControls`) satisfying only this rule — deliberately carries no `mfa`/`block` control, so it cannot join `_broad_lockout_policies` (the set `break-glass-excluded`/`no-overly-broad-block` reason about, which only considers policies with `mfa`/`block` in `grantControls`). Added under `DECISION-039` after the un-amended candidate's test run showed the regression directly (`test_strong_tenant_scores_high`/`test_break_glass_evaluable_with_ids`: `96 != 100`). |

## Decisions and assumptions

- No assumptions beyond what `ISSUE-0016.md` specified for the rule logic
  itself. The `requires` list documents `conditions.includeUsers`,
  `conditions.includeRoles`, `conditions.excludeGroups`,
  `conditions.excludeRoles`, and `grantControls`, all of which
  `_field_declared_in_contract` confirms are guaranteed top-level/nested
  keys in the normalized policy shape.
- The fixture regression (and its resolution via `DECISION-039`, the same
  disposition as `ISSUE-0015`'s `DECISION-036`) was caught by actually
  running the required test suite before committing, not assumed away —
  the issue file's own "no fixture changes are needed" acceptance criterion
  turned out to be wrong for the same structural reason it was wrong for
  `ISSUE-0015`, and the human was asked before the fixture was touched.

## Acceptance-criteria mapping

| Criterion (from `ISSUE-0016.md`) | Implementation evidence | Status |
|---|---|---|
| 1. Tests pass, including new `test_graph.py` and four `terms-of-use-required` cases | `python3 -m unittest discover -s tests` → 195 passed | Met |
| 2. `normalize_policy({})`'s `grantControls` has exactly `operator`/`builtInControls`/`termsOfUse` | `test_normalize_handles_missing_fields`'s new `set(...)` assertion | Met |
| 3. Rule present with documented metadata | `rules.RULES` entry; covered automatically by `test_every_rule_has_metadata` | Met |
| 4. README table/weight sentence match `rules.py` | Manual diff, both updated in this commit | Met |
| 5. No regression to other rules' pass/fail state, except the one approved fixture addition | `DECISION-039`; full suite green at 195 tests | Met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 195 passed, exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files checked) | none |

The reviewer or CI must independently confirm required checks; this
handoff is not test authority.

## Documentation

- `README.md`'s "What it checks" table and rule-count/weight sentence
  updated in this same change (both required by the issue's acceptance
  criteria).

## Security and residual risk

- Threat-model change: none — reads a field already present in the same
  already-fetched, already in-memory Graph response; no new Graph call,
  scope, or permission.
- Residual risk/uncertainty: none identified beyond the issue's own
  documented non-goal (Terms of Use GUIDs are not resolved to agreement
  names/content — out of scope, would need the separate
  `identityGovernance/termsOfUse/agreements` Graph endpoint).
- Protected action attempted: No.

## Review request

- Base SHA: `bb01fabd6e6984ee89bc3b56ab56ed2f81000c5e`
- Head SHA: this commit (the launcher records the full HEAD SHA)
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0016 bb01fabd6e6984ee89bc3b56ab56ed2f81000c5e <HEAD-SHA>`
- PowerShell: `.\scripts\run-codex-review.ps1 issue ISSUE-0016 bb01fabd6e6984ee89bc3b56ab56ed2f81000c5e <HEAD-SHA>`
- Areas needing special attention: the `operator: "OR"` false-pass guard
  (F-003 from the plan review) and the meaningfully-scoped exclusion
  discipline are the two places most likely to hide a subtle logic error —
  a reviewer should re-derive both from `rules.py` rather than trust this
  handoff's claim.

## Round 1 repair

Round 0's fresh Codex issue review
(`project/reviews/issues/ISSUE-0016-bfa12f76053b-codex.json`) returned
`BLOCKED` with two findings, no implementation defect:

- **F-001** (medium, sandbox-only): the review sandbox could not complete
  any of the three required checks (denied `__pycache__` write, denied
  loopback socket binding, no writable temp directory) — the same class
  already accepted repeatedly in this project (most recently `ISSUE-0015`,
  `DECISION-037`). All three were independently run in this task's own
  environment with real passing results (below).
- **F-002** (low, advisory): `README.md`'s usage-section comment still said
  `188 tests`; fixed to `195 tests` in this round.

### Round 1 verification (real, run in this task's environment)

| Check | Exact command | Actual result/exit |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | 195 passed, exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files checked) |

## Round 2 repair

Round 1's fresh Codex issue review
(`project/reviews/issues/ISSUE-0016-3b2020bc30d0-codex.json`) returned
`BLOCKED` again: F-001 was the same sandbox-only class as round 0, but a
new F-002 (medium, REQUIRED) found `project/status/CURRENT.md` still
v5-shaped in its "Roadmap"/"Roadmap approval" rows (no v6/`DECISION-034`
mention) and several rows still describing round 0 as awaiting review
after round 1 had already been committed; `ISSUE-0016.md`'s own Candidate
SHA field also still said "round 0". This round resynchronizes all of
those rows and switches the Candidate SHA convention to the same
non-round-numbered form `ISSUE-0015` used, so it cannot go stale between
rounds again. No `graph.py`/`rules.py`/test-assertion source changed in
this round.

### Round 2 verification (real, run in this task's environment)

| Check | Exact command | Actual result/exit |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | 195 passed, exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files checked) |

This was the second and final permitted issue repair round. The round-2
fresh Codex review
(`project/reviews/issues/ISSUE-0016-5a63f84c7a58-codex.json`) returned
`BLOCKED` with zero content findings — its sole blocker is the review
sandbox's execution-evidence limitations, the same class already accepted
repeatedly in this project (most recently `ISSUE-0015`, `DECISION-037`).
Presented to the human for the advance/merge decision; not self-declared
as passing.
