# Start here

This repository is designed to survive a completely new chat. Git-tracked files,
not conversation history, are the project memory.

## What a fresh agent must do

Before proposing or changing anything:

1. Read `AGENTS.md`, `ROADMAP.md`, `docs/workflow.md`, `project/README.md`, and
   `project/status/CURRENT.md`.
2. Read the approved brief, current issue, relevant decisions, and latest
   reviews named by the status file. Do not assume a draft is approved.
3. Report the current branch and commit, workflow stage, approved artifacts,
   open blockers, and the next permitted action.
4. Stop if files disagree, required evidence is missing, or the next action
   needs human approval.

## Operating model

- The human owns intent, approvals, protected actions, risk acceptance, merges,
  milestone acceptance, and final acceptance.
- Claude is the requirements/planning lead and the only implementation writer.
- Codex is the independent read-only plan and code reviewer.
- Each issue starts in a fresh Claude task and ends with a fresh Codex review.
- Claude automatically launches that Codex review through the repository script.
  Required repairs are bounded to two rounds, each followed by a new review.
- Each milestone receives four blind reviews against one commit: Claude general,
  Codex general, Claude security, and Codex security.
- Milestone general remediation is limited to one cycle and security remediation
  to two cycles. No workflow loop may exceed five total iterations; exhaustion
  blocks for the human.
- Critical/high findings, uncertainty, missing evidence, protected actions, and
  exhausted loops stop for a human.

These are transparent repository conventions and review gates. They improve
discipline but are not a hard security boundary or a security certification.

## Starting a new project

The checked-in status is `TEMPLATE_READY`. In a newly derived repository, first
complete and commit the README customization checklist. Then add the project
description to `project/intake/PROJECT_DESCRIPTION.md` and use
`prompts/01-project-brief.md` in a new Claude task. Implementation must not begin
until separate brief and roadmap approvals have been recorded in Git.
