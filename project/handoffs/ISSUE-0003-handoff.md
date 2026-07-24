# Claude handoff: ISSUE-0003, repair round 1

**Repair round 1** addresses Codex round-0 findings on candidate `2495c32df08e`:
F-001 (bearer-token exfiltration via unvalidated next links) — every URL is now
host-validated (`is_graph_url`) before the token is attached and HTTP redirects
are refused (`_NoRedirect`); F-003 (silent partial paging) — cycles and a
`MAX_PAGES` bound now raise `GraphError` instead of returning a partial success;
F-002 (break-glass contract) — the optional break-glass input is now specified
below with `graph.sanitize_object_ids`; F-004 (stale issue metadata) — the
duplicate Starting-SHA line is removed and the candidate SHA is bound. 46 tests
pass. See `project/reviews/issues/ISSUE-0003-2495c32df08e-claude-response.md`.


**Claude issue task:** `CAreview ISSUE-0003 (Graph client)`
**Approved issue:** `project/issues/ISSUE-0003.md` at `98a20bc479b55b1cdab5e8958ed3630bff0e044a`
**Starting SHA (base):** `98a20bc479b55b1cdab5e8958ed3630bff0e044a`
**Candidate SHA:** this commit (branch `ai/ISSUE-0003-graph-client` HEAD; launcher binds the exact SHA)
**Created at:** `2026-07-24T14:33:54Z`

## A3 resolution + normalized data contract (prerequisite)

The MVP calls **only** `GET /v1.0/identity/conditionalAccess/policies` — no
separate named-location or directory-role lookups. Policies reference users,
groups, roles, applications, and locations by identifier, and the analyzer
(ISSUE-0004) matches those identifiers (e.g. built-in admin role template IDs)
without extra Graph calls. Enrichment with display names would be a later issue.

Normalized policy contract (`graph.normalize_policy`):
`id, displayName, state, conditions{includeUsers, excludeUsers, includeGroups,
excludeGroups, includeRoles, excludeRoles, includeApplications,
excludeApplications, clientAppTypes, includePlatforms, excludePlatforms,
includeLocations, excludeLocations, signInRiskLevels, userRiskLevels},
grantControls{operator, builtInControls}, sessionControls[names]`.

**Optional break-glass input (contract for ISSUE-0004, Codex F-002).** The
analyzer's break-glass rule needs to know which object IDs are emergency-access
accounts, which cannot be inferred from policy JSON. The contract is a local,
user-supplied `break_glass_ids: list[str]` of Entra object-ID GUIDs. IDs are
sanitized to well-formed GUIDs via `graph.sanitize_object_ids` (non-GUID entries
dropped); they are held in memory only and never committed. When the input is
absent or empty, the break-glass rule is **not evaluable** (excluded from
scoring), never scored as pass or fail. ISSUE-0004 consumes exactly this shape.

## Changed files

| Path | Change and reason |
|---|---|
| `graph.py` | New: `GraphClient.fetch_policies` (bearer GET, `@odata.nextLink` paging, bounded loop), `normalize_policy`, transport-injectable, `GraphError` with stable codes; `urllib_graph_transport` normalizes network/malformed errors |
| `server.py` | Add `GET /api/policies`: 401 when no token, `GraphError` → structured 401/403/502, else `{policies, count}`; module-level `GRAPH` |
| `tests/test_graph.py` | New: single/multi-page paging, normalization, 401/403/network/empty-token errors |
| `tests/test_server.py` | Add `/api/policies` unauthenticated → 401 |

## Acceptance-criteria mapping

| Criterion | Evidence | Status |
|---|---|---|
| `/api/policies` returns normalized policies | `server._policies`, `graph.fetch_policies`; `test_single_page_normalizes` | met (mocked) |
| Multi-page followed via `@odata.nextLink` | `test_follows_next_link` | met |
| 403/consent → clear message | `GraphError("consent_required")`; `test_403_is_consent_required` | met |
| Unit tests: paging + normalization to contract | `tests/test_graph.py` | met |
| No policy JSON/token persisted | in-memory only; access logging silenced | met |
| Live fetch (protected) | deferred; requires human approval | not attempted (by design) |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 46 passed, exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | passes (out-of-band; sandbox cannot per DECISION-004) | none |

## Security and residual risk

- Threat-model change: reads sensitive tenant configuration into memory over TLS
  to `graph.microsoft.com` only; policy JSON never persisted or logged.
- Residual risk: unauthenticated loopback API (RISK-002, accepted); live fetch not
  exercised (protected action).
- Protected action attempted: No.

## Review request

- Base SHA: `98a20bc479b55b1cdab5e8958ed3630bff0e044a`
- Head SHA: this candidate's commit (launcher binds the exact SHA).
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0003 <BASE-SHA> <HEAD-SHA>`
- Gate policy: per `DECISION-004`, static review + author out-of-band evidence; human merge under `DECISION-005`.
- Attention: paging termination/bound; normalization safety on malformed policies; error-code mapping; no egress beyond Graph.
