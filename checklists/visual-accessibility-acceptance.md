# GitHub README visual acceptance: a reproducible field check

**Purpose:** check a real, GitHub-rendered README or visual example before
calling its layout accessible or its screenshots useful. This is a manual
verification recipe with a reusable evidence record, **not** a WCAG certificate.
It complements [design intent](../templates/DESIGN_INTENT.template.md) and
[source-only visual guidance](../guides/readme-visuals.md).

## 1. Freeze what is actually being tested

Use the **rendered** GitHub `blob/<full-commit-SHA>/...` page, not Raw,
a local Markdown preview, a mutable branch URL, or an SVG viewed alone.
Record whether you are signed in; GitHub navigation and overlays can vary.

- Repository, full commit SHA, README path and rendered URL:
- Browser version / operating system / sign-in state:
- Date, tester, display scaling and baseline window width:
- Image assets and the expected text-equivalent location:
- Source evidence for any command or screenshot (fixture, command, observed output):

An image that looks correct in a standalone browser tab can still fail when
GitHub wraps, sanitizes or theme-switches the Markdown. If you cannot open
the GitHub-rendered page, mark those checks **NOT RUN**, even if local HTML
or screenshots looked good.

## 2. Verify claims before evaluating decoration

Read from top to bottom without viewing the images. Can the visitor identify
the task, outcome, limitations and first useful action? Run a documented
first-success command **only in an authorized disposable environment** and
record its actual output. Never silently run third-party install scripts,
start services or publish anything as part of a visual review.

Then compare each informative image with the command/result and the text
alternative beside it. A drawing of a verified transcript is not a terminal
screenshot; a fictional mockup is not product output. Record any inconsistency
as a **FAIL**, not a visual preference.

## 3. GitHub rendering matrix

Repeat the same page at the same full commit SHA. Capture actual viewport
measurements and an annotated screenshot only when safe to share.

| Check | Procedure | What to record |
| --- | --- | --- |
| Light and dark | Render with each effective colour scheme; inspect the actual `picture` source/fallback and images | Selected asset, text/background visibility, clipped or absent meaning |
| Narrow reflow | Set the browser's **CSS viewport** to 320 px where supported, at 100% zoom; scroll the document | Unwanted page-level two-dimensional scrolling, overlap, truncated prose or controls |
| Real zoom | In a desktop browser, use **400% browser zoom** from a 1280 px-wide starting window; confirm the effective CSS viewport rather than assuming it | Whether content reflows, what stays readable and any necessary two-dimensional exceptions |
| Images unavailable | Disable image loading or block the checked-in images, then reload | Whether headings, meaningful alt text, results and copyable first-success steps remain available |
| Keyboard | Without a pointer, Tab and Shift+Tab through README links, activate a representative link with Enter and return | Focus visibility, logical order, unreachable links, traps; distinguish GitHub chrome from authored content |
| Assistive technology | If available, use an identified screen reader/browser pair to navigate headings, links and informative image alternatives | Spoken content/announced names, missing or duplicated meaning, tester and software version |
| Motion, if present | Exercise reduced-motion preference and default motion | Autoplay, flashing, essential information tied to animation |

### Optional local measurements in the browser console

A small, **read-only** [README measurement probe](../examples/readme-visuals/github-readme-probe.js)
can help fill in the numeric observations above without installing packages.
First inspect its source: it reads the current DOM but does not fetch, edit,
copy or transmit anything. On the rendered GitHub page at the **full pinned
commit SHA**, open developer tools, execute that inspected JavaScript expression
in the Console, and record its returned object. Do not run pasted code you
have not personally reviewed.

Repeat for light and dark themes, the 320 CSS px viewport, and **actual**
400% browser zoom. The object records the measured CSS viewport, document
and Markdown scroll widths, overflow in pixels, browser scheme preference,
GitHub appearance attributes when present, **sampled** image-load counts and
up to eight selected `picture` image paths; it deliberately omits URL query
strings. The probe visits at most 2,000 DOM descendants plus one truncation
check for **all** measurements. `imageCountsPartial: true` means `images`
and `unloadedImages` are lower bounds, not totals; `pictureSelectionsTruncated: true` means additional `picture` choices may be missing. Never claim every
image rendered successfully when a sample was truncated. Save each observation with its browser/version, real zoom setting
and screenshot **only if the material is safe to share**.

GitHub can use a manually selected dark/light theme even when the operating
system prefers the opposite scheme. The probe's `prefersDark` reports the
**browser media preference**, while `githubAppearance` reads optional page
`data-color-mode`, `data-light-theme` and `data-dark-theme` attributes;
these are observations, **not a stable GitHub API or proof of the visible
theme**. They can disagree or be absent. Judge the actual rendered colours,
image selection and text contrast in each screenshot instead of treating the
media query as a GitHub theme verdict. GitHub's
[theme-setting documentation](https://docs.github.com/en/get-started/accessibility/managing-your-theme-settings)
was reviewed **2026-10-28**.

The probe also returns `overflowInspection`: up to **eight** element rectangles
that extend beyond the rendered Markdown container. It walks at most **2,000**
descendants (plus one check for truncation) without building a full element
list or allocating unbounded image query results, and reports `truncated` if
more descendants exist. The output
includes only a zero-based descendant index, tag name and left/right pixel
excess; no element text, class names, IDs, attributes or URLs are included.
To inspect `elementIndex` in the **same** browser tab, evaluate
the following bounded traversal, substituting the returned integer for `INDEX`:

```js
const article = document.querySelector("article.markdown-body, .markdown-body");
const walker = document.createTreeWalker(article, NodeFilter.SHOW_ELEMENT);
let node;
for (let n = 0; n <= INDEX; n++) node = walker.nextNode();
node // Inspect locally; don't publish unreviewed content.
```

Only use an index returned by the probe (0–1,999). Do not share inspected
nodes or page text without checking for private content.

Rectangles are **candidates, not violations**: code and tables can require
local horizontal scrolling. Hidden, transformed or CSS-generated content may
escape the sample. Zero candidates do not cancel a positive
`markdownOverflowPx`. Inspect actual reader impact before changing the
layout. See [W3C WAI Reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html),
reviewed 2026-10-28.

The numbers are **diagnostics, not PASS/FAIL labels**. GitHub's own navigation
can affect page overflow; code blocks or tables can have permitted local
horizontal scrolling. An image that loads is not necessarily understandable.
The probe cannot establish zoom percentage, keyboard behaviour, screen-reader
speech, contrast or WCAG conformance. If no rendered Markdown container is
found, it returns `NOT RUN` rather than a success. These manual checks and
their evidence receipt still have to be completed by a tester.

**Reflow interpretation:** WCAG 2.2 Success Criterion 1.4.10 describes
content presentation without loss of information/functionality at the
equivalent of 320 CSS pixels wide for vertically scrolling content. Some
content *requiring* two-dimensional layout, such as data tables or detailed
diagrams, has a scoped exception. Do not call any horizontal scrollbar a
failure without identifying the element and reader impact. Conversely, do not
accept page-wide horizontal scrolling merely because a code block is long.
For vertical writing modes the corresponding height criterion differs.

**Zoom is not viewport simulation:** an emulated 320 px viewport and actual
400% browser zoom exercise different behaviours. Record both. At a 1280
physical/CSS-pixel baseline, 400% zoom is often approximately 320 CSS pixels
of layout width, but browser chrome, device scale and display settings can
change the effective viewport. Measure rather than infer.

**Image semantics:** informative and functional images need relevant
alternatives. Genuinely decorative images may use `alt=""`. For a complex
diagram, provide a nearby full textual explanation. A present `alt` attribute
is not evidence that the wording is useful.

## 4. Evidence receipt — copy and complete

Use `PASS`, `FAIL`, `NOT RUN` or `N/A` (with a reason). **Blank cells are
not passes.** Do not turn one tested browser or zoom setting into a claim of
platform-wide accessibility.

| Case | Status | Observation / evidence file | Follow-up |
| --- | --- | --- | --- |
| Exact source and first-success output | NOT RUN | | |
| GitHub rendered, light | NOT RUN | | |
| GitHub rendered, dark | NOT RUN | | |
| Narrow CSS viewport | NOT RUN | | |
| Actual 400% zoom | NOT RUN | | |
| Images blocked / nonvisual meaning | NOT RUN | | |
| Keyboard and focus | NOT RUN | | |
| Screen reader (name combination) | NOT RUN | | |
| Reduced motion (or N/A reason) | NOT RUN | | |

**Decision:** SHIP / REVISE / DEFER / INCONCLUSIVE — _reason and responsible
follow-up_. List materially different environments not tested. Link any
public evidence only after checking it contains no secrets, private data,
unpublished product screenshots or personal information.

A fully completed receipt supports a **bounded observation on one page and
environment**. It is not a substitute for broad accessibility testing, a
user study or a formal conformance claim.

## 5. Apply this to BeautifulRepo itself

Start with the working [Rowcount first screens](../examples/readme-visuals/rowcount/README.md):
its terminal-led image is original art based on real `Data rows: 3` output,
and the command/result remain selectable text. Compare the rendered
[terminal-led presentation](../examples/readme-visuals/rowcount/terminal-led.md)
with the [contract-first presentation](../examples/readme-visuals/rowcount/contract-first.md)
without changing the facts. The original isolated Chromium preview recorded
in the [visual guide](../guides/readme-visuals.md) **does not** fill in this
GitHub acceptance receipt. Until the checks above are performed, the result
remains **NOT RUN**.

## Primary references

The method below was reviewed against primary guidance **2026-10-27**;
that date does not mean a browser or screen-reader test happened.

- [W3C WAI — Understanding Reflow (WCAG 2.2)](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html):
  CSS-pixel threshold, zoom relationship, exceptions and rationale.
- [W3C WAI — Images Tutorial](https://www.w3.org/WAI/tutorials/images/):
  informative, functional, decorative and complex-image alternatives.
- [W3C WAI — Decorative Images](https://www.w3.org/WAI/tutorials/images/decorative/):
  when empty alternative text is appropriate.
- [GitHub Docs — Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax):
  rendering context; actual behaviour must still be inspected.
