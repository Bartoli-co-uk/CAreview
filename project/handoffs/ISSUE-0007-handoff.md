# Claude handoff: ISSUE-0007, round 0

**Claude issue task:** `ISSUE-0007 trim-scopes implementation`
**Approved issue:** `project/issues/ISSUE-0007.md` at this commit
**Starting SHA:** `d1df24760a878cf976f69fd153eb3954c3a5e028`
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-27`

## Outcome

Implemented in full. `auth.py`'s `SCOPES` constant is now exactly
`https://graph.microsoft.com/Policy.Read.All`, down from three requested
scopes (`Policy.Read.All`, `Application.Read.All`, `Directory.Read.All`), two
of which `graph.py` never used (it only calls
`identity/conditionalAccess/policies`). No behavioural change to the
device-code flow itself — same request shape, one fewer scope in the body.

## Changed files

| Path | Change and reason |
|---|---|
| `auth.py` | `SCOPES` reduced to a single-scope string constant; docstring comment updated to explain why. |
| `tests/test_auth.py` | Added `test_scopes_is_policy_read_all_only` (asserts the constant's exact value) and `test_devicecode_request_body_carries_only_policy_read_all` (parses the request body and asserts the `scope` field is exactly the one scope); added `urllib.parse` import. |
| `README.md` | "Read-only, least privilege" bullet updated to name `Policy.Read.All` only. |
| `docs/security-boundaries.md` | "Least privilege" bullet updated to name `Policy.Read.All` only, with the reason. |
| `project/issues/ISSUE-0007.md` | New issue record. |

## Decisions and assumptions

- No behavioural test changes were needed beyond the two additions above:
  every existing `tests/test_auth.py` test already referenced `auth.SCOPES`
  generically rather than hardcoding the old three-scope string, so they
  continue to pass unmodified against the new value.
- Did not touch `graph.py` or `server.py` — this issue's scope is the
  delegated scope constant only, per the roadmap's per-issue path boundary.

## Acceptance-criteria mapping

| Criterion | Implementation evidence | Status |
|---|---|---|
| `SCOPES` equals exactly the one scope | `auth.py:38` | Met |
| Unit test asserts the constant | `tests/test_auth.py::test_scopes_is_policy_read_all_only` | Met |
| Unit test asserts request body carries only that scope | `tests/test_auth.py::test_devicecode_request_body_carries_only_policy_read_all` | Met |
| Pre-existing tests pass unmodified in behaviour | Full suite run below | Met |
| README / security-boundaries no longer claim three scopes | `README.md:272-273`, `docs/security-boundaries.md:93-95` | Met |
| `unittest`, `py_compile`, `validate_repo.py` pass | See Verification below | Met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | `Ran 85 tests ... OK`, exit 0 | None — run locally, real network/tenant not used |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0, no output | None |
| Governance | `python3 scripts/validate_repo.py` | "Repository validation passed (67 required files checked)." | None |

The reviewer or CI must independently confirm required checks; this handoff is not test authority.

## Documentation

- `README.md` — least-privilege bullet corrected (in this change).
- `docs/security-boundaries.md` — least-privilege bullet corrected (in this change).

## Security and privacy

- Threat-model change: strictly narrows the delegated consent surface
  requested at sign-in; no new risk introduced.
- Residual risk/uncertainty: none identified for this issue.
- Protected action attempted: No.

## Review request

- Base SHA: `d1df24760a878cf976f69fd153eb3954c3a5e028`
- Head SHA: (this commit; recorded by the launcher)

## Repair round 1

Round-0 Codex review (`project/reviews/issues/ISSUE-0007-54e207a04b1c-codex.json`,
candidate `54e207a04b1c5f86cc18c3f4860977e4d8dd6f0d`) returned `BLOCKED`: one
required finding (`ISSUE-0007-F001`, low severity) plus sandbox
execution-evidence limitations that are an accepted residual under
`DECISION-015` and not independently repairable.

- **F001 fix:** `README.md`'s "Verify it offline" block still said "83
  tests"; the suite is now 85 (two tests added by this issue). Updated the
  comment to "85 tests" (`README.md:250`). No other user-facing doc referenced
  the stale count; `project/milestones/M1.md` and prior review records
  correctly keep "83 tests" as they describe the frozen M1 candidate, not the
  current tree.
- Rechecked after the fix: `python3 -m unittest discover -s tests` → 85
  passed, exit 0; `python3 -m py_compile $(git ls-files '*.py')` → exit 0;
  `python3 scripts/validate_repo.py` → "Repository validation passed (67
  required files checked)."
- This is round 1 of at most two permitted issue repair rounds.
