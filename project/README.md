# Project memory

This directory holds the durable records that let a fresh Claude or Codex task understand the project without prior chat history.

The repository is the shared memory. Chat, resumed sessions, provider memory, and GitHub labels are not authoritative substitutes.

## Read order for a fresh task

1. Read `AGENTS.md` and the provider-specific instructions.
2. Read `project/status/CURRENT.md` for the current gate and next permitted action.
3. Read the exact artifacts linked from that status file.
4. Read `project/intake/PROJECT_DESCRIPTION.md` and, when present, `project/brief/PROJECT_BRIEF.md`.
5. Read the approved root `ROADMAP.md`.
6. Read only the active issue, relevant dependency handoffs, decisions, risks, and review evidence.
7. Check the current branch, commit, and working-tree state before proposing action.

After this read, a fresh task must be able to state:

- how Claude, Codex, and the human work together;
- which approvals and reviews are mandatory;
- the current workflow stage;
- the exact approved brief and roadmap, if any;
- the active milestone and issue, if any;
- the candidate or reviewed commit;
- open blockers and residual risks;
- the next action currently permitted.

If the repository cannot answer one of these questions, stop and repair the project records before implementation.

## Live paths

| Path | Purpose |
|---|---|
| `project/intake/PROJECT_DESCRIPTION.md` | Verbatim, untrusted human description of the proposed project |
| `project/brief/PROJECT_BRIEF.md` | Claude's structured interpretation, created from the brief template |
| `ROADMAP.md` | Live root roadmap; not executable until exact human approval is recorded |
| `project/status/CURRENT.md` | Compact current stage, bindings, blockers, and next permitted action |
| `project/issues/` | One approved, dependency-ordered `ISSUE-ID.md` file per roadmap item |
| `project/handoffs/` | Claude implementation and repair handoffs |
| `project/reviews/` | Exact Codex, Claude general, and security reports bound to commits |
| `project/decisions/` | Exact human approvals, rejections, protected actions, and completion decisions |
| `project/risks/` | Open risks and time-bounded risk acceptances |
| `project/milestones/` | Four-review milestone packages and completion records |
| `project/templates/` | Copyable starters; never approvals or live state by themselves |

## Status is the entry point

Update `project/status/CURRENT.md` whenever any of these changes:

- a project description or brief is created;
- brief or roadmap approval is recorded;
- an issue starts, completes, or becomes blocked;
- a candidate commit or review becomes current or stale;
- a milestone gate begins or completes;
- a material risk, uncertainty, or protected-action request appears;
- the next permitted action changes.

Commit the status update with the evidence that caused it. The status file is an index, not proof: follow its links to the underlying brief, roadmap, decision, handoff, and review artifacts.

## Naming guidance

Use stable IDs and include short commit SHAs in review filenames:

```text
project/issues/ISSUE-0001.md
project/handoffs/ISSUE-0001-round-0.md
project/reviews/issues/ISSUE-0001-a1b2c3d4e5f6-codex.json
project/reviews/milestones/M1-a1b2c3d4e5f6-claude-general.md
project/reviews/milestones/M1-a1b2c3d4e5f6-codex-security.json
project/decisions/2026-07-21-roadmap-approval.md
project/risks/RISK-001.md
project/milestones/M1.md
```

Exact names may vary, but IDs, reviewed SHA, role, outcome, and evidence must remain unambiguous.

## Issue closeout and context reset

When an issue is complete or blocked:

1. Save Claude's handoff, every Codex report, real check evidence, and the exact candidate SHA.
2. Record the human advance, merge, or block decision when required.
3. Update the issue file and `project/status/CURRENT.md`.
4. Commit these metadata records. Saving metadata after review is allowed when it does not change the reviewed product tree; every report must still name the exact product SHA it reviewed.
5. End the top-level Claude issue task. Do not resume, continue, or fork it for the next issue.
6. Start the next issue in a new top-level Claude task that reconstructs context from committed repository files only.

Each Codex review and re-review is a separate fresh, ephemeral, read-only process. The same Claude author task may implement up to two repair rounds for its one issue, but it must not continue into another issue.

At milestones, allow at most one general-remediation cycle and two
security-remediation cycles. No workflow loop may exceed five total iterations;
exhaustion blocks for an exact human decision.

This clears working context by convention. It does not guarantee deletion of provider-side records or memory.

## Template use

Copy a template and replace every bracketed field. Delete guidance comments that no longer help. A template with placeholders, `DRAFT`, or no exact human decision is not approved.

Agents may draft or update factual records, but only the human can supply approvals, protected-action consent, business choices, and risk acceptance. Never infer those entries.
