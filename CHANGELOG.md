# Changelog

## Documentation-link checker candidate — 2026-10-04

**BR-LINKS-005** adds a dependency-free offline checker for repository-owned inline Markdown
link and image destinations, wires it into CI and contributor instructions, and adds behavioral
tests for valid paths, missing targets, repository-root escapes, external links and code examples.
Review repair: fenced-code parsing now keeps the opening marker length and ignores shorter inner
fences until an equal-or-longer closing fence of the same marker type appears.
Review repair: inline destinations now preserve balanced and backslash-escaped parentheses,
including nested pairs, instead of truncating at the first closing parenthesis.
Review repair: inline link-text scanning now accepts balanced and backslash-escaped brackets,
so valid nested labels and image alt text are not silently skipped.
Review repair: valid semicolon-terminated GFM character references in destinations are decoded
before URL classification and path resolution; invalid named references remain literal text.
Review repair: inline links are scanned across non-blank lines, so GFM titles that span line
endings still validate their repository-owned destination while blank-line crossings stay invalid.
Review repair: inline-code masking now follows equal-length GFM backtick strings across line
endings while leaving escaped or unmatched delimiters literal, preventing links inside code spans
from being checked without hiding real links behind non-code backticks.
Review repair: indented-code masking now treats standalone four-column code (including tabs)
as literal while preserving paragraph continuation and common list-item precedence, preventing code
examples from creating false broken-link failures without hiding real links in indented prose.
Review repair: code masking now descends through explicit GFM block-quote containers, including nested quotes, so fenced and indented code examples inside quotes do not create false link failures while quoted prose links remain checked.
Review repair: code masking now descends through explicit list-item containers before root fence parsing, including marker-only items, nested lists and list/quote combinations, so legal child fences stay literal without hiding following prose links.
Review repair: list-container masking now respects paragraph interruption rules: only non-empty bullets and ordered items starting at 1 may interrupt open paragraphs, preventing faux list markers from hiding prose links as nested code. Dedicated regression coverage now locks the ordered-start boundary.
Review repair: GFM type-1 raw HTML blocks (`script`, `pre`, `style`) are masked as literal regions, including inside explicit list and quote containers, so Markdown-looking examples inside them do not create false broken-link reports. A regression keeps other HTML tags from being overextended with type-1 end-tag semantics.
The implementation follows GitHub's current relative-link guidance but deliberately does not
claim external URL, raw-HTML attribute, reference-style-link or section-anchor validation.

## Initial foundation candidate — 2026-10-03

Added the reader-first front page, repository checklist, README guide and scaffold,
three source-bounded pattern studies, dated program guidance and contribution workflow.
Added a structured catalog, offline validator, deterministic view and negative tests.
Preserved the existing MIT LICENSE.

This is production evidence, not a claim of independent review or a released version.
The bootstrap issue owns its acceptance work; repository-native checks and merge state
remain the evidence for integration. Later semantic changes should name their affected
unit or issue rather than silently rewriting the original rationale.
