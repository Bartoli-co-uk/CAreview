# Claude handoff: ISSUE-0004, round 0

**Claude issue task:** `CAreview ISSUE-0004 (analyzer + rules + scoring)`
**Approved issue:** `project/issues/ISSUE-0004.md` at `e94ef5abad6e95ec899a7bca04e30e9dc3dbea81`
**Starting SHA (base):** `e94ef5abad6e95ec899a7bca04e30e9dc3dbea81`
**Candidate SHA:** this commit (branch `ai/ISSUE-0004-analyzer` HEAD; launcher binds the exact SHA)
**Created at:** `2026-07-24T14:59:34Z`

## Outcome

Implemented the data-driven analyzer: a declarative rule set, a heuristic 0-100
score (evaluable-weighted), severity-sorted findings, and a per-rule *not
evaluable* path so missing evidence is never scored. Verified offline against
sanitized strong/weak/incomplete fixtures. `/api/analysis` exposes it on live
policies (protected fetch).

## Changed files

| Path | Change and reason |
|---|---|
| `rules.py` | New: `Rule` dataclass + 9 starter rules with documented severity/weight/required-fields; each `check` returns pass/fail/not_evaluable + affected policy names; built-in admin role template IDs for the MFA-admins rule; break-glass rule consumes the ISSUE-0003 contract |
| `analyzer.py` | New: `analyze(policies, break_glass_ids)` → weighted 0-100 score (evaluable rules only), severity-sorted findings, `notEvaluable` list; a per-rule guard so a rule bug cannot crash the analysis; `scoreIsHeuristic: true` |
| `server.py` | Add `GET /api/analysis` (401 unauth; GraphError mapped; else score+findings) |
| `tests/test_analyzer.py` + `tests/fixtures/{strong,weak,incomplete}_tenant.json` | New: sanitized fixtures + tests (strong=100, weak=0, sorted findings, not-evaluable, break-glass pass/fail, deterministic, rule metadata) |
| `tests/test_server.py` | Add `/api/analysis` unauthenticated 401 + success |

## Scoring model (documented, RISK-004)

`score = round(100 * passed_weight / evaluable_weight)`. Rules whose required
data-contract fields (or the optional break-glass input) are absent are *not
evaluable* and excluded from both numerator and denominator. The score is a
heuristic (`scoreIsHeuristic: true`), not a compliance certification.

## Acceptance-criteria mapping

| Criterion | Evidence | Status |
|---|---|---|
| Tests pass | 62 passed | met |
| Strong scores high / weak low, deterministic | `test_strong_tenant_scores_high` (100), `test_weak_tenant_scores_low` (0), `test_deterministic` | met |
| Each rule documents weight/fields/severity | `rules.RULES`; `test_every_rule_has_metadata` | met |
| Findings severity-sorted | `analyzer.analyze` sort; `test_findings_sorted_by_severity` | met |
| Score labeled heuristic | `scoreIsHeuristic`; documented | met |
| Not-evaluable path | `test_incomplete_tenant_marks_not_evaluable`, `test_break_glass_*` | met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 62 passed, exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | passes (out-of-band; sandbox cannot per DECISION-004) | none |

## Security and residual risk

- Threat-model change: none new; operates on already-fetched in-memory policies.
- Data/secret impact: fixtures are sanitized (fake GUIDs, no real tenant data).
- Protected action attempted: No.

## Review request

- Base SHA: `e94ef5abad6e95ec899a7bca04e30e9dc3dbea81`
- Head SHA: this candidate's commit (launcher binds the exact SHA).
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0004 <BASE-SHA> <HEAD-SHA>`
- Gate policy: `DECISION-004` (static review + author evidence), `DECISION-007` (repair budget), merge under `DECISION-005`.
- Attention: scoring determinism; not-evaluable correctness; rule predicate edge cases; fixtures sanitized.
