# ISSUE-[NNNN]: [short title]

**Status:** `[PLANNED / IMPLEMENTING / REVIEWING / REPAIRING / BLOCKED / COMPLETE]`
**Milestone:** `[M1]`
**Approved roadmap:** `ROADMAP.md` version `[n]` at `[commit SHA]`
**Dependencies:** `[None / issue IDs]`
**Branch:** `ai/ISSUE-[NNNN]-[slug]`
**Starting SHA:** `[SHA]`
**Candidate SHA:** `[Not created / this commit; the launcher records the full HEAD SHA]`

## Objective

[One small, coherent outcome.]

## In scope

- `[Path, behaviour, or artifact]`

## Out of scope

- `[Explicit exclusion]`

## Allowed paths

- `[path or narrow glob]`

## Acceptance criteria

1. `[Observable criterion]`
2. `[Observable criterion]`

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| `[name]` | `[exact command]` | `[result]` |

## Documentation

- `[File and required change, or reason no change is needed]`

## Security and privacy impact

- Threat-model delta: `[description or none with reason]`
- Data/secret impact: `[description]`
- Dependency/supply-chain impact: `[description]`
- Protected actions: `[none / exact separate approval required]`

## Stop conditions

- `[Ambiguity, unavailable evidence, path expansion, protected action, etc.]`

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `[path]` | `[SHA]` | `[path/summary]` | `[path]` | `[outcome]` |

Maximum two repair rounds. Every Codex review/re-review must be a new ephemeral read-only process against the named SHA.
No workflow loop may exceed five total iterations; the tighter two-round issue
limit applies first, and exhaustion blocks for the human.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
