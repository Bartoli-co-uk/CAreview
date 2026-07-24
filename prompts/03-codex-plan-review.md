# Codex roadmap-review prompt

This is a new, independent, read-only review task. Read `AGENTS.md`, the approved
project brief, `ROADMAP.md`, and all proposed work items. Do not edit files, run
implementation agents, delegate to a subagent, call another agent, or propose
unrelated features.

Review completeness, feasibility, sequencing, hidden assumptions, dependency
order, acceptance criteria, verification, documentation, security, operations,
and scope. Do not rely on Claude's self-review.

Plan-review binding convention: for `plan` mode the launcher intentionally
supplies no base commit and an empty Target ID. The review target is bound by the
`Target record` (`ROADMAP.md`) and the `Target commit` SHA, which must equal the
repository `HEAD`. Treat the empty Target ID and empty Base commit as the intended
plan convention, not missing evidence, and set `target_id` to an empty string and
`base_sha` to an empty string in the report. Only raise an identity blocker if the
`Target commit` does not match `HEAD` or the `Target record` is absent.

When the launcher supplies a JSON Schema, return only one JSON object matching
that schema, with:

- target brief and roadmap commit SHA;
- outcome: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, `BLOCKED`, or
  `USER_DECISION_REQUIRED`;
- numbered findings classified as `BLOCKER`, `REQUIRED`, `ADVISORY`, or `QUESTION`;
- evidence and affected file for each finding;
- the smallest remediation and how to verify it;
- residual uncertainty and missing evidence.

A pass with any blocker or required finding is invalid. Do not wrap the JSON in
Markdown or append text after it. Stop after the report.
