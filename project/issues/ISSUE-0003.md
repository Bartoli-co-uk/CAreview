# ISSUE-0003: Microsoft Graph client for Conditional Access policies

**Status:** `PLANNED`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `1` at `[SHA pending roadmap approval]`
**Dependencies:** `ISSUE-0002`
**Branch:** `ai/ISSUE-0003-graph-client`
**Starting SHA:** `[set at implementation start]`
**Candidate SHA:** `Not created`

## Objective

Fetch the tenant's Conditional Access policies from Microsoft Graph using the
in-memory token, handle paging, normalize them into a stable internal shape the
analyzer and UI consume, and surface consent/permission errors clearly.

## In scope

- `graph.py` — read-only `GET https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies`
  with bearer token, `@odata.nextLink` paging, and normalization to an internal
  policy model. Optionally fetch named locations if a starter rule needs them
  (resolve brief A3 before coding).
- `server.py` — `/api/policies` returns normalized policies (or a structured
  error, e.g. 403 → "admin consent to Policy.Read.All required").
- `tests/` + `tests/fixtures/` — mocked Graph responses (single page, multi-page,
  403) and a normalization test.

## Out of scope

- Scoring/findings (ISSUE-0004) and rendering (ISSUE-0005).
- Any write to Graph; strictly read-only.

## Allowed paths

- `graph.py`, `server.py`, `tests/**`

## Acceptance criteria

1. `/api/policies` returns the tenant's normalized CA policies for a signed-in user.
2. Multi-page responses are fully followed via `@odata.nextLink`.
3. A `403`/consent error returns a clear, actionable message rather than a crash.
4. Unit tests cover paging and normalization against mocked responses/fixtures.
5. No policy JSON or token is written to disk or logs.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Manual fetch | Signed-in run → open `/api/policies` | tenant policies returned |

## Documentation

- README: note the scopes used and the consent requirement.
- If named locations/roles are added, document why in the handoff.

## Security and privacy impact

- Threat-model delta: reads sensitive tenant configuration into memory.
- Data/secret impact: policy JSON is sensitive; keep in memory, never persist/log.
- Dependency/supply-chain impact: none; `urllib` only.
- Protected actions: none; adding any non-Graph egress host is reviewable.

## Stop conditions

- Any need for a write scope, a non-Microsoft egress host, or persistence of
  policy data; unresolvable A3 (named locations) ambiguity.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `[path]` | `[SHA]` | `[path/summary]` | `[path]` | `[outcome]` |

Maximum two repair rounds; every Codex review is a fresh ephemeral read-only
process against the named SHA.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
