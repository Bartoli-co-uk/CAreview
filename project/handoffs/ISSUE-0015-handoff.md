# Claude handoff: ISSUE-0015

**Claude issue task:** `ISSUE-0015 location-restriction-rule implementation`
**Approved issue:** `project/issues/ISSUE-0015.md` at this commit (bound to `M4`, roadmap v6, `DECISION-034`; start authorized by `DECISION-035`)
**Starting SHA:** `ee29aa91346c5246d75ae48cdfdcf39137de0858`
**Candidate SHA:** this commit — the launcher records the full HEAD SHA at review time
**Created at:** `2026-07-31`

## Round 1 repair (this section)

Round 0's fresh Codex review (`project/reviews/issues/ISSUE-0015-1ff0b987d2f7-codex.json`)
returned `BLOCKED` with three findings. This repair addresses all three:

- **F-001** (candidate-identity mismatch): round 0's docs commit hardcoded a
  Candidate SHA (`bcfeacdb0e264db42badf4a6a945acb94f3fc3ff`) that was the
  *product* commit, one commit behind the actual reviewed HEAD
  (`1ff0b987d2f75377589e6c4875724b94aef81591`). Fixed by switching both
  `ISSUE-0015.md` and this handoff to the self-referential "this commit —
  the launcher records the full HEAD SHA" phrasing already used by
  `ISSUE-0014.md`, so the record can never point one commit behind the
  actual reviewed target again.
- **F-002** (fixture change outside allowed paths): the `strong_tenant.json`
  addition (policy `...0008`) was real and necessary — without it, the new
  rule would newly fire against `strong_tenant.json` and regress
  `test_strong_tenant_scores_high`. Per the issue's own stop conditions,
  this should have triggered a stop-and-rescope in round 0, not a silent
  change. Resolved after the fact by `DECISION-036`, which the human
  approved: `ISSUE-0015.md`'s allowed paths now explicitly include
  `tests/fixtures/strong_tenant.json`, scoped to exactly this one additive
  policy. No file content changed for this finding — only the issue's
  scope record.
- **F-003** (no durable start-authorization record): resolved by
  `DECISION-035`, recorded retroactively after the human confirmed they had
  authorized starting `ISSUE-0015`. `ISSUE-0015.md`'s stale "Not yet
  started" section (which contradicted its own `REVIEWING` status and the
  already-implemented candidate) is replaced with a round-history table
  naming this authorization and the round-0 finding it resolves.

No `rules.py`, `README.md`, or `tests/test_analyzer.py` source content
changed in this round — only `project/issues/ISSUE-0015.md`, this handoff,
`project/status/CURRENT.md`, and the two new decision records.

## Outcome

Implemented in full. Adds the `location-restriction-present` analyzer rule
exactly as specified in `ISSUE-0015.md`. No `graph.py` change was needed —
`conditions.includeLocations`/`excludeLocations` were already captured by
`normalize_policy`.

## Changed files

| Path | Change and reason |
|---|---|
| `rules.py` | New `_check_location_restriction` helper and `Rule("location-restriction-present", ...)` entry (medium, weight 10). Presence-only check: PASS if any enabled policy's `includeLocations ∪ excludeLocations` (case-insensitive) contains anything beyond the `all`/`alltrusted` sentinels. |
| `README.md` | "What it checks" table gains one row; rule-count/total-weight sentence updated (10 → 11 rules, 120 → 130 weight); the `rules.py` file-list row's count updated too. |
| `tests/test_analyzer.py` | Two new cases: `test_location_restriction_flagged_without_named_location` (fail-trip) and `test_location_restriction_not_flagged_with_named_location` (pass). Verified individually, not just via the full-suite run. |
| `tests/fixtures/strong_tenant.json` | One new, narrowly-scoped policy (`...0008`, group/app-scoped, no MFA/block grant control) satisfying only this rule — deliberately does **not** use `includeUsers: ["All"]` or an `mfa`/`block` control, so it does not join the "broad lockout" set `break-glass-excluded`/`no-overly-broad-block` already reason about. Verified directly: `analyzer.analyze()` on the updated fixture still returns `score: 100`, `findings: []`, `notEvaluable: ['break-glass-excluded']` — identical to before this change except for the new rule now passing. |

## Decisions and assumptions

- No assumptions beyond what `ISSUE-0015.md` specified. The rule's `requires`
  list matches the issue file exactly.
- The two test names were initially backwards on first draft (asserted
  `assertIn`/`assertNotIn` correctly, but the names described the opposite
  of what they asserted) — caught and corrected during self-review before
  this handoff, not left for the reviewer to find.

## Acceptance-criteria mapping

| Criterion (from `ISSUE-0015.md`) | Implementation evidence | Status |
|---|---|---|
| 1. Tests pass, including two new cases | `python3 -m unittest discover -s tests` → 190 passed | Met |
| 2. Rule present with documented metadata | `rules.RULES` entry; covered automatically by `test_every_rule_has_metadata` | Met |
| 3. README table/weight sentence match `rules.py` | Manual diff, both updated in this commit | Met |
| 4. No regression to the other 10 rules' pass/fail state | Directly verified: `analyzer.analyze()` on `strong_tenant.json` → `score: 100`, `findings: []` (unchanged) | Met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 190 passed, exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files checked) | none |
| Fixture regression | `analyzer.analyze(normalize_policy(p) for p in strong_tenant.json)` | `score: 100`, `findings: []`, `notEvaluable: ['break-glass-excluded']` | none — run directly in this environment, not asserted from memory |

The reviewer or CI must independently confirm required checks; this handoff is not test authority.

## Documentation

- `README.md`'s "What it checks" table and rule-count/weight sentence updated in this same change (both required by the issue's acceptance criteria).

## Security and residual risk

- Threat-model change: none — read-only analysis of already-fetched, already in-memory policy data; no new Graph call, scope, or permission.
- Residual risk/uncertainty: none identified. The rule deliberately does not resolve location GUIDs to friendly names/countries (out of scope per the issue, would need the separate `namedLocations` Graph endpoint).
- Protected action attempted: No.

## Review request

- Base SHA: `ee29aa91346c5246d75ae48cdfdcf39137de0858`
- Head SHA: this commit (the launcher records the full HEAD SHA)
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0015 ee29aa91346c5246d75ae48cdfdcf39137de0858 <HEAD-SHA>`
- PowerShell: `.\scripts\run-codex-review.ps1 issue ISSUE-0015 ee29aa91346c5246d75ae48cdfdcf39137de0858 <HEAD-SHA>`
- Areas needing special attention: the fixture-isolation reasoning (that the new policy entry doesn't join the "broad lockout" set) is the one place a reviewer should double-check independently rather than trust this handoff's claim.
