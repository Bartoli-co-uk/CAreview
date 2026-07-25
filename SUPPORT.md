# Support

## Using CAreview

Start with [`README.md`](README.md) — it covers running the tool, what each rule
checks, how the score is calculated, and the known limitations.

Common first stops:

- **The page loads but the health badge is not "ok"** — check the terminal
  running `python3 server.py` for an error, and confirm you opened the same port
  the server printed.
- **You want to see it without signing in** — click "View a sample analysis";
  it renders committed sanitized sample data through the real rendering path.
- **Sign-in fails or consent is refused** — this is the documented `RISK-001`
  case in the README. A tenant can block first-party device-code sign-in or
  withhold `Policy.Read.All`. Live sign-in has not yet been verified against a
  real tenant, so reports about it are especially useful.
- **A finding looks wrong** — the rule set is in [`rules.py`](rules.py) with each
  rule's severity, weight, rationale, and required fields. Include the rule ID
  and a sanitized description of the policy shape in your report.

## Understanding how the project is built

The Claude + Codex governance workflow is documented in
[`START_HERE.md`](START_HERE.md) and [`docs/workflow.md`](docs/workflow.md), and
the current state is always in
[`project/status/CURRENT.md`](project/status/CURRENT.md).

## Reporting a problem

For a reproducible problem, open a GitHub issue using the most relevant form and
include:

- the affected commit;
- operating system and Python version;
- what you expected and what happened;
- the smallest safe reproduction; and
- relevant output with tenant identifiers, tokens, and policy contents removed.

General project-design decisions remain with the project owner. Provider
authentication, billing, availability, and account issues belong with the
relevant provider (Microsoft, Anthropic, or OpenAI).

Support is best effort. There is no guaranteed response time, compatibility
promise, or production-readiness assurance.

Never post secrets, tenant data, or private vulnerability details in a public
issue. Follow [`SECURITY.md`](SECURITY.md) for those reports.
