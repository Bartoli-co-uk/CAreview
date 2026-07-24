# Milestone general-review prompt

Run this prompt in two separate new read-only tasks: one Claude task and one
Codex task. Do not show either reviewer the other review before both finish.

Review milestone `<MILESTONE-ID>` at exact candidate commit `<CANDIDATE-SHA>`.
Read `AGENTS.md`, the approved brief and roadmap, milestone work items,
decisions, handoffs, repository tree, and real test evidence. Do not edit files.
Do not delegate to a subagent, spawn another agent, or ask another agent to
reach the review conclusion.

Cover requirement traceability, cross-issue integration, architecture,
regressions, test sufficiency, error handling, performance, operability,
accessibility where relevant, documentation, migrations, release readiness, and
known limitations. When the launcher supplies a JSON Schema, return only one
JSON object matching it with the reviewed SHA, outcome (`PASS`,
`PASS_WITH_NOTES`, `CHANGES_REQUIRED`, or `BLOCKED`), evidence, numbered
findings, missing checks, and residual risks.

A changed candidate invalidates all four milestone reviews. The workflow permits
at most one general-remediation cycle, which must create a new candidate and
rerun both general and both security reviews; a remaining required change then
blocks for the human.
No workflow loop may exceed five total iterations. Do not wrap schema-bound JSON
in Markdown or append text after it. Stop after the report.
