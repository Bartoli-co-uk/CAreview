# Milestone security-review prompt

Run this prompt in two separate new read-only tasks: one Claude task and one
Codex task. Keep the initial reviews blind to each other's conclusions.

Review milestone `<MILESTONE-ID>` at exact candidate commit `<CANDIDATE-SHA>`.
Read `AGENTS.md`, `docs/security-boundaries.md`, the approved brief and roadmap,
threat assumptions, dependency/build files, workflows, repository tree, and real
scanner/test evidence. Do not edit files and do not claim certification.
Do not delegate to a subagent, spawn another agent, or ask another agent to
reach the review conclusion.

Cover trust boundaries, abuse cases, authentication/authorization, secrets and
logs, validation and injection, paths and command execution, dependencies and
supply chain, network egress, configuration defaults, CI/fork/token exposure,
privacy/retention, migrations, and evidence gaps.

When the launcher supplies a JSON Schema, return only one JSON object matching
it with the reviewed SHA, outcome (`PASS`, `PASS_WITH_NOTES`,
`REMEDIATION_REQUIRED`, `BLOCKED`, or `INCONCLUSIVE`), and findings with severity,
fingerprint, category, confidence, blocking status, location, evidence, attack
preconditions, impact, exploitability, remediation, verification, and
disposition. Critical/high findings, uncertainty, wrong-SHA or
missing evidence block. Every repair requires a new candidate and reruns both
general reviews and both security reviews against that one new SHA.
The workflow permits at most two security-remediation cycles; unresolved
remediation after the second rerun blocks for the human.
No workflow loop may exceed five total iterations.

State only that the review passed within its documented scope and evidence. Do
not wrap schema-bound JSON in Markdown or append text after it.
