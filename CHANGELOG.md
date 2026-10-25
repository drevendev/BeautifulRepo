# Changelog

This log describes handbook, tool and GitHub Action changes. Tagged versions are
published as [GitHub Releases](https://github.com/drevendev/BeautifulRepo/releases).
Pin the commit SHA a tag points to rather than the tag name. Dates identify work on
the repository, and the linked pull requests keep the integration history.

From v0.2.0 on, entries follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
sections: Added, Changed, Deprecated, Removed, Fixed and Security. v0.1.0 and earlier
keep their original themed headings.

## [Unreleased]

### Added

- Add an opt-in, no-model real Git-history fixture generator for release-note agent-eval preflights: deterministic synthetic commits, tagged and untagged cases, overwrite refusal and black-box tests against the actual offline inventory. Model triggering and publication are not verified (related to #74).

- Compare three distinct first-screen README treatments of the same fictional
  PocketDiff example, with an audience/design-intent matrix and regression
  checks for the shared facts and explicit fictional status. No browser,
  assistive-technology or model-design trial is claimed (related to #16).

- The offline HTML navigation checker now reports raw HTML `<img>` tags that
  omit the `alt` attribute in active Markdown. `alt=""` remains valid for
  decorative images; source checks do not judge alternative-text meaning or
  certify accessibility. Added regression coverage (related to #16).

- Add an all-skills manual Codex/Claude smoke-test matrix: fixture visibility,
  positive/negative triggers, hostile README checks, before/after snapshots,
  evidence fields and explicit PASS/FAIL/INCONCLUSIVE grading. This is a
  procedure and static regression, **not a model-run result** (related to #74).

- Add the development-only `trust-surfaces` Agent Skill for licence-neutral,
  evidence-based review of CONTRIBUTING, SECURITY and conduct promises, with
  explicit preview/approval before any edits. Unverified reporting routes
  remain private drafts. Two positive and one negative synthetic eval plus
  static tests were added; no model-run safety or live reporting route was
  verified (related to #71 and #74).

- Add a development-only `improve-readme` agent skill that proposes an exact file/diff preview, demands explicit approval before edits, rejects unverified CI badges and separates edit permission from execution. Include two synthetic positive evals, a negative trigger and structural safety contracts. No real model evaluation or released plugin version is claimed (related to #70 and #74).
- Add a development-only `draft-release-notes` agent skill using the offline Git inventory, exact SHA evidence and explicitly unpublished no-tag fallback. Include synthetic positive/negative eval definitions and structural safety tests; **no model-run result or released plugin version is claimed** (related to #72 and #74).
- Add a read-only offline Git commit inventory tool for release-note drafting with exact base/head SHAs, no-tag/root fallback, bounded history and synthetic Git regression tests. It does not publish a release or verify commit claims (related to #72).
- Add a portable offline agent-eval file-integrity snapshot tool with
  an outside-target baseline, byte hashes, symlink-safe traversal, black-box
  tests and a Codex/Claude manual smoke recipe. This verifies target-file
  changes, **not** agent triggering or prompt-injection resistance (related to #74).
- Add a dated, source-linked GitHub.com plan matrix for private/internal
  repositories, plus explicit callouts for disclosure, Pages, CI enforcement,
  reporting and public-only checklist items (related to #76).
- Add an uncued synthetic hostile-README eval with an ordinary onboarding
  request, safety/tool-use graders and a source-level regression that prevents
  priming the prompt. Neither fixture visibility nor agent resistance has been
  verified by a model run (#74).
- Prepared four native Claude Code plugin-eval scenarios for `audit-repo`:
  two positive triggers, one negative trigger and hostile README bait.
  Added static coverage checks and a manual, usage-gated evaluation guide.
  **No model eval run or injection-resistance result is claimed** (#74).
- Four synthetic repositories and an isolated, read-only CLI regression suite for
  the `audit-repo` skill. They pin expected audit findings, broken-link behavior,
  deterministic output and no writes, including hostile README text. These do not
  claim to test actual agent triggering or prompt-injection resistance (#74).
- Run the existing plugin contract tests on v* tag pushes too: validate
  release versions against both plugin manifests and a dated CHANGELOG
  heading, reject duplicate or unclosed skill frontmatter, and document
  a joint Action/plugin release checklist in CONTRIBUTING (#73).
- An internal/private README scaffold, navigable template index and filled
  fictional Sample Queue example with a real offline fixture verifier and a
  regression asserting zero warnings under `repo_audit.py --profile internal` (#77).
- An explicit public/internal/private profile for the offline repository audit and
  composite Action, with internal owner/contact observations, less prescriptive
  missing-license guidance, additive JSON profile metadata, and raw GitHub image
  portability warnings. Default profile stays public; no remote visibility lookup (#75).
- Private/enterprise Action adoption guidance (organization policy, runner costs,
  SHA-preserving mirrors, GHES/GHE.com caveats, and local-only use) and an offline
  contract regression test for tools and composite Action shell steps (#79).
- A source-backed [confidentiality checklist](checklists/confidentiality.md)
  for private and internal repositories: content, public metadata exceptions,
  CI/report output, and safe agent use, with explicit secret-scanning limits (#78).
- The first case that follows the case procedure: PatchPitch, a local-AI app
  (`case-studies/patchpitch.md`). A documentation-only pull request in PatchPitch
  (PatchPitch#90) leads its README with a run that needs no model. The case records
  the before and after commits, pinned tool runs, a fresh-clone first run with Ollama
  stopped, 320 px measurements, CI on the merge commit, and what was not tested (#81).
- `case-studies/README.md` describes the procedure every real case follows: before
  snapshot, audit with pinned tools, a pull request in the target, after snapshot and
  write-up. It adds a fill-in skeleton, the rule that unlicensed repositories are used
  for ideas only, and the known tool caveats (#80).

### Changed

- Cache pip downloads for the lint CI job using the hash-pinned Ruff
  requirements as the cache key. Keep `--require-hashes --no-deps` installation
  and the standard-library-only tools unchanged; no measured speedup is claimed.
  The configuration follows the pinned `actions/setup-python` cache inputs
  (reviewed 2026-10-25; related to PR #157).

- Remove the legacy `hacktoberfest` label from the current contributor
  work-finding table. Closed historical issues may retain that label, but a
  2026 PR/MR cannot earn event rewards and the label does not signal enrollment
  or eligibility (related to #100). No provider label was changed.
- Recheck Hacktoberfest 2026 against the organizer's homepage, FAQ and online
  activity page on 2026-10-24; clarify that PRs earn no event rewards, distinguish
  genuine contributions from event participation and update the catalog's verified
  source date (related to #100; post-event label review remains pending).
- The adoption guide pins the Action to the `v0.2.0` commit, and `master` starts
  plugin version `0.3.0-dev.0` (#101).

### Removed

- Remove the Hungry Crab execution configuration (`.crab.yml`) and decision ledger
  (`.crab/ledger.json`) from the public repository. These were maintainer tooling
  state, not reusable BeautifulRepo product examples. Ignore future local Crab files;
  public guidance and issue history remain available.

### Fixed

- Scan `.markdown` sources alongside `.md` files in the offline
  documentation link checks, and validate section fragments pointing to
  either extension. Previously `.markdown` source links and target anchors
  could pass unchecked. Add synthetic missing-link and good/bad-fragment
  regressions; no network access or new dependencies.

- Handle repeated HTML navigation/image/anchor attributes with browser-compatible
  first-value precedence, and report malformed duplicates instead of letting a later
  `href`, `src` or `alt` hide an invalid first value (related to #16).
- Reject Windows directory junctions and other non-symlink reparse points in
  the agent-eval snapshot tool before traversal, so a supposed synthetic target
  cannot silently lead the snapshot outside its directory. Add a portable
  simulated-junction regression; this is still not a sandbox or race-proof
  filesystem monitor (related to #74).
- Reject ambiguous duplicate JSON members and boolean format versions in
  agent-evaluation snapshot baselines. Verification now fails closed instead of
  potentially reporting `UNCHANGED` for an edited or malformed baseline (#74).

## [v0.2.0] — 2026-10-23

First release with the Claude Code and Codex plugin. The GitHub Action changes too,
including a security fix, so adopters should update their pin.

### Added

- A `Lint` CI job runs ruff 0.16.10, installed by hash, over `tools/`, `tests/` and
  `examples/` with a small rule set: syntax, pyflakes and bugbear, no style rules. The
  first run's 20 findings are fixed: an unused variable, semicolon-joined statements,
  and `zip()` calls that now state `strict=True` where the lengths must match. The
  tools still have no runtime dependencies, and the job is not yet required (#55).
- Decision records in `docs/decisions/` explain seven standing choices: standard
  library only, offline and read-only tools, commit pins and immutable tags, a
  composite Action, the protected `master`, no unverified contact routes, and the
  plugin living at the repository root. CONTRIBUTING and the handoff guide link
  them, and a test keeps their shape (#61).
- A real before/after case for BeautifulRepo's own README
  (`case-studies/readme-first-success-case.md`): fixed revisions, a clean-clone run
  of the first success and all five checks, and GitHub's rendering measured at
  1280, 375 and 320 px in light and dark themes, with its limits stated (#21).
- The Pocket Board example records a dated, rendered keyboard, contrast and reflow
  check: light and dark themes at 375 and 320 px in Chrome 152, with what was not
  checked. Its contrast test now also guards the focus outline and text colours (#28).
- `tools/review_dates.py` lists guide sources whose "Reviewed" date is due for a
  recheck (180 days, 30 for the programs guide) and rejects future or impossible
  dates. The maintenance workflow describes the recheck routine (#64).
- `AGENTS.md` gives coding agents the five checks, the house rules and the layout.
  Codex reads it directly; Claude Code reads it through `.claude/CLAUDE.md`, because
  a root `CLAUDE.md` fails `claude plugin validate --strict` (#53).
- A pushed `v*` tag opens a **draft** GitHub Release (`.github/workflows/release.yml`)
  once its commit is on `master` and every required check from the `master` ruleset
  passed there. The draft is filled from the release-note template with the tag,
  SHA, previous tag, compare link and CI run; a maintainer edits and publishes it.
  `guides/maintenance-workflow.md` describes the release steps (#56).
- Package BeautifulRepo as one plugin for Claude Code and Codex, version
  `0.2.0-dev.0`. Its read-only `audit-repo` skill runs the offline tools from the
  installed copy against a target repository and applies the checklists. The plugin
  comes with ground rules for agents (`guides/agent-safety.md`), an install guide
  (`guides/agent-plugin.md`) and manifest/skill contract tests.
- Publish BeautifulRepo's own `SECURITY.md`, backed by GitHub private vulnerability
  reporting (enabled 2026-10-22): triage owner, scope for the tools, Action and plugin,
  no promised response time. Issue forms link the private route. A conduct policy is
  still pending a verified reporting channel.
- Route questions to the newly enabled Discussions from the issue chooser (blank
  issues off; security and abuse routes listed), label new issues from the forms, and
  explain every label in CONTRIBUTING.
- CI hygiene borrowed from the owner's other repositories: a superseded pull-request
  run is cancelled and checks can be started by hand; Dependabot proposes weekly
  updates for the SHA-pinned Actions; a daily scheduled workflow verifies that every
  `drevendev/BeautifulRepo@<sha> # vX.Y.Z` pin in the docs matches its tag, and
  reports catalog freshness and self-audit warnings.
- Add `.editorconfig` (UTF-8, LF, final newline, 4/2-space indents) that keeps
  trailing spaces in Markdown, where two of them are a hard line break.
- Commit the Hungry Crab maw config (`.crab.yml`) and decision ledger
  (`.crab/ledger.json`), so later `crab` runs skip practices already served and
  `crab tune` can learn from decisions.

### Changed

- The roadmap lists what shipped since v0.1.0: the plugin, the security policy,
  hardened checks, maintenance automation and the real README case. "Next" names the
  open epics with links: agent skills, real cases, private repositories and the
  self-check. The README and CONTRIBUTING describe the roadmap and the conduct
  decision the same way (#98).
- The community safety guide records the owner's conduct decision (2026-10-23):
  no `CODE_OF_CONDUCT.md` until a checked private channel and an independent
  enforcement path exist. The repository checklist's conduct item is "not applicable,
  with a reason" rather than a pass, with a trigger to reconsider (#30).
- The discoverability guide's BeautifulRepo example matches the live repository: a
  signed-out read-back of 2026-10-23, a one-line reason for each of the seven topics,
  the decision to keep GitHub's default social card, and the decision to turn off the
  empty wiki (#67).
- The README's first-use path starts with a copyable `git clone` and `cd`, names
  the platforms CI tests (Ubuntu with Python 3.11 and 3.14, Windows with 3.14; not
  macOS) and says what a passing self-check looks like, without fixed counts (#66).
- CONTRIBUTING describes the `hacktoberfest` label as historical instead of as
  participation, in line with the programs guide: Hacktoberfest 2026 does not count
  pull requests. The label itself stays until its post-event review (#100).
- `docs_links.py` and `html_navigation.py` now scan the current directory when
  `--root` is omitted, like `repo_audit.py`. Previously they silently checked
  BeautifulRepo's own checkout. `html_navigation.py` also runs under `python -I`.
  Commands run from the BeautifulRepo root behave as before.
- Name one check list everywhere: README, CONTRIBUTING, the maintenance guide and
  CI now all run the same five checks, including `repo_audit.py .`. The workflow is
  renamed "Quality checks" (required job names unchanged), and CONTRIBUTING
  describes the protected `master`.
- Pin the adoption guide's example workflow to the `v0.1.0` commit and explain how
  to check where a tag points.

### Fixed

- The daily scheduled run now fails when a catalog entry or a guide source is due for
  a recheck, so GitHub notifies the owner. It used to print warnings and stay green
  (`catalog.py` and `review_dates.py` gain `--fail-on-warning`; pull-request checks
  are unchanged and calendar-independent) (#99).
- Action: a `checks` list written one name per line, separated by tabs, or left
  empty used to pass validation and then run **no** checks, so the job went green.
  The setup step now hands a normalized list to the check steps, fails on an empty
  list, and rejects an invalid `audit-fail-on` even when `audit` is not selected.
  The self-test covers both new failure cases (#104).
- Link checkers report destinations that only work on case-insensitive or Windows
  file systems: wrong letter case (`docs/guide.md` for `docs/Guide.md`), a `:`, a
  trailing dot or space, and Windows device names such as `NUL` or `con.md`. Before,
  these passed on Windows and macOS although GitHub serves none of them (#103).
- `html_navigation.py` generates heading anchors the way GitHub does: each space is
  its own hyphen (`terms--conditions`), entities are decoded after tags are
  stripped, emphasis underscores and images drop out, and combining marks stay. A
  link to the anchor GitHub actually generates no longer fails, and a link to a
  collapsed one no longer passes (#102).
- Only `\n`, `\r\n` and `\r` end a line in the tools now, as in CommonMark. A form
  feed, vertical tab, NEL or Unicode line/paragraph separator inside code or prose
  used to crash `html_navigation.py` or make it reject a valid anchor, and to shift
  `repo_audit.py` line numbers (#105).
- Scanning time no longer grows quadratically on adversarial Markdown. Link text
  brackets are paired in one pass. A bare link destination stops at its 33rd unclosed
  `(`, as in GitHub's cmark-gfm. The audit's heading parser no longer backtracks over
  trailing spaces. 200 KB of unmatched `[` went from hours (extrapolated) to under a
  second (#107).
- `repo_audit.py` treats an NTFS junction in `.github` or `docs` like a directory
  symlink: it reports `path.symlink` and does not read through it. Before, a junction
  passed the symlink check, and documents outside the target were read (#108).
- `repo_audit.py` matches backtick code spans within one paragraph or heading. Two
  stray backticks in different paragraphs used to form one span and hide every
  finding between them, such as a TODO or an image without alt text (#106).
- The plugin manifests, the `audit-repo` skill and the agent guides no longer
  promise that nothing leaves the machine. BeautifulRepo's Python checks make no
  network requests, but an agent session may send repository context to its model
  provider; the guides link Claude Code's and OpenAI's data-control pages (#97).

### Security

- [GHSA-9rpm-g83x-47w7](https://github.com/drevendev/BeautifulRepo/security/advisories/GHSA-9rpm-g83x-47w7): on Windows, a Markdown link, an HTML attribute or
  a symbolic link in the checked repository that named a UNC share (`\\host\share`,
  also percent-encoded) made `docs_links.py`, `html_navigation.py` and the Action open
  that share before reporting "escapes repository root". The connection could expose
  the user's Windows credentials to that host. Destinations with a backslash or a drive
  letter are now reported as non-portable without being opened, sources and
  destinations are resolved inside the root with link and junction targets checked
  as text first, and the Markdown walk no longer follows links or junctions (#110).
  **Action adopters should move their pin to v0.2.0.**

## [v0.1.0] — 2026-10-22

First tagged version, at commit `96e04e6a79027354c5e84a4a28f3ba5f5441d484`.
See the [release notes](https://github.com/drevendev/BeautifulRepo/releases/tag/v0.1.0).
It includes all earlier handbook work listed below.

### Checks for other repositories

- Publish the audit and both link checks as a composite GitHub Action
  (`action.yml`) that other repositories pin to a reviewed commit. It uses the
  caller's Python 3.11+, validates its inputs and makes no network requests.
- Never scan `.git` or `node_modules` Markdown, and add a repeatable `--exclude`
  glob to `docs_links.py` and `html_navigation.py` for vendored or archived docs.
- Add a consumer guide with a copy-paste workflow and a step-by-step rollout,
  plus a CI self-test that runs the action on Ubuntu and Windows, including
  cases that must fail.

### Windows checkout parity

- Check out text files with LF everywhere so fixture hashes and the
  generated-catalog comparison no longer fail on a Windows `core.autocrlf` checkout.
- Write the curated starter's JSON/Markdown output as UTF-8 when stdout is
  redirected on Windows, instead of crashing on non-ASCII collection text.
- Compare the preserved catalog file mode with what the platform actually stores,
  and run the full checks on Windows with Python 3.14 in CI.

### Maintainer continuity recipe

- Add a source-backed one-maintainer handoff checklist, fictional filled-in
  before/after example and actual local-check recovery route; distinguish public
  contributor rules from write/admin permissions and unverified private intake.

### Evidence-first reader journey

- Put a tested local Rowcount result and an honest source/command path near
  BeautifulRepo's README introduction, replacing duplicated navigation with
  three clear entry routes while retaining all five working starter types.
- Document why the explicitly fictional PocketDiff visual example uses its
  existing theme-aware assets, text equivalents and restrained hierarchy.
- Add an editorial evidence kit with fact-preserving README, announcement and
  changelog examples, plus three distinct lead angles and explicit limits.
- Expand regression checks for reader routes and editorial/example contracts.
  Rendered desktop/mobile, high-zoom and assistive-technology acceptance remain
  separately scoped, not claimed by these source-level tests.

### Input integrity and reading fidelity

- Refuse ambiguous repeated JSON keys before validating catalog resources or
  loading the Pocket Board fixture; nested and Unicode-escaped aliases are errors.
- Reject control characters and malformed percent escapes in catalog URLs while
  retaining percent-encoded paths, queries, IPv6 and fragment normalization.
- Keep literal empty fragments out of the curated collection's canonical URLs.
- Render user-authored scope as labelled prose and escape GFM strikethrough
  markers in generated catalogue and collection Markdown.
- Strengthen form-control boundary colors in both Pocket Board themes; this
  source-level contrast check is not a browser or assistive-technology audit.
- Preserve existing generated catalog bytes on UTF-8 encoding or replacement
  errors (PR #36) and test Python 3.11/3.14 explicitly in CI (PR #35).

### Working repository workshop

#### Added

- [Pocket Board application starter](examples/application-starter/README.md): a read-only,
  standard-library web example with a native status filter, light/dark styles, fictional
  data, controlled error responses and loopback HTTP regression tests.
- [Curated collection starter](examples/curated-starter/README.md): three annotated primary
  sources, deterministic Markdown/JSON reports, input validation and optional stale-review
  detection. It checks metadata, not live destination availability.
- [Application README template](templates/APPLICATION_README.template.md) and
  [collection README template](templates/CURATED_README.template.md).
- [Working-example index](examples/README.md), [first-success checklist](checklists/first-success.md)
  and [reproducible maintenance workflow](guides/maintenance-workflow.md).

#### Corrected

- Collection parsing rejects repeated JSON keys, including nested and escaped spellings,
  before a decoder can silently overwrite metadata. Invalid UTF-8, excessive nesting and
  input beyond the documented 1 MiB limit produce a controlled error.
- Collection URL validation rejects unpaired Unicode surrogates, malformed percent escapes,
  invalid DNS labels and unsupported authority syntax instead of producing a traceback or
  accepting malformed output. This is deliberately a bounded syntax check, not a safety verdict.
- Application readiness detects missing or invalid data and unavailable styles. Invalid
  Unicode task titles are rejected; local filesystem paths are not returned in errors.
- Application testing instructions now disclose the temporary loopback listener. README
  and roadmap routes preserve all five starter types rather than replacing earlier additions.

### Research/data and test discovery — 2026-10-17

[Research/data starter (#13)](https://github.com/drevendev/BeautifulRepo/pull/13) adds a fully
fabricated CSV, deterministic analysis, fixture digest, README template, provenance/citation
advice and mandatory navigation tests. The example makes no scientific or data-rights claim.

[Library test discovery (#14)](https://github.com/drevendev/BeautifulRepo/pull/14) replaces a
fixed nested test count with successful nonempty discovery. Real temporary suites cover
legitimate growth, zero tests, test failures, import errors and missing execution summaries.

### Library starter and local audit — 2026-10-16

[Library starter (#10)](https://github.com/drevendev/BeautifulRepo/pull/10) provides a tested
checkout-only API example, guide and README template without advertising an unpublished package.

[Repository audit (#12)](https://github.com/drevendev/BeautifulRepo/pull/12) adds bounded,
read-only checks for reader entry points, actionable findings, text/JSON reports and a
before/after example. Empty image alternatives and absent dedicated contribution guidance
are informational, not universal failures; no beauty score or certification is produced.

### Release guidance and accessible front page — 2026-10-14

[Release-note guidance (#9)](https://github.com/drevendev/BeautifulRepo/pull/9) adds a guide,
editable draft and tests distinguishing tags, GitHub Releases and maintained changelogs.

[README accessibility (#11)](https://github.com/drevendev/BeautifulRepo/pull/11) replaces a
layout-only feature table with a list and preserves the visitor journey as real text next
to the Mermaid diagram. Tests guard these structural properties, not assistive-technology certification.

### Earlier handbook foundations — October 2026

The initial handbook introduced a reader-first front page, repository checklist, README
scaffold, annotated pattern studies, dated program guidance and an offline source catalog.
Later additions included the CLI row-counting starter, theme-aware PocketDiff before/after
example, public contribution guidance and explicit community reporting limitations.

The documentation-destination checker gained coverage for nested/escaped parentheses and
labels, character references, multiline links, equal-length inline code delimiters,
indented/fenced code and list/quote containers. It also handles invalid UTF-8 and NUL paths
with controlled diagnostics. Its documented exclusions still apply: it is not an external
link crawler, reference-link parser or heading-anchor validator.

Visual regressions preserve theme switching, meaningful alt text, nearby text equivalence,
SVG title/description linkage and non-color labels. Historical source observations remain
qualified in their guides. Linked content keeps its original rights and trademarks.

The [MIT license](LICENSE) is unchanged.

[Unreleased]: https://github.com/drevendev/BeautifulRepo/compare/v0.2.0...HEAD
[v0.2.0]: https://github.com/drevendev/BeautifulRepo/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/drevendev/BeautifulRepo/releases/tag/v0.1.0
