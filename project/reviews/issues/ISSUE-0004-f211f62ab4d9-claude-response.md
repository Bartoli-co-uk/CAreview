# Claude response to Codex issue review — ISSUE-0004 (round 0 → repair 1)

**Reviewed candidate:** `f211f62ab4d941ba53f77d1d02e6e9819596de44`
**Codex report:** `project/reviews/issues/ISSUE-0004-f211f62ab4d9-codex.json` (outcome `BLOCKED`)
**Responder:** Claude issue task, 2026-07-24 (repair round 1; approach approved by the human)

| Finding | Disposition | Action |
|---|---|---|
| F-001 (REQUIRED/high) Required-field metadata does not control evaluability | Accepted (CA-appropriate model, human-approved) | The analyzer now enforces declared **external-input** requirements (`rules.EXTERNAL_INPUTS`, currently `break_glass_ids`): a rule needing an input the caller didn't supply is not-evaluable, driven by `requires`. The model is documented in `rules.py`/`analyzer.py`: for CA, absence of a protective policy is a genuine FAIL, not "missing evidence"; not-evaluable applies to external inputs and the empty-tenant case. Tests cover it. |
| F-002 (REQUIRED/medium) Overly-broad-grant rule absent | Accepted | Added `no-overly-broad-block` (enabled all-users + all-apps block with no exclusions → finding) with weight/severity/fields/rationale/remediation; positive + negative + fixture tests. |
| F-003 (REQUIRED/medium) API cannot consume break-glass input | Accepted | `POST /api/breakglass` (same-origin) sanitizes GUIDs to an in-memory store; `/api/analysis` passes them into `analyze`; tests for supplied/invalid/cleared and origin gate. |
| F-004 (REQUIRED/high) Break-glass passes partial exclusions | Accepted | The rule now requires every break-glass ID excluded from **every** applicable enabled broad lockout policy; reports non-compliant policy names (never the account IDs). Fixtures updated; pass/fail tests added. |
| F-005 (REQUIRED/medium) Analyzer docs stale/missing | Accepted | README "Verify it" now documents the offline fixtures, the deterministic test command, the scoring formula, the not-evaluable model, and the heuristic (non-compliance) meaning. |

## Out-of-band check evidence (repaired candidate)

- `python3 -m py_compile $(git ls-files '*.py')` → exit 0.
- `python3 -m unittest discover -s tests` → 67 passed, exit 0.
- `python3 scripts/validate_repo.py` → passes.

Remaining review limitation is the execution-evidence sandbox constraint
(DECISION-004). A fresh re-review follows.
