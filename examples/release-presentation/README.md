# One verified change, two useful release-note layouts

**Status: editorial examples only, 2026-10-27. No release, tag, download or
announcement is created by this page.** Both specimens describe a *real merged
change* in BeautifulRepo, not a fictional product or an unverified launch.

The evidence is [PR #179](https://github.com/drevendev/BeautifulRepo/pull/179),
merged as [`9468525`](https://github.com/drevendev/BeautifulRepo/commit/9468525f5c38c245bd6ccdcc9476dcdc467933e9).
Its [PR-head CI run](https://github.com/drevendev/BeautifulRepo/actions/runs/40550896841)
completed successfully for `79ae4c7`; **that run is evidence for the PR
head, not a new release or a fresh post-merge test**. The implementation is
[tools/docs_links.py](../../tools/docs_links.py), with
[regressions](../../tests/test_docs_links_references.py).

## Facts held constant

- **Who notices:** maintainers running BeautifulRepo's offline Markdown
  destination checker against local repository documentation.
- **Before:** a broken relative destination used via a Markdown reference
  definition could pass that check.
- **After:** one-line full, collapsed and shortcut reference-style links and
  images have their repository-local destinations checked. The diagnostic is
  attached to the *use* line, not only the definition.
- **What to do:** from a checkout with Python 3.11+, run
  `python tools/docs_links.py`. A broken destination is reported with a
  nonzero result.
- **Limits:** this is not a full GitHub Flavored Markdown renderer.
  Multiline definitions, nested container definitions and external live links
  remain outside this bounded check.

These facts come from the reviewed change and its code/tests, not from a user
study or claims about how many repositories it helped.

## Treatment A — changelog entry

**Reader:** someone scanning durable history for the change they need.
Place the behavior under `[Unreleased]` until it belongs to an actual
published version. Here is a compact **illustrative entry**, *not a newly
published CHANGELOG update*:

> ### Added
>
> - Check repository-local destinations used by one-line full, collapsed and
>   shortcut Markdown reference links and images. Broken destinations now
>   appear at the link-use line. Run `python tools/docs_links.py` from a
>   Python 3.11+ checkout. Multiline and nested-container definitions and
>   external links are not checked by this feature. See
>   [PR #179](https://github.com/drevendev/BeautifulRepo/pull/179).

This layout is intentionally short. It makes the new capability findable
without implying a download, version or migration that never happened.

## Treatment B — reader-facing release-note **draft**

**Reader:** someone who needs to decide whether and how to use the checker.
This is an **unpublished draft for a potential future release**, *not a
GitHub Release*.

> ### Local documentation links: reference forms are now checked
>
> **Who is affected.** Maintainers who use the offline Markdown link checker
> with `[Guide][docs]`, `[Guide][]` or `[Guide]` references.
>
> **What changed.** Missing relative targets behind supported one-line
> definitions now produce a diagnostic at the link-use line instead of
> silently escaping this check.
>
> **Try it.** From a Python 3.11+ checkout, run
> `python tools/docs_links.py`. Review any reported paths and fix the
> references or their targets.
>
> **Known boundaries.** This is not a complete Markdown renderer. It does
> not follow live external links or parse multiline/nested-container
> definitions. No migration or package install is claimed.
>
> **Evidence.** [Merged source change](https://github.com/drevendev/BeautifulRepo/pull/179)
> and [successful PR-head CI](https://github.com/drevendev/BeautifulRepo/actions/runs/40550896841).
> **Publication: not performed.**

The second layout spends more words on *who*, *effect*, *next step* and
*limitations*. That is useful for a release reader, but repeating this whole
paragraph in a changelog would make routine history hard to scan.

## Choose a presentation deliberately

| Decision | Changelog entry | Release-note draft |
| --- | --- | --- |
| Reader's question | What changed? | Does this matter to me and what should I do? |
| First line | Behavior | Reader impact |
| Proof | One source PR | Change, test evidence and limits |
| Length | Short, easy to scan | Enough detail to act |
| Publication status | `[Unreleased]` | Clearly marked **draft** |

The factual change and its limitations are identical. Neither variant
claims the PR introduced a tagged version, measured adoption, published
download, or guaranteed coverage on untested Markdown constructs. No
decorative screenshot is needed to communicate the result.

## Turn this into real release notes

Before publishing a genuine release, a maintainer must separately establish
the exact tag and comparison range, inspect the changes included *in that
release*, check relevant tests and platforms on the intended revision,
verify any download or installation claim, and review the rendered text.
GitHub's automatically generated notes can supply a **draft inventory** of
merged changes, but they do not make the editorial or release decision.

See the [release-notes guide](../../guides/release-notes.md), the
[editable release-note template](../../templates/RELEASE_NOTES.template.md)
and [visual README guidance](../../guides/readme-visuals.md). This example
does not publish anything or check GitHub's rendered view, browser zoom,
keyboard navigation or screen readers.

**Primary references, checked 2026-10-27:**
[GitHub — About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases),
[GitHub — Automatically generated release notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes),
and [Keep a Changelog 1.1](https://keepachangelog.com/en/1.1.0/).
