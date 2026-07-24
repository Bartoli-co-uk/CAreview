# Milestone [M1]: [name]

**Status:** `[PLANNED / REVIEWING / BLOCKED / AWAITING_HUMAN_APPROVAL / COMPLETE]`
**Approved roadmap:** `ROADMAP.md` version `[n]` at `[SHA]`
**Frozen candidate SHA:** `[this commit; every launcher report records the full SHA]`
**Tree identity:** `[digest or description]`

## Outcome and traceability

[Milestone outcome and how completed issues satisfy it.]

| Requirement/outcome | Completed issue | Evidence |
|---|---|---|
| `[requirement]` | `[ISSUE-ID]` | `[path/check]` |

## Verification evidence

| Check | Command/method | Candidate SHA | Result | Evidence gap |
|---|---|---|---|---|
| `[check]` | `[command]` | `[SHA]` | `[result]` | `[gap]` |

## Four mandatory reviews

| Order | Fresh review | Report path | Reviewed SHA | Outcome |
|---:|---|---|---|---|
| 1 | Claude general | `[path]` | `[SHA]` | `[outcome]` |
| 2 | Codex general | `[path]` | `[SHA]` | `[outcome]` |
| 3 | Claude security | `[path]` | `[SHA]` | `[outcome]` |
| 4 | Codex security | `[path]` | `[SHA]` | `[outcome]` |

Initial peer conclusions were withheld: `[yes/no; explain no]`

## Findings, remediation, and invalidation

- General findings: `[list/links]`
- Security findings: `[list/links]`
- Remediation issues: `[list]`
- General-remediation cycles used: `[0 or 1; maximum 1]`
- Security-remediation cycles used: `[0, 1, or 2; maximum 2]`
- Highest iteration count for any loop: `[number; absolute maximum 5]`
- Reviews invalidated and rerun: `[list/reason]`
- Critical/high findings remaining: `[must be none]`

Exhausting a remediation limit blocks for an exact human decision. It never
waives a required report or permits a finding to be downgraded.

## Documentation and release readiness

- Documentation audit: `[evidence]`
- Migration/rollback: `[evidence or N/A]`
- Onboarding/operations: `[evidence]`
- Known limitations: `[list]`

## Residual risks

| Risk | Severity | Treatment or exact human acceptance | Owner/review date |
|---|---|---|---|
| `[risk]` | `[severity]` | `[path]` | `[owner/date]` |

## Human decision

- Decision record: `[path]`
- Exact package/candidate approved: `[SHA and artifact paths]`
- Result: `[approved/rejected/remediation required]`

Reviews passing means only that they passed for the documented scope, SHA, and evidence. It is not a security certification.
