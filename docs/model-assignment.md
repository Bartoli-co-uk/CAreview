# Model assignment

This repository runs several agent roles. They do not all need the same model.
Mechanical drafting (documentation prose, status metadata) can run on a cheaper,
faster model, while planning, implementation, and every review stay on a strong
model. This document is the governed record of which model each role uses and
why. It is a convention and a cost control, not a security boundary; read
[`docs/security-boundaries.md`](security-boundaries.md) before relying on it for
sensitive work.

## Tiers

Two tiers, referred to by **alias** rather than a dated model id so this policy
stays durable as model versions roll:

- **strong** (`opus`): high-stakes reasoning where a mistake is expensive or
  poisons downstream work — planning, implementation, and all reviews.
- **cheap** (`sonnet`): genuinely mechanical drafting that a strong actor still
  reviews before it is committed.

An alias resolves to whatever the account maps it to; this document assigns
tiers, it does not guarantee a price, a capability, or availability.

## Assignments

| Role | Side | Tier | Model | Rationale |
|---|---|---|---|---|
| requirements-planner | Claude | strong | `opus` | The brief and roadmap gate everything downstream |
| implementation-author | Claude | strong | `opus` | Code correctness and security matter |
| milestone-reviewer | Claude | strong | `opus` | Gate-review rigor |
| security-reviewer | Claude | strong | `opus` | Highest stakes — see the floor below |
| docs-scribe | Claude | cheap | `sonnet` | Non-gating documentation drafting |
| status-scribe | Claude | cheap | `sonnet` | Non-gating status/metadata drafting |
| plan-reviewer | Codex | strong | account default | Gate review |
| issue-reviewer | Codex | strong | account default | Gate review |
| milestone general reviewer | Codex | strong | account default | Gate review |
| milestone security reviewer | Codex | strong | account default | Gate review — **hard floor** |

## The security and gate floor

**Cost tiering must not downgrade a security review.** A security review always
runs on a strong model. More generally, no gate review is downgraded by default;
the strong tier is the default for every review.

The Codex side is deliberately conservative: the launcher overrides no model by
default, so every Codex review uses the account's configured strong default. A
human may tier a **non-security** Codex review (plan, issue, or milestone
general) down to a specific cheaper model, accepting the documented quality
trade-off, but the security review is floor-protected and the launcher fails
closed if it is pointed at a model that has not been explicitly vetted.

## How each side is enforced

- **Claude agents** declare `model:` in their front matter under
  [`.claude/agents/`](../.claude/agents). The four gate roles declare `opus`; the
  two non-gating scribes declare `sonnet`.
- **Codex reviews** are governed entirely by the launcher
  [`scripts/run_codex_review.py`](../scripts/run_codex_review.py):
  - `MODE_MODELS` holds the per-mode model (default `None` = account default).
  - `SECURITY_FLOOR_MODES` marks modes that must never be weakened;
    `APPROVED_STRONG_MODELS` is the (initially empty) allowlist of vetted strong
    model ids a floored mode may use in place of the account default.
  - The launcher records the model it actually used in every report envelope
    (`metadata.model`), so the model is part of the review evidence rather than
    an untracked runtime choice.
  - The `.codex/agents/*.toml` files document each role's intended tier but are
    not loaded by the launcher; the launcher is the sole enforcer.

## Non-gating helper agents

`docs-scribe` and `status-scribe` are drafting assistants, not writers or
reviewers. They run inside the owning author or closeout task, never commit,
never satisfy a gate, and never act as an independent reviewer. The single
responsible writer reviews, integrates, and commits their output in the same
coherent change. This keeps the one-writer and documentation-with-behaviour
rules in [`AGENTS.md`](../AGENTS.md) intact while letting the mechanical drafting
run on a cheaper model.

## Changing this policy

The model assignment is a governed decision. Changing a tier, adding a model to
`APPROVED_STRONG_MODELS`, or tiering a review down is an agent-configuration
change and requires its own review under the rules in
[`AGENTS.md`](../AGENTS.md) and [`docs/workflow.md`](workflow.md); it is not a
routine edit. Never weaken the security floor to save cost.
