# Claude issue-repair prompt

This is a repair round within the current fresh Claude issue task for
`<ISSUE-ID>`. Read `AGENTS.md`, `CLAUDE.md`, the approved issue, the exact
independent review report, current diff, and check evidence. Do not broaden the
issue or carry this task into the next issue.

Address every numbered finding as `accepted`, `partially accepted`, `rejected
with evidence`, or `requires user decision`. Implement only accepted in-scope
repairs, update tests and documentation, rerun the declared checks, and produce
a new handoff with the new commit SHA. Do not merge or mark the review passed.

Run the review launcher again so a new ephemeral, read-only Codex process reviews
the repaired commit. After two failed repair rounds, stop and escalate to the
human with all unresolved findings. Once the issue passes or blocks, persist the
status and end this Claude task; the next issue starts in a new top-level task.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first.
