# Changelog

## Documentation-link checker candidate — 2026-10-04

**BR-LINKS-005** adds a dependency-free offline checker for repository-owned inline Markdown
link and image destinations, wires it into CI and contributor instructions, and adds behavioral
tests for valid paths, missing targets, repository-root escapes, external links and code examples.
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
