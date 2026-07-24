# Session prompts

Use these prompts in order. Start new top-level tasks at the role boundaries
described below; do not reuse an author task for independent review or for the
next issue.

1. `01-project-brief.md` — Claude turns the user's description into a brief.
2. `02-roadmap.md` — Claude creates the roadmap and work items after brief approval.
3. `03-codex-plan-review.md` — Codex independently reviews the roadmap.
4. `04-implement-issue.md` — Claude implements one approved work item.
5. `05-codex-issue-review.md` — Codex reviews the exact implementation commit.
6. `06-repair-issue.md` — the current issue-scoped Claude task addresses required findings, then launches a fresh Codex re-review.
7. `07-milestone-general-review.md` — run once with Claude and once with Codex.
8. `08-milestone-security-review.md` — run once with Claude and once with Codex.

Replace angle-bracket placeholders before use. Review tasks must not edit source
files, delegate to subagents, or ask another agent to reach their conclusions.
Save their final reports verbatim under `project/reviews/`, or link the
corresponding immutable pull-request review from the milestone record. Planning
and issue repair allow at most two rounds; milestone general and security
remediation allow at most one and two cycles respectively; no loop may exceed
five total iterations.
