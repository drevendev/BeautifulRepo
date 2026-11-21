# CODEOWNERS: route reviews without inventing a merge gate

A `CODEOWNERS` file helps contributors discover who can review which files.
It **does not** by itself require approval or prove that a maintainer is
available. For a one-maintainer project with no backup, clear CONTRIBUTING
guidance may be more honest than automated ownership requests.

Start with the [editable example](../templates/CODEOWNERS.template).
It is intentionally stored under `templates/`, **not** as an active
`.github/CODEOWNERS` in BeautifulRepo. Every `@YOUR-*` value is a
placeholder, not a real or verified account.

## 1. Name reviewers who can actually review

Confirm each user or organization team exists, agrees to review that area,
and has **write** access to the repository. An organization team must also be
**visible** and have its *own* write access; individual members' permissions
do not substitute for the team's permission. Do not invent team names,
notification destinations or availability guarantees.

## 2. Use the intended base branch and correct precedence

After adapting the template, propose `.github/CODEOWNERS` in a normal PR.
GitHub searches `.github/`, then the repository root, then `docs/`;
if multiple CODEOWNERS files exist, only the first location is used. Check
for and reconcile older copies before installing a new one. Review routing
uses the **base branch** of a PR, not the proposing feature branch.

Illustrative mapping (the names below are **not** install-ready accounts):

```text
*                   @YOUR-REPO-OWNER
/docs/              @YOUR-DOCS-OWNER
/tools/             @YOUR-TOOLS-OWNER
/.github/CODEOWNERS @YOUR-REPO-OWNER
```

The **last matching pattern** wins. On `docs/setup.md`, `/docs/`
overrides `*`; the owners do not accumulate. To offer more than one eligible
owner for a single pattern, place them on the **same line**. Paths are
case-sensitive. Unlike `.gitignore`, CODEOWNERS does not support `!`
negation or `[abc]` ranges; invalid lines can be ignored. GitHub does
not load a CODEOWNERS file over 3 MB. Make sure the CODEOWNERS file itself
has a verified owner as well.

## 3. Validate through GitHub before trusting it

On the branch containing your adapted file, use the provider's native
syntax-error endpoint (replace the three placeholders):

```sh
gh api --method GET \
  'repos/OWNER/REPO/codeowners/errors?ref=YOUR-BRANCH'
```

A successful response with `"errors": []` means GitHub found no
**reported syntax errors** for that ref, not that your mapping is complete
or reviewers will respond. A 404, permission failure or unavailable API
is **unknown**, not proof of a valid/invalid configuration. Also inspect
the CODEOWNERS file in GitHub for highlighted errors and the file-view
owner badge for sample paths.

After the file is on the PR's **base branch**, open a subsequent
**non-draft** PR touching a matched path and observe the requested reviewer.
Draft PRs do not automatically request code-owner reviews until marked ready.
Record the actual observed request and whether the intended user/team has
permission; do not claim a host test from source inspection alone.

## 4. Keep enforcement separate

CODEOWNERS routes requests; required code-owner approval is configured
**separately** through protected branches or rulesets by authorized admins.
Do not change those settings to make this example pass and do not add
unverified review gates. Where a required code-owner gate exists, approval
from **one** eligible owner on a matching rule normally suffices; listing
two does not require both. Check the actual provider rules before merge.

Recheck owner access, team visibility, pattern precedence and reviewers
when maintainers or repository structure change. If no real reviewer exists,
remove the dead rule rather than leaving a misleading badge.

## Sources and limits

Official material reviewed **2026-11-21**:

- [GitHub: About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub: List CODEOWNERS errors API](https://docs.github.com/en/rest/repos/repos#list-codeowners-errors)
- [GitHub: Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

This guide is a **recipe**, not a tested installation, active ownership
configuration, required review policy or security audit. It changes no
repository settings, credentials or other repositories. For actual merge
judgement, see [evidence-led PR review](pull-request-review.md) and
[maintainer capacity](maintainer-capacity.md).
