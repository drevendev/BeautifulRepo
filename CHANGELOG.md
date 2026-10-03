# Changelog

## Visual README patterns candidate — 2026-10-03

BR-VISUAL-002 adds a source-backed visual README guide and an original theme-aware
PocketDiff before/after example. The guide records concrete observations from current
uv, Immich and Awesome Python READMEs without copying their media or branding. Five
offline structural tests cover theme switching, alt text, local assets, SVG descriptions
and non-color labels.

Later-run review found that the text-equivalence test could pass using facts that existed
only inside the image markup. The test now removes the `<picture>` block before checking
the four report facts, so it actually verifies a nearby real-text equivalent.

This is a stacked production candidate based on BR-FOUNDATION-001, not acceptance or a
released edition. Rendered GitHub light/dark appearance and assistive-technology behavior
remain manual review items.

## Initial foundation candidate — 2026-10-03

Added the reader-first front page, repository checklist, README guide and scaffold,
three source-bounded pattern studies, dated program guidance and contribution workflow.
Added a structured catalog, offline validator, deterministic view and negative tests.
Preserved the existing MIT LICENSE.

This is production evidence, not a claim of independent review or a released version.
The bootstrap issue owns its acceptance work; repository-native checks and merge state
remain the evidence for integration. Later semantic changes should name their affected
unit or issue rather than silently rewriting the original rationale.
