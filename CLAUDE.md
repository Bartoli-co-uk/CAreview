@AGENTS.md

# Claude Code

Claude is the requirements, planning, and implementation author. Claude may self-review, but may never approve its own brief, roadmap, implementation, milestone, security finding, or residual risk.

At the start of every fresh task, before changing anything, read `START_HERE.md`, `AGENTS.md`, `ROADMAP.md`, `docs/workflow.md`, `project/README.md`, and `project/status/CURRENT.md`. Summarize the recorded workflow state, the relevant approvals, and the next allowed action. Repository files are the source of truth; do not rely on a previous chat or auto-memory.

Use plan mode for analysis when helpful. Permission to write a draft brief or roadmap is not approval of that artifact. Product implementation remains blocked until the human separately approves the exact brief and reviewed roadmap. Use one writer at a time and keep implementation within the approved issue. After committing an issue, always launch its fresh Codex review with `./scripts/run-codex-review.sh issue <ISSUE-ID> <BASE-SHA> <HEAD-SHA>` (or the documented PowerShell equivalent), then follow the bounded repair and re-review loop. Never silently skip this gate.

One fresh Claude author task owns one issue, including at most two repair rounds. Every Codex review and re-review is a new ephemeral read-only process. When the issue completes or blocks, save its evidence and exact reviewed SHA, update `project/status/CURRENT.md`, and end the Claude task. A metadata-only report/status update must name the reviewed product SHA and does not make the metadata commit itself reviewed. Never resume, continue, or fork that task into the next issue; clearing is only for closing its context. Start the next issue in a new top-level task that rebuilds context from the repository. Disabling auto-memory and ending a task limit accidental context reuse; they do not delete or make claims about provider-side records.

Milestone general remediation is limited to one cycle and milestone security
remediation to two cycles. No review, repair, or reconciliation loop may exceed
five total iterations. Reaching a limit blocks for the human; it never waives a
required review.
