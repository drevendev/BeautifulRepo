# Three-checker audit: reproducible broken-link repair

This **fictional Pocket Trails example** shows a real execution of
BeautifulRepo's [combined offline audit](../../guides/combined-audit.md)
without cloning, executing or modifying any outside repository.

From the BeautifulRepo root with Python 3.11+:

```bash
python -I examples/combined-audit/demo.py
python -I examples/combined-audit/demo.py --format json
python -I examples/combined-audit/demo.py --format html > pocket-trails-audit.html
```

The HTML option produces a **responsive, self-contained before/after page** from the same real checker observations on synthetic fixtures. Its first screen now shows source-derived **before/after check counts** above the diff, so narrow-window captures show the outcome before the long diagnostics; complete evidence remains below. It also displays the *actual unified diff* of the two temporary README files: one broken local link is replaced with an existing destination. The diff is derived from the fixtures, not an illustrative screenshot. Removed and added lines have visible `-`/`+` prefixes, text labels for assistive technology and contrasting backgrounds in light/dark themes; color is never the only distinction. This is authored markup, not evidence of screen-reader or contrast certification. A visible outcome line states how many of the two local-link checks pass in each state; the **Jump to after repair** link skips the long before-report on mobile and is reachable by keyboard. Open `pocket-trails-audit.html` locally to inspect it. No JavaScript, remote assets or invented screenshot is used. Shell redirection writes the HTML in your current working directory, **not inside a checked fixture**; it may create an empty file if the demo fails. Check the command exit status before sharing. Outputs from real projects can contain sensitive source paths.

The demo creates two disposable local directories. Each contains a README,
LICENSE, CONTRIBUTING.md and a guide. The *before* README links to
`docs/setup.md`, which does not exist. The *after* README links to the
existing `docs/guide.md`. It invokes the real `tools/audit_bundle.py`
twice, checks that neither invocation changed any fixture bytes, and validates
that both link checkers saw the missing destination and then stopped
reporting it. The script fails rather than claiming success if a checker is
incomplete, the expected broken link is not found, or after still fails.

Expected **invariants**, enforced by
[the demo's tests](../../tests/test_combined_audit_demo.py), are:

- Before: combined exit 1, `markdown_links` exit 1,
  `html_navigation` exit 1, both naming `docs/setup.md`.
- After: combined exit 0, both link checks exit 0.
- The independent entry-point audit completes in both; its actual warning
  and informational counts are printed, not assumed to be zero.
- JSON includes the unmodified, per-checker reports so each diagnostic can
  be inspected. The script itself exits 0 **only if the stated experiment
  was reproduced**, not because every audit warning disappeared.

This deliberately tests a **synthetic broken relative link**, not a
production repository improvement, web link reachability, actual GitHub
rendering, WCAG conformity, or user satisfaction. It is independent of the
[fictional entry-point audit example](../repository-audit/README.md) and the
[revision-pinned PatchPitch case](../../case-studies/patchpitch.md).

For your own checkout, use the combined audit directly instead of running
this temporary demonstration:

```bash
python -I tools/audit_bundle.py ../your-repository --format json
```

It is a read-only, local source inspection, not a sandbox for hostile files.
See [the limitations and exit-code guide](../../guides/combined-audit.md).

## Capture actual browser screenshots (optional)

With **Chromium or Chrome already installed**, run the checked-in capture helper
from the BeautifulRepo root:

```bash
python -I examples/combined-audit/capture.py --output-dir ../beautifulrepo-audit-capture
```

It first executes the **real combined checkers** via this disposable demo,
then opens the resulting local HTML with the installed headless browser. The
output directory receives `report.html`, `desktop.png` (requested 1280×900 window)
and `mobile.png` (requested 390×844 window). Use `--view desktop` or
`--browser PATH` if needed. Existing files are **not overwritten**. Both screenshots are staged before
publication, so a **browser rendering failure** publishes none. Final publication uses
exclusive file creation, so a competing writer's file is **never replaced**;
a concurrent destination or a late disk/permissions error can still leave
partial output already published. No Python browser package or
browser auto-installation is performed.

These are **real browser-rendered screenshots of synthetic test data**, not
screenshots of a real repository, a real phone, or a recorded user session.
Window-size flags alone do not establish actual viewport geometry, mobile
behavior, focus order, accessibility or dark-theme acceptance. Review the PNGs
visually and compare them with `report.html` before publishing.
The Python demo itself makes no network requests; browser flags reduce
background activity but **do not guarantee a network-air-gapped browser**.
Do not use this capture recipe to open untrusted or private project HTML.
The screenshot helper is optional: the existing CLI and CI checks require
no browser.

### Record a browser walkthrough (optional, synthetic only)

For a short, real Chromium **screen recording of the already-generated
fictional report**, use the optional [WebM recorder](record.py) after the
screenshot capture above. The media-production environment must separately
provide **Python Playwright**, its video encoder (FFmpeg bundled by Playwright
or otherwise available), and installed Chrome/Chromium. These are **not**
runtime or CI requirements of BeautifulRepo's documentation checkers; the
recorder never installs them.

```bash
python -I examples/combined-audit/record.py \
  --input ../beautifulrepo-audit-capture/report.html \
  --output ../beautifulrepo-audit-capture/walkthrough.webm
```

The helper opens only the validated, local **synthetic** HTML string in a
network-disabled Chromium context, holds the outcome overview, scrolls through
both checker reports and returns to the top. The planned motion is about
22 seconds at a 1280×720 browser viewport; encoding may add time. It does not
audit live repositories, record a terminal command being executed, prove a
real person's interaction, test assistive technology, or capture a real phone.
The video has no narration or captions; use the companion `evidence.md`
for a text explanation and write time-coded captions before distributing it
where accessibility or platform rules require them.

The tool refuses to overwrite an existing video, rejects unmatched report
markers and active HTML embedding tags, and blocks network requests in the
browser context. This does not turn arbitrary HTML into a safe input: use only
the generated, disposable fixture report, never confidential or third-party
HTML. The optional video is not automatically published or attached to CI.
The test suite checks input boundaries and the planned scroll, **not actual
Playwright availability or visual acceptance**. Manually watch the output,
confirm its source revision, and label it synthetic before public reuse.

### Reproduce screenshots in GitHub Actions (synthetic only)

The opt-in [browser evidence workflow](../../.github/workflows/showcase-capture.yml)
runs the same checked-in capture helper on an Ubuntu runner with Chrome. It
checks the generated HTML for the observed before/after diagnostics, reads the
**actual PNG dimensions**, and attaches `report.html`, `desktop.png` and
`mobile.png` together as the short-lived
`pocket-trails-synthetic-browser-capture` workflow artifact. It also runs on
pull requests that change the demo/checkers or this workflow. To reproduce on
`master`, open GitHub Actions → **Synthetic audit browser evidence** →
**Run workflow**. No screenshots are committed automatically.

The artifact also contains `evidence.md`, a **source-labeled text alternative**
with the checked-out commit, the before/after result, actual PNG header
dimensions and SHA-256 hashes for the HTML and both images. Generate the same
companion locally, after the capture, with:

```bash
python -I examples/combined-audit/evidence.py ../beautifulrepo-audit-capture
```

The companion checks expected synthetic HTML markers and PNG headers, but
does **not** decode the pixels or prove the displayed layout. It refuses to
replace an existing `evidence.md`. Its checksums help recipients identify
matching bytes, not certify independent provenance or real user outcomes.

Download the artifact from the **specific successful run**, then **inspect both
images manually** before citing them. A green job proves the browser produced
PNG files from the synthetic report; it does not prove the requested window
size was the effective mobile viewport, that layouts are accessible, or that
any real repository was improved. Workflow artifacts expire after seven days.
The workflow uses only read-only repository access and pinned Actions; it does
not publish a release, push to another repository, or execute an audited target.
