# Offline repository tools

`catalog.py` uses Python 3.11+ and the standard library. From the repository root:

```bash
python tools/catalog.py                 # validate and check the generated view
python tools/catalog.py --write         # explicitly regenerate catalog/README.md
python tools/docs_links.py               # check repository-owned Markdown destinations
python tools/html_navigation.py          # verify local HTML/media and Markdown section anchors
python -m unittest discover -s tests -v
```

To run `repo_audit.py`, `docs_links.py` and `html_navigation.py` in another
repository's CI, use the [GitHub Action](../guides/adopting-the-checks.md).

`--data` and `--output` accept alternative paths for a separate collection.
`--write` prepares UTF-8 bytes and atomically replaces the selected output via a temporary sibling; review the path before using it. Failed encoding/replacement leaves the previous file unchanged (this is not an fsync/crash-durability guarantee).

## Contract

The JSON root has integer `schema_version: 1` and a nonempty `resources` array. Entries
have exactly the fields shown in `catalog/resources.json`. Categories are guide, checklist,
program, tool and example. Metadata currently records only `source-reviewed` evidence;
runtime verification belongs in separate, reproducible trial records before the schema
claims to represent it.

Errors include ambiguous repeated JSON object keys (including nested/escaped equivalents), missing or blank fields, malformed identifiers, duplicate IDs, duplicate
source URLs (ignoring fragment, trailing slash, host case and default HTTPS port), malformed
HTTPS URLs (including raw controls and malformed percent escapes), unsupported categories and invalid/future dates. Query strings remain meaningful; fragments are ignored for duplicate-source normalization rather than banned.
URL syntax validation does not establish destination safety or availability.

Exit code 0 means the metadata is structurally valid and its generated view is current.
Exit code 1 means validation, input/output or synchronization failed. Argument-parsing
errors use argparse's exit code 2. Warnings request rechecking programs after 30 days and
other entries after 180 days; they do not assert that a source actually changed.
Current UTC date affects freshness warnings and future-date validation, not rendering.
`--fail-on-warning` turns a due recheck into exit code 1. Only the scheduled
workflow uses it, because pull-request checks must not depend on the calendar.

The tool does not fetch links, follow redirects, execute repositories, judge editorial
quality, decide licenses, verify claims or score beauty. Source review dates must come
from real inspection, never from regenerating the view. Markdown output order is stable.


## Manual agent-eval file-integrity check

[agent_eval_snapshot.py](agent_eval_snapshot.py) is an optional **operator tool**
for verifying whether a disposable synthetic target changed during an authorized
agent smoke test. It uses only the standard library and does not execute target
code or fetch anything. See [the complete runbook](../evals/README.md) for
a capture/verify example, exit codes and important limits.

It snapshots file bytes (SHA-256), directory entries and symlink target **text**.
It does not traverse symlink directories or touch their destinations, and
refuses to write the JSON baseline inside the target. A match only establishes
unchanged watched entries, not successful agent skill triggering, a sandbox,
resistance to prompt injection, or absence of side effects elsewhere.

## Local release-history inventory

[release_inventory.py](release_inventory.py) produces a **read-only JSON inventory** of
commits for drafting release notes from a local Git checkout:

```bash
python -I tools/release_inventory.py .
python -I tools/release_inventory.py ../another-checkout --base 0123456789abcdef
```

Replace the illustrative base SHA with an actual ancestor commit. By default the
tool compares HEAD against the nearest reachable `v[0-9]*` tag, or the unique
root commit if there is no matching tag. It names both exact commit SHAs, the
boundary kind and each commit SHA/subject. The initial root commit itself is
excluded from a root-based comparison. More than 200 commits (configurable up
to 500) fails instead of silently truncating; the tool requires a unique root
or an explicit base on unusual histories.

This inventory **is not a release and does not prove anything shipped**.
Tag presence does not establish a GitHub Release, downloadable asset or test pass.
Commit subjects are untrusted inputs, not verified user-visible behavior. Review
the underlying diffs and [release-note guidance](../guides/release-notes.md)
before writing public claims. The tool needs Python 3.11+ and Git, makes no
network requests, doesn't execute project code and writes no files. Exit 0
prints JSON; invalid inputs or Git read errors exit 2 without partial JSON.
## Guide review dates

`review_dates.py` finds the dates on which someone re-read a guide's sources, such as
`Reviewed **2026-10-22**` or `Checked: 2026-10-03`, in `guides/`, `checklists/`,
`CONTRIBUTING.md`, `SECURITY.md` and this file. It warns when a date is older than
180 days (30 for `guides/programs.md`, whose rules change every season) and reports
impossible or future dates as errors. As with the catalog, `--fail-on-warning` is for
the scheduled run, and `--today YYYY-MM-DD` fixes the date for tests. A warning means
"re-read this source", not "this source changed".

## Relative documentation link checker

`docs_links.py` scans Markdown files under the repository root and verifies that inline,
repository-owned link and image destinations resolve to existing files or directories. It
supports paths relative to the current document, repository-root paths beginning with `/`,
URL-encoded path characters, and ordinary query/fragment suffixes on an otherwise local path.
It rejects destinations that escape the repository root. Like GitHub's renderer
(cmark-gfm), it stops reading a bare destination at its 33rd unclosed `(`, which also
keeps scanning time roughly linear in the size of a file.

A destination containing a backslash or a drive letter (`docs\guide.md`, `C:/x`,
or either one percent-encoded) is reported as non-portable without being opened. On
Windows such a path could name another drive, a UNC network share or a device. GitHub
doesn't treat a backslash as a folder separator either. A `:`, a trailing dot or space,
or a Windows device name (`NUL`, `CON`, `COM1.txt` and so on) is non-portable too.
Every name must match its directory entry exactly, letter case included, so
`docs/guide.md` for `docs/Guide.md` is reported on Windows and macOS as it is on
GitHub and Linux. Symbolic links and NTFS
junctions are never descended into while looking for Markdown files. When a source or
destination passes through one, its target is read as text first and followed only
if it stays inside the root. A link cycle is reported after 40 hops.

`.git` and `node_modules` directories are never scanned. Repeat `--exclude GLOB` to
skip other root-relative paths, such as `--exclude vendor`. A matching directory is
not descended into, and excluded files remain valid link destinations.
`html_navigation.py` accepts the same option.

Without `--root`, both link checkers scan the **current directory**, like
`repo_audit.py`, never the checkout the tools live in. All three also run under
`python -I` (isolated mode), the safer way to run them next to a repository you
don't control. For example, from inside another repository:

```bash
python -I /path/to/BeautifulRepo/tools/docs_links.py
python -I /path/to/BeautifulRepo/tools/html_navigation.py
python -I /path/to/BeautifulRepo/tools/repo_audit.py .
```

The checker deliberately does **not** fetch external URLs, validate redirect targets, certify
rendered HTML, or validate section fragments/heading anchors. It ignores links inside fenced
and single-backtick inline code because documentation examples should not become dependencies.
Reference-style Markdown links and raw HTML links are not parsed in this first bounded version.

GitHub recommends relative links for repository-owned files because they follow the branch a
reader is viewing and remain useful in clones. Source reviewed 2026-10-04:
<https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#relative-links>.

## HTML navigation and fragment checker

`html_navigation.py` complements `docs_links.py`: it checks repository-local
`a href`, `img src` and `source srcset` destinations in active Markdown
HTML, plus local section fragments in HTML and inline Markdown links.
It ignores code examples using the same GFM literal-region masking as the
existing checker. Explicit HTML `id` and `a name` anchors and ordinary
Markdown ATX headings (including duplicate suffixes) are supported.

Heading anchors follow GitHub's rules. The rendered text is lowercased. Every
character other than a letter, mark, digit, connector punctuation, hyphen or space
is dropped, and each space becomes a hyphen, so `Terms & Conditions` becomes
`terms--conditions`. Code-span text counts. Images, tags, comments and emphasis
markers don't. The expected values in `tests/test_github_heading_slugs.py` were read
back from GitHub's Markdown API. Known differences: setext headings aren't scanned,
and characters newer than the Unicode version GitHub uses may be kept or dropped
differently.

This offline source check is not a complete GitHub-flavored Markdown renderer.
It does not crawl external resources, support every Markdown extension or
reference-style link, or certify browser, keyboard or assistive-tech behavior.

## Repository entry-point audit

`repo_audit.py` inspects a local repository's selected README, license and contribution
documents without network requests, project execution or modifications. Findings carry
relative paths, source lines where applicable, explanations and suggested next steps.

```bash
python tools/repo_audit.py .
python tools/repo_audit.py ../your-repository --format json
python tools/repo_audit.py ../your-repository --fail-on warning
python examples/repository-audit/demo.py
```

The default failure threshold is errors only; warnings and informational findings remain
visible. Missing dedicated contribution guidance and empty image alternatives are not
unconditional failures. Exit 0 means the configured threshold was not reached, not that
all quality or accessibility questions were answered.

Read the [complete contract and limitations](../guides/repository-audit.md) and the
[tested before/after walkthrough](../examples/repository-audit/README.md). This bounded
source inspection is not a complete GitHub community-profile check, license classifier,
screen-reader audit or beauty score. Its tests join the existing default unittest suite;
no new required repository-protection rule is introduced.
