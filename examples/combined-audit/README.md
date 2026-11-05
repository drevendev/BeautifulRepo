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

The HTML option produces a **responsive, self-contained before/after page** from the same real checker observations on synthetic fixtures. It also displays the *actual unified diff* of the two temporary README files: one broken local link is replaced with an existing destination. The diff is derived from the fixtures, not an illustrative screenshot. A visible outcome line states how many of the two local-link checks pass in each state; the **Jump to after repair** link skips the long before-report on mobile and is reachable by keyboard. Open `pocket-trails-audit.html` locally to inspect it. No JavaScript, remote assets or invented screenshot is used. Shell redirection writes the HTML in your current working directory, **not inside a checked fixture**; it may create an empty file if the demo fails. Check the command exit status before sharing. Outputs from real projects can contain sensitive source paths.

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
