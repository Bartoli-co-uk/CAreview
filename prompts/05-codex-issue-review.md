# Codex issue-review prompt

This is a new, independent, read-only review of `<ISSUE-ID>` at commit
`<REVIEWED-SHA>`. Read `AGENTS.md`, the approved brief/roadmap/issue, the exact
diff, and real check output. Do not edit files or implement fixes.
Do not delegate to a subagent, spawn another agent, or ask another agent to
reach the review conclusion.

Check correctness, regressions, scope, acceptance criteria, tests, error paths,
security, documentation, and maintainability. Treat author claims as claims
unless supported by repository or command evidence.

When the launcher supplies a JSON Schema, return only one JSON object matching
that schema, with:

- reviewed SHA and diff/base identity;
- outcome: `PASS`, `PASS_WITH_NOTES`, `CHANGES_REQUIRED`, `BLOCKED`, or
  `USER_DECISION_REQUIRED`;
- numbered findings with severity, confidence, location, evidence, expected and
  observed behaviour, remediation, and verification;
- missing or stale evidence;
- residual risks.

Any code change invalidates this review. Do not wrap the JSON in Markdown or
append text after it. Stop after the report.
