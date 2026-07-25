# Start here

This is **CAreview**, a locally-hosted Microsoft Entra ID Conditional Access
policy analyzer. See [`README.md`](README.md) for what it does and how to run it.

It is built under a governed Claude + Codex workflow, and this file is the
entry point for that side of the repository. The design goal is that the project
survives a completely new chat: **Git-tracked files, not conversation history,
are the project memory.**

## Where the project currently stands

Read [`project/status/CURRENT.md`](project/status/CURRENT.md) — it is the single
authoritative index of the current stage, the approved artifacts, open blockers,
and the next permitted action. Everything below tells you how to interpret it.

Do not trust this section over that file. If the two ever disagree, the status
file and the records it links to win, and the disagreement itself should be
repaired before any other work.

## What a fresh agent must do

Before proposing or changing anything:

1. Read [`AGENTS.md`](AGENTS.md), [`ROADMAP.md`](ROADMAP.md),
   [`docs/workflow.md`](docs/workflow.md),
   [`project/README.md`](project/README.md), and
   [`project/status/CURRENT.md`](project/status/CURRENT.md).
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

## Reusing this workflow on another project

The governance layer here is project-agnostic: `AGENTS.md`, `CLAUDE.md`,
[`docs/`](docs/workflow.md), [`prompts/`](prompts/README.md),
[`scripts/`](scripts/validate_repo.py), `project/templates/`, `.claude/`, and
`.codex/` contain nothing specific to Conditional Access.

To start a different project from it: copy those paths into a new repository,
clear the live records under `project/` while keeping `project/templates/`, reset
[`project/status/CURRENT.md`](project/status/CURRENT.md) to your starting stage,
write your project description into `project/intake/PROJECT_DESCRIPTION.md`, and
begin with [`prompts/01-project-brief.md`](prompts/01-project-brief.md) in a new
Claude task. Implementation must not begin until separate brief and roadmap
approvals have been recorded in Git.
