# A small, reproducible maintenance workflow

A useful change should leave another maintainer able to reproduce its result.
Keep the scope clear, capture failures before fixing them, and make review evidence
specific to the changed code. More checkboxes are not automatically better.

## 1. Find the smallest useful outcome

Read the [roadmap](../ROADMAP.md) and existing issues or pull requests before
starting another implementation. A duplicate effort creates review work without
creating another reader benefit. State the expected visible result and a practical
failure case; use the [first-success checklist](../checklists/first-success.md).

## 2. Run the relevant checks

From the BeautifulRepo root, with Python 3.11+:

```bash
python tools/catalog.py
python tools/docs_links.py
python tools/html_navigation.py
python -m unittest discover -s tests -v
python tools/repo_audit.py .
```

These commands check catalog metadata and generated drift, repository-owned
Markdown destinations, local HTML links/media and Markdown section anchors, and the
full default regression suite. The HTML checker complements the Markdown checker;
it is not a complete GitHub renderer, external URL crawler or screen-reader audit.
These commands do not fetch external sources, certify accessibility or evaluate a
deployed production service.
The application tests open and close a short-lived loopback HTTP listener.
See [tool contracts](../tools/README.md) for the precise offline check boundaries.

When changing `catalog/resources.json`, regenerate deliberately, inspect the diff,
then rerun the check:

```bash
python tools/catalog.py --write
python tools/catalog.py
```

Do not alter a source-review date simply because the generator ran. The catalog
and the [small collection example](../examples/curated-starter/README.md) have
different schemas; each tool documents its own scope.

## 3. Prove the regression

Write the failing case against the old implementation first, then run it against
the correction. A duplicate JSON key is an instructive example: Python's default
decoder keeps the last value, so field validation alone cannot notice the lost one.
The collection example rejects duplicates while decoding, before validating fields.

A useful report states the command, code revision, environment, failure before the
change and result afterward. A partial local checkout must be called partial;
provider CI checks the actual repository tree. A static browser preview is useful
visual evidence but does not prove navigation over HTTP.

## 4. Review, integrate, and leave an accurate history

Review the actual diff, tests and current check results. Respect repository rules
and unresolved material findings. Keep unrelated polish in a follow-up rather than
continually enlarging a useful, already-correct change. Update reader-facing
navigation and the [changelog](../CHANGELOG.md) in the feature's own pull request,
under the matching `Unreleased` section (Added, Changed, Deprecated, Removed, Fixed
or Security).

Do not create a release, public support channel or response-time promise just to
make a checklist look complete. The [community guide](community-safety.md) explains
why such promises must match the project's actual capacity.

## 5. Keep pinned dependencies and published pins current

- **Actions used by CI** are pinned to full commit SHAs with a dated comment, for
  example `# v7.0.1 inspected 2026-10-05`. Dependabot (`.github/dependabot.yml`)
  proposes updates weekly for the `github-actions` ecosystem only. Before merging such
  a PR, look at the new release and refresh the inspected date by hand; Dependabot
  updates the SHA, not your review.
- **Pins this repository publishes**, such as `drevendev/BeautifulRepo@<sha> # v0.1.0`
  in the adoption guide, are checked daily by `.github/workflows/pins.yml`: every
  tag must exist and point at the documented commit. The same scheduled workflow
  runs `tools/catalog.py` and `tools/repo_audit.py . --fail-on warning`, so review-date
  and entry-point drift show up without a push. Run it by hand from the Actions tab
  (`workflow_dispatch`) after tagging a release.

## Sources and boundaries

Reviewed **2026-10-17**:

- [Open Source Guides: best practices](https://opensource.guide/best-practices/)
  supports documented contribution rules and repeatable tests.
- [Python JSON decoding](https://docs.python.org/3.13/library/json.html#repeated-names-within-an-object)
  documents repeated-key behavior and `object_pairs_hook`.

Commands above are this repository's workflow, not a required standard for other
projects. Use the [contributor guide](../CONTRIBUTING.md) for the actual submission route.
