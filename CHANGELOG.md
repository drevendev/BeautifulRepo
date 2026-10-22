# Changelog

This log describes handbook, tool and GitHub Action changes. Tagged versions are
published as [GitHub Releases](https://github.com/drevendev/BeautifulRepo/releases).
Pin the commit SHA a tag points to rather than the tag name. Dates identify work on
the repository, and the linked pull requests keep the integration history.

## Unreleased

- Publish BeautifulRepo's own `SECURITY.md`, backed by GitHub private vulnerability
  reporting (enabled 2026-10-22): triage owner, scope for the tools, Action and plugin,
  no promised response time. Issue forms link the private route. A conduct policy is
  still pending a verified reporting channel.
- Name one check list everywhere: README, CONTRIBUTING, the maintenance guide and
  CI now all run the same five checks, including `repo_audit.py .`. The workflow is
  renamed "Quality checks" (required job names unchanged), and CONTRIBUTING
  describes the protected `master`.
- Add `.editorconfig` (UTF-8, LF, final newline, 4/2-space indents) that keeps
  trailing spaces in Markdown, where two of them are a hard line break.
- CI hygiene borrowed from the owner's other repositories: a superseded pull-request
  run is cancelled and checks can be started by hand; Dependabot proposes weekly
  updates for the SHA-pinned Actions; a daily scheduled workflow verifies that every
  `drevendev/BeautifulRepo@<sha> # vX.Y.Z` pin in the docs matches its tag, and
  reports catalog freshness and self-audit warnings.
- Pin the adoption guide's example workflow to the `v0.1.0` commit and explain how
  to check where a tag points.
- `docs_links.py` and `html_navigation.py` now scan the current directory when
  `--root` is omitted, like `repo_audit.py`. Previously they silently checked
  BeautifulRepo's own checkout. `html_navigation.py` also runs under `python -I`.
  Commands run from the BeautifulRepo root behave as before.
- Package BeautifulRepo as one plugin for Claude Code and Codex, version
  `0.2.0-dev.0`. Its read-only `audit-repo` skill runs the offline tools from the
  installed copy against a target repository and applies the checklists. The plugin
  comes with ground rules for agents (`guides/agent-safety.md`), an install guide
  (`guides/agent-plugin.md`) and manifest/skill contract tests.

## v0.1.0 — 2026-10-22

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
