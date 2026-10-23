# An offline audit of your repository's first impression

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

**Image alternatives:** an HTML image without an `alt` attribute or supported explicit
naming/decorative marker is a warning. Empty alternative text in a Markdown or HTML image
is informational, not an automatic failure: empty `alt` is appropriate for purely decorative
images. The tool cannot infer the image's purpose or check the resulting accessible name.

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

Only the three selected documents are read. Markdown analysis applies to `.md` and
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

`--format json` emits an object with `schema_version: 1`, a `documents` mapping, a
`read_files` list, severity counts in `summary`, and an ordered `findings` array. Each
finding contains `rule_id`, `severity`, `path`, `line` (integer or null), `message` and
`remediation`. Output contains no timestamps or machine-specific absolute root path, and
findings are sorted by severity, relative path, line and rule identifier.

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

The [repository checklist](../checklists/repository.md) covers broader reader questions that
these mechanical checks intentionally cannot answer.
