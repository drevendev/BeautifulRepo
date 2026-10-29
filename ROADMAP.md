# Roadmap

BeautifulRepo is a working handbook, not a promise of future releases.
Milestones describe useful outcomes rather than dates or assumed volunteer labor.

## Available in this repository

- Reader-first [README](README.md), [repository checklist](checklists/repository.md),
  [README guide](guides/readme.md) and [README scaffold](templates/README.template.md).
- [Visual README patterns](guides/readme-visuals.md), including a before/after example
  with theme-aware assets, text equivalents and a
  [project-specific design brief](examples/readme-visuals/DESIGN_INTENT.md).
- [Three fictional README first-screen treatments](examples/readme-visuals/variants/README.md)
  with identical facts, different reader priorities, an explicit design-intent
  comparison and static regressions (not measured browser accessibility).
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

- [Evidence-led issue triage recipe](guides/issue-triage.md), with a copyable
  decision card, real issue examples and explicit not-run/permission boundaries.

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
  BeautifulRepo itself, including a clean-clone run and GitHub-rendered reflow
  observations at three emulated widths. Contrast was recorded only in light
  mode at 1280 px and dark mode at 375 px; real 400% zoom, keyboard and
  screen-reader checks were not performed.

These linked resources are repository source files. Tagged versions are listed on
the [Releases page](https://github.com/drevendev/BeautifulRepo/releases). There is
no installable package.

## Current work: verify agents, finish real cases and test visuals

This section reflects issue states inspected **2026-10-28**. It is not a
promise of a release date or evidence that unrun manual tests passed.
For live status, follow the linked GitHub issues.

- **Agent behavior** ([#86](https://github.com/drevendev/BeautifulRepo/issues/86)):
  the pinned `v0.2.0` release includes `audit-repo`, while
  `improve-readme` ([#70](https://github.com/drevendev/BeautifulRepo/issues/70))
  and `draft-release-notes` ([#72](https://github.com/drevendev/BeautifulRepo/issues/72))
  remain development-only skills. The `trust-surfaces` implementation issue
  [#71](https://github.com/drevendev/BeautifulRepo/issues/71) is closed, but
  that does **not** establish real-agent reliability. Synthetic
  [fixture and model evaluations](https://github.com/drevendev/BeautifulRepo/issues/74)
  still need authorized execution and evidence; static CI is not a model test.
- **Real before/after cases**
  ([#88](https://github.com/drevendev/BeautifulRepo/issues/88)):
  the [repeatable procedure](case-studies/README.md) and
  [PatchPitch case](case-studies/patchpitch.md) are published. Remaining
  candidates must keep before/after revisions, observed commands and actual
  PR evidence; their separate target repositories are **not** writable as
  part of BeautifulRepo maintenance.
- **Visual accessibility evidence**
  ([#16](https://github.com/drevendev/BeautifulRepo/issues/16)):
  alternative README entrances, source-bound design briefs and the
  [GitHub-rendered acceptance checklist](checklists/visual-accessibility-acceptance.md)
  exist. Actual light/dark, 320 px reflow, 400% zoom, keyboard and screen-reader
  results still require a completed manual evidence receipt; a passing source
  check cannot supply one.
- **Historical event labels**
  ([#100](https://github.com/drevendev/BeautifulRepo/issues/100)):
  the public Hacktoberfest 2026 guidance already disclaims PR reward credit.
  The outdated native label description remains a separate owner decision,
  with the requested post-event review **after 2026-11-01**.

The [private/internal repository guidance](guides/private-repositories.md) and
[confidentiality checklist](checklists/confidentiality.md) are already published
([#87](https://github.com/drevendev/BeautifulRepo/issues/87) closed).
The [repository self-check](https://github.com/drevendev/BeautifulRepo/issues/85)
and [readiness review](https://github.com/drevendev/BeautifulRepo/issues/33)
are likewise completed; do not list them as pending work.

## Later: evidence-backed extensions

Explore cross-ecosystem case studies, practical examples drawn from Open
Source Guides material on governance, sustainability and finding users, and a
verified migration story in the release-note guide when a specific release
provides suitable evidence. Extend the local audit only where
observations are actionable and its limitations remain explicit. Spending, domains,
releases, applications and external promotion require separate owner authority.

## Maintenance

Keep verified examples working, recheck time-sensitive sources, review
contributions, retire redundant material and improve BeautifulRepo by applying
its own guidance. Progress means integrated useful work—not file, link or star counts.
