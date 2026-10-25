# Visual README patterns that earn their space

A visual README should reduce the time between landing on a repository and understanding
its result. Decoration is optional; comprehension is not. Start with a useful sentence,
then let one visual prove or clarify something the prose cannot show as quickly.

## The first screen

Use the opening area for four jobs, in roughly this order:

1. **Identity:** project name and a one-sentence outcome.
2. **Evidence:** one screenshot, diagram, terminal capture or benchmark that represents the result.
3. **Interpretation:** a caption or nearby text that says what the reader should notice.
4. **Next move:** the shortest useful path to try, inspect or learn more.

Do not make a visitor decode a logo, badge wall or animation before learning what the
project does. A repository with no useful visual is better than one with a decorative hero
that pushes the actual result below the fold.

## Make one visual carry evidence

A hero image earns its space when it answers a real question:

- **Application:** what does the product actually look like?
- **CLI:** what command and result will I see?
- **Library:** what output or transformation does the API produce?
- **Research/data:** what is in the dataset, model or result?
- **Collection:** how is a large body of material organized?

A caption should name the evidence, not repeat “screenshot above.” Keep installation,
limitations, warnings and commands as real text outside the image.

## Support light and dark themes deliberately

GitHub documents the HTML `picture` element with `prefers-color-scheme` sources for
theme-aware README images. Use it when a single asset loses contrast or meaning in one
theme. Always keep a default `img`, and give it useful alternative text.

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./preview-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./preview-light.svg">
  <img alt="A concrete description of the result shown in the preview."
       src="./preview-light.svg">
</picture>
```

Prefer repository-relative image paths for repository-owned assets. They continue to work
across branches and clones more reliably than hard-coded branch URLs.

## Accessibility is part of the visual design

The Open Source Guides accessibility guidance recommends meaningful alt text, real text
instead of images of text where possible, and a nearby text alternative for complex
diagrams. It also warns against communicating meaning only through color.

For README visuals:

- describe the information conveyed, not the decorative style;
- repeat critical numbers, labels or conclusions in nearby text;
- use labels, shapes or words in addition to color;
- avoid auto-playing motion and flashing content;
- keep heading order and link text understandable without the image;
- manually inspect narrow widths, light/dark themes, zoom and assistive technology when available.

An automated source check can catch missing assets and markup regressions. It cannot certify
contrast, screen-reader behavior or whether a screenshot is genuinely understandable.

The offline `python tools/html_navigation.py` check also flags **raw HTML
`<img>` elements missing an `alt` attribute** in active Markdown content.
Use meaningful text for informative images; `alt=""` is correct when an
image is genuinely decorative or its information is fully supplied nearby.
The check deliberately permits an empty attribute: deciding the image's
purpose and checking the quality of an alternative require human judgement.
Markdown `![alt](path)` syntax already contains an alt-text slot; the
checker does not grade its content, and it does not inspect a browser's
rendered accessibility tree. Duplicate HTML `href`, `src`, `srcset`, `alt`,
`id` and `name` attributes are reported: the first value is used for offline
checks, as in HTML parsing, so a later duplicate cannot conceal a broken link. For complex diagrams, preserve a full textual
equivalent near the image.

## Patterns observed in current repositories

### uv — evidence before expansion

The `astral-sh/uv` README at blob
`66caaf9ccc62add8c63de8e71184c9b7677377ad` opens with a concise promise, then a
theme-aware benchmark image with descriptive alt text and a caption, followed by highlights
and installation. The useful pattern is **promise → visual evidence → interpretation → action**.
Do not copy its benchmark, numbers or brand assets.

### Immich — show the product early, not its exact image markup

The `immich-app/immich` README at blob
`ba774d44cdd7b9e9baed4cc4166d4c317e3ebae8` puts its brand and a large product
screenshot before detailed feature tables, while warnings and documentation links remain
real text. For visual applications, a representative product state can answer “what is this?”
faster than another paragraph.

Borrow the **placement and product-first evidence**, not the exact image markup: the inspected
logo and main screenshot use `title` attributes without `alt` attributes. BeautifulRepo's
recommended pattern keeps meaningful fallback `img alt` text because GitHub's responsive-image
example and current accessibility guidance both treat alternative text as reader-facing
content. Badge rows and activity graphics are not automatically useful for smaller repositories.

### Awesome Python — navigation can be the visual system

The `vinta/awesome-python` README at blob
`c8d5186e427f4068718ebdc26b5a86eafbe386ee` relies primarily on headings and category
navigation rather than a hero screenshot. For a collection, information architecture can be
the dominant visual design. Do not add media just to make a long catalog look more graphical.

## A bounded before/after example

See the original fictional
[`PocketDiff` before/after example](../examples/readme-visuals/README.md).
It demonstrates a theme-aware local asset, descriptive alt text, nearby text equivalence,
a concrete command/result, and a small source test that verifies the structural promises.

The SVGs are original fixtures created for BeautifulRepo. They are examples, not copied
screenshots or endorsements of another project.

## Choose a voice before choosing decoration

The [three PocketDiff first-screen specimens](../examples/readme-visuals/variants/README.md)
keep identical fictional command, input and report facts while changing the
opening hierarchy for different readers. Compare the actual Markdown pages
with images disabled. Their words are **not** verified product output; replacing
the facts with real, revision-bound evidence is necessary for adaptation.
Static unit and link tests cover fact preservation and paths, not visual quality.

## Review checklist

Before merging a README visual:

- [ ] The one-sentence outcome still makes sense with images disabled.
- [ ] The visual proves or clarifies something specific.
- [ ] Alt text communicates the information a non-visual reader needs.
- [ ] Complex visual meaning also exists in nearby text.
- [ ] Status is not communicated by color alone.
- [ ] Repository-owned media uses relative paths.
- [ ] Light and dark variants exist only when they materially improve legibility.
- [ ] The rendered result was inspected at narrow width and both themes.
- [ ] Motion, file size and third-party asset licensing are justified.
- [ ] Tests are described honestly; source lint is not called an accessibility audit.

## Sources

Sources and repository examples rechecked 2026-10-05.

- [GitHub writing quickstart](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github)
- [GitHub basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [Open Source Guides: Accessibility Best Practices](https://opensource.guide/accessibility-best-practices-for-your-project/)
- [uv README at inspected blob](https://github.com/astral-sh/uv/blob/66caaf9ccc62add8c63de8e71184c9b7677377ad/README.md)
- [Immich README at inspected blob](https://github.com/immich-app/immich/blob/ba774d44cdd7b9e9baed4cc4166d4c317e3ebae8/README.md)
- [Awesome Python README at inspected blob](https://github.com/vinta/awesome-python/blob/c8d5186e427f4068718ebdc26b5a86eafbe386ee/README.md)

Source inspection records markup and information architecture, not runtime behavior,
visual-quality certification or permission to reuse third-party media.

**Alt-text semantics rechecked 2026-10-25:** [W3C WAI Images Tutorial](https://www.w3.org/WAI/tutorials/images/)
and [Decorative Images](https://www.w3.org/WAI/tutorials/images/decorative/).
The distinction between an absent `alt` attribute and an intentional
`alt=""` is from WAI guidance; the checker's static scope is our own.
