# ISSUE-0003: Microsoft Graph client for Conditional Access policies

**Status:** `REPAIRING`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `3` at `125d74f6d4bfe85f1a727293064d0887f2d121c7`
**Dependencies:** `ISSUE-0002` (COMPLETE); A3 resolved + data contract recorded in the handoff (single endpoint; identifier matching, no enrichment)
**Branch:** `ai/ISSUE-0003-graph-client`
**Starting SHA:** `98a20bc479b55b1cdab5e8958ed3630bff0e044a`
**Candidate SHA:** `2495c32df08ee11a563122bde4a5fca6fe93fae1` (round 0); repair candidates rebind at review time

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

### A3 prerequisite (Codex F-003)

Before implementation, record the resolved A3 decision and the **normalized policy
data contract**: the exact fields the analyzer consumes (state, conditions,
users/groups/roles include+exclude, applications, grant/session controls,
client-app types, named-location references), and whether named locations /
directory-role assignments are fetched or deferred. ISSUE-0004 rules bind to this
contract.

The contract also defines an **optional local, user-supplied break-glass input**
(a small config of sanitized break-glass object IDs the user considers their
emergency-access accounts). Break-glass accounts cannot be inferred from CA policy
JSON alone (Codex F-002); the analyzer only evaluates the break-glass rule when
this input is supplied, and otherwise marks that rule *not evaluable*. No such IDs
are committed to the repository.

## Acceptance criteria

Completion is gated on the mocked checks (criteria 1–5). Criterion 6 (live fetch)
is a protected action, not a completion precondition (Codex F-002).

1. `/api/policies` returns policies normalized to the documented data contract.
2. Multi-page responses are fully followed via `@odata.nextLink`.
3. A `403`/consent error returns a clear, actionable message rather than a crash.
4. Unit tests cover paging and normalization to the data contract against mocked
   responses/fixtures (single page, multi-page, 403).
5. No policy JSON or token is written to disk or logs.
6. (Protected, post-approval) A live fetch against a **named** tenant returns that
   tenant's policies — performed only after separate human approval; evidence
   recorded without embedding real policy data.

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
- Protected actions (Codex F-002): a **live Graph fetch against a named tenant**
  requires the signed-in token and is gated behind the same separate human
  approval as ISSUE-0002's live sign-in. Adding any non-Graph egress host is a
  separate reviewable change.

## Stop conditions

- Any need for a write scope, a non-Microsoft egress host, or persistence of
  policy data; unresolvable A3 (named locations) ambiguity.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `ISSUE-0003-handoff.md` | `2495c32df08e…` | py_compile 0; 42 tests pass; validator pass | `ISSUE-0003-2495c32df08e-codex.json` | BLOCKED (F-001 SSRF, F-003 paging, F-002 contract, F-004 metadata) |
| 1 (repair) | `ISSUE-0003-handoff.md` | repair-1 candidate (launcher binds SHA) | py_compile 0; 46 tests pass; validator pass | pending re-review | pending |

Maximum two repair rounds; every Codex review is a fresh ephemeral read-only
process against the named SHA.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
