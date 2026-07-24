# Workflow gates

The repository is durable project memory. Every fresh task must first read `START_HERE.md`, `AGENTS.md`, `ROADMAP.md`, `docs/workflow.md`, `project/README.md`, and `project/status/CURRENT.md`, then summarize the recorded state and next allowed action before changing anything. Prior chat and model memory are not authoritative.

Follow this sequence:

1. Claude drafts the project brief; the human approves the exact brief.
2. Claude drafts the roadmap; a fresh read-only Codex task reviews it; Claude responds to every finding; the human approves the exact final roadmap.
3. One fresh Claude author task implements one approved issue at a time on an isolated branch or worktree. After real checks and a commit, Claude MUST run `./scripts/run-codex-review.sh issue <ISSUE-ID> <BASE-SHA> <HEAD-SHA>` or the documented PowerShell equivalent. The launcher starts a new ephemeral read-only Codex process against the exact SHA or diff and stores its report.
4. The same Claude issue task inspects the report. `CHANGES_REQUIRED` starts a bounded repair; each repair gets real checks, a new commit, and another launcher invocation so Codex re-reviews in another new ephemeral read-only process. Default maximum: two plan repair rounds and two issue repair rounds. Stop on `BLOCKED`, `USER_DECISION_REQUIRED`, uncertainty, protected action, missing evidence, or unavailable Codex. Never silently skip or relabel the gate.
5. At each milestone, freeze one candidate. All four reviews are required: a fresh blind Claude general review, a fresh blind Codex general review, a fresh blind Claude security review, and a fresh blind Codex security review against that same candidate. Permit at most one general-remediation cycle and at most two security-remediation cycles; every cycle creates a new candidate and reruns all four fresh reviews against that one SHA.
6. The human decides milestone and final approval and any permitted residual-risk acceptance.

Within a writer's own task, non-authoritative helper agents (`docs-scribe`, `status-scribe`) may draft documentation prose or the metadata-only status update. They never commit, satisfy a gate, or review; the responsible writer reviews, integrates, and commits their draft in the same coherent change, so the one-writer and documentation-with-behaviour rules still hold. Each role's model is governed by [`docs/model-assignment.md`](../../docs/model-assignment.md); reviews use the strong tier and a security review is never downgraded.

No implementation starts before both brief and roadmap approval. Only one implementation writer is active at a time. `PASS_WITH_NOTES` never advances automatically. A changed candidate invalidates its reviews.

Plan and issue outcomes are `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`,
`BLOCKED`, or `USER_DECISION_REQUIRED`. Milestone general reviews omit
`USER_DECISION_REQUIRED`; `REMEDIATION_REQUIRED` and `INCONCLUSIVE` are reserved
for milestone security. No review, repair, or reconciliation loop may exceed
five total iterations; exhaustion blocks for an exact human decision.

The launcher, prompts, and agent instructions are workflow conventions rather than a hard security boundary. Human approval and inspection remain required for consequential decisions.

When an issue completes or blocks, preserve the handoff, real check results, Codex report, reviewed SHA, and decision in repository files; then update `project/status/CURRENT.md` in a separate metadata-only workflow-status change that binds the reviewed product SHA. Product or source changes invalidate the review; recording metadata does not retroactively review the metadata commit. End the Claude task after recording status. Never reuse it for another issue through resume, continue, or fork; clearing is only for closing context. The next issue begins in a new top-level task that reads only the current repository sources listed above. This context hygiene does not delete or claim deletion of provider-side records.
