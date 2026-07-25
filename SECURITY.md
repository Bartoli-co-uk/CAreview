# Security policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability, exposed credential, or sensitive incident.

Use GitHub's **Security → Report a vulnerability** private reporting flow on the `Bartoli-co-uk/CAreview` repository. If that is unavailable, contact the repository owner (`@Jay-cli`) privately through an agreed channel rather than opening a public issue.

Include only the information needed to reproduce and assess the problem:

- affected commit or version;
- affected files or component;
- impact and plausible attack path;
- minimal reproduction steps; and
- any temporary mitigation.

Do not include live credentials, tenant identifiers, real Conditional Access policy exports, personal data, exploit traffic against systems you do not own, or unnecessary secret material. Revoke exposed credentials through the relevant provider rather than committing them to a report.

## Response expectations

CAreview is a personal, best-effort project. Receipt, remediation, disclosure timing, and supported versions will be agreed case by case. A report is not accepted or rejected merely because an AI reviewer assigned it an outcome.

## What is in scope

The application's own trust boundaries, as implemented:

- the loopback bind and the `Host`/`Origin` allowlists that protect the local API;
- handling of the device-code access token, which must stay in process memory and never reach disk, logs, or the repository;
- outbound request targeting — tokens must only ever be attached to Microsoft Graph, and the token endpoint must only be Microsoft identity;
- rendering of untrusted tenant-supplied strings in the UI;
- the delegated Graph scopes requested, which are read-only by design;
- the review launcher's curated checkout, environment stripping, and symlink/submodule rejection.

Known and already-documented limitations are listed under "Known limitations" in [`README.md`](README.md) — notably that the local API has no authentication beyond the loopback and Host/Origin checks (`RISK-002`), so another process running as the same user could reach it while a token is in memory. Reports that restate a documented limitation are welcome but will be closed as known.

## What this project does not claim

The repository supplies operating conventions, prompts, and templates for a governed AI build process. That process does not provide a hard sandbox, enforce role separation technically, protect secrets from a local process, or prove that a fresh model session was used.

CAreview has not had an independent security assessment. Passing AI reviews is not certification, compliance, or assurance. Read [`docs/security-boundaries.md`](docs/security-boundaries.md) before applying any of this to sensitive work.
