# Curated repository references — runnable starter

This tiny **hand-selected demonstration** shows a collection as useful recommendations rather than a pile of links. Three real primary sources are paired with a specific use case, selection rationale, limitation and dated review. Checked **2026-10-17** by inspecting the linked public pages; nothing here implies endorsement, ongoing live-link monitoring or exhaustive coverage.

From this directory, with **Python 3.11+** and no third-party dependencies:

```bash
python curate.py --as-of 2026-10-17
python curate.py --as-of 2026-10-17 --format json
python curate.py --as-of 2026-10-17 --fail-on-stale
```

Each command validates [`items.json`](items.json) without fetching URLs. The default renderer groups recommendations into navigable categories, preserves a reason to click, and visibly flags items older than 180 days relative to the supplied review date. `--fail-on-stale` returns exit status `2` if a human source recheck is due; it **does not** claim the destination is broken. Malformed input returns status `1` and a generic diagnostic. The script never changes the input file.

A review date means a person actually checked the source that day. **Do not update dates simply to quiet CI.** Remove obsolete links, revise guidance and record the new review date only after checking the source. You can pass a custom `--data` file with the same schema; the tool rejects duplicate item IDs and URLs, ambiguous dates, unsafe URLs and missing application notes.

From the repository root, regression tests run with:

```bash
python -m unittest discover -s tests -v
```

**Rights and boundaries:** This sample's code and original annotations follow BeautifulRepo's [MIT license](../../LICENSE). Linked websites retain their own rights, licenses and trademarks. This example is not a submission to the `awesome` repository, does not claim to follow its specific admission requirements, and is not a third-party content redistribution license. See the [curated collection guide](../../guides/curated-collections.md) for a reusable decision process.
