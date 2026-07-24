# Security policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability, exposed credential, or sensitive incident.

For CAreview, use GitHub's **Security → Report a vulnerability** private reporting flow on the `Bartoli-co-uk/CAreview` repository. If that is unavailable, contact the repository owner (`@Jay-cli`) privately through an agreed channel rather than opening a public issue.

Include only the information needed to reproduce and assess the problem:

- affected commit or version;
- affected files or component;
- impact and plausible attack path;
- minimal reproduction steps; and
- any temporary mitigation.

Do not include live credentials, personal data, exploit traffic against systems you do not own, or unnecessary secret material. Revoke exposed credentials through the relevant provider rather than committing them to a report.

## Response expectations

This is a pre-release template maintained on a best-effort basis. Receipt, remediation, disclosure timing, and supported versions will be agreed case by case. A report is not accepted or rejected merely because an AI reviewer assigned it an outcome.

## Security model

The repository supplies operating conventions, prompts, and templates. It does not provide a hard sandbox, enforce role separation, protect secrets from a local process, or prove that a fresh model session was used. Read [`docs/security-boundaries.md`](docs/security-boundaries.md) before applying it to sensitive work.
