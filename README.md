# CAreview — Conditional Access policy analyzer

CAreview is a locally-hosted tool that signs into Microsoft Entra ID, reads your
Conditional Access (CA) policies through Microsoft Graph, scores them against
security best practice, and flags configuration weaknesses. It is inspired by
[`Jhope188/ca-policy-analyzer`](https://github.com/Jhope188/ca-policy-analyzer)
but runs entirely on your own machine.

> **Status: in development.** The application code does not exist yet. This
> repository currently holds the governance skeleton and project records. Work is
> built one reviewed issue at a time under the workflow described below, so the
> `Run it` commands become real as the implementing issues land.

## Design goals

- **Local only.** A small Python process serves the UI and API on
  `http://localhost:8765`. Your policies and tokens stay on your machine; the
  only network calls are to Microsoft.
- **Zero registration, zero build.** No Azure app registration and no Node.js
  toolchain. Authentication uses the OAuth 2.0 **device-code flow** against a
  Microsoft first-party public client — click *Sign in*, get a code, approve it
  at `microsoft.com/devicelogin`.
- **Standard library only.** No third-party Python dependencies; nothing to
  `pip install`.
- **Read-only, least privilege.** Delegated Graph scopes limited to
  `Policy.Read.All`, `Application.Read.All`, and `Directory.Read.All`. A
  Security Reader role is sufficient.

## Scope

The current target is a focused MVP: sign in → fetch CA policies → 0–100 security
score → best-practice / vulnerability findings → simple policy visualization.
CIS-17 alignment, the FOCI database, persona scoring, baseline comparison, and
PowerPoint/deployment-bundle exports are tracked as later roadmap items, not part
of the MVP.

## Run it (once the implementing issues have landed)

```sh
python3 server.py            # serves http://localhost:8765
```

Then open the URL, click *Sign in*, and approve the device code with a work or
school account that can read Conditional Access policies. Reading policies
requires admin consent to `Policy.Read.All` in your tenant, exactly as the
original tool does.

## Verify it (offline)

```sh
python3 -m unittest discover -s tests    # analyzer scores sample fixtures
python3 -m py_compile $(git ls-files '*.py')
```

The analyzer is unit-tested against committed sample-policy JSON fixtures, so its
scoring is verifiable without signing in.

## How this project is built — governance

CAreview is developed under a Claude + Codex workflow: **Claude** is the planner
and sole implementation author, **Codex** is an independent read-only reviewer,
and the **human owner** approves every gate. The repository — not chat history —
is the durable memory.

Every fresh agent task must read, in order: [`START_HERE.md`](START_HERE.md),
[`AGENTS.md`](AGENTS.md), [`ROADMAP.md`](ROADMAP.md),
[`docs/workflow.md`](docs/workflow.md), [`project/README.md`](project/README.md),
and [`project/status/CURRENT.md`](project/status/CURRENT.md), then state the
current stage and next allowed action before changing anything.

The flow is: project description → **Claude brief** (human approves) → **roadmap**
reviewed by a fresh **Codex** process (human approves) → implement each issue on
its own branch with a **mandatory fresh Codex review** before completion →
four blind reviews at each milestone. **No implementation begins until** both the
brief and the roadmap are approved.

At each milestone one frozen candidate receives four fresh, blind reviews against
the **same commit**:
a **Claude full general review**, a **Codex full general review**,
a **Claude security review**, and a **Codex security review**.
Any repair creates a new candidate and reruns all four.

The repository is the durable memory. Starting a fresh task reduces context
carry-over but **does not delete provider-side records** or prove zero retention.

### Codex review launcher

After each implementation candidate is committed, Claude runs the review
launcher, which starts a fresh, ephemeral, read-only `codex exec` process against
that exact commit and validates a schema-bound JSON report:

```sh
./scripts/run-codex-review.sh plan  <HEAD-SHA>
./scripts/run-codex-review.sh issue <ISSUE-ID> <BASE-SHA> <HEAD-SHA>
./scripts/run-codex-review.sh milestone-general  <MILESTONE-ID> <SHA>
./scripts/run-codex-review.sh milestone-security <MILESTONE-ID> <SHA>
```

Reports are staged under `.git/claudex/reviews/` and committed into
[`project/reviews/`](project/reviews/README.md). The launcher fails closed: no
nonzero or unknown result is ever treated as a pass.

| Exit | Meaning |
|---:|---|
| `0` | `PASS` |
| `10` | `PASS_WITH_NOTES` — human review still required |
| `20` | `CHANGES_REQUIRED` / milestone-security `REMEDIATION_REQUIRED` |
| `30` | `BLOCKED` / milestone-security `INCONCLUSIVE` |
| `40` | `USER_DECISION_REQUIRED` |
| `64` | Invalid usage or repository precondition |
| `65` | Missing or malformed evidence |
| `69` | Codex unavailable, unauthenticated, or execution failed |
| `78` | Explicit test-provider run; never valid review evidence |

See [`docs/workflow.md`](docs/workflow.md) for the full gate detail and
[`prompts/README.md`](prompts/README.md) for the session prompts.

## Prerequisites

- Python 3.10+ (the launcher and validator; 3.11+ also validates TOML).
- Git.
- Codex CLI, authenticated, for the review gates.
- Claude Code, for planning and implementation.
- A Microsoft Entra ID (work/school) account able to read Conditional Access
  policies, to run the app against a real tenant.

## Validate the governance skeleton

```sh
python3 scripts/validate_repo.py
```

This runs the same free, local checks as CI (required files, JSON/TOML syntax,
Markdown links, workflow language). It does not call any model, GitHub, or the
network, and it does not prove the process was followed.

## Security and limitations

- The workflow is a set of documented conventions and manual review gates, not a
  hard security boundary or a certification. A local user or agent can bypass it.
- Device-code tokens live only in the running process's memory; never commit
  tokens, client secrets, tenant data, or policy exports.
- See [`SECURITY.md`](SECURITY.md) for private vulnerability reporting and
  [`docs/security-boundaries.md`](docs/security-boundaries.md) for operating
  boundaries.

## Licence

Licensed under the [Apache License 2.0](LICENSE).
