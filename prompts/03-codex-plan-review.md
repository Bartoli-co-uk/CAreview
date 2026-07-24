# Codex roadmap-review prompt

This is a new, independent, read-only review task. Read `AGENTS.md`, the approved
project brief, `ROADMAP.md`, and all proposed work items. Do not edit files, run
implementation agents, delegate to a subagent, call another agent, or propose
unrelated features.

Review completeness, feasibility, sequencing, hidden assumptions, dependency
order, acceptance criteria, verification, documentation, security, operations,
and scope. Do not rely on Claude's self-review.

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
