# Design a README around a result

The front page is an invitation and a decision aid. Detailed reference belongs one link
away. A strong visual identity can help, but it cannot replace a comprehensible example.

## A practical order

1. **Promise:** what the project does, for whom, and what makes it useful.
2. **Result:** one representative example, with enough explanation to judge relevance.
3. **First success:** prerequisites, commands and the result the reader should see.
4. **Navigation:** documentation, examples, troubleshooting and important limitations.
5. **Participation and trust:** status, contribution route, maintenance expectations and license.

This is a starting pattern, not a universal law. A research dataset needs provenance and
schema before installation; a library benefits from an import example; a knowledge
collection should provide a reading path rather than inventing an install command.

## Before and after

**Before:** “An awesome, powerful, next-generation utility with lots of features.”

**After:** “Compare two CSV exports and produce a row-level change report without
uploading either file.”

The second sentence is a fictional wording example, not a claim about BeautifulRepo's
features. It identifies a concrete outcome and a useful boundary without unsupported
superlatives. Follow it with representative input and output, not another slogan.

## Make evidence visible

Distinguish current capabilities, experiments and planned work. Link a build badge to
its workflow; name what a test actually covers. Avoid unsupported “production-ready”,
“secure” and “always green” promises. State missing evidence without treating it as failure
or success. Example commands must match the documented revision and environment.

## Add personality without adding friction

Use one memorable visual idea rather than competing banners. Keep essential text outside
images, explain complex diagrams, and prefer a static preview before a large animation.
Use badges as compact navigation to evidence, not as a wall of decoration. A technical
mascot or metaphor needs a plain-language explanation for readers unfamiliar with it.

Before accepting a visual change, inspect the rendered page at a narrow width and in both
themes. Check heading order and descriptive link text; test keyboard and assistive-technology
flows where available. A source-code inspection alone is not a completed visual or
accessibility audit.

## A review question

Can someone who has never met the author identify the purpose, find the first useful
result and locate the contribution path without guessing? Record where that journey
breaks; do not replace the observation with a subjective score.

## Sources and examples

Basis: [Starting an Open Source Project](https://opensource.guide/starting-a-project/)
and [Accessibility Best Practices](https://opensource.guide/accessibility-best-practices-for-your-project/).
See our [pattern studies](../case-studies/first-patterns.md) for concrete applications.
