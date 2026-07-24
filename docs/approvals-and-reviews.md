# Approvals and reviews

This workflow uses explicit, human-operated gates. Nothing in the repository technically forces a provider or user to obey them, so approvals and review bindings must be visible and checked deliberately.

## What makes an approval exact

Record approvals using `project/templates/decision.md`. An approval should include:

- decision type;
- artifact path, version, and commit SHA;
- relevant candidate or target SHA;
- exact scope and exclusions;
- accepted consequence;
- approver identity as the human provides it;
- UTC decision time;
- expiry or review date when relevant;
- the human's approval words copied verbatim or linked to a durable source.

If the artifact, commit, action, target, scope, or material assumptions change, the approval is stale. Broad consent does not cover protected actions, residual risk, or later roadmap versions.

An agent may prepare the record but must not fabricate the human's words, identity, or decision.

## Mandatory human gates

Human approval is required for:

1. The exact project brief.
2. The exact final roadmap after independent Codex review.
3. Any protected action or external side effect listed in `AGENTS.md`.
4. An issue advance or merge when the chosen operating mode is manual.
5. Any material ambiguity, scope change, or unresolved reviewer disagreement.
6. Any permitted residual-risk acceptance.
7. Every milestone package after four required reviews.
8. Final project completion.

No autonomy convention may bypass brief approval, roadmap approval, protected actions, security blockers, or risk acceptance.

## Review binding

Every report must record:

- review role and provider;
- fresh session or task identifier if available;
- reviewed artifact and exact commit SHA;
- tree or patch identity when useful;
- inputs and verification evidence considered;
- checks not available;
- outcome;
- findings and limitations;
- creation time.

A review is stale after any code or relevant documentation change. A report for a different SHA, a dirty working tree, or unclear target is not valid evidence.

## Finding format

Every material finding should include:

- stable ID or fingerprint;
- category and short title;
- severity and confidence;
- whether it blocks;
- affected path and location;
- expected and observed behaviour;
- evidence;
- impact and likely preconditions;
- recommended remediation;
- verification method;
- disposition and owner.

Do not hide uncertainty inside a passing summary. Plan, issue, and milestone
general reviews use `BLOCKED` when evidence is insufficient. Milestone security
reviews may use `INCONCLUSIVE`. A required reviewer must reach its own conclusion
without delegating to a subagent or calling another agent.

## Plan and issue review outcomes

| Outcome | Meaning | Default next step |
|---|---|---|
| `PASS` | Acceptance criteria and review scope are satisfied with no unresolved blocker | Human may approve advance |
| `PASS_WITH_NOTES` | No blocker, but visible limitations or follow-up remain | Human decides; no automatic advance |
| `CHANGES_REQUIRED` | One or more findings require repair | Claude planning/issue task repairs within scope, then checks and a fresh Codex re-review |
| `BLOCKED` | Review cannot complete safely or prerequisites are missing | Stop and request an exact human or environmental resolution |
| `USER_DECISION_REQUIRED` | Evidence supports more than one material product or risk choice | Human chooses; agent must not infer |

Those five values are the complete outcome set for both roadmap and issue
reviews. Milestone general reviews use `PASS`, `PASS_WITH_NOTES`,
`CHANGES_REQUIRED`, or `BLOCKED`. Milestone security reviews use `PASS`,
`PASS_WITH_NOTES`, `REMEDIATION_REQUIRED`, `BLOCKED`, or `INCONCLUSIVE`.
`REMEDIATION_REQUIRED` and `INCONCLUSIVE` are reserved for milestone security.

## Planning disagreement

Codex classifies roadmap findings as `BLOCKER`, `REQUIRED`, `ADVISORY`, or `QUESTION`. Claude answers each one as:

- `accepted`;
- `partially_accepted`;
- `rejected_with_evidence`;
- `requires_user_decision`.

Retain each roadmap version and report in Git. Use at most two repair rounds. If a material disagreement remains, present both positions without advocacy, along with evidence, consequence, and the effect on implementation. A plan reviewer may return `USER_DECISION_REQUIRED` when the evidence supports more than one material choice. The human decides whether to revise, defer, narrow, or reject the roadmap.

## Issue repair limit

The initial review may be followed by no more than two Claude repair and Codex re-review rounds. Exceeding the limit stops the issue; it does not permit downgrading findings or continuing silently.

In the lean issue loop, one top-level Claude author task owns the issue and its maximum two repair rounds. Each Codex review or re-review is still a separate fresh ephemeral process. End the Claude task when the issue completes or blocks, and start the next issue in a new task from repository files only.

Use `scripts/run-codex-review.sh` or its PowerShell equivalent for every issue review. Exit `0` is the only automatic pass. Exit `10` needs a human decision; `20`, `30`, `40`, `64`, `65`, and `69` all stop automatic progression. Missing tools, authentication, output, or a valid outcome never permits review bypass.

No review, repair, or reconciliation loop may exceed five total iterations.
Tighter limits, including the two-round planning and issue limits, always win.
Limit exhaustion blocks for an exact human decision; it never makes a report
optional. The initial run is iteration one; each repair, rerun, or
reconciliation pass adds one.

## Four milestone reviews

Every milestone and the final project require:

1. Fresh Claude general review.
2. Fresh Codex general review.
3. Fresh Claude security review.
4. Fresh Codex security review.

The two initial general reports are independent and blind to each other's conclusion. The same applies to the two security reports. All four reports bind to one frozen candidate SHA.

Any repair that creates a new milestone candidate invalidates the entire
four-report set. Rerun both general reviews and both security reviews against
the same new commit, regardless of which review found the defect.

Permit at most one milestone general-remediation cycle and at most two milestone
security-remediation cycles. Every cycle creates a new candidate and reruns all
four fresh reviews. If the relevant finding remains after its final
permitted cycle, or if the absolute five-iteration cap is reached first, the
milestone blocks for a human decision.

Missing, malformed, stale, wrong-SHA, contradictory, or evidence-free reports block the milestone. Scanner or check failure is `INCONCLUSIVE`, not a pass. Critical and high security findings always block.

## Risk acceptance

The default workflow does not allow acceptance of critical or high security findings. For another material risk, use `project/templates/risk-acceptance.md` and bind the acceptance to:

- finding ID and report;
- exact reviewed SHA and affected scope;
- named human approver and risk owner;
- rationale and business need;
- compensating controls and their verification;
- expiry or review date;
- reopening trigger.

An agent cannot create, broaden, renew, or infer acceptance. A changed SHA or expired record makes it invalid unless the record explicitly defines a still-valid non-code scope.

## Review language

Use restrained conclusions such as:

> The required reviews passed for the named commit under the documented scope and available evidence.

Do not claim that a project is secure, vulnerability-free, certified, compliant, or suitable for a regulated purpose based solely on agent reviews.
