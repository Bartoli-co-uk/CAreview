# Claude handoff: ISSUE-0006, repair round 1

**Repair round 1** addresses Codex round-0 findings on candidate `30a75c425bf1`:
F-002 (alternate-port walkthrough URL), F-003 (narrow the no-disk-write claim),
F-004 (stale `CURRENT.md` next-action). No product code changed. See
`project/reviews/issues/ISSUE-0006-30a75c425bf1-claude-response.md`.


**Claude issue task:** `CAreview ISSUE-0006 (docs + E2E verification)`
**Approved issue:** `project/issues/ISSUE-0006.md` at `4e8e999ef2204ee7089726b205f5895dc73b38b0`
**Starting SHA (base):** `4e8e999ef2204ee7089726b205f5895dc73b38b0`
**Candidate SHA:** this commit (branch `ai/ISSUE-0006-docs-verification` HEAD; launcher binds the exact SHA)
**Created at:** `2026-07-24T16:06:32Z`

## Outcome

Finalized README: updated the stale "in development" status blockquote (sign-in,
Graph fetch, and analysis are all implemented, not upcoming), added an explicit
end-to-end walkthrough, and a known-limitations section naming RISK-001/002/004.
Performed a genuine clean-checkout verification (fresh `git clone` to a temp
directory) proving the documented steps work exactly as written. No product code
changed; no new features.

## Changed files

| Path | Change and reason |
|---|---|
| `README.md` | Replace stale MVP-status blockquote; add "End-to-end walkthrough" section; expand "Security and limitations" with RISK-001/002/004 |

## Acceptance-criteria mapping

| Criterion | Evidence | Status |
|---|---|---|
| Fresh clone: README steps run app + tests, no third-party installs | Clean-checkout verification below | met |
| `py_compile` + `unittest` clean | Verified in the clean checkout and in-place | met |
| Documented E2E walkthrough matches actual behaviour | README "End-to-end walkthrough"; steps followed verbatim in the clean checkout | met |
| Known limitations + heuristic-score caveat documented | README "Security and limitations" (RISK-001/002/004) | met |

## Verification requested and observed (clean-checkout, `/private/tmp/careview-clean-check`)

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Fresh clone | `git clone --branch ai/ISSUE-0006-docs-verification …` | succeeded | none |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 | none |
| Tests | `python3 -m unittest discover -s tests` | 80 passed, exit 0 | none |
| Governance | `python3 scripts/validate_repo.py` | passed (67 required files) | none |
| Run | `CAREVIEW_PORT=8899 python3 server.py` | started; `/api/health` → `{"status":"ok"}`; `/sample-data.json` → 200 | live sign-in against a real tenant still needs a human + protected-action approval |

## Documentation

- This issue is documentation-only; see README diff.

## Security and residual risk

- Threat-model change: none.
- Data/secret impact: none; no product code touched.
- Protected action attempted: No.

## Review request

- Base SHA: `4e8e999ef2204ee7089726b205f5895dc73b38b0`
- Head SHA: this candidate's commit (launcher binds the exact SHA).
- Review command: `./scripts/run-codex-review.sh issue ISSUE-0006 <BASE-SHA> <HEAD-SHA>`
- Gate policy: `DECISION-004` (static + evidence), `DECISION-007` (repair budget), merge under `DECISION-005`.
- Attention: README accuracy against actual server/UI behaviour; no residual stale wording.
