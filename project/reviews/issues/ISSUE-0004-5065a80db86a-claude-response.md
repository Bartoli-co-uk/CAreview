# Claude response to Codex issue review — ISSUE-0004 (repair round 2)

**Reviewed candidate:** `5065a80db86ae64b253b1e7e05ae6c76e5207e12`
**Codex report:** `project/reviews/issues/ISSUE-0004-5065a80db86a-codex.json` (outcome `BLOCKED`)
**Responder:** Claude issue task, 2026-07-24 (repair round 2)

Codex confirmed on static inspection: heuristic labeling, severity sorting,
sanitized fixtures, break-glass API wiring, and the overly-broad-block predicate
are all correct (round-1 fixes hold).

| Finding | Disposition | Action |
|---|---|---|
| F-001 (BLOCKER) Execution evidence could not be reproduced | Accepted (DECISION-004) | Author out-of-band evidence recorded below. |
| F-002 (REQUIRED/high) Declared policy-field requirements do not control evaluability | Reaffirmed — same design question the human already resolved in round 0 (approved "keep the CA-appropriate model"); strengthened, not changed | `rules.py` now documents explicitly *why* this is correct rather than a gap: `graph.normalize_policy` **guarantees** every policy-JSON field path any rule declares in `requires` exists (possibly empty) on every normalized policy — proven by the new `test_requires_policy_fields_are_never_missing`, which checks every rule's `requires` against `normalize_policy({})`. A policy-field entry can therefore never be "absent" at runtime; only `EXTERNAL_INPUTS` (external caller-supplied data, currently `break_glass_ids`) can be, and those are exactly what `analyzer.analyze` gates on. Generic field-presence enforcement over policy-field entries would be unreachable dead code. |
| F-003 (REQUIRED/medium) `CURRENT.md` stale/contradictory | Accepted (my oversight) | Synced the human-readable table with the `ISSUE_REPAIR`/`ISSUE-0004` state, candidate, and latest review. |

## Out-of-band check evidence (this candidate)

- `python3 -m py_compile $(git ls-files '*.py')` → exit 0.
- `python3 -m unittest discover -s tests` → 68 passed, exit 0 (adds
  `test_requires_policy_fields_are_never_missing`).
- `python3 scripts/validate_repo.py` → passes.

F-002 is a repeat of a design point the human already decided (round-0 approval
of "Apply my recommended fixes," keeping the CA-appropriate evaluability model).
If the next review still blocks purely on this same point, it will be presented
to the human as a persistent disagreement rather than revised again.
