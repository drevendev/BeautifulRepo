# A contrast decision with reproducible evidence

This **original, illustrative** light/dark palette shows four failing text/background
pairs and four corrected pairs. The numbers are computed by BeautifulRepo's
[offline calculator](../../tools/color_contrast.py), not copied from a screenshot.
This is a color-selection demonstration, **not** a tested website or a claim of
full WCAG conformance.

From the BeautifulRepo checkout (Python 3.11+, no packages or network needed):

```sh
python -I examples/contrast-palette/demo.py
```

Expected output (verified with the checked-in `pairs.json` on Python 3.13.5):

```text
Light help text (light, AA normal): 4.478:1 FAIL -> 7.005:1 PASS (threshold 4.5:1)
Dark help text (dark, AA normal): 3.638:1 FAIL -> 8.487:1 PASS (threshold 4.5:1)
Light large heading (light, AA large): 2.615:1 FAIL -> 3.545:1 PASS (threshold 3:1)
Dark high-contrast text (dark, AAA normal): 6.109:1 FAIL -> 12.814:1 PASS (threshold 7:1)
OK: 4 illustrative palette corrections pass declared numerical thresholds
```

The process exits **0** only if each before-pair fails and each after-pair
passes its selected AA/AAA text threshold, using the **unrounded** ratios.
Malformed fixture data (including duplicate JSON object members), invalid hex
colors, an accidental regression in a corrected pair, or a before-pair that no
longer fails yields exit **2** with an error. The sample is deliberately
locked to its four checked-in rows, so it is an example rather than a
general-purpose palette linter.

**How to adapt:** identify the *actual rendered* foreground and opaque background
of each normal/large text style in **both** themes; choose an accessible
replacement; check the pair with
`python tools/color_contrast.py "#595959" "#ffffff" --text normal --level AA` and write down the
result beside the style. Re-run for interactive states, not just default text.
Do not copy this invented palette's color choices into a real product without
checking that product's computed values and text size.

**Evidence boundary:** these tests don't inspect computed CSS, translucent layers,
gradients, images, text classification, focus indicators, browser rendering,
320 px reflow, keyboard use or screen readers. They cannot establish that a
real page meets WCAG. Use the [visual acceptance checklist](../../checklists/visual-accessibility-acceptance.md)
and [visual README guidance](../../guides/readme-visuals.md) before making
rendered-UI claims.

Primary rule: [WCAG 2.2 SC 1.4.3](https://www.w3.org/TR/WCAG22/#contrast-minimum)
and [W3C contrast explanation](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html),
reviewed **2026-11-19**. No third-party assets or code are included.
