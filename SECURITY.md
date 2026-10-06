# Security Policy

IBRAMIND treats security, tenant isolation, evidence integrity, and customer confidentiality as product requirements.

## Reporting a vulnerability

Please **do not** disclose vulnerabilities, credentials, private URLs, customer information, or exploitable details in a public GitHub issue.

Report security concerns privately to:

**security@ibramind.com**

Include:
- A concise description of the issue
- Affected file, endpoint, or workflow
- Reproduction steps where safe
- Potential impact
- Any suggested mitigation

Do not include real customer data or secrets in a report.

## Scope of this public repository

This repository is a public prototype/showcase and intentionally excludes production credentials, production customer data, private enterprise integrations, and the private IBRAMIND production platform.

## Safe-harbor intent

Good-faith security research that avoids privacy violations, destructive testing, service disruption, data access beyond what is necessary to demonstrate an issue, and public disclosure before remediation is welcomed.

## Secrets

Never commit API keys, access tokens, passwords, private keys, production environment files, or customer data. If a secret is accidentally committed, treat it as compromised and rotate/revoke it immediately.
