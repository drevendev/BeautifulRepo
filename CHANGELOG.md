# Changelog

This log describes handbook and source changes, not packaged releases or version tags.
Dates identify work on the repository; the linked pull requests retain integration history.

## Unreleased — working repository workshop

### Added

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

### Corrected

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

## Research/data and test discovery — 2026-10-17

[Research/data starter (#13)](https://github.com/drevendev/BeautifulRepo/pull/13) adds a fully
fabricated CSV, deterministic analysis, fixture digest, README template, provenance/citation
advice and mandatory navigation tests. The example makes no scientific or data-rights claim.

[Library test discovery (#14)](https://github.com/drevendev/BeautifulRepo/pull/14) replaces a
fixed nested test count with successful nonempty discovery. Real temporary suites cover
legitimate growth, zero tests, test failures, import errors and missing execution summaries.

## Library starter and local audit — 2026-10-16

[Library starter (#10)](https://github.com/drevendev/BeautifulRepo/pull/10) provides a tested
checkout-only API example, guide and README template without advertising an unpublished package.

[Repository audit (#12)](https://github.com/drevendev/BeautifulRepo/pull/12) adds bounded,
read-only checks for reader entry points, actionable findings, text/JSON reports and a
before/after example. Empty image alternatives and absent dedicated contribution guidance
are informational, not universal failures; no beauty score or certification is produced.

## Release guidance and accessible front page — 2026-10-14

[Release-note guidance (#9)](https://github.com/drevendev/BeautifulRepo/pull/9) adds a guide,
editable draft and tests distinguishing tags, GitHub Releases and maintained changelogs.

[README accessibility (#11)](https://github.com/drevendev/BeautifulRepo/pull/11) replaces a
layout-only feature table with a list and preserves the visitor journey as real text next
to the Mermaid diagram. Tests guard these structural properties, not assistive-technology certification.

## Earlier handbook foundations — October 2026

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
