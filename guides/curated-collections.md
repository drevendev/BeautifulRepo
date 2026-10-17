# Curated collections: selection beats accumulation

A collection repository should answer **who it is for, why each item is here and when each source was last checked**. A giant alphabetized link list is not necessarily useful: readers still have to solve the selection problem themselves.

## Design the selection contract

1. **Scope and audience:** state the task the reader needs to complete and what falls outside the collection. Prefer a small, maintained set over accidental category sprawl.
2. **Evidence for each entry:** link to a stable official project page or primary document. Add a short *use when*, *why*, and *limitation* note; do not copy whole external articles into the repository.
3. **Selection policy:** say why inclusion helps and why an item might be rejected or retired. Check for conflicts of interest; placement is not an endorsement or a warranty.
4. **Freshness:** record an actual source-review date separately from automated local syntax validation. A stale date should trigger a recheck, not an invented updated date.
5. **Contributions and removal:** provide criteria for PRs, corrections, broken destinations, duplicate entries and deprecations. Avoid promising confidential response channels or review service levels you do not operate.
6. **Rights:** confirm the rights to your original descriptions and any copied assets separately. Linking to a source does not relicense its text, logo or diagrams. Choose a license appropriate to the kind of repository; BeautifulRepo itself remains MIT.

## Tested offline starter

The [collection example](../examples/curated-starter/README.md) contains three primary sources in [structured metadata](../examples/curated-starter/items.json), a [deterministic Python validator and renderer](../examples/curated-starter/curate.py) and black-box regression tests. It demonstrates source notes, exact metadata checks, duplicate detection, safe Markdown output and optional stale-review exit codes.

Run `python curate.py --as-of 2026-10-17` inside the example directory to render its three entries, or `python curate.py --as-of 2027-05-01 --fail-on-stale` to see that old reviews require attention (exit status `2`). The date is injectable so the tests stay deterministic. The tool never crawls links, installs packages, calls an API or verifies current upstream behavior. It is a **review ledger**, not a live-link verifier.

## Present the result

Start with a single-sentence promise and an audience-first contents section. Group entries by the task they solve, not by which provider is famous. Use informative anchor text, a short rationale and an explicit caveat. Make the path to contribute or suggest a correction conspicuous. Avoid unexplained badges, sponsorship implications and a misleading "up to date" claim without an actual review procedure.

For a narrow, rapidly changing subject, highlight **what was verified and when**, and retire outdated items. If the scope needs dozens of categories with no maintainers, consider a search-driven database or split into focused lists instead of hiding the maintenance problem behind a huge README.

## Source review (2026-10-17)

- [Awesome manifesto](https://github.com/sindresorhus/awesome/blob/main/awesome.md): encourages selective inclusion, reasons for recommendations, contribution guidelines and clear scope. Its specific badge and list-submission criteria **do not** transfer automatically to unrelated collections.
- [GitHub community profiles](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories): shows how recognized community health files help readers locate participation guidance. A green checklist is not proof of operational readiness.
- [Open Source Guides — best practices](https://opensource.guide/best-practices/): makes the case for repeatable tests and helpful contributor workflows. These are patterns to adapt, not a universal standard or legal advice.

This guide does not grant rights to upstream content, certify accessibility, guarantee link availability or claim that a tool can replace human judgement about quality.
