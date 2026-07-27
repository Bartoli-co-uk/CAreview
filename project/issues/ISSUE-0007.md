# ISSUE-0007: Trim delegated Graph scope to Policy.Read.All

**Status:** `REVIEWING`
**Milestone:** `M2`
**Approved roadmap:** `ROADMAP.md` version `4` at `9e5ba6d2f6c2b7f7efa81dcfc415e1f787aaa458` (approved by `DECISION-015`)
**Dependencies:** `None` (brief v2 approved, `DECISION-013`)
**Branch:** `ai/ISSUE-0007-trim-scopes`
**Starting SHA:** `d1df24760a878cf976f69fd153eb3954c3a5e028`
**Candidate SHA:** `this commit (branch HEAD); the launcher records the full SHA`

## Objective

Trim `auth.py`'s delegated `SCOPES` constant from three requested Graph scopes
to the one actually used, reducing consent-screen friction for the same read
behaviour, ahead of the M2 app-only work that touches the same constant.

## In scope

- `auth.py` — `SCOPES` reduced to exactly `https://graph.microsoft.com/Policy.Read.All`.
- `tests/test_auth.py` — assertions that the constant and the device-code
  request body carry only that one scope.
- `README.md`, `docs/security-boundaries.md` — scope-count wording corrected
  to match.

## Out of scope

- Any app-only/client-credentials code (`ISSUE-0008` onward).
- `graph.py`, `server.py`, `web/` — untouched.

## Allowed paths

- `auth.py`, `tests/test_auth.py`, `README.md`, `docs/security-boundaries.md`

## Acceptance criteria

1. `auth.py`'s `SCOPES` equals exactly `"https://graph.microsoft.com/Policy.Read.All"`.
2. A unit test asserts the constant's exact value.
3. A unit test asserts the device-code request body's `scope` form field
   carries only that one scope.
4. Every pre-existing test in `tests/test_auth.py` still passes with no
   behavioural change to the device-code flow itself.
5. `README.md` and `docs/security-boundaries.md` no longer claim three
   delegated scopes.
6. `python3 -m unittest discover -s tests`, `python3 -m py_compile $(git ls-files '*.py')`,
   and `python3 scripts/validate_repo.py` all pass.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | all pass (85 tests) |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

## Documentation

- `README.md`: "Read-only, least privilege" bullet now names `Policy.Read.All`
  only.
- `docs/security-boundaries.md`: "Least privilege" bullet now names
  `Policy.Read.All` only, with the reason (`graph.py` calls only
  `identity/conditionalAccess/policies`).

## Security and privacy impact

- Threat-model delta: reduces the delegated consent surface; strictly a
  narrowing, not a widening. No new risk.
- Data/secret impact: none — no secret exists in this issue's scope.
- Dependency/supply-chain impact: none.
- Protected actions: none. No live tenant sign-in performed.

## Stop conditions

- None encountered. No ambiguity, no path expansion beyond the allowed list,
  no protected action attempted.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `project/handoffs/ISSUE-0007-handoff.md` | `54e207a04b1c5f86cc18c3f4860977e4d8dd6f0d` | 85 tests pass; compile clean; validator passed | `project/reviews/issues/ISSUE-0007-54e207a04b1c-codex.json` | `BLOCKED` — F001 (README stale 83-test count) + sandbox execution-evidence limitations (accepted residual, `DECISION-015`) |
| 1 | `project/handoffs/ISSUE-0007-handoff.md` (Repair round 1 section) | `79f28638411dd82e04cf3d836baef86ad664cb44` | 85 tests pass; compile clean; validator passed | `project/reviews/issues/ISSUE-0007-79f28638411d-codex.json` | `BLOCKED` — F001 (second stale 83-test count in README) + F002 (CURRENT.md/ISSUE-0007.md not synced with round-0 review) + sandbox execution-evidence limitations (accepted residual) |
| 2 | `project/handoffs/ISSUE-0007-handoff.md` (Repair round 2 section) | `b314d82087f36b5fadae3119410e838ec2255997` | 85 tests pass; compile clean; validator passed | `project/reviews/issues/ISSUE-0007-b314d82087f3-codex.json` | `BLOCKED` — zero findings; sole blocker is the sandbox execution-evidence limitation (accepted residual, `DECISION-015`) |

Maximum two repair rounds — **both used**. Round 2 was the last permitted
repair round; no further Claude-initiated repair may occur in this task.
Every Codex review/re-review must be a new ephemeral read-only process
against the named SHA. No workflow loop may exceed five total iterations;
the tighter two-round issue limit applies first, and exhaustion blocks for
the human.

## Completion

- Final reviewed product SHA: `b314d82087f36b5fadae3119410e838ec2255997` — clean of
  all actionable findings; `BLOCKED` solely on the accepted sandbox
  execution-evidence residual.
- Human advance/merge decision: `pending` — per `AGENTS.md`'s completion
  standard and the `DECISION-010` precedent for the analogous ISSUE-0006
  case, this requires an explicit human decision even though no product
  defect remains; this Claude task does not decide it.
- Merge/result SHA: `pending`
- Residual risks or follow-up: none identified beyond the accepted,
  previously-approved sandbox execution-evidence limitation.
- Status record updated: this commit.
