# Claude issue-implementation prompt

This is a new implementation task for `<ISSUE-ID>`. Read `AGENTS.md`,
`CLAUDE.md`, the approved brief and roadmap, the issue file, relevant decisions,
and dependency handoffs. Do not work on another issue.

Before editing, restate the objective, allowed scope, non-goals, acceptance
criteria, assumptions, security impact, and verification plan. Stop if the issue
or its dependencies are not approved, the working tree contains unexplained
changes, or a protected action is required.

Implement the smallest coherent change on branch `<ISSUE-BRANCH>`. Update tests
and documentation with the behaviour. Run the declared checks. Do not merge,
approve your own work, alter governance to make the issue pass, or perform
external/production/credential/repository-setting actions.

Finish with a structured handoff based on
`project/templates/implementation-handoff.md`, including the exact ending commit
SHA, changed files, commands and results, decisions, documentation, and residual
risks. Then automatically run:

```sh
./scripts/run-codex-review.sh issue <ISSUE-ID> <BASE-SHA> <HEAD-SHA>
```

Use `scripts/run-codex-review.ps1` on PowerShell. The launcher must start a new,
ephemeral, read-only Codex process. If changes are required, address only the
recorded findings and launch another fresh review, for at most two repair rounds.
Stop on pass for the human merge gate, or on a blocker, user decision, missing
Codex/authentication, protected action, uncertainty, or exhausted loop. Never
skip or impersonate the Codex review. No workflow loop may exceed five total
iterations; the tighter two-round issue limit applies first.
