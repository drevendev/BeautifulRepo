# Community safety files that actually work

A `SECURITY.md` or `CODE_OF_CONDUCT.md` is not a trust badge. It is an operational
promise: somebody must be able to receive a report, protect sensitive details, make a
decision and follow the process the repository publishes.

This guide is for maintainers deciding whether those files are ready to ship. It does not
replace legal, incident-response or platform-specific advice.

## Security reporting: publish the route you can really operate

GitHub recognizes a repository security policy and recommends that it explain supported
versions and how to report vulnerabilities. For public repositories, GitHub also supports
private vulnerability discussion through repository security advisories; availability and
configuration must be verified for the actual repository before you promise that route.

A useful security policy answers:

- Which versions or branches receive security fixes?
- Where should a reporter send sensitive details?
- What information is useful in the first report?
- What should *not* be posted in a public issue?
- What acknowledgement or disclosure process can the maintainers genuinely support?

Do not invent an email address, response-time SLA or "private channel" just to complete a
community checklist. Test the chosen route with the same permissions a reporter would use.
If the route cannot be verified, say that the policy is not ready rather than publishing a
placeholder that directs sensitive material nowhere.

Use [the reusable security-policy scaffold](../templates/SECURITY.template.md) as a drafting
aid. It deliberately refuses to supply a fictional contact method.

## Code of conduct: enforcement is part of adoption

GitHub's code-of-conduct guidance explicitly asks maintainers to choose a policy that fits
their community and to consider whether they are willing and able to enforce it. If you
adopt text written by another project or organization, follow its attribution requirements.

Before publishing a code of conduct, decide:

1. **Scope:** where the policy applies.
2. **Expected and unacceptable behavior:** specific enough to guide decisions.
3. **Reporting:** a real route for sensitive conduct reports.
4. **Enforcement:** who can act, what actions are possible and how conflicts are handled.
5. **Attribution and versioning:** where the adopted text came from and which version you use.

Copying a popular code without an enforcement owner is weaker than an honest statement that
the project is still establishing its process.

## Keep sensitive reports out of public issue templates

Open Source Guides recommends public, searchable communication for ordinary project work,
while calling out security issues and sensitive code-of-conduct violations as exceptions
that need a private route. GitHub's coordinated-disclosure guidance likewise warns that,
without a security policy, reporters may fall back to public issues or ad-hoc contact.

That leads to a practical split:

- bugs, feature requests and documentation problems → public issue or discussion;
- vulnerability details, secrets and sensitive abuse reports → verified private route;
- sanitized follow-up and public disclosure → only after the sensitive phase is complete.

Never ask a reporter to paste a secret or exploit into a public issue "for reproducibility."

## Readiness review

Before marking either policy as complete, verify all of these:

- [ ] The reporting destination exists and the intended maintainer can access it.
- [ ] A reporter can discover the route without already knowing a maintainer personally.
- [ ] Public issue templates warn against posting secrets or sensitive exploit details.
- [ ] The policy does not promise response times, confidentiality or staffing that are unproven.
- [ ] The maintainer knows who makes enforcement or disclosure decisions.
- [ ] Third-party policy text, if any, is used under its actual license/attribution terms.
- [ ] The route is rechecked when repository ownership, permissions or platform settings change.

File presence can satisfy a platform checklist while still failing every item above. Treat
the checklist as discovery, then inspect whether the process works.

## BeautifulRepo's current decision

As reviewed on **2026-10-06**, BeautifulRepo does not publish a root `SECURITY.md` or
`CODE_OF_CONDUCT.md`. That is intentional: a dedicated confidential reporting route and
conduct-enforcement path have not been verified. `CONTRIBUTING.md` therefore tells readers
not to post private material and points sensitive abuse to GitHub's platform reporting
facilities without pretending that this repository operates a confidential inbox.

The next step is operational, not cosmetic: verify a private reporting mechanism and an
enforcement owner, then adapt and publish the relevant policy. Until then, the reusable
security scaffold remains a template, not BeautifulRepo's own security policy.

## Sources and limits

Reviewed **2026-10-06**:

- [GitHub: About community profiles for public repositories](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories) — file recognition and community-profile behavior.
- [GitHub: Adding a security policy to your repository](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy) — supported versions and vulnerability-reporting instructions.
- [GitHub: Coordinated disclosure of security vulnerabilities](https://docs.github.com/en/code-security/concepts/vulnerability-reporting-and-management/coordinated-disclosure) — private advisory workflow and disclosure context.
- [GitHub: Adding a code of conduct to your project](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-code-of-conduct-to-your-project) — adoption, enforcement readiness and attribution.
- [Open Source Guides: Building Welcoming Communities](https://opensource.guide/building-community/) — public communication with explicit security/conduct exceptions.

This is bounded source review, not complete coverage of GitHub security features, incident
response, employment law, moderation law or the full Open Source Guides corpus.
