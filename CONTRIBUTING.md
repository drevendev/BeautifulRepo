# Contribute to BeautifulRepo

Thank you for helping make repositories easier to understand. Useful contributions
include a clearer example, a repaired link, an accessibility improvement, a tested
workflow or a small tool with a well-defined purpose.

## Start small

Read the [roadmap](ROADMAP.md) and search existing issues and pull requests. Describe the
reader's problem before proposing a solution. An issue is helpful for a large change;
a small correction can go straight to a pull request. Keep one topic per contribution.
Coding agents follow the short contract in [AGENTS.md](AGENTS.md). The
[decision records](docs/decisions/README.md) explain why the tools, the Action and
`master` work the way they do.

## Ask a question

Questions, ideas and stories about using BeautifulRepo belong in
[Discussions](https://github.com/drevendev/BeautifulRepo/discussions); the **Q&A**
category lets an answer be marked as accepted. Issues are for reproducible problems and
concrete improvements. Security vulnerabilities go through [SECURITY.md](SECURITY.md).

## Find work by label

| Label | Meaning |
| --- | --- |
| `good first issue` | Scoped, with files and acceptance criteria named; a good first contribution. |
| `bug`, `enhancement`, `documentation`, `accessibility` | The kind of change. Issue forms set the first two. |
| `epic` | An umbrella issue; the work happens in its sub-issues. |
| `self-check` | BeautifulRepo passing its own checklists. |
| `borrowed-practice` | A practice adopted from another drevendev repository (`hungry-crab` marks those Hungry Crab suggested). |
| `agent-skill` | The Claude Code and Codex plugin and its skills. |
| `private-repos` | Support for private and internal repositories. |
| `real-case` | A before/after case on a real repository. |

Seasonal labels are not an invitation to earn event rewards. Hacktoberfest 2026
**does not count pull requests or merge requests toward rewards**; see the
[dated programs guide](guides/programs.md) and the
[organizer FAQ](https://hacktoberfest.com/questions/). Some closed, historical
issues may still carry a `hacktoberfest` label. It does not indicate current
work, event enrollment, organizer endorsement or reward eligibility.

If no `good first issue` is open, none is curated right now; ask in Discussions before
starting something large.

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
python tools/repo_audit.py .
```

The first command explicitly regenerates `catalog/README.md`; the others are the five
checks CI runs. `repo_audit.py` audits BeautifulRepo's own README, licence and
contribution entry points.
The original documentation-link check covers repository-owned inline Markdown
link and image paths. The HTML navigation checker adds bounded local HTML/media
and section-fragment checks. Neither checks external URLs, completely renders
Markdown, or certifies accessibility. Review the generated diff. No network
access or third-party Python packages are needed.

CI also runs [ruff](https://docs.astral.sh/ruff/) in a separate `Lint` job, with the
rules in `ruff.toml`. You don't need it locally. To run it anyway, install the pinned
version with `python -m pip install --require-hashes -r .github/lint-requirements.txt`
on Linux x86-64, or the same `ruff==` version elsewhere, then run `ruff check`.

## How a change reaches `master`

`master` is protected: every change arrives through a pull request, merged with
**squash** only, after the required checks pass on a branch that is up to date with
`master`. The required checks are `Python 3.11`, `Python 3.14`,
`Python 3.14 (Windows)`, `Action self-test (ubuntu-latest)` and
`Action self-test (windows-latest)`. Force-pushes and deletion of `master`, and
moving or deleting `v*` release tags, are blocked for everyone, including admins.

## Before an authorized Action or plugin release

The Action and the Claude Code/Codex plugin share this repository. A release
must be reviewed as one compatible public artifact, not as unrelated version
numbers. A release/tag requires separate owner authorization.

1. Set the same release version in `.claude-plugin/plugin.json` and
   `plugin.json`; marketplace entries must **not** have a version.
2. Add a dated `## [vX.Y.Z] — YYYY-MM-DD` heading to `CHANGELOG.md`.
   Document Action compatibility, security changes and whether consumers
   should update a commit pin.
3. Run the five local checks above and review the actual required Ubuntu,
   Windows and Action self-test jobs on the intended commit. The existing
   `tests/test_agent_plugin.py` checks skill frontmatter, commands,
   references and manifest consistency.
4. If an authorized `vX.Y.Z` tag is pushed, the quality workflow also runs
   on the tag and checks that the two manifest versions equal `X.Y.Z` and
   the changelog contains the dated release heading. A green check does
   not independently approve the release or a public announcement.
5. Review the resulting draft GitHub Release and the immutable tag's
   commit before any authorized publication; never rewrite an existing
   tag. Keep `master` on an explicit development version afterwards.

The agent skill reference tests are static contract checks, not proof that
an agent will trigger correctly or ignore prompt injections. Those model-
driven evaluations are tracked separately in
[Issue #74](https://github.com/drevendev/BeautifulRepo/issues/74).

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
Change a "Reviewed" or `reviewed_on` date only after actually re-reading that source.
Do not add tracking images, copied brand assets, misleading badges, unsupported benchmark
claims, referral promotions or bulk low-effort changes.

A pull request should explain the change, evidence, checks actually run and remaining
limitations. Reports about documentation, code and accessibility are all welcome. The
maintainer handles review and implementation; contributors are not expected to rescue an
abandoned queue. No guaranteed response-time service level is claimed.

## Respect and safety

Discuss the work, not personal attributes. Harassment, doxxing and discriminatory conduct
are not welcome. Do not post secrets, private logs or personal contact information in
issues. Report security vulnerabilities privately as described in [SECURITY.md](SECURITY.md).
BeautifulRepo has no conduct policy yet, for the reasons in the
[community safety guide](guides/community-safety.md); its absence must not be represented
as complete community compliance. For sensitive abuse that cannot safely be posted here,
use GitHub's platform reporting facilities rather than disclosing private details in an issue.
