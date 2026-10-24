# Private and internal GitHub repositories: choose features by plan

**Checked: 2026-10-24 (GitHub.com documentation).** This is a decision guide,
not a visibility audit, a security certification or a request to change settings.
GitHub Enterprise Server and GitHub Enterprise Cloud with data residency have
different deployment policies; verify those separately before applying a row.
An **internal** repository is an enterprise visibility option, not another name
for every private repository.

## First choose the audience, not a badge

1. Record who is allowed to see the source, documentation, CI logs, artifacts,
   images and generated reports. A private repository can still publish a
   **public website**.
2. Verify the owning account's actual plan and any organization policy. Features
   below are plan entitlements, not proof that they are enabled in your repository.
3. Name a working internal owner, help path and security intake. Do not invent a
   contact, a reporting SLA or a public contribution route for a closed project.
4. Run checks on a local checkout and share only findings approved for the
   intended audience. An agent session may transmit context to its model provider;
   BeautifulRepo's offline Python scripts do not.

For a concrete starting point, adapt the [internal README template](../templates/INTERNAL_README.template.md)
and [confidentiality checklist](../checklists/confidentiality.md), then compare the
[fictional filled example](../examples/internal-repository/README.md).

## Feature matrix for private repositories on GitHub.com

The columns mean **availability on that plan**, not that an owner has switched
anything on. Every feature name links to its primary GitHub documentation.

| Feature | Free | Pro | Team | Enterprise Cloud |
| --- | --- | --- | --- | --- |
| [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) in private repos | No | Yes | Yes | Yes |
| [Repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) for private repos | No | Yes | Yes | Yes |
| [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) on private repos | No | Yes | Yes | Yes |
| [Pages from private source](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) | No | Yes* | Yes* | Yes* |
| [Privately published Pages](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site) | No | No | No | Eligible organizations* |
| [Private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository) | Public repos only | Public repos only | Public repos only | Public repos only |
| [Repository security advisories](https://docs.github.com/en/code-security/concepts/vulnerability-reporting-and-management/repository-security-advisories) | Public repos only | Public repos only | Public repos only | Public repos only |
| [External workflow-status badges](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge) | Not accessible | Not accessible | Not accessible | Not accessible |

`*` GitHub Pages usually publishes a **publicly accessible site** even when its
source repository is private. Enterprise Cloud organizations can configure private
Pages publishing; Enterprise Managed Users have additional restrictions. Check the
[Pages access-control conditions](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site)
before using confidential content. Pages is not an internal-documentation
security boundary merely because the source code is private.

Additional cross-plan behavior:

- [Topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)
  are allowed on private repositories, but **topic names are always public**.
  Never put an internal customer, incident or unannounced code name in one.
- [Social previews](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
  can only be shared from a **public** repository. Do not promise a private
  repository's image will appear to signed-out visitors.
- [Account-wide default community files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
  may apply to private repositories, but the source `.github` repository must
  be **public**. Avoid publishing private contacts or company-only instructions
  in those shared defaults; override locally when necessary.
- [GitHub Actions on private repositories](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
  uses plan-dependent allowances for hosted minutes and storage; usage beyond
  included amounts can be billed to the **repository owner**. Confirm spending
  policies and runner permissions before enabling workflows.

## Apply the rules without making false promises

### First use and licence

An internal repository can give authorized readers explicit usage and ownership
terms instead of asserting an open-source licence that was never granted.
Record the actual company policy; do not interpret a missing licence as
permission to reuse the code. Replace signed-out demo and public-contributor
instructions with authorized access requests, exact local prerequisites and
an expected offline result. Never paste internal output into a public issue.

### Contribution, conduct and reporting

A private team may use an internal issue queue and a verified corporate security
route. GitHub's **private vulnerability reporting** and **repository advisories**
listed above are public-repository features on GitHub.com, not generic private
inboxes for every visibility setting. A security policy can still describe a real
internal route, but do not claim that adding the file enables a form. A conduct
policy needs both a reporting destination and an owner able to enforce it. If
your organization uses a central policy, link only a destination reachable by
your intended readers.

Mark a public-only checklist item **not applicable, with the reason**. For example:
"Public contribution instructions: N/A — access is limited to named employees;
the internal issue queue is in the approved company portal." Do not mark an
unavailable feature as a pass or mislabel a missing internal route as N/A.

### Checks, badges and distribution

You can run BeautifulRepo's three [offline checks](adopting-the-checks.md#without-github-actions)
on a private checkout. If you use the [GitHub Action](adopting-the-checks.md),
confirm account policies, the reviewed commit pin and private-runner billing.
A protected branch is a separate plan-dependent feature, **not** a prerequisite
for running CI. Avoid public badge/image URLs or artifacts that imply strangers
can inspect a private run. For evidence, cite a run only to people with access,
and record a sanitised result if sharing is authorized.

## Recheck triggers and limits

Re-read the source of a row before making a purchasing, security or release
decision; review the matrix after a GitHub plan, Pages, security-feature or
organizational-policy change. These observations were checked on
**2026-10-24**, not guaranteed permanently. This guide does not test any paid
plan, enterprise tenant, private publishing configuration, protected-branch
settings, notification delivery or actual confidential reporting endpoint.
Do not upgrade a plan, enable Pages, change visibility or turn on a setting
solely on the strength of this documentation.
