# Changelog

## BR-COMMUNITY-006 community-readiness candidate — 2026-10-06

Added a source-backed guide for deciding when community policy files are operationally
ready, plus a reusable drafting scaffold with explicit placeholders instead of invented
project-specific promises. The source review was refreshed on 2026-10-07 against current
GitHub documentation and the relevant Open Source Guides material. The guide explicitly
separates `SECURITY.md`, GitHub Private Vulnerability Reporting and repository security
advisories; public issue forms warn against vulnerability/exploit details, and the handbook
links readers directly to this guidance.

BeautifulRepo does not claim that the scaffold is a live repository policy or that all
community-profile processes are complete. This is production evidence; provider CI and
later-run acceptance remain separate gates.

## Visual README patterns candidate — 2026-10-03

BR-VISUAL-002 adds a source-backed visual README guide and an original theme-aware
PocketDiff before/after example. The guide records concrete observations from current
uv, Immich and Awesome Python READMEs without copying their media or branding. Five
offline structural tests cover theme switching, alt text, local assets, SVG descriptions
and non-color labels.

Later-run review found that the text-equivalence test could pass using facts that existed
only inside the image markup. The test now removes the `<picture>` block before checking
the four report facts, so it actually verifies a nearby real-text equivalent.

A later exact-head review found a narrower SVG regression gap: the tests did not prove that
`aria-labelledby` still referenced the intended `title`/`desc` nodes, and the description
assertion covered only one of the four reader-facing facts. The structural test now locks both
ID linkage and all four facts without claiming runtime assistive-technology certification.

On 2026-10-05 the cited README examples were rechecked. The guide now distinguishes
Immich's useful product-first placement from its missing main-image alt text and uses
immutable README permalinks for the inspected repository examples.

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
