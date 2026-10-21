# Contribute to BeautifulRepo

Thank you for helping make repositories easier to understand. Useful contributions
include a clearer example, a repaired link, an accessibility improvement, a tested
workflow or a small tool with a well-defined purpose.

## Start small

Read the [roadmap](ROADMAP.md) and search existing issues and pull requests. Describe the
reader's problem before proposing a solution. An issue is helpful for a large change;
a small correction can go straight to a pull request. Keep one topic per contribution.

## Add a resource

Edit `catalog/resources.json`, not its generated README. Each resource needs a primary
source, a specific benefit, a local application, a limitation, a real review date and
honest coverage. “Popular” and “awesome” are not sufficient reasons to list something.
Separate reading documentation from running a tool. Link to copyrighted material rather
than copying it; check permissions and preserve required attribution before any reuse.

From the repository root with Python 3.11 or newer:

```bash
python tools/catalog.py --write
python tools/catalog.py
python tools/docs_links.py
python tools/html_navigation.py
python -m unittest discover -s tests -v
```

The first command explicitly regenerates `catalog/README.md`; the others are checks.
The original documentation-link check covers repository-owned inline Markdown
link and image paths. The HTML navigation checker adds bounded local HTML/media
and section-fragment checks. Neither checks external URLs, completely renders
Markdown, or certifies accessibility. Review the generated diff. No network
access or third-party Python packages are needed.

## Link issues without closing unfinished work

A pull request can **mention** an issue without promising to finish it. If acceptance
remains open, use a plain reference such as `Related: #28` or `Follow-up: #28`
and say what remains. For example:

> Related: #28 — Pocket Board's keyboard, contrast, and zoom review is still open.

Do **not** write a negated closing phrase such as `Does not fix #28`.
GitHub recognizes the closing keyword next to the issue number even when
the surrounding sentence says the work is unfinished. In this repository,
[PR #37](https://github.com/drevendev/BeautifulRepo/pull/37) unintentionally
closed [Issue #28](https://github.com/drevendev/BeautifulRepo/issues/28)
on merge; the issue was reopened because its visual/accessibility acceptance
was not complete. A negative sentence is not a safe substitute for a plain
issue reference.

When a pull request **actually completes** all acceptance criteria, deliberately
include `Closes #<issue-number>` in its description. Before merging, check the
linked issues and the PR description (and relevant commit messages) for unintended
closing references. GitHub recognizes `close` / `closes` / `closed`,
`fix` / `fixes` / `fixed`, and `resolve` / `resolves` / `resolved`.
The PR-description keyword behavior applies when the PR targets the default branch.

**Primary source (reviewed 2026-10-20):**
[GitHub Docs — Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).
This is guidance about native issue-linking behavior, not an automated policy
or a change to the repository's auto-close settings.

## Quality expectations

Public documentation is in English. Use descriptive headings and links, text alternatives
for meaningful images, and short, verified examples. Identify incomplete investigations.
Do not add tracking images, copied brand assets, misleading badges, unsupported benchmark
claims, referral promotions or bulk low-effort changes.

A pull request should explain the change, evidence, checks actually run and remaining
limitations. Reports about documentation, code and accessibility are all welcome. The
maintainer handles review and implementation; contributors are not expected to rescue an
abandoned queue. No guaranteed response-time service level is claimed.

## Respect and safety

Discuss the work, not personal attributes. Harassment, doxxing and discriminatory conduct
are not welcome. Do not post secrets, private logs or personal contact information in
issues. A dedicated conduct policy and confirmed confidential reporting route remain on
the roadmap; their absence must not be represented as complete community compliance.
For sensitive abuse that cannot safely be posted here, use GitHub's platform reporting
facilities rather than disclosing private details in an issue.
