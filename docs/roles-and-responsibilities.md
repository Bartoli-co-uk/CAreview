# Roles and responsibilities

Clear separation matters more than agent names. Each material role uses a fresh top-level process and receives only the context needed for that role.

## Human

The human:

- supplies project intent and answers material questions;
- approves the exact brief and roadmap;
- approves protected actions and external side effects;
- makes product, business, legal, privacy, and residual-risk decisions;
- approves milestone and final completion packages;
- decides how to handle unresolved disagreement or exhausted repair loops.

The human does not delegate risk acceptance through broad phrases such as “do everything” or “use your judgement.” Approval should name the artifact or action, commit, scope, and decision.

## Claude requirements interpreter

Claude turns the raw description into a structured brief. It must distinguish facts, assumptions, contradictions, unknowns, risks, questions, and measurable success criteria. It does not implement the project during intake and cannot approve its interpretation.

## Claude planner

In a fresh process, Claude converts the approved brief into a dependency-ordered roadmap. It defines small issues, acceptance criteria, checks, documentation, risks, and milestone definitions of done. It must answer every independent Codex planning finding and expose unresolved disagreement to the human.

## Claude implementer

Claude is the sole AI writer of product source in this workflow. For one approved issue at a time, it:

- restates objective, boundaries, assumptions, and checks;
- edits only the approved branch and scope;
- adds or updates tests and documentation;
- runs allowed checks or requests them explicitly;
- records decisions, limitations, and a structured handoff;
- stops before protected, destructive, ambiguous, or out-of-scope action.

Claude may use bounded assistance for exploration, but remains accountable for the handoff. Another AI must not write concurrently to the same worktree.

## Claude repair rounds

The same top-level Claude author task may perform up to two repair rounds for its one issue. It receives the exact findings, candidate diff, and verification evidence and addresses each item without expanding scope. It cannot dismiss a finding silently or continue into a different issue. Once the issue completes or blocks, end that task; do not resume, continue, or fork it for later work.

## Claude general reviewer

At milestones and final review, a fresh Claude process acts only as a reviewer. It is read-only and cannot approve or repair the candidate. Its report covers requirements, cross-issue integration, architecture, regressions, test sufficiency, error handling, operability, documentation, migrations, and release readiness.

This reviewer is a separate role from the Claude author even if the same provider or model family is used.
It must reach its own conclusion without delegating to a subagent or calling
another agent.

## Claude security reviewer

In another fresh, read-only process, Claude performs the security review defined in `docs/security-boundaries.md`. It reviews one frozen commit and does not see Codex's initial security conclusion.

## Codex plan reviewer

A fresh Codex process independently reviews the roadmap for completeness, feasibility, sequence, hidden assumptions, security, verification, operability, and scope. Codex does not edit the roadmap. Findings are returned for Claude and the human to resolve.

## Codex issue reviewer

A fresh Codex process reviews the exact issue candidate commit after checks run. It is read-only: it may inspect files, diffs, and evidence and produce a report, but it must not implement fixes in that review. If changes are needed, the issue-scoped Claude author task performs them and a new ephemeral Codex process re-reviews.

## Codex milestone and security reviewers

Fresh Codex processes independently review the frozen milestone or final candidate. General and security review are separate roles. Initial contexts withhold Claude's peer report to reduce anchoring and circular agreement.
Each reviewer reaches its own conclusion without delegating to a subagent or
calling another agent. General remediation is limited to one cycle; security
remediation is limited to two cycles; no loop exceeds five total iterations.

## Verification executor

Verification is a function, not an approval role. It may be a human, CI job, or controlled local command runner. It runs predeclared checks and records real command evidence against the exact candidate commit. It must not accept an agent's test claim as a substitute for execution.

## Documentation auditor

For material changes, a human or fresh read-only agent checks that commands, links, configuration, public behaviour, security guidance, migration notes, and known limitations match the implementation. Missing required documentation blocks issue or milestone completion.

## GitHub

GitHub hosts collaboration artifacts such as branches, issues, pull requests, and checks. It does not decide workflow state. Human edits and repository permissions remain important, but committed project records are the durable source for briefs, roadmaps, decisions, reviews, and risks.

## Prohibited combinations

- An author cannot approve or independently review its own work.
- Codex cannot implement fixes during the review that identified them.
- A reviewer cannot accept risk for the human.
- A verifier cannot turn a failed or missing check into a pass through judgement alone.
- A concierge or existing chat cannot become an implementation or review session.
- Two agents cannot write to the same product worktree concurrently.
- A GitHub label, comment, or merged state cannot silently override a committed decision record.

## Handoff between roles

Every handoff should name:

- role and fresh-session identity where available;
- approved input artifacts;
- starting and ending or reviewed commit SHA;
- files and scope;
- decisions and assumptions;
- checks requested and actual evidence available;
- documentation impact;
- findings, limitations, and residual risks;
- exact next decision or role.

Do not include private chain-of-thought. Include conclusions and supporting evidence that another person can verify.
