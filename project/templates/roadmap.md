# Roadmap: [project name]

Use this starter to replace the contents of the live root `ROADMAP.md` after the brief is approved.

**Status:** `DRAFT`
**Version:** `[1]`
**Approved brief:** `project/brief/PROJECT_BRIEF.md` at `[commit SHA]`
**Claude planning task:** `[identifier]`
**Codex plan review:** `[path and reviewed SHA]`
**Human approval:** `[Not recorded / decision path]`

## Outcome

[Observable project outcome.]

## Constraints and non-goals

- Constraint: `[constraint]`
- Non-goal: `[exclusion]`

## Architecture and security assumptions

- `[Decision or assumption, source, and point at which it must be resolved]`

## Milestones

| ID | Outcome | Dependencies | Exit criteria | Planned reviews | Status |
|---|---|---|---|---|---|
| `M1` | `[outcome]` | `None` | `[criteria]` | Claude + Codex general and security | `PLANNED` |

## Dependency-ordered issues

| Order | Issue | Objective | Depends on | Acceptance/checks | Documentation | Risk | Status |
|---:|---|---|---|---|---|---|---|
| 1 | `ISSUE-0001` | `[objective]` | `None` | `[criteria/checks]` | `[docs]` | `[risk]` | `PLANNED` |

## Verification strategy

- Unit: `[commands or N/A]`
- Integration: `[commands or N/A]`
- Security: `[commands or N/A]`
- Documentation/onboarding: `[checks]`
- Known evidence gaps: `[list]`

## Risks and decisions

| ID | Description | Impact | Owner | Treatment or decision | Review date |
|---|---|---|---|---|---|
| `RISK-001` | `[risk]` | `[impact]` | `[human owner]` | `[treatment]` | `[date]` |

## Definitions of done

### Issue

- Acceptance criteria, tests, documentation, fresh Codex review, and human advance decision are complete.

### Milestone

- All issues are complete and four fresh same-SHA milestone reviews pass with no unresolved blocker.
- General remediation uses at most one cycle, security remediation uses at most
  two cycles, and no loop exceeds five total iterations; exhaustion blocks for
  the human.

### Project

- Full-project general/security reviews, onboarding/release evidence, known limitations, and final human approval are complete.

## Planning reconciliation

| Round | Codex review | Claude response | Remaining decision |
|---:|---|---|---|
| 0 | `[path]` | `[path or summary]` | `[none or decision]` |

Maximum two repair rounds. Any remaining material disagreement must be shown to the human before exact roadmap approval.
No workflow loop may exceed five total iterations; the tighter two-round limit
above applies first.
