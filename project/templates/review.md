# [Codex/Claude] [plan/issue/general] review: [subject]

**Outcome:** `[choose one role-appropriate value below]`
**Reviewer role:** `[role]`
**Provider/model:** `[provider and model if known]`
**Fresh session/task ID:** `[identifier if available]`
**Reviewed artifact:** `[path]`
**Reviewed SHA:** `[full SHA]`
**Base SHA:** `[SHA or N/A]`
**Created at:** `[UTC timestamp]`

- Plan or issue: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, `BLOCKED`, or
  `USER_DECISION_REQUIRED`.
- Milestone general: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, or
  `BLOCKED`.
- `REMEDIATION_REQUIRED` and `INCONCLUSIVE` are reserved for the separate
  milestone security-review template.

## Scope and inputs

- Requirements/issue: `[path and version]`
- Patch/tree: `[identity]`
- Verification evidence: `[path or summary]`
- Excluded or unavailable evidence: `[list]`
- Peer report withheld for blind review: `[yes/no/not applicable]`

## Summary

[Evidence-based conclusion. Do not claim security certification or human approval.]

## Findings

### [FINDING-ID]: [title]

- Classification: `[BLOCKER / REQUIRED / ADVISORY / QUESTION]`
- Severity: `[critical/high/medium/low/info]`
- Confidence: `[high/medium/low]`
- Blocking: `[yes/no]`
- Location: `[path:line or artifact section]`
- Expected: `[expected behaviour]`
- Observed: `[observed behaviour]`
- Evidence: `[verifiable evidence]`
- Impact: `[impact and preconditions]`
- Remediation: `[recommended change]`
- Verification: `[how to prove fixed]`
- Disposition: `[open/accepted/rejected-with-evidence/user-decision/closed]`

## Check accounting

| Required check | Evidence against reviewed SHA | Result |
|---|---|---|
| `[check]` | `[evidence]` | `[pass/fail/missing/inconclusive]` |

## Limitations and uncertainty

- `[What was not established]`

Any candidate source change invalidates this report. Saving this exact report as later metadata does not change the SHA it reviewed.
