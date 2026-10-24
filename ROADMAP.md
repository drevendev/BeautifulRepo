# Roadmap

BeautifulRepo is a working handbook, not a promise of future releases.
Milestones describe useful outcomes rather than dates or assumed volunteer labor.

## Available in this repository

- Reader-first [README](README.md), [repository checklist](checklists/repository.md),
  [README guide](guides/readme.md) and [README scaffold](templates/README.template.md).
- [Visual README patterns](guides/readme-visuals.md), including a before/after example
  with theme-aware assets, text equivalents and a
  [project-specific design brief](examples/readme-visuals/DESIGN_INTENT.md).
- [Editorial evidence kit](guides/editorial-evidence.md), with fact-preserving
  before/after README, announcement and changelog copy examples.
- [Offline catalog validation](tools/README.md) and repository-owned Markdown
  destination checks, both exercised by CI.
- [Offline repository entry-point audit](guides/repository-audit.md), with bounded
  read-only checks, actionable findings and a
  [tested before/after walkthrough](examples/repository-audit/README.md).
- [Community safety readiness](guides/community-safety.md) guidance and an explicitly
  non-live security-policy scaffold, without fictitious confidential reporting routes.
- [Tested CLI repository starter](guides/cli-repositories.md), including an executable
  [sample command](examples/cli-starter/README.md) and black-box tests.
- [Library repository starter](guides/library-repositories.md) with a runnable
  [checkout-only example](examples/library-starter/README.md) and
  [README template](templates/LIBRARY_README.template.md); no package is published.
- [Application repository starter](guides/application-repositories.md), with the
  [read-only Pocket Board demo](examples/application-starter/README.md), local HTTP
  integration tests and honest development-server boundaries.
- [Research/data repository starter](guides/research-data-repositories.md), including
  a [synthetic CSV analysis](examples/research-data-starter/README.md), fixture integrity
  checks and a [README template](templates/RESEARCH_DATA_README.template.md).
- [Release-note writing guide](guides/release-notes.md) and
  [editable draft template](templates/RELEASE_NOTES.template.md), distinguishing
  tags, GitHub Releases and maintained changelogs without implying a release.
- [Annotated pattern studies](case-studies/first-patterns.md) and a
  [curated source catalog](catalog/README.md).
- [Curated collection starter](guides/curated-collections.md), with
  [three annotated references](examples/curated-starter/README.md), deterministic
  Markdown/JSON output and explicit input boundaries.
- [Working-example index](examples/README.md), [first-success checklist](checklists/first-success.md),
  [maintenance workflow](guides/maintenance-workflow.md) and application/collection README templates.

- [Maintainer handoff recipe](guides/maintainer-handoff.md), with a fictional
  one-maintainer pause notice, responsibility checklist and real checkout commands.

- [GitHub Action and adoption guide](guides/adopting-the-checks.md) for running the
  audit and link checks in other repositories, first tagged as
  [`v0.1.0`](https://github.com/drevendev/BeautifulRepo/releases/tag/v0.1.0).

- [Claude Code and Codex plugin](guides/agent-plugin.md) with a read-only `audit-repo`
  skill and [ground rules for agents](guides/agent-safety.md), first released in
  v0.2.0.
- A [security policy](SECURITY.md) backed by GitHub private vulnerability reporting,
  Discussions for questions, and labelled issue forms. A conduct policy is
  [not applicable for now](guides/community-safety.md), with the reason recorded.
- Hardened checks: link destinations and symlink targets are resolved inside the
  repository, wrong letter case and Windows-only names are reported, heading anchors
  follow GitHub's rules, and worst-case scanning time is bounded.
- Maintenance automation: scheduled pin and review-date checks, a
  [release draft workflow](guides/maintenance-workflow.md), a hash-pinned linter in
  CI, [AGENTS.md](AGENTS.md) and [decision records](docs/decisions/README.md).
- A [real README before/after case](case-studies/readme-first-success-case.md) for
  BeautifulRepo itself, including a clean-clone run and GitHub's rendering at three
  widths in both themes.

These linked resources are repository source files. Tagged versions are listed on
the [Releases page](https://github.com/drevendev/BeautifulRepo/releases). There is
no installable package.

## Next: agent skills, real cases and private repositories

Each workstream is an epic issue whose sub-issues hold the concrete work.

- A **development-only** `improve-readme` skill proposes scoped diff previews with an explicit approval gate; it is not part of the pinned `v0.2.0` plugin and is not validated by a real model run (#70, #74).

- **Agent skills** ([#86](https://github.com/drevendev/BeautifulRepo/issues/86)):
  release the plugin as v0.2.0
  ([#101](https://github.com/drevendev/BeautifulRepo/issues/101)), validate the
  manifests and skills in CI, add `improve-readme`, `trust-surfaces` and
  `release-notes` skills, and evaluate every skill against fixture repositories.
- **Real before/after cases**
  ([#88](https://github.com/drevendev/BeautifulRepo/issues/88)): document the
  repeatable case workflow, then apply it through normal pull requests to three of
  the owner's public repositories, with fixed revisions and stated limits.
- **Private and internal repositories**
  ([#87](https://github.com/drevendev/BeautifulRepo/issues/87)): a visibility
  profile for the audit and the Action, plan-aware guidance, an internal README
  template, a confidentiality checklist for people and agents, and a tested
  no-network promise for mirrored or enterprise use of the Action.
- **Self-check** ([#85](https://github.com/drevendev/BeautifulRepo/issues/85),
  readiness index [#33](https://github.com/drevendev/BeautifulRepo/issues/33)):
  re-audit BeautifulRepo against its own checklists at a named commit and record
  the result.

## Later: evidence-backed extensions

Explore cross-ecosystem case studies, distinctive presentation patterns backed by
real visual evidence ([#16](https://github.com/drevendev/BeautifulRepo/issues/16)),
practical examples drawn from Open Source Guides material on governance,
sustainability and finding users, and a verified migration story in the
release-note guide once real releases exist. Extend the local audit only where
observations are actionable and its limitations remain explicit. Spending, domains,
releases, applications and external promotion require separate owner authority.

## Maintenance

Keep verified examples working, recheck time-sensitive sources, review
contributions, retire redundant material and improve BeautifulRepo by applying
its own guidance. Progress means integrated useful work—not file, link or star counts.
