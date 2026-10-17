# Curated collections: selection beats accumulation

A collection should answer **who it is for, why each item belongs and when the
source was checked**. A long alphabetical list still leaves readers to solve the
selection problem. Start with a small set that has a reason to exist.

## Define the selection contract

State the reader's task and the exclusions. For each entry, choose a primary
source and write three short original notes: **use when**, **why**, and **limit**.
A tool may be an excellent fit for one workflow and a poor fit for another.

Make inclusion and removal criteria visible. Describe how contributors can propose
a replacement, correct a claim or report a stale entry. Do not silently sell
placement, imply upstream endorsement or promise moderation response times the
project cannot support.

Keep source-review dates separate from automated validation dates. A stale review
is a request to inspect the source, not evidence that the source disappeared.
Do not replace an old date with today's date merely because local tests passed.

## Work through the example

The [runnable collection](../examples/curated-starter/README.md) contains three
primary sources, deterministic Markdown/JSON output and regression tests. From
its directory:

```bash
python curate.py --as-of 2026-10-17
python curate.py --as-of 2027-05-01 --fail-on-stale
```

The first run reports three entries with no review due. The second intentionally
returns status 2 with three due reviews. It never fetches a URL or edits a date.
Its [input contract](../examples/curated-starter/README.md#input-contract) describes
bounds and supported URL forms; rejecting a URL is not a destination-safety verdict.

## Present useful choices

Group by the task solved, not by provider fame. Use descriptive link labels, a
specific rationale and a caveat rather than copying upstream advertising.
Keep the correction route close to the selection policy. The
[README template](../templates/CURATED_README.template.md) gives these sections a
place without inventing facts for them.

For rapidly changing subjects, emphasize what was inspected and retire superseded
advice. If the collection needs dozens of categories with no realistic maintenance
capacity, narrow the scope rather than disguising the problem with a larger index.

## Source review — 2026-10-17

- [Awesome manifesto](https://github.com/sindresorhus/awesome/blob/main/awesome.md):
  selective inclusion, informative descriptions and contribution criteria.
  Its badge and admission rules belong to that project, not every collection.
- [GitHub community profiles](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories):
  recognized community files help readers find participation guidance; presence
  alone does not prove a project's operational readiness.
- [Open Source Guides: best practices](https://opensource.guide/best-practices/):
  clear contribution rules and repeatable tests reduce avoidable review work.
- [Python JSON decoding](https://docs.python.org/3.13/library/json.html#repeated-names-within-an-object):
  default decoding keeps only the last repeated key. The example deliberately
  rejects ambiguity using `object_pairs_hook` before metadata validation.

The guide does not certify accessibility or link availability. Original annotations
and linked content have separate rights; linking does not relicense an article,
logo or diagram. See also the [maintenance workflow](maintenance-workflow.md).
