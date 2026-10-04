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
The implementation follows GitHub's current relative-link guidance but deliberately does not
claim external URL, raw-HTML, reference-style-link or section-anchor validation.

## Initial foundation candidate — 2026-10-03

Added the reader-first front page, repository checklist, README guide and scaffold,
three source-bounded pattern studies, dated program guidance and contribution workflow.
Added a structured catalog, offline validator, deterministic view and negative tests.
Preserved the existing MIT LICENSE.

This is production evidence, not a claim of independent review or a released version.
The bootstrap issue owns its acceptance work; repository-native checks and merge state
remain the evidence for integration. Later semantic changes should name their affected
unit or issue rather than silently rewriting the original rationale.
