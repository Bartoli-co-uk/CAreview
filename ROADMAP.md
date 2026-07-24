# Project roadmap

This is the canonical project roadmap. A new project should replace the placeholders below only after its brief has been approved.

**Current status:** `NOT APPROVED`
**Roadmap version:** `0`
**Approved brief:** `[project/brief/PROJECT_BRIEF.md and commit SHA]`
**Codex plan review:** `[path and reviewed SHA]`
**Human approval record:** `[path]`

No implementation may begin while the status is `NOT APPROVED`.

## How this roadmap is approved

1. Claude drafts the project brief from the human's description.
2. The human approves that exact brief.
3. A fresh Claude planning session drafts this roadmap.
4. A fresh, read-only Codex session independently reviews it.
5. Claude responds to every finding and revises the roadmap if needed.
6. Repeat review and repair no more than twice.
7. The human reviews the final roadmap, outstanding disagreements, and risks, then records approval of the exact version and commit.

No workflow loop may exceed five total iterations. A tighter limit always wins;
reaching either limit blocks for an exact human decision rather than permitting
an agent to weaken or ignore a finding.

Use `project/templates/roadmap.md` when replacing this baseline and `project/templates/decision.md` to record the approval. The human's verbatim description lives at `project/intake/PROJECT_DESCRIPTION.md`. Approval of the brief is not approval of the roadmap.

## Project outcome

<!-- Replace after brief approval. -->

`[One paragraph describing what will exist when the project is complete.]`

## Users and success measures

| User or stakeholder | Need | Measurable success criterion |
|---|---|---|
| `[user]` | `[need]` | `[measure]` |

## Constraints and non-goals

### Constraints

- `[Technical, legal, cost, time, platform, data, or operational constraint.]`

### Non-goals

- `[Explicitly excluded outcome.]`

## Architecture and security assumptions

- `[Architecture decision or link to its approved record.]`
- `[Data classification and trust-boundary assumption.]`
- `[Deployment and operational assumption.]`
- `[Known uncertainty that must be resolved before a named issue.]`

## Milestones

Each milestone must have a single frozen candidate commit and four fresh reviews: Claude general, Codex general, Claude security, and Codex security. Allow at most one general-remediation cycle and at most two security-remediation cycles. Every remediation creates a new candidate and reruns all four fresh reviews against that one SHA. Exhaustion blocks for the human. The human makes the milestone decision after seeing all four reports.

| ID | Outcome | Dependencies | Exit criteria | Status |
|---|---|---|---|---|
| `M1` | `[Outcome]` | `None` | `[Observable criteria]` | `PLANNED` |

## Issue sequence

Issues run sequentially unless the human explicitly approves a different arrangement. Keep them small enough for one fresh Claude issue task, up to two in-task repair rounds, and independent fresh Codex review processes.

| Order | Issue | Objective | Depends on | Acceptance and checks | Risk | Status |
|---:|---|---|---|---|---|---|
| 1 | `ISSUE-0001` | `[Small coherent objective]` | `None` | `[Criteria and commands]` | `[Low/medium/high and why]` | `PLANNED` |

## Verification strategy

- Unit checks: `[commands or not applicable]`
- Integration checks: `[commands or not applicable]`
- Security checks: `[commands or not applicable]`
- Documentation checks: `[commands or review method]`
- Clean-environment or onboarding check: `[method]`
- Evidence gaps that require human judgement: `[list]`

Agent-reported claims do not count as test evidence. Record actual commands, commit SHA, exit status, and limitations in the handoff or milestone report.

## Documentation plan

List the user, operator, API, architecture, security, migration, or release documentation that must change with each milestone.

- `M1`: `[documentation outcome]`

An issue cannot be complete when required documentation is missing or knowingly inaccurate.

## Risks and decisions

| ID | Risk or decision | Impact | Owner | Treatment or decision record | Review date |
|---|---|---|---|---|---|
| `RISK-001` | `[Description]` | `[Impact]` | `[Human owner]` | `[Mitigation or path]` | `[UTC date]` |

Critical or high security findings cannot use the default risk-acceptance path. Other material risk requires an exact human acceptance record with an owner, rationale, controls, and expiry or review date.

## Definitions of done

### Issue

- Approved scope and acceptance criteria are satisfied.
- Required checks ran against the candidate commit.
- Tests and documentation were updated in the same change.
- `scripts/run-codex-review.sh issue ...` or the PowerShell equivalent launched a fresh read-only Codex review of the exact base/head, and its committed report has no unresolved blocker.
- Repair rounds have not exceeded two.
- Residual risks and the human advance decision are recorded.
- Handoff, reviews, decision, issue state, and `project/status/CURRENT.md` are committed; the Claude issue task is ended before another issue begins.

### Milestone

- All planned issues and dependencies are complete.
- Claude and Codex general reviews pass against the frozen candidate.
- Claude and Codex security reviews pass against that same candidate.
- Critical and high findings are closed.
- Other material risks are repaired or explicitly accepted by the human where permitted.
- General remediation did not exceed one cycle, security remediation did not
  exceed two cycles, and no workflow loop exceeded five total iterations.
- Documentation, integration, and release-readiness evidence are complete.
- The human approves the exact milestone package.

### Project

- Every milestone is approved.
- Fresh full-project Claude and Codex general and security reviews are complete against one final commit.
- Installation, onboarding, rollback, support, security, and known limitations are accurate.
- The human records final approval.

## Change control

After approval, do not silently edit this roadmap. Proposed changes must state:

- the current approved version and commit;
- the exact proposed diff;
- the reason, effect on scope, sequence, cost, risk, and verification;
- which existing approvals or reviews become stale;
- the new human decision.

Keep previous versions in Git history. A changed roadmap requires a new version and exact approval.
