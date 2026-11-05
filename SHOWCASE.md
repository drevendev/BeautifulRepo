# One broken README link, two independent checks

**Before: 0/2 local-link checks pass. After: 2/2 pass.** This is a
reproducible **fictional** Pocket Trails fixture, not a repaired external
repository or evidence of real users. BeautifulRepo invokes its actual
read-only offline Markdown-link and HTML-navigation checkers on both versions.

## The exact change

The fixture already includes `docs/guide.md`, but its README links to
`docs/setup.md`, which does not exist. The one-line repair is:

```diff
-Read the [setup guide](docs/setup.md) to begin.
+Read the [setup guide](docs/guide.md) to begin.
```

**Observed checker results** (tested against the fixture, not an invented
quality score):

- **Before:** the combined audit exits **1**. Both `markdown_links` and
  `html_navigation` exit **1**, naming the missing `docs/setup.md`.
- **After:** the combined audit exits **0**. Both local-link checks exit
  **0**, with no missing-link diagnostics for the repaired destination.
- Both entry-point checks also complete, but their warning/info counts are
  separate observations: a successful exit does not certify a good README.

[Inspect the actual fixture, checked assertions and generated diff](examples/combined-audit/README.md),
or inspect [the source of the synthetic experiment](examples/combined-audit/demo.py)
and [its behavioral tests](tests/test_combined_audit_demo.py). The test rejects
a false "after" success and checks that the audit never writes the fixture.

## Reproduce it with no extra Python packages

Requires **Git and Python 3.11+**. In a terminal:

```bash
git clone https://github.com/drevendev/BeautifulRepo.git
cd BeautifulRepo
python -I examples/combined-audit/demo.py
```

The command produces a readable text transcript including the exact diff,
both checker statuses and the **BEFORE: combined exit 1** / **AFTER: combined
exit 0** lines. Its own exit status is **0 only if the before/after experiment
was reproduced**; it is not the failing status of the fictional "before"
checkout. It uses disposable local fixtures and does not execute outside
project code or fetch URLs.

To see the responsive, standalone HTML from the same source observations:

```bash
python -I examples/combined-audit/demo.py --format html > pocket-trails-audit.html
```

Open `pocket-trails-audit.html` locally. The page includes the checker
diagnostics, the exact diff and a text alternative; it contains no scripts
or remote assets. Check the command status before sharing the file: shell
redirection can create an empty HTML file if the command fails.

## Apply the checks to your repository

Keep the two repositories adjacent in a workspace, e.g. `workspace/BeautifulRepo`
and `workspace/your-repository`. From `workspace/BeautifulRepo`:

```bash
python -I tools/audit_bundle.py ../your-repository --fail-on never
```

This runs three tools: entry-point/README structure, local Markdown
destinations, and local HTML/fragment navigation. The `never` option treats
entry-point findings as advisory **but does not ignore broken local links**.
Combined exit codes are **0** (complete and below selected thresholds),
**1** (at least one finding met the threshold, including broken local
links), and **2** (incomplete scan; do not interpret as clean).

[Exact behavior, JSON/HTML output and privacy limits](guides/combined-audit.md).
To adopt checks in a PR, use the [SHA-pinned v0.2.0 Action recipe](guides/adopting-the-checks.md).
The combined wrapper is **current-source only**, not part of the released
v0.2.0 Action.

## Optional browser captures and video

The same checked-in synthetic HTML can be rendered in an actual installed
Chromium/Chrome browser. The [capture instructions](examples/combined-audit/README.md#capture-actual-browser-screenshots-optional)
produce a desktop PNG, a narrow-window PNG and an HTML report. The optional
[recording instructions](examples/combined-audit/README.md#record-a-browser-walkthrough-optional-synthetic-only)
produce a real WebM scroll recording, provided Playwright, its video encoder
and a browser are installed separately. Normal audits need none of those
dependencies. The [seven-day GitHub Actions artifact](examples/combined-audit/README.md#reproduce-screenshots-in-github-actions-synthetic-only)
is **expiring**, not a permanent public video. No video file is claimed
to be published by this page.

**Text alternative for the visuals:** a heading says "One broken link,
two independent checkers"; the first overview reads "Before: 0/2
local-link checks pass" and "After: 2/2 local-link checks pass"; the
diff replaces `docs/setup.md` with `docs/guide.md`. Detailed checker
diagnostics follow. The visuals are screenshots/recordings of **synthetic
source findings**, not of a user session, actual phone, external site,
accessibility audit or external repository repair.

## What is real, and what is not

For **revision-pinned observations on an actual repository**, read the
[PatchPitch case study](case-studies/patchpitch.md). That older v0.2.0 audit
reported one informational `contributing.missing` finding before a
contribution guide was added and none afterward; it **did not detect**
the more important first-run README improvement. Those results are
historical, not a fresh scan.

These are bounded, offline source checks. They do not check external URLs,
execute a repository's application, certify rendered Markdown or WCAG,
validate the meaning of a license, guarantee filesystem isolation against
hostile inputs, or prove that readers can follow the instructions.
