# Risks

Store material project risks here with stable IDs such as `RISK-001.md`.

Record the description, evidence, affected commit and scope, severity,
confidence, owner, treatment, controls, status, and next review date. Link each
risk from `project/status/CURRENT.md`, the relevant issue, roadmap, or milestone.

## Current register for CAreview

This directory holds no per-risk files. CAreview's four material risks were
identified during planning and are recorded in the "Risks and decisions" table
of [`ROADMAP.md`](../../ROADMAP.md), with their acceptances in
[`project/decisions/`](../decisions/README.md):

| ID | Summary | Treatment |
|---|---|---|
| `RISK-001` | A tenant may block first-party device-code sign-in or withhold `Policy.Read.All` | Accepted for the MVP (`DECISION-001`); app-registration fallback deferred |
| `RISK-002` | The loopback API is reachable by another local process while a token is in memory | Accepted for the MVP (`DECISION-001`); loopback bind plus Host/Origin allowlists |
| `RISK-003` | Accidental logging of tokens or policy JSON | Mitigated by construction; request logging disabled, checked per issue |
| `RISK-004` | The heuristic score is mistaken for a compliance certification | Documented in the UI, `README.md`, and `rules.py` |

A new risk that needs its own evidence, owner, and review date should get a
`RISK-00N.md` file here and be linked from
[`project/status/CURRENT.md`](../status/CURRENT.md).

Only a human may accept residual risk. Use
`project/templates/risk-acceptance.md`; critical and high security findings are
not eligible for the default acceptance path. An expired, broadened, or
wrong-commit acceptance is invalid.
