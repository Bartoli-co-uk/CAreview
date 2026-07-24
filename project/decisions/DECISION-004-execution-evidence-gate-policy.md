# Human decision: Execution-evidence gate policy for Codex issue reviews

**Decision ID:** `DECISION-004`
**Type:** `agent-configuration / review-gate policy`
**Decision:** `ACCEPT PERMITTED RISK` (standing policy)
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T12:46:57Z`

## Exact binding

- Artifact/action: the Codex issue-review gate as operated by
  `scripts/run-codex-review.sh` on this project.
- Scope: all CAreview implementation issues (ISSUE-0001..0006) and any future
  issue, until superseded.
- Exclusions: does not lower the bar for substantive **code** findings; does not
  authorize any protected action; does not apply to the milestone security gate's
  own acceptance beyond the same execution-evidence limitation.

## Context

The launcher runs Codex in a read-only, socket-restricted, temp-less isolated
checkout. Consequently Codex cannot execute this project's checks:
`python3 -m unittest` needs loopback sockets, `python3 -m py_compile` needs to
write `__pycache__`, and `scripts/validate_repo.py` needs a writable temp dir.
Codex therefore always reports an execution-evidence limitation and, per its
rules, cannot return `PASS`. This is a property of the skeleton's launcher, not of
the reviewed code.

## Decision text

> Gate-policy question answered "Static review + author evidence; you merge".

## Policy

For each issue:

1. Codex reviews the candidate **statically**; its structured report is committed.
2. Claude (the author) runs every required check **out-of-band** against the exact
   reviewed SHA and records the real command, exit status, and result.
3. A Codex outcome of `BLOCKED` whose blocking basis is **only** the
   execution-evidence limitation (no unresolved substantive code or security
   finding) is treated as acceptable evidence.
4. The **human** makes the merge decision for that issue after seeing the Codex
   report and the author's out-of-band evidence.

Substantive code, correctness, or security findings must still be fixed within the
issue's two repair rounds before the human merges. This policy only disposes of
the execution-evidence limitation that Codex cannot overcome in its sandbox.

## Consequence

- Permitted next action: with substantive findings resolved, present ISSUE-0001's
  Codex report + out-of-band evidence to the human for the merge decision.
- This decision dispositions the recurring "required execution evidence is
  unavailable" blocker (e.g. ISSUE-0001 review F-001) as an accepted
  environment limitation.

## Notes

An alternative (relaxing the launcher sandbox so Codex runs checks itself) was
considered and declined for now to preserve the launcher's read-only isolation.
The identical launcher schema bug and the validator wrong-stage self-test bug
remain separate follow-ups.
