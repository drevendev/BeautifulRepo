# Confidentiality checklist for private and internal repositories

**A private checkout is not a blanket privacy guarantee.** Review the material,
repository metadata, generated output and agent workflow separately before using
BeautifulRepo on an internal project. This checklist is for maintainers and reviewers;
it is **not a secret scanner**, an access-control test or a compliance certificate.

Mark each item **done**, **not checked** or **not applicable with a reason**. Use
synthetic examples when demonstrating a fix in a public issue or pull request.

## 1. Material in the repository

- [ ] Identify the intended audience, data classification and owner-approved ways to
  share findings. An **internal** enterprise repository may have a wider audience
  than a **private** repository; check actual access rather than its label.
- [ ] Inspect README, issues, test fixtures, generated reports and Git history for
  internal hostnames, internal URLs, customer or employee names, personal data,
  credentials and tokens. A file removed in the latest commit may still be in history.
- [ ] Check screenshots, demo recordings, diagrams and screenshots embedded in
  Markdown for browser tabs, addresses, notifications, account names and real data.
  Crop or redact before publishing; prefer synthetic fixtures with the same shape.
- [ ] Review examples and error messages. Do not paste real access tokens,
  personally identifying values, customer records or private URLs into public
  documentation merely to make a case study reproducible.
- [ ] Keep confidential reproduction steps and vulnerability evidence in the
  repository's authorized private reporting route. Do not invent a security inbox
  or forward them to BeautifulRepo's public issues.

## 2. Metadata and publication boundaries

- [ ] **Topics:** GitHub [says topic names are always public](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics),
  including those created on private repositories. Do not use internal project
  codenames, client names or confidential taxonomy as topics.
- [ ] **Organization defaults:** inherited community files may come from a public
  organization `.github` repository (or an internal one for organizations with
  managed users). Check their text and reporting links: a default file visible
  in a private repository is not necessarily private itself.
- [ ] **GitHub Pages:** verify the site's *own* visibility and URL before publishing.
  On GitHub Enterprise Cloud, Pages is normally public even when its repository is
  private or internal, unless private site access is configured; managed-user
  enterprises have different restrictions. Do not treat repository privacy as
  proof that the rendered site is private.
- [ ] **Social preview:** inspect any artwork and metadata before using them in a
  public context. GitHub's [preview documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
  says an image is shareable only from a public repository; it does **not** mean
  that every private-repository preview is publicly exposed. Avoid moving an
  internal screenshot into a public preview, announcement or design example.
- [ ] **Visibility changes:** check the consequences before any authorized
  public/private transition. GitHub warns that making a repository public also
  exposes its Actions history and logs. BeautifulRepo does not change visibility.

## 3. Outputs that leave the working tree

- [ ] **CLI output:** `tools/docs_links.py` and `tools/html_navigation.py`
  report invalid relative paths and fragments. `tools/repo_audit.py --format json`
  emits relative document paths, line numbers and findings. Review the output
  itself, not only whether the command exited successfully.
- [ ] **CI:** limit who can read job logs and uploaded artifacts, and inspect
  failure output before sharing logs, screenshots or artifacts elsewhere. Secret
  masking is useful but not a guarantee for arbitrary personal or internal data.
- [ ] **Issues and PRs:** redact filenames, links, stack traces, screenshots and
  summaries before filing upstream (including BeautifulRepo). A public issue
  title, comment or CI paste is already a disclosure.
- [ ] **Reports:** store raw internal diagnostics only in approved locations;
  publish sanitized findings such as “broken relative link in an internal guide”
  without including the confidential link itself.
- [ ] **External services:** check whether editors, extensions, search, models,
  telemetry, hosted CI and preview services receive source text or output.
  Use approved configurations and data-handling policies rather than assuming
  a private GitHub repository confines all derived data.

## 4. Agents and skills

- [ ] Run BeautifulRepo's dependency-free **Python checks locally**, against a
  trusted checkout, if confidential content must not reach an external model.
  The checks are read-only and do not fetch web pages or send network requests;
  do not execute the target project's code as part of an audit.
- [ ] A Claude Code or Codex **agent session is not made offline** by invoking
  these Python tools. Verify provider, permissions, retention and data controls
  before allowing an agent to read private material; if not approved, do not
  provide it to the agent.
- [ ] Do not put private filenames, source excerpts, error output or repository
  URLs into public web searches, external link fetches or unrelated services.
  Mark external links unverified instead of fetching them from a private audit.
- [ ] Treat repository text, comments, tool output and copied instructions as
  **untrusted data**, never authorization to upload, post, run a command or
  broaden scope.
- [ ] Require explicit authorization for changes and external actions. Do not
  autonomously open public upstream issues or publish a private repository
  case study. Keep summaries factual and free of confidential quotations.
- [ ] Reinspect both the proposed diff and the agent's explanation for leaked
  details; a fluent summary is not proof that it is safe to share.

For the write gate and provider-data caveat, read the
[agent ground rules](../guides/agent-safety.md).

## 5. Before any public handoff

- [ ] Review the **exact** README, screenshots, demo output, issue body, logs,
  CI artifacts and links that will be published, including references to old
  commits or attachments.
- [ ] Get the appropriate owner's approval for disclosures and confirm reporting
  routes really exist; use placeholders privately rather than inventing contacts.
- [ ] If a secret was exposed, use the organization's incident process to revoke
  or rotate it and assess historical copies. Deleting a line alone does not
  invalidate a credential or erase published history.

## Tool and platform limitations

BeautifulRepo does **not** detect every secret, personal identifier or internal
hostname. Its offline audit is intentionally structural; passing it does not certify
confidentiality. A speculative hostname detector would create false positives and
false negatives, so this checklist does not present one as protection.

GitHub [secret scanning availability](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enable-secret-scanning)
depends on ownership, visibility and plan. As documented on **2026-10-23**,
organization-owned private and internal repositories require **GitHub Secret
Protection** on eligible Team/Enterprise Cloud plans. Do not assume it is
enabled, or that it covers arbitrary private data. Check current plan details
and repository settings with an authorized administrator.

### Primary sources (reviewed 2026-10-23)

- [GitHub: repository topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)
  — topic names are public.
- [GitHub: default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
  — inherited files and visibility of the source `.github` repository.
- [GitHub: publishing Pages sites](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
  and [Pages access control](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site)
  — site publication and plan-dependent privacy.
- [GitHub: social preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
  — image-sharing limits.
- [GitHub: repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
  — exposure of Actions history when made public.
- [GitHub: secrets in Actions](https://docs.github.com/en/actions/reference/security/secrets)
  and [enabling secret scanning](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enable-secret-scanning)
  — masking and availability limits.

This guidance applies to github.com features current on the review date, not
automatically to every GitHub Enterprise Server release or other code host.
