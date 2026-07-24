# Author and reviewer boundaries

- Claude owns requirements, planning, implementation, tests, documentation, and repair. Claude cannot approve its own output.
- Codex is the independent plan, issue, milestone, and security reviewer. Review tasks are read-only and do not implement their own fixes.
- Required reviewers do not delegate to subagents, spawn other agents, or ask
  another agent to reach their conclusions.
- Non-authoritative helper agents (`docs-scribe`, `status-scribe`) may draft documentation prose or status metadata inside the owning writer's task. They never commit, satisfy a gate, or act as a reviewer; the single responsible writer reviews, integrates, and commits their draft in the same change. This is a drafting aid to the author, not a delegation of any review.
- Each role's model is assigned in [`docs/model-assignment.md`](../../docs/model-assignment.md); a security review always runs on the strong tier and is never downgraded.
- Every Codex review and re-review uses a new ephemeral read-only process, not resume, continue, fork, cleared chat, or accumulated memory. A new process rebuilds context from the repository source-of-truth files. If freshness cannot be established, label the result advisory or blocked.
- Initial peer reviews are blind: do not show one reviewer's conclusions to the other before both reports exist.
- Bind every code review to an exact commit SHA or immutable diff. Any later product or source change invalidates it. A later metadata-only report/status record must identify the reviewed product SHA and must not imply that its own metadata commit was reviewed.
- Findings include evidence, location, severity, confidence, expected and observed behavior, remediation, and verification.
- Missing, stale, contradictory, wrong-target, or inconclusive evidence blocks advancement. Critical and high security findings always block.
- Only the human may approve artifacts, protected actions, milestone/final completion, or a precisely scoped and time-bounded residual risk.
- Every milestone requires four separate fresh reviews against one frozen candidate: Claude general, Codex general, Claude security, and Codex security. One report cannot substitute for another.
- Permit at most one milestone general-remediation cycle and at most two
  milestone security-remediation cycles. No loop may exceed five total
  iterations. Exhaustion blocks for the human.
- Disabled auto-memory and fresh tasks reduce context contamination; they do not erase provider-side records or prove zero retention.
