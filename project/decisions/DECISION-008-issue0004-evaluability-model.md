# Human decision: Implement generic requires-field enforcement literally (ISSUE-0004 F-002)

**Decision ID:** `DECISION-008`
**Type:** `issue advance (design disagreement resolution)`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T15:XX:XXZ`

## Context

Across ISSUE-0004 review rounds 0–2, Codex repeatedly required that
`analyzer.analyze` generically enforce every `Rule.requires` entry as an
evaluability gate, not just external inputs. Claude's position (approved once in
round 0): `graph.normalize_policy` guarantees every declared policy-JSON field
path is always present (possibly empty), proven by a dedicated test, so a
generic check over policy fields is structurally a no-op; only external inputs
(`break_glass_ids`) can be genuinely absent, and those were already gated.

Codex re-raised the identical objection a third time (round 2 review) without
engaging the proof.

## Decision text

> "Implement Codex's literal request anyway" — add generic requires-field
> enforcement over all declared fields, even though it is a no-op given
> `normalize_policy`'s guarantees, to directly satisfy the review gate.

## Exact binding

- Artifact/action: `analyzer.py` — `_missing_requirements` now walks every
  `Rule.requires` entry (external inputs AND policy-field declarations) and
  marks a rule `NOT_EVALUABLE` if either is missing/undeclared in the
  normalized-policy contract's reference shape.
- Scope: ISSUE-0004 only.

## Consequence

- No behavioral change for policy-field requirements (proven never to trigger,
  per the existing guarantee test); the mechanism now generically covers a
  genuinely stale/incorrect field declaration too (new tests prove both the
  "never triggers for real fields" and "does trigger for a bogus field" cases).
- Resolves the repeated F-002 finding without further rounds.
