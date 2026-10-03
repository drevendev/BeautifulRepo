# Security policy template

> **Template only. Do not publish this file as `SECURITY.md` until every placeholder is
> replaced and the private reporting route has been tested.**

## Supported versions

| Version | Supported |
| --- | --- |
| {{CURRENT_SUPPORTED_VERSION}} | Yes |
| {{OLDER_OR_UNSUPPORTED_VERSION}} | No |

Replace this table with versions or branches that actually receive security fixes.

## Reporting a vulnerability

Please do **not** open a public issue for a suspected vulnerability.

Verified private route:

**{{VERIFIED_PRIVATE_REPORTING_ROUTE}}**

Examples include a tested project security mailbox or GitHub Private Vulnerability Reporting
after the repository owner has verified that the feature is enabled. A `SECURITY.md` file by
itself does not enable GitHub private vulnerability reporting.

Include, when possible:

- affected version or commit;
- reproduction steps or proof of concept;
- expected security impact;
- relevant environment details;
- whether the issue is already public elsewhere.

Do not include unrelated personal data, credentials, or production secrets.

## What to expect

Replace this section with commitments the project can actually meet.

- A maintainer will acknowledge receipt through the verified private channel.
- The project may request additional reproduction details.
- Validation, remediation, and disclosure timing depend on severity and fix complexity.
- The reporter will not be asked to publish sensitive details before coordinated disclosure.

Do not promise a response-time SLA unless the project can consistently meet it.

## Coordinated disclosure

After a fix is ready, maintainers and the reporter should agree on an appropriate disclosure
plan. For public GitHub repositories, repository security advisories may support private
discussion and coordinated publication.

## Maintainer verification before adoption

- [ ] Every placeholder in this file is replaced.
- [ ] The reporting route was tested from a non-maintainer perspective.
- [ ] The intended responder received the test.
- [ ] Supported versions reflect actual maintenance policy.
- [ ] Public issue forms warn against posting vulnerability details.
- [ ] Response promises are realistic.
- [ ] The final file is linked from relevant contributor documentation.
