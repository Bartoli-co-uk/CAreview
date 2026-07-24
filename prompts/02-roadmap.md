# Claude roadmap prompt

This is a new planning task. Read `AGENTS.md`, `CLAUDE.md`, the approved
`project/brief/PROJECT_BRIEF.md`, `ROADMAP.md`, and the templates under
`project/templates/`.

Do not implement code. Confirm that a human decision record approves the exact
brief commit. If it does not, stop.

Create or update `ROADMAP.md` and create dependency-ordered issue records as
`project/issues/<ISSUE-ID>.md`. Each issue must be small enough for one review cycle
and include objective, scope, non-goals, dependencies, acceptance criteria,
tests, documentation, security considerations, and definition of done.

Group work items into milestones. Every milestone must reserve four independent
reviews against one candidate commit: Claude general, Codex general, Claude
security, and Codex security. Finish with assumptions, risks, unresolved human
decisions, and a mapping from requirements to work items. Stop and request
roadmap review; do not implement the first issue.
