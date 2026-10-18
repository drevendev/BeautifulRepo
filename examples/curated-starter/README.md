# Curated repository references — runnable starter

A small hand-selected collection should explain *why* a reader should follow each
link. This demonstration pairs three primary sources with a use case, selection
rationale, limitation and actual review date. The source checks are dated
**2026-10-17**, not refreshed automatically by running the tool.

## First success

From this directory, with Python 3.11+ and no third-party dependencies:

```bash
python curate.py --as-of 2026-10-17
python curate.py --as-of 2026-10-17 --format json
```

The Markdown report groups three recommendations into Community, Curation and
Maintenance. The JSON report has three entries and `review_due: 0`. Both commands
read [`items.json`](items.json) and write only to standard output.

To demonstrate a due review, without claiming a broken link:

```bash
python curate.py --as-of 2027-05-01 --fail-on-stale
```

All three entries are then due for a human recheck and the exit status is **2**.
Without `--fail-on-stale`, the same report exits **0**. Malformed input exits **1**
with a generic diagnostic. Invalid command-line arguments use argparse's status
**2**; distinguish them by stderr and the absence of a report.

## Input contract

The root object has exactly `title`, `scope` and `entries`. Each of 1–50 entries
contains `id`, `title`, `url`, `category`, `why`, `use_when`, `limitation` and
`verified_on`. The [sample](items.json) is the smallest useful schema reference;
the [validator](curate.py) contains the exact text bounds.

IDs and categories are lowercase slugs. Dates are valid ASCII `YYYY-MM-DD` values,
not later than `--as-of`. Review age becomes due only when it is **greater than**
`--max-age-days` (180 by default). Duplicate IDs, canonical destinations and JSON
object keys are rejected, including escaped spellings and nested keys.

URLs use HTTPS and ordinary ASCII DNS hostnames. Unicode path text and valid
percent escapes are accepted; credentials, explicit ports, fragments, whitespace,
unpaired Unicode surrogates, malformed host labels and malformed percent escapes
are rejected. Host case and trailing path slashes are ignored for duplicate checks;
query strings remain meaningful. This bounded syntax policy does **not** establish
that a destination is safe, reachable, reputable or current.

Input reads are capped at **1 MiB** before decoding. Invalid UTF-8 and excessively
nested JSON get the same controlled CLI error. This is a local-file teaching tool,
not a sandbox against concurrent filesystem changes or a hostile special file.

## Maintenance and tests

A date means someone actually checked the source. Do not move dates forward merely
to quiet a checker. Revisit the source, correct the annotation or retire the entry,
then record the new date. Automated syntax checks cannot perform that review.

From the repository root:

```bash
python -m unittest discover -s tests -p 'test_curated*.py' -v
```

Tests cover deterministic output, preserved input, due-review boundaries, malformed
metadata, duplicate keys, generic errors, URL syntax and Markdown escaping.

This example teaches a small standalone collection. The separate
[main catalog](../../catalog/README.md) is BeautifulRepo's larger handbook index;
this tool does not replace its schema or its validator.

## Reuse

Adapt the [collection README template](../../templates/CURATED_README.template.md)
and [selection guide](../../guides/curated-collections.md). Code and original
annotations follow BeautifulRepo's [MIT license](../../LICENSE). Linked websites
retain their own rights and trademarks. No upstream endorsement, live monitoring,
Awesome-list admission or redistribution license is implied.
