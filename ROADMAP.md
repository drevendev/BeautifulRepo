# Roadmap

BeautifulRepo is a working handbook, not a promise of future releases.
Milestones describe useful outcomes rather than dates or assumed volunteer labor.

## Available in this repository

- Reader-first [README](README.md), [repository checklist](checklists/repository.md),
  [README guide](guides/readme.md) and [README scaffold](templates/README.template.md).
- [Third-party asset provenance](guides/third-party-assets.md) with a
  [reusable rights-evidence record](templates/ASSET_PROVENANCE.template.md),
  hypothetical include/defer/replace decisions and a real existing notice example.
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
- [Game repository README guidance](guides/game-repositories.md),
  [editable game README template](templates/GAME_README.template.md), and
  [runnable Lantern Row terminal example](examples/game-starter/README.md)
  with a deterministic win, failure/quit routes and standard-library tests.
  This is source-only, not a hosted or published game; code and asset rights
  remain separate.
- [Research/data repository starter](guides/research-data-repositories.md), including
  a [synthetic CSV analysis](examples/research-data-starter/README.md), fixture integrity
  checks and a [README template](templates/RESEARCH_DATA_README.template.md).
- [Release-note writing guide](guides/release-notes.md) and
  [editable draft template](templates/RELEASE_NOTES.template.md), distinguishing
  tags, GitHub Releases and maintained changelogs without implying a release.
- [Annotated pattern studies](case-studies/first-patterns.md) and a
  [curated source catalog](catalog/README.md).
- [Public-evidence gate for source-only cases](case-studies/README.md#source-only-reviews-useful-but-not-a-beforeafter)
  and [reusable source-only template](templates/SOURCE_ONLY_CASE.template.md),
  distinguishing inspected source from unrun commands and upstream changes.
- [Curated collection starter](guides/curated-collections.md), with
  [three annotated references](examples/curated-starter/README.md), deterministic
  Markdown/JSON output and explicit input boundaries.
- [Working-example index](examples/README.md), [first-success checklist](checklists/first-success.md),
  [maintenance workflow](guides/maintenance-workflow.md) and application/collection README templates.

- [Small-project governance decisions](guides/governance-decisions.md): a
  copyable decision card and annotated real offline-tool choice, without invented roles.
- [Dependency-update review recipe](guides/dependency-review.md) and
  [editable decision card](templates/DEPENDENCY_REVIEW.template.md), grounded
  in source/privilege/test evidence without new security settings.
- [Evidence-led pull request review](guides/pull-request-review.md) with a
  [copyable review record](templates/PULL_REQUEST_REVIEW.template.md), an
  annotated existing PR and explicit separation of actual GitHub gates from
  reviewer judgement; no new review policy or repository settings.
- [Capacity-based maintenance guide](guides/maintainer-capacity.md) with a
  [copyable, explicitly non-binding capacity card](templates/MAINTAINER_CAPACITY.template.md),
  a worked fictional monthly allocation and verified support-route boundaries.
- [Evidence-led issue triage recipe](guides/issue-triage.md), with a copyable
  decision card, real issue examples and explicit not-run/permission boundaries.
- [First-contribution route](guides/first-contribution.md) with a
  [copyable good-first-issue template](templates/GOOD_FIRST_ISSUE.template.md),
  a clearly fictional broken-link repair example, contributor and maintainer
  acceptance steps, and no implied assignments or review guarantees.
- [Contributor-program guidance](guides/programs.md) and the
  [draft GSoC project-idea card](templates/GSOC_PROJECT_IDEA.template.md),
  with observed-scope, mentor-capacity and AI-policy checks; neither template
  nor guide implies program enrollment or a confirmed next-year schedule.

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

This section reflects source inspection on **2026-11-18**. It is not a
release date or evidence of passing model tests. Consult the linked GitHub
issues for their live status.

- **Four-skill plugin candidate** ([#257](https://github.com/drevendev/BeautifulRepo/issues/257)):
  released `v0.2.0` contains **only** `audit-repo`. The [current four-skill
  development candidate](guides/agent-plugin.md#try-all-four-skills-from-a-pinned-development-candidate)
  is pinned to `4d74e840792fe87c79e1202d982a95103d97ba73` (`0.3.0-dev.0`). It includes
  the local-executor declaration, hard-link guards from #380–#383 and #408,
  the cache verifier from #387, the README path guard from #402, and the
  release-inventory path preflight from #410. Earlier candidates
  `76c39ed5732304334358b9d4b214821d7030b39f` and `70b792b7f09d4bd03e36b6ca1cf6c869e5036872`
  are historical; their results do not transfer.
  [Exact-source Quality CI](https://github.com/drevendev/BeautifulRepo/actions/runs/44266792229)
  on this SHA completed **6/6 SUCCESS** on 2026-11-18. Repository CI does
  **not** prove fresh host installation, skill discovery or model behavior
  in Claude Code/Codex. The [manual matrix](evals/manual-smoke.md),
  [fixtures](https://github.com/drevendev/BeautifulRepo/issues/74) and
  [tester request](https://github.com/drevendev/BeautifulRepo/issues/258)
  cover remaining positive, negative and hostile tests. Issues #257/#258
  now use source candidate `4d74e840792fe87c79e1202d982a95103d97ba73`
  and reviewed setup documentation from `775e1ba9de4b20fd9e6b60f4648d558f85944b63`.
  Pin their roles separately: instructions are not host evidence, and no test
  results transfer across source candidates. No stable four-skill release or
  real host acceptance is claimed.
- **Standalone skills CLI distribution** ([#333](https://github.com/drevendev/BeautifulRepo/issues/333)):
  the four skills now carry their individual required files in-source. The
  [real skills CLI copy trial](guides/agent-plugin.md#standalone-skill-manager-installations-separate-from-full-plugins)
  checks individual and combined fresh copies plus synthetic local tool
  execution; consult the current GitHub run for an observed result. A
  successful file copy does **not** prove skill discovery or model execution
  inside Claude Code/Codex. Use the pinned full-plugin candidate for its
  separate host-acceptance tests; do not advertise an agent-verified
  standalone installation yet.
- **Public HungryCrab first-command case**
  ([source-only review](case-studies/hungrycrab-first-command.md)):
  a verified public README at a fixed upstream commit, with a specific
  first-visit obstacle and copyable proposed improvement. It is **not** an
  upstream PR, after-state or observed installation; the full procedure
  remains open under #88.
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

**Experimental local MCP:** a [development-only stdio adapter](guides/local-mcp.md)
wraps the existing three offline checkers behind a fixed, configured repository
root, using the optional official Python SDK v2. This is not yet verified in
Claude Code or Codex and is not a release announcement; [#255](https://github.com/drevendev/BeautifulRepo/issues/255)
tracks real client and protocol acceptance.

The [private/internal repository guidance](guides/private-repositories.md),
[confidentiality checklist](checklists/confidentiality.md) and repository
self-check are published. The experimental [local MCP adapter](guides/local-mcp.md)
has its own optional real-stdio protocol smoke and negative-root checks, but
it is **not yet independently host-verified or released**. Its remaining
[acceptance work](https://github.com/drevendev/BeautifulRepo/issues/255)
is separate from the four-skill plugin candidate, and MCP is not a prerequisite
for that plugin release.

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
