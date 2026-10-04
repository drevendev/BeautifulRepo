# Offline catalog tool

`catalog.py` uses Python 3.11+ and the standard library. From the repository root:

```bash
python tools/catalog.py                 # validate and check the generated view
python tools/catalog.py --write         # explicitly regenerate catalog/README.md
python tools/docs_links.py               # check repository-owned Markdown destinations
python -m unittest discover -s tests -v
```

`--data` and `--output` accept alternative paths for a separate collection.
`--write` replaces the selected output file; review the path before using it.

## Contract

The JSON root has integer `schema_version: 1` and a nonempty `resources` array. Entries
have exactly the fields shown in `catalog/resources.json`. Categories are guide, checklist,
program, tool and example. Metadata currently records only `source-reviewed` evidence;
runtime verification belongs in separate, reproducible trial records before the schema
claims to represent it.

Errors include missing or blank fields, malformed identifiers, duplicate IDs, duplicate
source URLs (ignoring fragment, trailing slash, host case and default HTTPS port), malformed
HTTPS URLs, unsupported categories and invalid/future dates. Query strings remain meaningful.
URL syntax validation does not establish destination safety or availability.

Exit code 0 means the metadata is structurally valid and its generated view is current.
Exit code 1 means validation, input/output or synchronization failed. Argument-parsing
errors use argparse's exit code 2. Warnings request rechecking programs after 30 days and
other entries after 180 days; they do not assert that a source actually changed.
Current UTC date affects freshness warnings and future-date validation, not rendering.

The tool does not fetch links, follow redirects, execute repositories, judge editorial
quality, decide licenses, verify claims or score beauty. Source review dates must come
from real inspection, never from regenerating the view. Markdown output order is stable.


## Relative documentation link checker

`docs_links.py` scans Markdown files under the repository root and verifies that inline,
repository-owned link and image destinations resolve to existing files or directories. It
supports paths relative to the current document, repository-root paths beginning with `/`,
URL-encoded path characters, and ordinary query/fragment suffixes on an otherwise local path.
It rejects destinations that escape the repository root.

The checker deliberately does **not** fetch external URLs, validate redirect targets, certify
rendered HTML, or validate section fragments/heading anchors. It ignores links inside fenced
and single-backtick inline code because documentation examples should not become dependencies.
Reference-style Markdown links and raw HTML links are not parsed in this first bounded version.

GitHub recommends relative links for repository-owned files because they follow the branch a
reader is viewing and remain useful in clones. Source reviewed 2026-10-04:
<https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#relative-links>.
