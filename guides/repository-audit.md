# An offline audit of your repository's first impression

The [complete rule-ID reference](audit-rule-reference.md) lists severity, scope and tests for every emitted finding.

The [entry-point audit](../tools/repo_audit.py) reports observable issues in local README,
license and contribution documents. Each finding has a rule identifier, severity, relative
file path, line when applicable, explanation and suggested next step. It does not assign a
beauty score, execute the project, fetch URLs, or certify accessibility or licensing.

## Run it

Use Python 3.11 or newer and a stable local checkout. No third-party package is required.
From the BeautifulRepo root:

```bash
python tools/repo_audit.py .
python tools/repo_audit.py ../your-repository --format json
python tools/repo_audit.py ../your-repository --fail-on warning
```

The first form audits the current repository; the second inspects a different local
checkout and writes its report to standard output. The tool does not modify either tree.
To save JSON, redirect stdout to a chosen file outside the inspected project:

```bash
python tools/repo_audit.py ../your-repository --format json > audit-report.json
```

That file is written by the shell, not by the audit. Review reports before sharing them:
although the tool does not include document contents or absolute filesystem paths, it
includes relative document names and the kinds of findings detected.

Try the [tested before/after walkthrough](../examples/repository-audit/README.md).

## Choose a profile explicitly

Before testing a private or internal README, adapt the
[internal README template](../templates/INTERNAL_README.template.md) or inspect
the [fictional, locally verified example](../examples/internal-repository/README.md).
A passing structural audit does **not** verify that owner contacts or access
instructions actually exist in a real organization.

The default is `public`, preserving the original text report for unchanged
fixtures. `internal` and `private` are opt-in interpretations of the **local
README**, not claims about GitHub visibility, company policy or access rights:

```bash
python tools/repo_audit.py ../team-repository --profile internal
python tools/repo_audit.py ../private-repository --profile private --format json
```

In these two profiles a missing dedicated license is **informational**, with
a suggestion to state internal-use terms or link the applicable company policy,
rather than an automatic recommendation to add an open-source license. They
also warn as `readme.owner_contact` when the README has no recognizable
owner, maintainer, contact or support heading or labelled field. Put an approved
internal contact route in the actual README; never invent one. A missing or
unreadable README retains its existing error instead of duplicating that warning.

Every profile also warns as `readme.absolute_repo_asset` for common
Markdown inline/reference or HTML images loaded from
`raw.githubusercontent.com` or a `github.com/OWNER/REPO/raw/…` URL.
Prefer checked-in relative image paths that work in authorized clones and
mirrors. A legitimate external image can be documented as an exception; these
heuristics cannot determine whether a viewer has access. Code spans, fenced
blocks and HTML comments are ignored in the supported syntax subset.

**Compatibility:** the new `--profile` option and Action input are
Unreleased additions on `master`; they are **not** part of the v0.2.0
Action pin used by the adoption-guide example. Use a reviewed checkout
containing this change until a release includes it.

## Findings you can act on

**Entry-point availability:** missing or empty README; missing or empty dedicated license
or contribution document within the documented scope. A missing license file is a warning
about a local artifact, not a legal determination. Dedicated contribution guidance is
optional, so its absence is informational; the project may use an intentional alternative.

**README structure:** missing level-one title, skipped heading levels, additional level-one
titles, and tables whose header cells are all empty. These observations prompt a rendered
review; they do not prove that every heading or table is semantically wrong.

**Unfinished prose:** uppercase `TODO`, `TBD`, `FIXME` or tokens such as `{{PROJECT_NAME}}`
outside supported code/comment syntax. Intentional discussion of these terms can still
trigger a warning; inspect the cited line before changing it.

**Link purpose (heuristic):** an informational `link.vague_text` finding marks
simple, single-line **inline Markdown** links labelled `here`, `click here`,
`read more`, `learn more`, `more info` or `this link` (ignoring case and
extra spaces). Prefer a destination-specific label where it improves the reader's
journey. WCAG 2.2 SC 2.4.4 permits a link's purpose to be established by its
programmatically determined context, so **this is not an automatic accessibility
failure**. The checker does not compute that context, parse arbitrary nested
Markdown labels, resolve reference links or check HTML anchor names. It ignores
supported code/comment syntax and reports no URL contents. Destinations longer
than 2,048 characters are outside this heuristic to bound malformed-input work.
[W3C Understanding Link Purpose (In Context)](https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context),
reviewed 2026-10-31.

**Image alternatives:** an HTML image without an `alt` attribute or supported explicit
naming/decorative marker is a warning. Empty alternative text in a Markdown or HTML image
is informational, not an automatic failure: empty `alt` is appropriate for purely decorative
images. For HTML `<img>`, duplicate `alt`, `src`, `role`, `aria-label`,
`aria-labelledby` or `aria-hidden` attributes are warnings. The tool uses the
**first** occurrence for its findings, consistent with HTML parsing, so a later
`alt="Description"` cannot conceal an earlier `alt=""`. This is a bounded
source diagnostic, not a complete parser, image-purpose classifier or check of
the resulting accessible name. Whitespace-only `aria-label` or `aria-labelledby`
values do not count as naming candidates. For `role`, the checker reads the
**first whitespace-separated token**: `role="none presentation"` is treated as
presentational, but `role="img presentation"` is not. Unsupported leading-role
fallbacks and browser presentational-role conflict resolution are **not**
computed. Nonempty `aria-labelledby` references are not resolved against IDs,
so a clear audit is not proof of an accessible name.

**Readable input:** non-UTF-8, NUL-containing, oversized, unreadable and non-regular selected
documents are reported without printing their contents. A selected file that cannot be
read is not silently replaced by a lower-priority candidate.

## Scope and reading boundaries

The audit inventories only `.github`, the repository root and `docs`, without recursive
traversal. It looks for README and CONTRIBUTING stems in that location order. Root-level
LICENSE, LICENCE or COPYING names are considered license documents. Names are matched
case-insensitively. Recognized suffixes, in the tool's deterministic same-directory priority,
are `.md`, `.markdown`, `.rst`, `.txt`, and no suffix. This is a deliberately bounded subset
of the formats and license arrangements a real project may use, not an exact reproduction
of every GitHub rendering rule.

Only the three selected documents are read. Profiles are chosen by the caller,
never auto-detected from remote settings. The profile check recognizes common
Markdown contact headings and labelled fields; it does not establish the
existence or reachability of a contact channel. Markdown analysis applies to `.md` and
`.markdown` READMEs; other recognized README formats produce an informational limitation
rather than a false missing-README finding. The audit does not inspect individual source
licenses, SPDX declarations, nested packages, inherited organization community files,
remote settings, branch protection, or private reporting routes.

Reads are capped at 500 KiB per document. A larger document is reported and not parsed;
parsing time grows roughly linearly with document size up to that cap.
Each of the three entry-point directories is capped at 4,096 entries; exceeding the bound
stops with an input error rather than silently reporting an incomplete inventory.
Selected symlinks and special files are not read. Directory symlinks and NTFS junctions
in `.github` or `docs` are not traversed. These protections assume a stable checkout: the
tool is not a sandbox against another process concurrently replacing filesystem entries.

The parser recognizes common ATX, setext and HTML headings; backtick/tilde fenced blocks;
HTML comments; inline backtick spans; and simple Markdown/HTML image forms. A backtick
span is matched within one paragraph or heading, never across a blank line, so a stray
backtick stays plain text as it does on GitHub. It is not a CommonMark renderer. Indented code, complex nested HTML, multiline image syntax and unusual
cross-line code/comment combinations can require manual interpretation. It does not verify
anchors, image destinations, external URLs, colors, keyboard navigation, image meaning,
Mermaid rendering, or screen-reader output. Use the existing
[documentation destination checker](../tools/README.md#relative-documentation-link-checker)
for its separately documented path checks.

## JSON contract and exit codes

`--format json` emits an object with `schema_version: 1`, a `documents`
mapping, a `read_files` list, severity counts in `summary`, and an ordered
`findings` array. With an explicitly selected `internal` or `private` profile,
JSON also includes `profile` as an additive field under schema 1. The default
`public` profile **does not add a JSON key**, preserving existing consumers. Each
finding contains `rule_id`, `severity`, `path`, `line` (integer or null), `message` and
`remediation`. Output contains no timestamps or machine-specific absolute root path, and
findings are sorted by severity, relative path, line and rule identifier.

To opt in to **precise source positions** for supported diagnostics, request
JSON explicitly:

```bash
python tools/repo_audit.py ../your-repository --format json --source-spans
```

In this mode each finding also has a `location` key: a
`{start: {line, column}, end: {line, column}}` object when determinable,
otherwise `null`. Currently only simple single-line `link.vague_text` and
`readme.placeholder` findings have source spans; a reported heading, HTML
image, missing document or other rule does **not** acquire a guessed location.
The legacy `path` and `line` values are unchanged. Without the opt-in flag
the entire prior JSON/text shape is unchanged.

Positions are **one-based** line and column numbers in the UTF-8-decoded
source text (after an optional UTF-8 BOM), with **end exclusive**. Columns
count Unicode code points, not UTF-8 bytes, visual character widths or
tab-expanded display cells. CRLF and bare CR count as line breaks; a file
without a final newline remains on its last line. The span describes the
matched source token (including the Markdown link destination's extent),
**not** GitHub's rendered or accessible DOM range. The tool neither emits
the destination URL in the finding nor resolves multiline Markdown links.
Run without `--source-spans` when integrating with an existing strict JSON
consumer; `--source-spans` requires `--format json`. Review location data
along with filenames before sharing an audit report.

Exit code **0** means the configured threshold was not reached; it does not mean the
repository has no findings. Code **1** means that threshold was reached. Code **2** means
invalid arguments or a target/inventory error prevented a complete bounded audit.

The default `--fail-on error` fails on errors only. `--fail-on warning` includes warnings;
`--fail-on never` keeps findings advisory, but does not hide invalid targets or scan-limit
errors. Informational findings never fail a valid audit. Do not adopt stricter thresholds
as a merge requirement without reviewing the trade-offs and repository policy.

For a CI experiment in another project, run the trusted BeautifulRepo tool from a pinned
checkout against a separate target directory. Start in advisory mode and review the actual
findings before deciding which observations deserve a required check. This tool does not
change your CI configuration or repository protection settings.

## Sources and limits

Reviewed **2026-10-14**. These sources motivate specific observations; the audit's severity
levels and supported syntax are BeautifulRepo implementation choices, not requirements
imposed by the cited organizations.

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes): README location precedence and the 500 KiB display limit.
- [GitHub: Contributor guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors): recognized locations, case-insensitive naming and inherited alternatives.
- [W3C WAI: Headings](https://www.w3.org/WAI/tutorials/page-structure/headings/): meaningful structure and generally avoiding skipped heading ranks.
- [W3C WAI: Decorative images](https://www.w3.org/WAI/tutorials/images/decorative/): empty alternative text can be correct; authors must decide an image's purpose.
- [WAI-ARIA 1.2: `presentation` role](https://www.w3.org/TR/wai-aria-1.2/#presentation): `none presentation` is a documented fallback pattern; this audit only handles the first token conservatively.

**HTML image naming and duplicate attributes rechecked 2026-10-31:**
[W3C WAI ACT, image has non-empty accessible name](https://www.w3.org/WAI/standards-guidelines/act/rules/23a2a8/)
notes that computed accessible names are trimmed of leading and trailing whitespace.
The source check rejects whitespace-only naming attributes but does not calculate a
full accessible name or establish image accessibility.

**HTML duplicate-attribute handling rechecked 2026-10-31:**
[WHATWG HTML Standard, parsing](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-duplicate-attribute) specifies that later duplicate attributes are ignored. This supports the source-checker precedence only, not a claim of browser or screen-reader testing.

The [repository checklist](../checklists/repository.md) covers broader reader questions that
these mechanical checks intentionally cannot answer.
