# Sensitive reporting and community safety

A repository should separate ordinary bugs, security reports, and conduct complaints. They
have different privacy needs and should not share a generic public reporting path.

Reviewed 2026-10-04 against GitHub Docs and Open Source Guides.

## Three reporting lanes

| Report | Public path | Private path |
| --- | --- | --- |
| Ordinary bug or docs problem | Issue or discussion | Usually unnecessary |
| Security vulnerability | Do not require a public issue | Verified security route or GitHub Private Vulnerability Reporting |
| Conduct complaint | Do not force public disclosure | Verified confidential conduct route with conflict fallback |

## Security policy

GitHub recommends a `SECURITY.md` file that tells people which versions are supported and
how to report a vulnerability. That file does not enable a private channel by itself.

Private Vulnerability Reporting is a separate repository setting. Only tell reporters to use
GitHub's private reporting form after verifying that the feature is enabled for the repository.

A repository with Private Vulnerability Reporting enabled may customize that form with
`.github/VULNERABILITY_REPORT.yml` or `.github/VULNERABILITY_REPORT.yaml`. The form file
customizes the questions; it does **not** enable Private Vulnerability Reporting. If GitHub
cannot parse or validate the custom form, reporters receive the default form instead.

A useful security policy states supported versions, the verified reporting route, the details
needed to reproduce the problem, realistic response expectations, and how disclosure will be
coordinated after a fix.

Use [the security-policy template](../templates/SECURITY.template.md) as a draft. It contains a
deliberate placeholder for the reporting route and must not be renamed to `SECURITY.md` until
the route has been tested.

## Code of conduct

GitHub recommends considering whether maintainers can enforce a code of conduct before adopting
one. Open Source Guides recommends defining its scope, who it applies to, consequences, and a
private reporting route. The route also needs a conflict fallback when a complaint concerns the
person who normally receives reports.

Before adoption, verify enforcement responsibility, a confidential route, a conflict fallback,
and any attribution requirements of the selected upstream policy. Use the
[adoption checklist](../templates/CODE_OF_CONDUCT.adoption-checklist.md).

## Community-profile checkmarks

GitHub's community profile checks for recommended files. That is useful discovery metadata, but
presence of a file does not prove that its process is monitored, enforced, responsive, or safe.

## Verify before publishing

- Test the private route from a reporter's point of view.
- Confirm the intended responder can read incoming reports.
- Keep public issue forms free of requests for secrets or vulnerability details.
- Do not promise response times the project cannot support.
- Do not copy confidential report content into public issues or examples.
- Re-read rendered policies after publication.

## Primary sources

- GitHub: <https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy>
- GitHub: <https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately>
- GitHub: <https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository>
- GitHub: <https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-code-of-conduct-to-your-project>
- GitHub: <https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories>
- Open Source Guides: <https://opensource.guide/code-of-conduct/>

## Limits

This guide does not enable a reporting feature, create a confidential mailbox, choose a final
code of conduct, or claim that BeautifulRepo currently has a confidential reporting channel.
