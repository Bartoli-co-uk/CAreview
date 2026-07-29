# Claude security review: project-level final review — CAreview

**Outcome:** `BLOCKED`
**Reviewer role:** `Project security reviewer (Claude, independent, read-only)`
**Provider/model:** `Anthropic — claude-sonnet-5 (Claude Code harness)`
**Fresh session/task ID:** `same top-level session; conducted as an independent read-only review task per the milestone-security prompt (reused for project scope), with project/reviews/milestones/PROJECT-* deliberately not consulted before writing this report`
**Candidate SHA:** `5ce510871a17677fe862e3098972d9a85a6727a9`
**Tree identity:** clean; product/backend/frontend content unchanged from `802ea4d` (this candidate's only diff from that commit is `project/milestones/PROJECT.md` + `project/status/CURRENT.md`)
**Threat model:** `docs/security-boundaries.md`, all sections, project-wide
**Created at:** `2026-07-29T20:20:00Z`
**Peer conclusion withheld:** `yes`

This report states only that the review passed within its documented scope
and evidence. It is not a security certification.

## Scope and evidence

- Requirements and roadmap: `ROADMAP.md` v5 (`DECISION-029`), all M1/M2/M3
  risk registers, `docs/security-boundaries.md` in full.
- Changed attack surface since the last security review (`M3`'s round 2,
  `PASS_WITH_NOTES`): none — product/CI-config content at this candidate
  is identical to `861f401`, unchanged since `M3`'s acceptance.
- Tests/scanners reviewed: `python3 -m unittest discover -s tests` (188
  passed at this candidate), `cd frontend && npm test` (91 passed),
  `frontend/src/test/noDangerousSinks.test.ts`,
  `frontend/src/test/hostileMarkup.test.tsx`, `tests/test_ui_safety.py`.
- Unavailable or failed evidence: no `npm audit`/registry-based dependency
  scan performed this session (`RISK-009`'s already-disclosed gap); no
  live-tenant test (protected action).
- Network/tool limits: none for this Claude review (unlike the
  concurrently-run Codex reviews' sandboxed environment) — this review
  ran with full local tool access and independently re-executed every
  check it cites.

## Coverage

| Area | Evidence considered | Result/gap |
|---|---|---|
| Threats and abuse cases | Loopback-only binding unchanged since M1; single-user, no multi-tenant concern | No change, no new finding |
| Authentication/authorization/privilege | `AuthManager`'s `_generation` counter, `_token_handle`-scoped `abandon()`, app-only secret retention per `DECISION-014` — all unchanged since M2/M3, re-read directly in `auth.py` | No change, no new finding |
| Secrets/logs/data exposure | No secret in any test/fixture beyond the committed synthetic sentinel; no `print`/`logging` of tokens found by direct source read of `server.py`/`auth.py` | No change, no new finding |
| Inputs/injection/deserialization/paths/commands | `STATIC_FILES` allowlist (not directory serving); JSON body parsing with type checks before use; no `subprocess`/`eval`/`exec` in product code (`grep -rn "subprocess\|eval(\|exec(" server.py auth.py graph.py analyzer.py rules.py` returns nothing) | No change, no new finding |
| Dependencies/build/release/CI supply chain | `frontend/package-lock.json` (170 packages, `RISK-009`, accepted `DECISION-028`); `.github/workflows/validate.yml` — `contents: read` only, SHA-pinned actions, `npm ci` from lockfile | No new finding; `RISK-009` remains the one genuinely new project-wide trust boundary since M1/M2, already accepted |
| Network/external integrations | Microsoft Graph via `graph.py` (unchanged since M1); no new external endpoint in M3 | No change, no new finding |
| Configuration/unsafe defaults | CSP `default-src 'self'; base-uri 'none'; form-action 'none'` unchanged; loopback bind unchanged; no debug flag or verbose-error mode found in `server.py` | No change, no new finding |
| Privacy/retention/migration/deletion | No persistence in any mode, unchanged since M1; no migration exists | No change, no new finding |
| Governance/session/review integrity | **See F-001, below.** `project/milestones/PROJECT.md` names a frozen candidate (`802ea4d`) that does not match this review's actual candidate (`5ce5108`) | **Blocking finding** |

## Findings

### SEC-001 (project general's F-001, security framing): frozen-candidate binding mismatch blocks exact-candidate security evidence

- Fingerprint: `PROJECT-SEC-TARGET-IDENTITY-MISMATCH` (same fingerprint
  Codex security independently assigned)
- Category/reference: review/governance integrity, not a product CWE
- Severity: `high`
- Confidence: `high`
- Blocking: `yes`
- Affected location: `project/milestones/PROJECT.md` lines 4–5, ~53
- Evidence: launcher target and `git rev-parse HEAD` both `5ce5108…`;
  `PROJECT.md` names `802ea4d…` as the frozen candidate and binds its
  verification table to that SHA.
- Attack preconditions: none — this is a record-integrity defect, not an
  exploitable condition.
- Impact: per `AGENTS.md`, wrong-commit-bound evidence must block a
  security review regardless of how clean the underlying code actually
  is. I independently re-ran every cited check against the *correct*
  candidate (`5ce5108`) myself in this review and found nothing — but the
  committed record's own claims remain mis-bound until fixed, and the
  record, not my private verification, is what a future reader relies on.
- Exploitability: none directly; the risk is a future human or reviewer
  trusting stale/misattributed evidence.
- Recommended remediation: same as general review's F-001 — rebind
  `PROJECT.md` to the actual candidate SHA throughout.
- Verification method: confirm `git rev-parse HEAD` matches `PROJECT.md`'s
  "Frozen candidate SHA" field exactly at the next candidate.
- Disposition: `open`

### SEC-002 (project general's F-002, security framing): `README.md`'s risk-disclosure table is stale/incomplete

- Fingerprint: `PROJECT-SEC-DISCLOSURE-STALE`
- Category/reference: security documentation accuracy
- Severity: `medium`
- Confidence: `high`
- Blocking: `yes` (per the milestone-security prompt's requirement to
  cover documentation/evidence-gap accuracy; `ROADMAP.md`'s project-level
  definition of done separately names "known limitations accurate" as a
  required property)
- Affected location: `README.md`, "Known limitations" table
- Evidence: table's `ISSUE-0013`/abandon row says "Blocked pending a
  human decision" (stale — accepted `DECISION-027`); `RISK-009`
  (build-time supply chain) and `RISK-010` (onboarding regression) are
  both absent despite the table's own preamble claiming to list "the
  recorded, accepted residual risks."
- Attack preconditions: none directly — a reader relying on this table
  for an accurate risk picture would under-count the project's actual
  accepted residual risk surface, most notably the newer `RISK-009` (npm
  build-time supply chain), which is the one genuinely new trust
  boundary introduced since M1/M2.
- Impact: disclosure-accuracy defect, not a code vulnerability.
- Exploitability: none directly exploitable.
- Recommended remediation: same as general review's F-002.
- Verification method: diff `README.md`'s table against `ROADMAP.md`'s
  risk register for completeness and current status.
- Disposition: `open`

## Conclusion and limitations

No new critical or high **product** finding — every security-relevant
property re-checked in this review (rendering safety, auth scoping, CSP,
CI least-privilege, secret handling, no injection/command-execution
surface) holds unchanged from M1/M2/M3's own already-accepted state. The
`BLOCKED` outcome here reflects the same review-integrity rule Codex
security independently applied: a security review cannot pass when the
record's own claimed evidence is bound to the wrong commit, even when the
underlying code is sound and independently re-verified by this reviewer
against the correct SHA. This does not certify the project as secure,
compliant, or free of vulnerabilities.
