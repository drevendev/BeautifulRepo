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
- [Read-only audit delta](guides/audit-before-after.md) for comparing saved
  JSON reports across pinned revisions, with coverage-change warnings and
  no claim that reduced finding counts prove an improved experience.
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
- [First-contribution route](guides/first-contribution.md) with a
  [copyable good-first-issue template](templates/GOOD_FIRST_ISSUE.template.md),
  a clearly fictional broken-link repair example, contributor and maintainer
  acceptance steps, and no implied assignments or review guarantees.

- [Repository pause and archive recipe](guides/repository-retirement.md) and
  [reusable status notice](templates/REPOSITORY_STATUS_NOTICE.template.md),
  distinguishing an unmaintained but writable repo from a GitHub-archived
  read-only repo and retaining last-verified evidence without inventing support.
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

## Current work: verify the four-skill candidate and demonstrate real use

This section reflects issue/source inspection on **2026-11-04**. It is not
a release date or evidence of passing model tests. Consult the linked GitHub
issues for their live status.

- **Four-skill plugin candidate** ([#257](https://github.com/drevendev/BeautifulRepo/issues/257)):
  the published `v0.2.0` plugin has **only** `audit-repo`. The [exact
  four-skill development candidate](guides/agent-plugin.md#try-all-four-skills-from-a-pinned-development-candidate)
  is pinned to `a6ff79ee137d2eee8517792ba693c2854d51ed48` (`0.3.0-dev.0`). Source/CI tests
  do not verify successful *fresh install*, skill discovery or model behavior
  in Claude Code and Codex. The [manual matrix](evals/manual-smoke.md),
  [fixture infrastructure](https://github.com/drevendev/BeautifulRepo/issues/74)
  and [independent tester invitation](https://github.com/drevendev/BeautifulRepo/issues/258)
  cover the remaining positive, negative and hostile cases. No stable
  four-skill release is claimed.
- **Real before/after cases**
  ([#88](https://github.com/drevendev/BeautifulRepo/issues/88)):
  the [repeatable procedure](case-studies/README.md) and
  [PatchPitch case](case-studies/patchpitch.md) are published. Additional
  case studies need exact before/after revisions, observed first-run commands
  and authenticated PR evidence. Changes to other repositories are outside
  BeautifulRepo's writable scope.
- **Launch-first-minute evidence**
  ([#254](https://github.com/drevendev/BeautifulRepo/issues/254)):
  README now leads with the offline audit, a reproducible synthetic before/after
  and a revision-pinned real audit result. The remaining evidence-led visual
  showcase, manual rendering observations and launch readiness must be verified
  separately; no external promotion is implied.
- **Visual verification boundaries:** the presentation work in
  [#16](https://github.com/drevendev/BeautifulRepo/issues/16) is **closed**,
  with alternative entrances, design briefs and a
  [manual acceptance checklist](checklists/visual-accessibility-acceptance.md).
  Structural tests alone still do not certify complete keyboard, screen-reader,
  real 400% zoom or light/dark accessibility behavior; those claims need
  separately recorded manual evidence.
- **Native historical label**
  ([#100](https://github.com/drevendev/BeautifulRepo/issues/100)):
  public Hacktoberfest 2026 guidance already disclaims PR reward credit;
  the remaining provider-side `hacktoberfest` label issue is separate from
  the public documentation. Do not infer participation from an old label.

The [private/internal repository guidance](guides/private-repositories.md),
[confidentiality checklist](checklists/confidentiality.md) and repository
self-check are published. The proposed [local MCP server](https://github.com/drevendev/BeautifulRepo/issues/255)
is a **separate future workstream**, not part of the installed four-skill
candidate or a prerequisite for the plugin release.

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
