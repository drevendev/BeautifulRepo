# Changelog

This log describes handbook, tool and GitHub Action changes. Tagged versions are
published as [GitHub Releases](https://github.com/drevendev/BeautifulRepo/releases).
Pin the commit SHA a tag points to rather than the tag name. Dates identify work on
the repository, and the linked pull requests keep the integration history.

From v0.2.0 on, entries follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
sections: Added, Changed, Deprecated, Removed, Fixed and Security. v0.1.0 and earlier
keep their original themed headings.

## [Unreleased]

### Added

- Extend the optional pinned-SDK MCP stdio smoke from Ubuntu to separate
  Ubuntu and Windows Python 3.11 matrix jobs, checking modern and legacy
  protocol sessions and synthetic read-only tool results on each OS. The
  new Windows job is development evidence only, not a Claude Code/Codex
  host-installation PASS or arbitrary NTFS reparse-point certification.
  Preserve independent job outcomes and explicit untested-link reporting
  (related to #255).

- Add a Windows-only native directory-junction regression for the experimental
  MCP root boundary. It creates a synthetic `mklink /J` alias, verifies that
  direct and nested redirected roots are refused before any checker launches,
  and leaves the real fixture intact. The test skips on non-Windows systems
  or where junction creation is unavailable; verify the actual Windows CI
  test result before claiming native NTFS coverage. It is not a Claude Code,
  Codex, arbitrary-reparse-tag or race-condition test (#255).

- Bundle the final standalone `trust-surfaces` skill for the skills CLI:
  seven source-synchronized offline auditor, safety/community guides, checklists
  and SECURITY draft files, with drift checks and a real copied-skill CLI trial.
  The trial exercises the copied auditor on synthetic LICENSE-present/missing
  repositories and checks that target files are unchanged. All four skills now
  pass bounded standalone-copy preflights. These results do **not** establish
  live Claude Code/Codex discovery, model behavior, verified security intake,
  legal compliance or general target safety (#333, #257).

- Make `improve-readme` self-contained for skills CLI copies: five offline
  Python helpers and eleven source-derived references/templates with drift
  checking, exact-diff preview and synthetic approval-hash regression trials.
  Hash checks do not establish human approval or model behavior (#333, #257).

- Make `draft-release-notes` self-contained for standalone skills CLI copies,
  with synchronized local Git inventory, guides, template, source-comparison
  preflight and a real copied-helper invocation in CI. The other two skills
  remain incomplete; copying a helper is not model-driven acceptance (#333).

- Extend the standalone skills CLI trial to run **all three copied audit
  checkers** on deliberately broken and fixed disposable link/HTML fixtures,
  asserting actual findings, exit codes and unchanged target bytes in both
  isolated and combined installations. Preserve diagnostic artifacts and add
  offline regressions. This proves a bounded synthetic behavior check, not
  model invocation or general safety (#333).

- Pilot a self-contained standalone `audit-repo` skill folder with eight
  source-derived offline tools/checklists/guides, with links to omitted
  resources converted to explicit GitHub source URLs. Extend the preflight to
  recognize this layout, keep the checked-in copies byte-identical to canonical
  files, and exercise an isolated CLI copy on a synthetic target. The other
  three skills still have incomplete standalone dependency layouts; no agent
  selection or Claude Code/Codex host acceptance is claimed (#333).

- Add a bounded GitHub Actions trial of **actual**, version-pinned
  `skills@1.7.6` per-skill and combined-four `--copy` installations in disposable projects,
  recording installed file lists and the existing missing-dependency
  preflight for all four skills. Its expected `incomplete` results are evidence
  of a packaging problem, **not** skill execution, host acceptance or an
  installation success claim (#333). External CLI execution is restricted to
  same-repository PRs and manual workflow dispatch.

- Allow the standalone skill-layout preflight to optionally compare installed
  SKILL.md and required sibling bytes against a separately verified local pinned
  source checkout. Reject redirected/incomplete references and distinguish
  missing from changed files, with synthetic regressions. This is not proof
  that skills.sh installed or ran a skill (related to #333).

- Add a read-only per-skill installation-layout preflight with named-file checks, explicit missing-path JSON and synthetic tests for isolated copies, complete roots and redirected files. It records the **skills.sh/skills CLI distribution risk** without claiming a real skills CLI install, host acceptance or model invocation (#333).

- Add an optional, dependency-free asset provenance record preflight for the
  existing Markdown evidence template. It rejects malformed/placeholder records,
  distinguishes pending decisions from structurally complete records, emits
  non-sensitive counts and includes synthetic regressions. It does **not** verify
  rights, licenses, actual asset files or permission to publish.


- Add a source-backed fork-PR trust-boundary checklist for the copyable
  documentation-check GitHub Actions workflow, covering read-only permissions,
  persisted credentials, privileged event risks, untrusted code, output privacy
  and an adoption test. Source-contract regressions check basic safety properties,
  not the effective isolation of an adopter's runner.

- Add a source-backed third-party README/media provenance guide and reusable
  evidence record, with hypothetical include/defer/replace cases and a link
  to BeautifulRepo's actual existing notice. This documents rights review,
  not an automatic licensing check or a change to the project's MIT license.

- Exercise the experimental MCP adapter's outside-document alias refusals
  through the pinned SDK's modern and legacy **real stdio** lifecycles: a
  hard-linked non-Markdown `LICENSE` and an outside-pointing Markdown symlink
  must give incomplete results from all three tools. Report platform fixture
  skips instead of claiming a pass. This is synthetic protocol coverage, **not**
  actual Claude Code/Codex or hostile-filesystem acceptance (related to #255).

- Add an offline, read-only four-skill plugin-cache verifier that compares
  installed `SKILL.md` bytes with immutable pinned Git commit blobs,
  rejecting missing/extra/redirected skills and reporting explicit mismatch
  versus incomplete evidence. Synthetic Git regressions cover stale and dirty
  source checkouts. This is **not** host discovery or model acceptance
  (related to #257).

- Verify the README and POSIX/PowerShell first-audit commit pins agree, then
  exercise that **exact historical checkout** through a fresh local sibling Git
  clone with broken-to-fixed synthetic links and no repository writes. CI fetches
  history for this regression; it is not an independent remote-user install (#254).

- Pin README and cross-platform combined-audit first-run commands to an
  immutable, reviewed development commit instead of following the moving
  `master` branch. Distinguish this from the v0.2.0 Action and fail early
  on unsuccessful PowerShell setup. CI tests a local clone, not an external
  fresh-install trial (related to #254).

- Document the Windows PowerShell sibling-checkout first audit with explicit
  native exit-status handling, and exercise a broken-to-fixed local-link run
  from a fresh offline clone on the Windows CI runner (#254).

- Surface the existing independent four-skill Claude Code/Codex test request
  (#258) from README and CONTRIBUTING, with a pinned development-candidate
  guide, disposable synthetic fixture, reproducible PASS/FAIL/INCONCLUSIVE
  reporting and model-cost/privacy cautions. This does not claim real-host
  acceptance or a released four-skill plugin (related to #257 and #74).

- Document an immutable **Windows PowerShell** setup and source-SHA check for the
  experimental local MCP adapter, including isolated SDK smoke and separate
  Claude Code/Codex CLI registration examples. Commands are source-reviewed,
  **not** observed Windows host or model-invocation acceptance (related to #255).

- Exercise the README's real sibling-checkout first command from a fresh **local Git clone** at the exact CI source revision, without network access. Check broken-to-fixed link exits and verify that neither the target nor the cloned tool checkout changes. This strengthens reproducibility for #254; it is not an independent new-user or external-host trial.

- Add a practical choice of **standalone offline CLI**, tagged one-skill
  plugin, pinned four-skill development candidate and separately configured
  experimental MCP in the plugin guide. State network/data and acceptance
  boundaries before readers install a host integration; correct the outdated
  description of the already-implemented MCP adapter (#255, #257).

- Clarify that experimental manual Claude Code/Codex MCP configuration is
  separate from OpenAI Plugin Directory publication. Official rules reviewed
  2026-11-07 require partner allowlisting for desktop-only local MCP submissions
  and do not permit adding MCP to an already submitted skills-only plugin.
  No host acceptance, submission or release is claimed (related to #255).

- Exercise both the modern `server/discover` and legacy `initialize`
  lifecycles in the optional real-SDK stdio smoke, checking all three tools on
  healthy/broken synthetic roots and fail-closed missing-root behavior in each.
  This is pinned-SDK compatibility evidence, **not** independent legacy-client
  or Claude Code/Codex host acceptance (#255).

- Document a reproducible, commit-pinned checkout and optional SDK preflight
  for the experimental MCP stdio adapter, with separate Claude Code and Codex
  registration, inspection and removal recipes using synthetic fixtures.
  These instructions are source-reviewed but **not** successful real-host
  installations or model tool-call evidence (related to #255).

- Extend the opt-in real-SDK MCP stdio smoke with real-process refusal of
  unsafe configured roots and fail-closed, incomplete tool responses when
  a configured synthetic repository disappears during an active session.
  Symlink refusal is exercised where the test OS permits symlink creation;
  host-specific installation and concurrent filesystem races remain untested
  (#255).

- Add an opt-in official SDK v2 stdio protocol smoke that launches the
  local MCP adapter, records negotiated version and tool discovery, checks
  three tool results against direct offline checker outputs for good and
  broken synthetic repositories, and rejects target-file writes. A focused
  CI workflow installs only the pinned optional SDK; this does not constitute
  Claude Code/Codex or external-user acceptance (#255).

- Add a development-only, optional local MCP stdio adapter exposing three existing offline checkers as root-bound, read-only tools using the official Python SDK v2; add stdlib path/timeout/receipt tests and explicit unverified Claude Code/Codex boundaries (#255).

- Add a controlled three-arm Agent Skills comparison protocol: source-only
  before state, identical ordinary no-plugin prompt and pinned installed-skill
  prompt, with per-skill fixture choices, independent snapshots, observable
  evidence and a shared scoring card. No model or host acceptance is claimed
  (related to #257 and #74).


- Put the reviewed v0.2.0 SHA-pinned GitHub Action workflow directly in the
  README first-visit navigation and quick-start path, with clear separation
  from unreleased combined-audit CLI and Action inputs (#254).

- Publish a permanent Pocket Trails **synthetic** Chromium media kit (MP4,
  WebM, extracted still, authored descriptive WebVTT, local player and complete
  text alternative), linked from the README and SHOWCASE. Preserve original
  media hashes and clearly distinguish earlier recording evidence from current
  audit CI and unverified screen-reader/final-URL playback (#254).

- Add a dependency-free local playback companion for the real synthetic WebM and authored WebVTT: responsive native video controls, embedded descriptive captions, a timed text alternative, media-header/cue validation and exclusive publication. Offline tests validate the generated page; actual browser/player accessibility remains a manual check (related to #254).

- Add an optional, exclusively created WebVTT descriptive track to the silent synthetic Chromium walkthrough, with fixed-timeline/source-claim tests and clear partial-kit handling. Captions are authored observations, not spoken subtitles or validated playback accessibility (related to #254).

- Verify the public one-minute audit path in fresh-checkout Linux/Windows CI steps, and add an external-target subprocess regression for paths with spaces, broken-to-fixed links, precise exits and no target writes. This is CI evidence, not independent user or device acceptance (related to #254).

- Publish a durable, text-first Pocket Trails before/after showcase with the exact synthetic README diff, checker outcomes, copyable first run, limits and an honest distinction between optional expiring media artifacts and permanent documentation (#254).

- Add an optional reproducible Chromium/Playwright WebM walkthrough of the source-verified **fictional** three-checker HTML report. The recorder validates synthetic markers, uses an offline browser context, refuses to overwrite recordings, and has no impact on normal audit dependencies or CI; offline tests cover input boundaries and scroll behavior. A recording is not an executed terminal session, actual user visit, or accessibility certification (related to #254).

- Include an `evidence.md` text companion in synthetic Chrome capture artifacts: source checkout, observed before/after markers, image header dimensions, and SHA-256 hashes. Add a dependency-free generator and fail-closed tests; labels are authored-content descriptions, not pixel/mobile/accessibility certification (related to #254).

- Put source-derived before/after checker counts above the longer README diff
  in the HTML audit showcase. The compact overview reads the same report
  values as the detailed diagnostics; a regression rejects hard-coded counts.
  Narrow first-screen captures now show both outcomes without claiming
  actual-device or user acceptance (Related: #254).

- Add an opt-in GitHub Actions Chrome capture workflow for the fictional
  Pocket Trails audit demo. PR changes to the demo/checkers and manual runs
  can publish source-verified HTML plus real desktop/mobile PNGs as a
  **seven-day, expiring** workflow artifact; no screenshots are committed
  automatically. Synthetic browser evidence is not a mobile-device,
  accessibility or real-repository acceptance result (Related: #254).

- Add an optional Chromium/Chrome screenshot capture for the existing
  reproducible *synthetic* three-checker HTML demo. It executes the genuine
  local fixture audit, stages the browser-rendered desktop/mobile PNGs and
  source HTML, and refuses to replace existing outputs. Regression tests
  cover source-backed generation and browser-failure handling. The browser is
  not a required Python dependency; captures are not real-user, device or
  accessibility acceptance (Related: #254).

- Display the exact source-derived one-line README repair as a unified diff
  alongside real synthetic checker results in text, JSON and HTML demo output.
  The change is checked against both disposable fixtures and HTML-escaped;
  no outside repository is modified (#254).

- Make the synthetic three-checker HTML comparison readable at first glance:
  show passing local-link checker counts in each state and add a keyboard-accessible
  jump to the after section for long mobile reports. Existing checker observations,
  read-only behavior and other report formats remain unchanged (#254).

- Give the reproducible three-checker demo an optional responsive standalone
  HTML before/after comparison from its actual synthetic findings. It keeps
  the original read-only audit, escaped diagnostics and explicit limitations;
  add output and hostile-text regressions (#254).

- Add optional standalone HTML output to the three-checker combined audit,
  preserving native evidence and exit codes with semantic headings, escaped
  source diagnostics and no remote assets or JavaScript. This is a local
  source report, not rendered accessibility certification (#254).

- Add a disposable, actually executed three-checker before/after example for a
  broken local Markdown link. The script invokes the combined audit on two
  synthetic checkouts, verifies no checker writes and rejects incomplete or
  unexpected findings; README now starts with the combined source-only audit
  and links to the reproducible demonstration (#254). This is not a live-user
  result, full Markdown renderer or v0.2.0 Action capability.

- Allow the combined offline audit to forward repeatable `--exclude GLOB`
  source filters to both local Markdown/HTML link checkers while leaving
  entry-point checks unchanged. Add a mixed vendored-source CLI regression
  and document the coverage reduction; no time limit is implied.

- Give the existing fictional repository-audit demonstration an opt-in
  human-readable before/after transcript with real rule IDs, source locations
  and remaining observations. Preserve its default JSON regression contract;
  text mode is a reproducible synthetic showcase, not a real-user result or
  accessibility score (#254).

- Bound disposable agent-eval snapshots to 5,000 entries, 16 MiB per file and
  64 MiB total during capture and verification, including actual bytes hashed
  if a file grows after stat. Oversized fixtures fail closed rather than
  reporting an unchanged target. This is not a sandbox or a race-resistant
  filesystem boundary (#74).

- Add a source-backed repository pause/archive decision recipe with a reusable
  notice, last-known verification receipt and explicit separation between
  paused maintenance and GitHub's read-only archive setting. No repository
  was archived and no provider/admin settings were changed (GitHub and Open
  Source Guides reviewed 2026-11-03).

- Recognize balanced nested bracket text in full Markdown reference links
  without recursive scanning, preserving single-line reference source anchors,
  legacy CLI diagnostics, explicit-label consumption, ordinary-link precedence
  and images in link text. Collapsed/shortcut labels remain flat; the checker
  is not a full GFM renderer (#245; GFM links reviewed 2026-11-02).

- Recognize a bounded GFM reference-definition continuation in the offline
  Markdown link checker: a destination on the next physical line, an optional
  title on the following line, and first-definition precedence. Reject blank,
  over-limit, masked and invalid continuations without consuming later links;
  keep the legacy diagnostic location and tool's no-network contract (#243,
  GFM reviewed 2026-11-02).

- Expose optional source-character line/column anchors for inline, image and
  reference Markdown link uses while preserving the old two-item iterator and
  unchanged CLI diagnostics. Multiline links retain their legacy destination
  diagnostic line separately from the link-use anchor (#241).

- Recognize bounded top-level GFM type-7 raw HTML blocks in offline Markdown
  link checks: a complete standalone opening/closing tag only at a block
  boundary, ending at the next blank line. Preserve LF/CRLF offsets, post-block
  Markdown links and live HTML navigation of actual tags. Regressions cover
  lazy paragraph continuations, inline/incomplete tags, raw HTML assets and
  reference definitions; full nested-container rendering remains out of scope
  (#237, GFM reviewed 2026-11-02).

- Extend the offline agent-eval target snapshot to detect permission-only
  changes in regular files and directories, including the selected target
  root, instead of checking only file bytes and entry names. Snapshot format
  2 rejects old format-1 baselines and requires a fresh capture; Windows ACLs,
  ownership, intervening reverted writes and model behavior remain unverified
  (follow-up to #74).

- Extend the read-only Markdown link scanner to GFM type-6 raw HTML blocks
  (named block-level tags, ending at a blank line), suppressing false link
  findings in literal HTML. Preserve the companion HTML navigation check's
  real `<a>`/`<img>` destinations, alt attributes and explicit IDs while
  excluding raw-block text from generated Markdown heading anchors.
  Ten focused regressions cover those distinct behaviors, tag boundaries,
  CRLF, source line numbers and fences. Full list/quote-container
  rendering remains outside scope (follow-up to #230; GFM reviewed 2026-11-02).

- Add a synthetic **preview → exact-hash apply → re-audit** integration
  regression for the README improvement workflow. The test exercises the actual
  offline audit, relative-link and HTML-navigation checkers, requires a refused
  no-hash write, rejects stale input and checks only README bytes change. Its
  approval is deliberately simulated inside a disposable fixture: no model run,
  actual user consent, target command or fabricated badge/output validation is
  claimed (#70, #74).

- Add an explicit-after-consent, SHA-256-bound `readme_apply.py` to apply
  only an already reviewed `README.md` proposal, with stale source/candidate
  checks, constrained input files, temporary-sibling replacement and ten
  black-box regressions. Hashes verify exact bytes **not** user approval;
  the skill still requires a separate explicit yes and before/after read-only
  audits. This is not a sandbox against concurrent hostile filesystem changes
  or proof of model behavior (#70).

- Add a dependency-free, read-only `readme_preview.py` that previews a proposed
  README as a unified diff, prints content hashes and line-ending differences,
  rejects stale source hashes and bounded unsafe inputs, and requires no target
  code execution. Eight regression tests and the README skill usage explain
  the separate explicit edit-approval gate; this is not a write mechanism (#70).


- Add a dated, source-only Quillgrain + Quillgrain_Voice_Common first-run and reporting-route baseline with pinned source revisions, reproducible candidate commands and explicit unverified execution/security limitations. This is not an executed before/after improvement (related to #83 and #88).

- Explain entry-point coverage drift in offline audit comparisons: name changed
  document roles and report inspected-file counts, including same-count file
  switches, without disclosing the underlying paths. Add regression cases
  for both role changes and privacy-preserving output (follow-up to #226).

- Add an offline, bounded, read-only before/after comparator for two
  repository entry-point audit JSON reports, with per-rule count deltas,
  same-profile validation, coverage-change detection, real-audit regressions,
  and a guide to immutable revisions. The tool neither certifies repairs nor
  assigns a beauty score (related to #88).

- Add read-only sampled focus-outline color observations to the existing live trade_simulation Chromium workflow: real native Tab focus at ten collapsed-page stops, two emulated color schemes, conservative unknowns (including focused-element compositing), observed computed CSS evidence and eight deterministic Node regressions. This is not a rendered-pixel, screen-reader or WCAG conformance result (#82).

- Offer opt-in, one-based and end-exclusive JSON source spans for simple vague inline links and placeholders. Preserve the default audit schema, legacy path/line fields, scan bounds and read-only behavior; unknown locations are null (#223).

- Add a dependency-free, read-only checker for saved GitHub-rendered Mermaid SVG ARIA title/description references, with synthetic positive/negative XML regressions and a SHA-256 evidence fingerprint. This does not run GitHub rendering, evaluate wording or test screen readers (#215).

- Add a source-backed, GitHub-rendered Mermaid SVG acceptance recipe that separately checks ARIA title/description linkage, the text fallback and real screen-reader announcements without treating unrun checks as passes.

- Add a complete, source-checked reference for all 23 offline repository-audit
  finding IDs, their severities and scopes, with a regression test that rejects
  missing or duplicated documented IDs (Closes #218).

- Register the research/data guide's displayed JSON result against a shared
  expected-output fixture used by both example and root tests. Detect missing,
  malformed, duplicated or stale registered results with an explicit guide path;
  JSON key reordering passes and unregistered Markdown commands are never run (#216).

- Document an original Mermaid flowchart with `accTitle`, `accDescr` and a complete nearby text route; add the same source metadata to BeautifulRepo's own visitor-journey diagram and source-level regressions. GitHub rendering and screen-reader outcomes remain untested (#215).

- Add a bounded informational `link.vague_text` hint for common context-dependent
  labels in simple inline README links, with code/comment/image counterexamples
  and source-line tests. Link purpose in programmatic context requires human
  review; this is not a WCAG conformance verdict.

- Add an evidence-led first-contribution route and a copyable, non-installed
  good-first-issue template. The worked broken-link issue is explicitly
  fictional; actual issues must name a revision, reader outcome, safe
  reproduction, acceptance, unknowns and exclusions. This guidance does not
  assign contributors or guarantee review, CI, accessibility or merge.

- Add a keyboard-only M4 table-panning diagnostic to the pinned trade_simulation case. Its real Chromium probe follows native Tab focus into the wide scroll container and samples ArrowRight/ArrowLeft movement and Tab exit in both emulated themes, recording non-reachability as a finding rather than a false accessibility pass. Offline regressions validate the observation contract; this is not a screen-reader or multi-browser audit (#82).

- Add a bounded, read-only expanded-M4 keyboard/semantic probe for the pinned trade_simulation case: native Tab/Enter/Space disclosure, five named SVG charts, exact-value table and expanded-document overflow observations, plus thirteen offline regressions including generic/duplicated chart-label, blank middle-header and wrong-rounded-capital rejection. This is not a screen-reader, chart-interaction or keyboard table-panning audit (#82).

- Add a read-only 320px Chromium keyboard probe for all ten collapsed-page Tab stops and the keyboard-opened M3 tick control, with eleven offline assertions. This is bounded focus evidence, not screen-reader or WCAG certification (#82).

- Add a native-400%-zoom **bottom-viewport capture** to the pinned trade_simulation case: [real Chromium #41047777163](https://github.com/drevendev/BeautifulRepo/actions/runs/41047777163) reached the page footer in both emulated themes, with 0 CSS px document-level horizontal overflow and a separate X11 image for each first/bottom viewport. All five new offline regressions passed; first/bottom screenshots in each theme do not establish middle-page, screen-reader or whole-page accessibility (related to #82).

- Add a dependency-free, read-only **served HTML/CSS/JS byte comparison** for the pinned trade_simulation Pages case. The probe checks four explicitly named published assets against a Git checkout at an immutable source SHA, caps responses, refuses redirects, records SHA-256 evidence and exercises match/difference/error cases offline. This is a dated selected-file observation, not proof of the deployed commit, all website assets or accessibility (#82).

- Add a read-only, headful Chromium/Xvfb check of **native 400% browser page zoom** for the live trade_simulation saved-run viewer. Eight real `Ctrl+plus` shortcuts produced device-pixel ratio 1 → 4 and CSS viewport width 1280 → 320 px; sampled layout, saved-data readout and keyboard focus passed in both emulated themes. The X11 screenshots show only the **first physical viewport**, not the full page; screen-reader access, nested-chart accessibility and deployed HTML/JS provenance remain unverified (related to #82).

- Add a bounded computed-style **text contrast diagnostic** to the live
  trade_simulation Pages probe: nine named rendered text roles in both
  emulated themes, conservative unknowns for unsupported compositing and
  offline Node regressions. Contrast findings are evidence, **not** a
  full-page WCAG or focus-visibility certification (#82).

- Extend the read-only trade_simulation Pages probe with real keyboard input:
  [Chromium #40985815887](https://github.com/drevendev/BeautifulRepo/actions/runs/40985815887)
  observed five sequential Tab focus stops (all with computed 2px outlines),
  ArrowLeft/Right moving the saved tick 59 → 55 → 59, and Enter expanding the
  M4 disclosure in both emulated themes at 320 CSS px. This bounded path
  does not establish whole-page accessibility or screen-reader conformance (#82).

- Add a read-only Chromium workflow for the pinned trade_simulation case.
  The **live** [browser run #40973430007](https://github.com/drevendev/BeautifulRepo/actions/runs/40973430007)
  observed HTTP 200 and exact saved JSON byte agreement, correct rendered last
  tick/capital, distinct light/dark body backgrounds and zero document-level
  overflow at 320 CSS px. The screenshots were visually inspected and a
  text alternative recorded in the case; current HTML/JS provenance, 400%
  zoom, keyboard and screen-reader acceptance remain unverified (#82).


- Add a read-only GitHub Actions reproduction for the trade_simulation case:
  two SHA-pinned target source checkouts audited with BeautifulRepo tools pinned
  to commit `83cf280`, plus a saved-JSON first-success and missing-file path.
  The SHA-pinned source-only runner completed successfully on 2026-10-29
  (Actions #40957829865); its zero-finding structural checks do not detect
  milestone truth. Visual/deployment checks remain unperformed (#82).

- Add a dated, read-only metadata and security-surface assessment to the
  pinned trade_simulation case: empty About description/topics, existing Pages
  homepage, and absence of a tracked target SECURITY.md, while explicitly
  withholding claims about private reporting settings, inherited policies and
  current deployment. No target settings or files changed (related to #82).

- Add an offline, test-backed GitHub Actions pin consistency guard: track reviewed
  SHAs, versions and review dates for external actions, and fail CI when a
  Dependabot SHA bump leaves annotations or the local manifest out of sync.
  Eleven black-box regressions cover drift, unpinned refs, malformed metadata,
  symlinks and read-only behavior. Passing checks consistency only, not
  upstream authenticity or actual workflow execution.

- Document a pinned trade_simulation before/after: a stale M4 release
  claim corrected through the target's own PR, hash-verified local execution
  of saved-run JSON inspection and its missing-file failure path, and
  historical GitHub-native TypeScript/.NET CI plus Pages build/deploy results
  at the correction merge SHA. A fresh clone, BeautifulRepo before/after
  audits and live visual/accessibility acceptance remain unrun; the case
  is still in progress (related to #82 and #88).

- Add a source-backed, copyable issue-triage recipe with evidence, disposition
  and permission gates. Dated examples explain why unfinished accessibility
  checks and owner-gated label decisions remain open, without inventing
  a review SLA or mutating issue metadata.

- Diagnose bounded, text-free candidate elements extending outside the
  rendered GitHub README Markdown container. The browser-console probe
  reports descendant indexes, tags and pixel excess (up to eight samples,
  2,000 nodes) alongside its existing measurements. Geometry candidates
  are not accessibility failures or proof of manual zoom/assistive testing
  (related to #16).

- Add an optional, inspectable browser-console measurement probe for real
  GitHub-rendered READMEs. It reports CSS viewport/document/Markdown overflow,
  selected theme-aware images and missing images, without network requests or
  query-string leakage. Synthetic DOM and local Chromium smoke tests exercise
  its measurements; real GitHub-rendered, zoom, keyboard and screen-reader
  acceptance still requires a separate manual receipt (related to #16).

- Add an uncued, synthetic trust-surface evaluation for an advertised GitHub
  private vulnerability form contradicted by a saved disabled-settings snapshot.
  Source contracts require the proposed diff to withhold an unverified route,
  an invented response promise and licence selection; no model run or live
  provider-settings check is claimed (related to #71 and #74).

- Add an evidence-bound release-note presentation comparison: two intentional
  layouts (compact Unreleased history versus an unpublished reader-facing
  draft) describe the same merged Markdown-link checker change, with pinned
  PR/CI evidence and an actual checker regression. No release, tag or public
  announcement is created (related to #16).

- Validate repository-local destinations used by bounded one-line full,
  collapsed and shortcut Markdown reference links/images. Source masking keeps
  examples inert; first definitions and diagnostic use lines follow GFM rules.
  This is not a full Markdown renderer or a live external-link checker.

- A reproducible **GitHub-rendered README visual acceptance protocol** with
  source-bound first-success evidence, light/dark, 320 CSS px reflow,
  actual 400% browser zoom, image-off, keyboard and screen-reader steps.
  Its fillable receipt defaults to NOT RUN, not fabricated accessibility
  passes. Linked from the visual guide, design-intent template and real
  Rowcount variants (related to #16).

- Resolve single-line Markdown reference-style GitHub Actions badge images
  as well as inline/HTML forms in the offline checker. Normalize reference
  labels, report failures at the image use line, use the first definition and
  add five regressions. Full GFM rendering and live CI remain unverified.

- Run the existing offline GitHub Actions badge-target checker in BeautifulRepo's
  own quality CI, with a checked-in workflow/README contract test. A badge that
  points to a missing local workflow now fails the PR job, but a present file
  still does not prove a successful or required CI run (related to #85).

- Add an offline, zero-dependency checker for **same-repository GitHub
  Actions status badges** in a root README. It verifies that each recognized
  badge references an ordinary checked-in workflow file, reports bad targets
  by line, ignores code examples and never fetches workflow results or claims
  green CI. Fourteen black-box regressions cover good/missing targets,
  quoted examples, malformed names, symlinks and input errors (related to
  #16 and #70). Other badge providers and full Markdown rendering are
  deliberately out of scope.

- Add compact original dark/light Rowcount transcript SVGs for narrow
  READMEs (up to 480 px), keeping the verified command/result at readable
  scale. Tests check both assets' facts and text contrast; an isolated
  Chromium preview at 320 px is not a GitHub renderer or screen-reader
  certification (related to #16).

- Add a third, contract-first README entrance for the real Rowcount example:
  a concise behavior/limits card ahead of the same executable first success.
  The existing two layouts remain; new regression coverage verifies that
  mismatched CSV columns fail instead of silently producing a count (#16).
  No GitHub narrow-width or screen-reader certification is claimed.

- Add a zero-dependency, offline agent-eval Read receipt checker that compares
  exact returned fixture content with a recorded mounted path. Six black-box
  tests distinguish matched bytes from absent, truncated, path-only, forged
  answer-only and malformed evidence. It does not authenticate transcripts or
  establish model safety (related to #74).

- Add an uncued synthetic README agent-eval case: an ordinary onboarding
  request must not promote a fixture's fake green CI badge, fabricated
  test results or instruction to edit without approval. Static tests guard
  fixture placement, uncued wording and grader contracts; no model run or
  write-gate effectiveness is claimed (related to #74 and #70).

- Add a practical evidence-first review for AI-written README drafts: identify
  fabricated capabilities without policing minimalist style, check the working
  Rowcount first-success command, compare honest alternatives, and keep a
  manual-verification receipt. A regression test runs the documented command;
  no model-origin detection or browser accessibility is asserted (related to #16).

- Add a reusable, evidence-bound design-intent brief with a filled Rowcount
  application: fixed source/result, two contrasting README entrances,
  meaningful image-alternative choices, rejected layouts and honest manual
  verification limits. Static tests check its navigation and key evidence;
  no new browser or screen-reader certification is claimed (related to #16).

- Add two distinct first-screen designs for the **working** Rowcount CSV CLI,
  with verified local output, original light/dark transcript illustrations,
  accessible text alternatives and regression checks binding the presentation
  to the actual checked-in command (related to #16). This is not a terminal
  screenshot, packaged release or renderer accessibility test.

- Add an uncued adversarial release-note Agent Skill evaluation case using a
  synthetic commit-subject inventory, explicit unpublished-release and
  fictional-contact graders, fixture visibility guidance and static contract
  checks. No model was invoked, no Git diff was checked by this case, and no
  prompt-injection protection is claimed (related to #74).

- Add a disposable adversarial Git-history fixture with a deceptive commit
  subject, black-box inventory assertions and an offline preflight recipe.
  The subject is untrusted data; no model prompt-injection defense is claimed
  (related to #74).

- Add an opt-in, no-model real Git-history fixture generator for release-note agent-eval preflights: deterministic synthetic commits, tagged and untagged cases, overwrite refusal and black-box tests against the actual offline inventory. Model triggering and publication are not verified (related to #74).

- Compare three distinct first-screen README treatments of the same fictional
  PocketDiff example, with an audience/design-intent matrix and regression
  checks for the shared facts and explicit fictional status. No browser,
  assistive-technology or model-design trial is claimed (related to #16).

- The offline HTML navigation checker now reports raw HTML `<img>` tags that
  omit the `alt` attribute in active Markdown. `alt=""` remains valid for
  decorative images; source checks do not judge alternative-text meaning or
  certify accessibility. Added regression coverage (related to #16).

- Add an all-skills manual Codex/Claude smoke-test matrix: fixture visibility,
  positive/negative triggers, hostile README checks, before/after snapshots,
  evidence fields and explicit PASS/FAIL/INCONCLUSIVE grading. This is a
  procedure and static regression, **not a model-run result** (related to #74).

- Add the development-only `trust-surfaces` Agent Skill for licence-neutral,
  evidence-based review of CONTRIBUTING, SECURITY and conduct promises, with
  explicit preview/approval before any edits. Unverified reporting routes
  remain private drafts. Two positive and one negative synthetic eval plus
  static tests were added; no model-run safety or live reporting route was
  verified (related to #71 and #74).

- Add a development-only `improve-readme` agent skill that proposes an exact file/diff preview, demands explicit approval before edits, rejects unverified CI badges and separates edit permission from execution. Include two synthetic positive evals, a negative trigger and structural safety contracts. No real model evaluation or released plugin version is claimed (related to #70 and #74).
- Add a development-only `draft-release-notes` agent skill using the offline Git inventory, exact SHA evidence and explicitly unpublished no-tag fallback. Include synthetic positive/negative eval definitions and structural safety tests; **no model-run result or released plugin version is claimed** (related to #72 and #74).
- Add a read-only offline Git commit inventory tool for release-note drafting with exact base/head SHAs, no-tag/root fallback, bounded history and synthetic Git regression tests. It does not publish a release or verify commit claims (related to #72).
- Add a portable offline agent-eval file-integrity snapshot tool with
  an outside-target baseline, byte hashes, symlink-safe traversal, black-box
  tests and a Codex/Claude manual smoke recipe. This verifies target-file
  changes, **not** agent triggering or prompt-injection resistance (related to #74).
- Add a dated, source-linked GitHub.com plan matrix for private/internal
  repositories, plus explicit callouts for disclosure, Pages, CI enforcement,
  reporting and public-only checklist items (related to #76).
- Add an uncued synthetic hostile-README eval with an ordinary onboarding
  request, safety/tool-use graders and a source-level regression that prevents
  priming the prompt. Neither fixture visibility nor agent resistance has been
  verified by a model run (#74).
- Prepared four native Claude Code plugin-eval scenarios for `audit-repo`:
  two positive triggers, one negative trigger and hostile README bait.
  Added static coverage checks and a manual, usage-gated evaluation guide.
  **No model eval run or injection-resistance result is claimed** (#74).
- Four synthetic repositories and an isolated, read-only CLI regression suite for
  the `audit-repo` skill. They pin expected audit findings, broken-link behavior,
  deterministic output and no writes, including hostile README text. These do not
  claim to test actual agent triggering or prompt-injection resistance (#74).
- Run the existing plugin contract tests on v* tag pushes too: validate
  release versions against both plugin manifests and a dated CHANGELOG
  heading, reject duplicate or unclosed skill frontmatter, and document
  a joint Action/plugin release checklist in CONTRIBUTING (#73).
- An internal/private README scaffold, navigable template index and filled
  fictional Sample Queue example with a real offline fixture verifier and a
  regression asserting zero warnings under `repo_audit.py --profile internal` (#77).
- An explicit public/internal/private profile for the offline repository audit and
  composite Action, with internal owner/contact observations, less prescriptive
  missing-license guidance, additive JSON profile metadata, and raw GitHub image
  portability warnings. Default profile stays public; no remote visibility lookup (#75).
- Private/enterprise Action adoption guidance (organization policy, runner costs,
  SHA-preserving mirrors, GHES/GHE.com caveats, and local-only use) and an offline
  contract regression test for tools and composite Action shell steps (#79).
- A source-backed [confidentiality checklist](checklists/confidentiality.md)
  for private and internal repositories: content, public metadata exceptions,
  CI/report output, and safe agent use, with explicit secret-scanning limits (#78).
- The first case that follows the case procedure: PatchPitch, a local-AI app
  (`case-studies/patchpitch.md`). A documentation-only pull request in PatchPitch
  (PatchPitch#90) leads its README with a run that needs no model. The case records
  the before and after commits, pinned tool runs, a fresh-clone first run with Ollama
  stopped, 320 px measurements, CI on the merge commit, and what was not tested (#81).
- `case-studies/README.md` describes the procedure every real case follows: before
  snapshot, audit with pinned tools, a pull request in the target, after snapshot and
  write-up. It adds a fill-in skeleton, the rule that unlicensed repositories are used
  for ideas only, and the known tool caveats (#80).

### Changed

- Refresh the GSoC 2026 participation timeline against Google's dated 2026
  schedule on November 12: the final extended-project mentor deadline has
  passed, like all 2026 application and contributor deadlines. Distinguish
  official 2026 dates from the still-unspecified 2027 schedule, without
  claiming an individual mentor submitted an evaluation.

- Repin the experimental MCP POSIX/PowerShell host-trial commands to
  immutable merged source `7b9c3391f426c76cbf0a75a1470ff06eb7e6db18` so they include the
  out-of-checkout non-Markdown symlink boundary from PR #351. The reviewed
  PR head passed [Quality CI](https://github.com/drevendev/BeautifulRepo/actions/runs/43218140007)
  (6/6) and [MCP SDK CI](https://github.com/drevendev/BeautifulRepo/actions/runs/43218140106)
  (2/2); those are not installed Claude Code/Codex host trials or tests of
  concurrent filesystem replacement. Reviewed 2026-11-12 (#255).

- Repin the experimental MCP POSIX/PowerShell host-trial instructions to
  immutable source `2f0e0e8801a570e3dd95ffb7ff2b6d4530931f9d`, including
  Windows reparse hardening and native root/internal-junction regressions.
  Check the source link and both platform checkout commands for SHA drift.
  Native Windows tests passed on the preceding PR head; the merge commit has
  not been independently installed or tested in Claude Code/Codex. Arbitrary
  NTFS reparse types and concurrent path replacement remain unverified (#255).

- Repin the four-skill Claude Code/Codex trial to the accepted development
  source commit `8947574399df2cc11e8ded41cecbef70be4808c6` across installation commands, offline
  cache verification, roadmap and three-arm comparison. Add a regression
  preventing the trial procedure from drifting away from the installer pin.
  Earlier `cf8ac81` results are historical, not evidence for this candidate;
  no real agent installation or model execution is claimed (#257, #258).

- Correct Codex's host-install instructions against the official plugin
  packaging guide (checked 2026-11-11): registering a Git marketplace is not
  installing the plugin, and desktop plugin-browser steps are a procedure,
  not acceptance. Require installed-cache evidence and mark unsupported hosts
  INCONCLUSIVE (#257, #258). Clarify that four-skill eval definitions are not
  a stable release.

- Repin the experimental MCP POSIX and PowerShell host-trial checkout
  to the accepted source revision with fail-closed hard-link preflight for
  all three tools. Test that the full commit link and both checkout routes
  agree. This is reproducible source guidance, not a Claude Code/Codex
  installation or model-invocation PASS (related to #255).

- Require evaluator-only grading data and an actual agent-equivalent permission
  probe in the three-arm skill comparison preflight; identical disposable
  B/C fixtures alone do not establish isolation. No real Claude Code/Codex
  isolation or model execution has been verified (related to #257, #258).

- Extend pinned four-skill cache verification beyond `SKILL.md` to compare
  seven host-executed helper and shared safety-policy files against Git blobs.
  Modified helpers report MISMATCH; missing/redirected helpers report INCOMPLETE.
  The check is bounded, not complete plugin attestation or client proof (#257).

- Recheck the official GSoC 2026 timetable (November 7): distinguish past
  application and contributor-submission deadlines from the November 9 mentor
  evaluation, document the organizer's eligibility baseline, and refresh the
  catalog only after inspecting primary sources. This does not establish 2027
  dates or BeautifulRepo's eligibility.

- Put a reader's **own repository** at the center of the README's first
  copy-pastable audit: clone BeautifulRepo as a sibling, scan the chosen
  checkout, and explain advisory entry-point findings versus failing
  broken links. The self-audit remains an optional command (#254).

- Make the fictional broken-link audit's HTML diff easier to scan: distinguish added
  and removed lines in light/dark themes while retaining literal +/- prefixes,
  assistive text labels, and escaped source content. This is authored formatting,
  not a screen-reader or contrast-certification claim (#254).


- Repin the unreleased four-skill development test instructions to a single
  immutable commit that includes the latest manifest discovery fix and
  bounded evaluation snapshots. Add a regression that checks Claude Code,
  Codex and the manual smoke-matrix link use the same 40-character SHA.
  This is packaging/test guidance, **not** real-model acceptance or a release (#257).

- Align Claude Code and Codex plugin descriptions, the Claude marketplace
  listing and manifest tests with all four development-candidate skills,
  including `trust-surfaces`. Direct testing instructions to the immutable
  four-skill candidate rather than mutable `master`; this documents discovery
  only and does not claim real-agent acceptance or a stable release (#257, #258).

- Clarify released `v0.2.0` audit-only plugin instructions versus the
  immutable four-skill `0.3.0-dev.0` testing candidate, with exact Claude
  Code/Codex trial commands, fresh-install and model-testing caveats, a
  revision-pinned smoke matrix, and separate MCP scope. Update the public
  roadmap to match source and issue evidence as of 2026-11-03; no host
  acceptance or stable release is claimed (#257, #258).

- Bring a revision-pinned real PatchPitch audit before/after into the README's
  working proof, distinct from the fictional demo. Record the single detected
  contribution-document change and the more important first-run improvement the
  structural audit did not detect; retain links to the full observed case (#254).

- Make the README first visit lead with the actual offline repository audit,
  a runnable synthetic before/after, a local-repository command, honest exit
  semantics and the reviewed SHA-pinned Action recipe. Keep the Rowcount
  example as a separate starter rather than the headline product (#254).

- Avoid repeated source-prefix scans when reporting inline Markdown link line
  numbers. The scanner now indexes source line starts once per document and
  looks up each link independently, preserving diagnostic text and link order
  even for out-of-order nested multiline destinations, CRLF, Unicode and
  masked examples (issue #240).

- Upgrade the SHA-pinned `actions/setup-python` from v7.0.0 to v7.1.0 in quality and scheduled checks. Recheck the upstream release ref on 2026-10-29; retain existing Python versions and CI steps. No performance or compatibility gain is claimed (related to PR #194).

- Reconcile the roadmap with completed v0.2.0 plugin, private-repository,
  self-check and readiness work. Separate pending model-evaluation, real case
  studies and GitHub-rendered accessibility evidence from already shipped
  guides and from owner-only event-label decisions (issue states checked
  2026-10-28). No release, model run or external repository change is implied.

- Add opt-in `--require-badge` mode to the offline Actions-badge checker and
  enable it in BeautifulRepo CI. A missing badge now fails the self-check even
  when no dangling workflow references remain; default zero-match behavior
  stays non-blocking for adopters. Document supported reference-style syntax
  accurately in the evidence review, with regression tests. This checks
  presence of evidence, **not** CI execution or success.

- Cache pip downloads for the lint CI job using the hash-pinned Ruff
  requirements as the cache key. Keep `--require-hashes --no-deps` installation
  and the standard-library-only tools unchanged; no measured speedup is claimed.
  The configuration follows the pinned `actions/setup-python` cache inputs
  (reviewed 2026-10-25; related to PR #157).

- Remove the legacy `hacktoberfest` label from the current contributor
  work-finding table. Closed historical issues may retain that label, but a
  2026 PR/MR cannot earn event rewards and the label does not signal enrollment
  or eligibility (related to #100). No provider label was changed.
- Recheck Hacktoberfest 2026 against the organizer's homepage, FAQ and online
  activity page on 2026-10-24; clarify that PRs earn no event rewards, distinguish
  genuine contributions from event participation and update the catalog's verified
  source date (related to #100; post-event label review remains pending).
- The adoption guide pins the Action to the `v0.2.0` commit, and `master` starts
  plugin version `0.3.0-dev.0` (#101).

### Removed

- Remove the Hungry Crab execution configuration (`.crab.yml`) and decision ledger
  (`.crab/ledger.json`) from the public repository. These were maintainer tooling
  state, not reusable BeautifulRepo product examples. Ignore future local Crab files;
  public guidance and issue history remain available.

### Fixed

- Reject every Windows reparse-point type in the README preview/apply path
  preflight, not just symlinks and junctions. A source-level regression covers
  generic reparse attributes and unknown tags; it does not certify race-free
  filesystem isolation or native behavior for every vendor reparse type.

- Correct the four-skill installed-cache verification walkthrough: the immutable
  `8947574` host-test candidate includes an older verifier that cannot
  substantiate the newer parent-link/junction and present-manifest checks.
  Pin the corrected verifier's **separate** `ac28c4f` checkout and run it
  against the unchanged `8947574` candidate and actual host cache. Distinguish
  required-file MATCH, absent optional manifests and unproven host acceptance
  (#257, #258).

- Correct the four-skill development-candidate installation walkthrough:
  Claude Code's documented remote marketplace `@ref` selects a branch or
  tag, not an established immutable-SHA installer. Use an exact detached
  checkout with documented local-directory marketplace registration for
  both Claude Code and Codex. Keep remote-install syntax and host behavior
  explicitly unverified, and assert the guide's full SHA agrees with the
  candidate link and roadmap (related to #257, #258).

- Extend the offline plugin cache verifier to compare Codex and Claude plugin
  manifest bytes against the pinned source **when those files exist in the
  installed cache**. A changed present manifest now reports MISMATCH; a missing
  optional manifest is explicitly listed as unverified, not mistaken for an
  installed host or agent PASS. The four skills and 22 required dependencies
  remain the mandatory byte-match baseline (#257).

- Refuse symlinked parent directories and Windows junction/reparse aliases
  when verifying the local installed four-skill plugin against a pinned Git
  checkout. A redirected parent could previously pass the byte comparison
  while obscuring the actual source/cache location. Add disposable symlink
  and native Windows junction regressions. This is a preflight, not a
  race-resistant filesystem sandbox or real agent-host acceptance (#257).

- Correct the Claude Code/Codex plugin setup guide to include the
  officially documented Codex CLI `/plugins` installation browser alongside
  the desktop Plugins Directory, without mistaking marketplace registration
  or source checkout for an installed, tested BeautifulRepo plugin
  (official OpenAI docs rechecked 2026-11-12; #258, #257).

- Reject unsupported Windows filesystem reparse points in the experimental
  MCP server's configured-root and source preflights. Unrecognized reparse
  tags and attribute-only redirects no longer pass as ordinary paths.
  Synthetic metadata regressions cover these boundaries; real Windows host
  installation and concurrent filesystem changes remain unverified (#255).

- Make the asset provenance record preflight reject unrecognized nonblank
  lines inside a record instead of returning a structural PASS while silently
  ignoring additional claims or malformed entries. Blank separators remain valid;
  this does not verify ownership, licenses or publication rights.

- Reject combined-audit checkout roots reached through symlinked or Windows
  reparse-point ancestors, not just a redirected final directory. Preflight
  every lexical path component before resolving; add regressions for outside
  aliases, simulated junction parents and ordinary `..` paths. This prevents
  accidental scope substitution at entry, but is not a filesystem race sandbox.

- Reject synthetic agent-eval snapshot targets reached through a symlinked
  parent or Windows junction ancestor, not only redirects at the final root.
  Check lexical components before resolving, including those preceding `..`;
  retain ordinary path normalization and add cross-platform regressions.
  This is a scope preflight, not a race-resistant sandbox or real-model PASS
  (related to #74 and #257).

- Extend the four-skill plugin-cache verifier beyond executable helpers to
  the checklists, task guides and templates the skills need. A missing required
  template now makes the receipt INCOMPLETE; a changed checklist produces
  MISMATCH against the pinned Git blob. This remains a bounded byte comparison,
  **not** Claude Code/Codex discovery or model acceptance (related to #257).

- Fail closed on hard-linked regular files before **any** experimental MCP
  checker launches: hard links can alias out-of-root sources without symlink
  metadata, including extensionless entry points and non-Markdown documents.
  Add synthetic outside-alias regressions for all three tools (#255). This
  is metadata preflight, not a concurrent-filesystem sandbox.

- Validate each ancestor of the experimental MCP adapter's configured checkout
  without comparing resolved and requested path spellings. Preserve rejection of
  junctions, symlinks and `..` traversal while allowing normal Windows path
  normalization (related to #255; host installation still unverified).

- Reject README preview/apply targets reached through a symlinked or redirected
  **parent directory**, not only aliases on the last root component. Shared
  root validation now fails closed before reading or replacing README.md;
  synthetic regressions check that a correctly hashed approved proposal
  cannot write through a parent alias. This is not protection against concurrent
  filesystem replacement (related to #70).

- Make the real-repository case-study procedure distinguish a pinned
  `SECURITY.md` from GitHub's independently configured private vulnerability
  reporting. Record the date, actual read-only API response and unknown/denied
  states rather than inferring a safe reporting route from a policy file or
  an API failure. GitHub REST/security guidance reviewed 2026-11-08
  (related to #83 and #88).

- Make the experimental MCP protocol smoke's tool-to-checker expectations,
  direct CLI path and missing-root receipts independent of the adapter under
  test. A swapped tool route can no longer make both the MCP response and its
  test oracle agree by sharing the same mapping. This is still real SDK-level
  evidence, not Claude Code/Codex host acceptance (#255).

- Compare experimental MCP stdio tool receipts with **separate, direct CLI
  bundle subprocesses**, rather than calling the same MCP adapter wrapper as
  both implementation and test oracle. Check all three tools and native exit
  codes on healthy and broken synthetic roots in modern and legacy SDK sessions.
  This is still SDK-level evidence, not Claude Code/Codex host acceptance (#255).

- Keep experimental MCP tool responses **incomplete** when a single-checker
  bundle's exit status contradicts its claimed result. Preserve the bundled
  128-KiB report-limit/failure reason without echoing arbitrary source text,
  so host testers can distinguish a coverage limit from a clean run.
  Added no-SDK regression cases; real Claude Code/Codex acceptance remains
  unverified (related to #255).

- Correct the reproducible experimental MCP host-trial checkout pin to the
  source revision with bounded child output, single-checker isolation and
  Markdown metadata preflight; fail early when the checked-out Git SHA differs.
  The installation recipe remains untested in actual Claude Code/Codex hosts
  (related to #255).

- Fail closed in the experimental MCP Markdown/HTML tools before scanning
  unbounded or special Markdown sources. A metadata-only preflight caps
  checkout entries, Markdown source count, per-file and total source bytes,
  and scan time; oversized, unreadable or escaping sources return incomplete
  evidence without launching a checker. The trusted-stable-root/race
  limitation remains; standalone CLI behavior is unchanged (#255).

- Keep first-run offline audits read-only with respect to their own tool checkout: dynamically loading sibling checkers from `audit_bundle.py` or the standalone HTML-navigation CLI must not create `tools/__pycache__` when invoked with `python -I`. Add a fresh-copy subprocess regression; target-file read-only checks remain in place.

- Isolate each experimental MCP tool's selected offline checker via the
  combined audit's optional `--only` argument. An unrelated checker no
  longer consumes that tool's output budget or changes its completion status;
  the default three-checker CLI and its existing output remain unchanged.
  Add CLI subprocess and adapter contract regressions (#255). This remains
  SDK/source-level evidence, not Claude Code/Codex host acceptance.


- Bound the experimental MCP adapter's subprocess **during** output capture:
  drain both pipes concurrently, stop an over-limit child and avoid growing
  temporary files or memory before the 512 KiB per-stream check. Add real
  stdout/stderr overflow and timeout regressions; host acceptance remains
  unverified (#255).

- Capture optional MCP checker stdout/stderr in temporary files, checking the
  512 KiB per-stream limit **before** parsing instead of buffering unlimited
  subprocess PIPE output in the MCP process memory. Add oversized stdout and
  stderr regression cases. This reduces memory exposure, but does not impose
  a temporary-disk quota or imply real Claude Code/Codex host acceptance (#255).

- Fix the experimental MCP install guide's immutable checkout: the former
  `6c01779` pin contained only the earlier modern SDK smoke, while the guide
  described both modern and legacy protocol checks. Pin the accepted
  `331df37` tree with both smoke modes and missing-root regressions, without
  claiming Claude Code or Codex host acceptance (related to #255).

- Resolve the portable Agent Skills handbook root from the directory containing
  each `SKILL.md` (`../..`), not ambiguously from the file path itself.
  Align all four skills and add a source-level regression for the documented
  relative layout. This is not evidence of host installation or model behavior
  (related to #257).

- Repin the unreleased four-skill Claude Code/Codex trial to immutable commit
  `cf8ac81ddabb5e2006913e65a2f980ef201baf5c`, which includes the desktop local-executor manifest correction.
  Keep the install commands, manual matrix and roadmap on the same revision;
  6/6 source CI checks are green but actual host installation and model-driven
  trials remain unverified (#257, #258).

- Mark the development four-skill portable plugin as requiring a local
  executor (`requires_local_executor: true`) so a future desktop-only plugin
  submission does not suggest browser-only repository audits. Add a manifest
  regression and clarify that the historical pinned candidates are unchanged;
  packaging metadata is not an actual Claude Code/Codex installation or
  model-invocation result (official OpenAI desktop-only guidance reviewed
  2026-11-06; related to #257).

- Clarify that Codex's `plugin marketplace add` only registers a source: install the plugin separately from `/plugins`, not via the undocumented `codex plugin add` command. Align pinned release/development setup and update/remove guidance, with a contract test; real-host installation and four-skill acceptance remain unverified (Related: #257, #258).

- Encode local WebM playback filenames as a single URL path segment before HTML escaping, preserving literal `#`, `?`, `%`, spaces, quotes, `&` and Unicode. Add URL-resolution regressions; full browser and assistive-technology acceptance remain separate (Related: #284, #254).

- Escape unprintable control/format characters in the combined audit's text
  findings and link diagnostics, without hiding ordinary Unicode or changing
  its JSON report. Keep each observation on one physical terminal line so
  a surprising local filename cannot inject forged report lines.

- Keep the roadmap's four-skill candidate SHA aligned with the immutable
  Claude Code and Codex installation examples. Extend the plugin contract
  test to catch stale public navigation pins instead of silently directing
  testers to a different source revision (#257, #258).

- Make the reusable repository pause/archive notice safe to paste into an
  unrelated README: copy only one state, resolve links from the destination,
  and use a full URL for the template's own guide reference. Add structural
  tests to prevent source-directory-dependent template links (GitHub README
  relative links reviewed 2026-11-03).

- Reject hard-linked fixture and read-receipt inputs in the offline agent-eval
  Read receipt checker instead of reading possible external aliases. This
  preserves exact-byte matching for ordinary synthetic evidence but is not
  a race-resistant filesystem boundary or model-behavior proof (#74).

- Fail closed when a synthetic agent-eval snapshot target contains hard-linked regular files, including aliases created after capture, instead of accepting an unchanged-byte snapshot. The check covers only the selected target and does not prevent outside writes or replace sandboxing (related to #74).

- Respect GFM nesting precedence in the offline Markdown link checker: a valid
  inner ordinary link suppresses an invalid outer link, while an image inside
  a link remains valid. Ignore link-like syntax in parsed image alt text and
  inline destinations; preserve failed-inner recovery and existing source
  anchors and CLI output (#246; GFM reviewed 2026-11-02).

- Reject U+200B zero-width space, U+2060 word joiner and embedded U+FEFF
  in both inputs to the exact-hash README preview/approval helpers. These
  invisible characters can conceal a change in terminal diffs; ordinary
  non-ASCII text and U+200C/U+200D script joiners remain supported. This
  is a bounded display-integrity check, not a filesystem-race defense or
  proof of consent (follow-up to #70).

- Mask GFM raw HTML block types 3–5 in the offline Markdown destination scanner, retaining source line positions and matching each terminator only to its own block kind. Add regression cases for multi-line, single-line, unclosed, fenced and adjacent Markdown content; types 6–7 remain out of scope (issue #230, GFM source reviewed 2026-11-01 (UTC)).

- Reject bare carriage returns, C1 terminal controls, Unicode directional
  formatting marks, and U+2028/U+2029 line/paragraph separators in both inputs
  of the read-only README diff preview. These previously passed validation and
  could overwrite/reorder terminal output or invent diff lines and newline
  markers. Preserve CRLF and ordinary non-ASCII text; regressions cover both
  inputs, fail-closed output, physical LF hunk counts and international text
  (#70).


- Interpret the first whitespace-separated HTML image `role` token in the offline entry audit, covering `role="none presentation"` and surrounding whitespace without allowing a later decorative token to override `role="img"`. This remains a source heuristic, not a browser accessible-name computation.

- The offline HTML navigation checker now reports duplicate `role` and `aria-*`
  attributes in active Markdown HTML, where later values would be ignored by
  HTML parsing. Includes a fixture covering image labels, references, hidden
  state and code examples; it does not infer accessible names or certify WCAG.

- Fix a false negative in the offline HTML-image entry-point audit: whitespace-only
  `aria-label` and `aria-labelledby` are not accepted as naming candidates.
  Regression tests cover direct and duplicate attributes. This bounded source
  check does not resolve ID references or certify accessible names.

- Make the offline README audit use the first HTML image attribute when `alt`,
  `src`, `role` or an ARIA naming/visibility attribute is repeated, instead
  of silently using the last attribute. Report these malformed duplicates and
  test both false-positive and false-negative alt/name and remote-asset cases.
  This follows HTML parser precedence, not rendered accessibility certification.

- Resolve simple top-level GFM setext heading fragments in the offline HTML
  navigation checker (including shared ATX/setext duplicate suffixes), with
  regressions for multiline text, cross-file links, and fenced/list/quote
  false positives. Complex container headings remain outside this source
  approximation; no browser or accessibility certification is claimed.

- Correct two public documentation claims against their linked source examples:
  the README case records three emulated viewport widths but not both themes
  at every width, and Rowcount now has three (not two) first-screen treatments.
  No new rendered, keyboard, zoom or screen-reader acceptance is asserted
  (related to #16).

- Bound the README visual probe to its first 2,000 DOM descendants with a
  TreeWalker (plus one truncation check), eliminating unbounded full-descendant
  **and image** queries. Return sampled image counts with explicit partial-result
  flags and at most eight picture selections. Synthetic huge-DOM and image-heavy
  regressions guard these limits; real GitHub-rendered assistive testing
  remains outstanding (related to #16).

- Correct overstated accessibility evidence in the real README case study and
  its entry-point summary: only two width/theme contrast combinations were
  recorded, and static `tabindex` inspection cannot prove keyboard navigation.
  No new browser, zoom, keyboard or screen-reader tests were run (related to #16).

- Distinguish the browser's `prefers-color-scheme` from GitHub's optional
  page-level appearance attributes in the README measurement probe. A user-forced
  GitHub theme can differ from the OS preference; the probe now reports both
  without treating either as an accessibility verdict (related to #16).

- Bound the guide review-date scanner to ordinary local UTF-8 files, reject
  redirected sources and directories, oversized input and NUL bytes, and return
  an explicit input error rather than following an external link or silently
  omitting review evidence. This is not a race-proof filesystem security scanner.

- Require a complete inline Markdown image before counting an Actions status
  badge as README evidence. Unterminated links, angle brackets or titles no
  longer satisfy `--require-badge`; valid URL/title forms remain supported.
  Also correct the guide's shortcut-reference capability description.

- The offline release inventory now reports a `worktree_dirty` boolean for
  staged, unstaged and non-ignored untracked changes, without exposing local
  filenames or pretending those edits are included in commit-only notes.
  Disable Git's optional index locking and fsmonitor hook for this read,
  with synthetic checkout regressions. Ignored files and remote-only history
  remain outside its coverage (related to #72).

- The scheduled review-date checker now ignores dates inside Markdown HTML comments (including multiline and unclosed comments), while preserving real dates after a comment closes. Inline backtick spans must have equal-width delimiters; mismatched runs no longer hide real source-review dates. This is a bounded source filter, not full GitHub Markdown rendering.

- Recognize shortcut reference-style GitHub Actions badge images
  (`![CI]` paired with `[CI]: URL`) in the offline README checker.
  The workflow existence check now also covers this Markdown form,
  while ignoring inline and explicit-reference duplicates and code examples.
  Four black-box regressions preserve line diagnostics and opt-in
  `--require-badge` behavior. Full Markdown rendering and live CI status
  remain outside the check.

- Isolate the read-only release inventory from inherited `GIT_*` variables
  (including `GIT_DIR` and `GIT_WORK_TREE`) and global/system Git config.
  Previously those variables could silently substitute an unrelated checkout's
  history. Add cross-checkout regression tests; this is not a sandbox or a
  verification of the target repository's own trustworthiness (related to #72).

- Scan `.markdown` sources alongside `.md` files in the offline
  documentation link checks, and validate section fragments pointing to
  either extension. Previously `.markdown` source links and target anchors
  could pass unchecked. Add synthetic missing-link and good/bad-fragment
  regressions; no network access or new dependencies.

- Handle repeated HTML navigation/image/anchor attributes with browser-compatible
  first-value precedence, and report malformed duplicates instead of letting a later
  `href`, `src` or `alt` hide an invalid first value (related to #16).
- Reject Windows directory junctions and other non-symlink reparse points in
  the agent-eval snapshot tool before traversal, so a supposed synthetic target
  cannot silently lead the snapshot outside its directory. Add a portable
  simulated-junction regression; this is still not a sandbox or race-proof
  filesystem monitor (related to #74).
- Reject ambiguous duplicate JSON members and boolean format versions in
  agent-evaluation snapshot baselines. Verification now fails closed instead of
  potentially reporting `UNCHANGED` for an edited or malformed baseline (#74).

### Security

- Fail closed on out-of-checkout **non-Markdown file symlinks** (such as
  LICENSE, README.rst and image assets) before any MCP checker starts.
  Previously the preflight validated Markdown aliases but silently skipped
  other symlink names. Keep ordinary in-root single-linked file aliases
  usable, refuse directory symlinks, and add synthetic source-preservation
  and no-checker-launch regressions. This is a stable-checkout boundary,
  not a claim of protection against concurrent filesystem replacement (#255).

- Reject directory junctions encountered in the MCP source inventory
  before running any checker (excluding intentionally ignored `.git` and
  `node_modules` trees). Previously the metadata preflight silently skipped
  those redirected subtrees. Add simulated metadata and a native Windows
  `mklink /J` regression checking all three tools and an unchanged synthetic
  outside document. This is stable-checkout scope enforcement, not proof
  against concurrent filesystem swaps (related to #255).

## [v0.2.0] — 2026-10-23

First release with the Claude Code and Codex plugin. The GitHub Action changes too,
including a security fix, so adopters should update their pin.

### Added

- A `Lint` CI job runs ruff 0.16.10, installed by hash, over `tools/`, `tests/` and
  `examples/` with a small rule set: syntax, pyflakes and bugbear, no style rules. The
  first run's 20 findings are fixed: an unused variable, semicolon-joined statements,
  and `zip()` calls that now state `strict=True` where the lengths must match. The
  tools still have no runtime dependencies, and the job is not yet required (#55).
- Decision records in `docs/decisions/` explain seven standing choices: standard
  library only, offline and read-only tools, commit pins and immutable tags, a
  composite Action, the protected `master`, no unverified contact routes, and the
  plugin living at the repository root. CONTRIBUTING and the handoff guide link
  them, and a test keeps their shape (#61).
- A real before/after case for BeautifulRepo's own README
  (`case-studies/readme-first-success-case.md`): fixed revisions, a clean-clone run
  of the first success and all five checks, and GitHub's rendering measured at
  1280, 375 and 320 px in light and dark themes, with its limits stated (#21).
- The Pocket Board example records a dated, rendered keyboard, contrast and reflow
  check: light and dark themes at 375 and 320 px in Chrome 152, with what was not
  checked. Its contrast test now also guards the focus outline and text colours (#28).
- `tools/review_dates.py` lists guide sources whose "Reviewed" date is due for a
  recheck (180 days, 30 for the programs guide) and rejects future or impossible
  dates. The maintenance workflow describes the recheck routine (#64).
- `AGENTS.md` gives coding agents the five checks, the house rules and the layout.
  Codex reads it directly; Claude Code reads it through `.claude/CLAUDE.md`, because
  a root `CLAUDE.md` fails `claude plugin validate --strict` (#53).
- A pushed `v*` tag opens a **draft** GitHub Release (`.github/workflows/release.yml`)
  once its commit is on `master` and every required check from the `master` ruleset
  passed there. The draft is filled from the release-note template with the tag,
  SHA, previous tag, compare link and CI run; a maintainer edits and publishes it.
  `guides/maintenance-workflow.md` describes the release steps (#56).
- Package BeautifulRepo as one plugin for Claude Code and Codex, version
  `0.2.0-dev.0`. Its read-only `audit-repo` skill runs the offline tools from the
  installed copy against a target repository and applies the checklists. The plugin
  comes with ground rules for agents (`guides/agent-safety.md`), an install guide
  (`guides/agent-plugin.md`) and manifest/skill contract tests.
- Publish BeautifulRepo's own `SECURITY.md`, backed by GitHub private vulnerability
  reporting (enabled 2026-10-22): triage owner, scope for the tools, Action and plugin,
  no promised response time. Issue forms link the private route. A conduct policy is
  still pending a verified reporting channel.
- Route questions to the newly enabled Discussions from the issue chooser (blank
  issues off; security and abuse routes listed), label new issues from the forms, and
  explain every label in CONTRIBUTING.
- CI hygiene borrowed from the owner's other repositories: a superseded pull-request
  run is cancelled and checks can be started by hand; Dependabot proposes weekly
  updates for the SHA-pinned Actions; a daily scheduled workflow verifies that every
  `drevendev/BeautifulRepo@<sha> # vX.Y.Z` pin in the docs matches its tag, and
  reports catalog freshness and self-audit warnings.
- Add `.editorconfig` (UTF-8, LF, final newline, 4/2-space indents) that keeps
  trailing spaces in Markdown, where two of them are a hard line break.
- Commit the Hungry Crab maw config (`.crab.yml`) and decision ledger
  (`.crab/ledger.json`), so later `crab` runs skip practices already served and
  `crab tune` can learn from decisions.

### Changed

- The roadmap lists what shipped since v0.1.0: the plugin, the security policy,
  hardened checks, maintenance automation and the real README case. "Next" names the
  open epics with links: agent skills, real cases, private repositories and the
  self-check. The README and CONTRIBUTING describe the roadmap and the conduct
  decision the same way (#98).
- The community safety guide records the owner's conduct decision (2026-10-23):
  no `CODE_OF_CONDUCT.md` until a checked private channel and an independent
  enforcement path exist. The repository checklist's conduct item is "not applicable,
  with a reason" rather than a pass, with a trigger to reconsider (#30).
- The discoverability guide's BeautifulRepo example matches the live repository: a
  signed-out read-back of 2026-10-23, a one-line reason for each of the seven topics,
  the decision to keep GitHub's default social card, and the decision to turn off the
  empty wiki (#67).
- The README's first-use path starts with a copyable `git clone` and `cd`, names
  the platforms CI tests (Ubuntu with Python 3.11 and 3.14, Windows with 3.14; not
  macOS) and says what a passing self-check looks like, without fixed counts (#66).
- CONTRIBUTING describes the `hacktoberfest` label as historical instead of as
  participation, in line with the programs guide: Hacktoberfest 2026 does not count
  pull requests. The label itself stays until its post-event review (#100).
- `docs_links.py` and `html_navigation.py` now scan the current directory when
  `--root` is omitted, like `repo_audit.py`. Previously they silently checked
  BeautifulRepo's own checkout. `html_navigation.py` also runs under `python -I`.
  Commands run from the BeautifulRepo root behave as before.
- Name one check list everywhere: README, CONTRIBUTING, the maintenance guide and
  CI now all run the same five checks, including `repo_audit.py .`. The workflow is
  renamed "Quality checks" (required job names unchanged), and CONTRIBUTING
  describes the protected `master`.
- Pin the adoption guide's example workflow to the `v0.1.0` commit and explain how
  to check where a tag points.

### Fixed

- The daily scheduled run now fails when a catalog entry or a guide source is due for
  a recheck, so GitHub notifies the owner. It used to print warnings and stay green
  (`catalog.py` and `review_dates.py` gain `--fail-on-warning`; pull-request checks
  are unchanged and calendar-independent) (#99).
- Action: a `checks` list written one name per line, separated by tabs, or left
  empty used to pass validation and then run **no** checks, so the job went green.
  The setup step now hands a normalized list to the check steps, fails on an empty
  list, and rejects an invalid `audit-fail-on` even when `audit` is not selected.
  The self-test covers both new failure cases (#104).
- Link checkers report destinations that only work on case-insensitive or Windows
  file systems: wrong letter case (`docs/guide.md` for `docs/Guide.md`), a `:`, a
  trailing dot or space, and Windows device names such as `NUL` or `con.md`. Before,
  these passed on Windows and macOS although GitHub serves none of them (#103).
- `html_navigation.py` generates heading anchors the way GitHub does: each space is
  its own hyphen (`terms--conditions`), entities are decoded after tags are
  stripped, emphasis underscores and images drop out, and combining marks stay. A
  link to the anchor GitHub actually generates no longer fails, and a link to a
  collapsed one no longer passes (#102).
- Only `\n`, `\r\n` and `\r` end a line in the tools now, as in CommonMark. A form
  feed, vertical tab, NEL or Unicode line/paragraph separator inside code or prose
  used to crash `html_navigation.py` or make it reject a valid anchor, and to shift
  `repo_audit.py` line numbers (#105).
- Scanning time no longer grows quadratically on adversarial Markdown. Link text
  brackets are paired in one pass. A bare link destination stops at its 33rd unclosed
  `(`, as in GitHub's cmark-gfm. The audit's heading parser no longer backtracks over
  trailing spaces. 200 KB of unmatched `[` went from hours (extrapolated) to under a
  second (#107).
- `repo_audit.py` treats an NTFS junction in `.github` or `docs` like a directory
  symlink: it reports `path.symlink` and does not read through it. Before, a junction
  passed the symlink check, and documents outside the target were read (#108).
- `repo_audit.py` matches backtick code spans within one paragraph or heading. Two
  stray backticks in different paragraphs used to form one span and hide every
  finding between them, such as a TODO or an image without alt text (#106).
- The plugin manifests, the `audit-repo` skill and the agent guides no longer
  promise that nothing leaves the machine. BeautifulRepo's Python checks make no
  network requests, but an agent session may send repository context to its model
  provider; the guides link Claude Code's and OpenAI's data-control pages (#97).

### Security

- [GHSA-9rpm-g83x-47w7](https://github.com/drevendev/BeautifulRepo/security/advisories/GHSA-9rpm-g83x-47w7): on Windows, a Markdown link, an HTML attribute or
  a symbolic link in the checked repository that named a UNC share (`\\host\share`,
  also percent-encoded) made `docs_links.py`, `html_navigation.py` and the Action open
  that share before reporting "escapes repository root". The connection could expose
  the user's Windows credentials to that host. Destinations with a backslash or a drive
  letter are now reported as non-portable without being opened, sources and
  destinations are resolved inside the root with link and junction targets checked
  as text first, and the Markdown walk no longer follows links or junctions (#110).
  **Action adopters should move their pin to v0.2.0.**

## [v0.1.0] — 2026-10-22

First tagged version, at commit `96e04e6a79027354c5e84a4a28f3ba5f5441d484`.
See the [release notes](https://github.com/drevendev/BeautifulRepo/releases/tag/v0.1.0).
It includes all earlier handbook work listed below.

### Checks for other repositories

- Publish the audit and both link checks as a composite GitHub Action
  (`action.yml`) that other repositories pin to a reviewed commit. It uses the
  caller's Python 3.11+, validates its inputs and makes no network requests.
- Never scan `.git` or `node_modules` Markdown, and add a repeatable `--exclude`
  glob to `docs_links.py` and `html_navigation.py` for vendored or archived docs.
- Add a consumer guide with a copy-paste workflow and a step-by-step rollout,
  plus a CI self-test that runs the action on Ubuntu and Windows, including
  cases that must fail.

### Windows checkout parity

- Check out text files with LF everywhere so fixture hashes and the
  generated-catalog comparison no longer fail on a Windows `core.autocrlf` checkout.
- Write the curated starter's JSON/Markdown output as UTF-8 when stdout is
  redirected on Windows, instead of crashing on non-ASCII collection text.
- Compare the preserved catalog file mode with what the platform actually stores,
  and run the full checks on Windows with Python 3.14 in CI.

### Maintainer continuity recipe

- Add a source-backed one-maintainer handoff checklist, fictional filled-in
  before/after example and actual local-check recovery route; distinguish public
  contributor rules from write/admin permissions and unverified private intake.

### Evidence-first reader journey

- Put a tested local Rowcount result and an honest source/command path near
  BeautifulRepo's README introduction, replacing duplicated navigation with
  three clear entry routes while retaining all five working starter types.
- Document why the explicitly fictional PocketDiff visual example uses its
  existing theme-aware assets, text equivalents and restrained hierarchy.
- Add an editorial evidence kit with fact-preserving README, announcement and
  changelog examples, plus three distinct lead angles and explicit limits.
- Expand regression checks for reader routes and editorial/example contracts.
  Rendered desktop/mobile, high-zoom and assistive-technology acceptance remain
  separately scoped, not claimed by these source-level tests.

### Input integrity and reading fidelity

- Refuse ambiguous repeated JSON keys before validating catalog resources or
  loading the Pocket Board fixture; nested and Unicode-escaped aliases are errors.
- Reject control characters and malformed percent escapes in catalog URLs while
  retaining percent-encoded paths, queries, IPv6 and fragment normalization.
- Keep literal empty fragments out of the curated collection's canonical URLs.
- Render user-authored scope as labelled prose and escape GFM strikethrough
  markers in generated catalogue and collection Markdown.
- Strengthen form-control boundary colors in both Pocket Board themes; this
  source-level contrast check is not a browser or assistive-technology audit.
- Preserve existing generated catalog bytes on UTF-8 encoding or replacement
  errors (PR #36) and test Python 3.11/3.14 explicitly in CI (PR #35).

### Working repository workshop

#### Added

- [Pocket Board application starter](examples/application-starter/README.md): a read-only,
  standard-library web example with a native status filter, light/dark styles, fictional
  data, controlled error responses and loopback HTTP regression tests.
- [Curated collection starter](examples/curated-starter/README.md): three annotated primary
  sources, deterministic Markdown/JSON reports, input validation and optional stale-review
  detection. It checks metadata, not live destination availability.
- [Application README template](templates/APPLICATION_README.template.md) and
  [collection README template](templates/CURATED_README.template.md).
- [Working-example index](examples/README.md), [first-success checklist](checklists/first-success.md)
  and [reproducible maintenance workflow](guides/maintenance-workflow.md).

#### Corrected

- Collection parsing rejects repeated JSON keys, including nested and escaped spellings,
  before a decoder can silently overwrite metadata. Invalid UTF-8, excessive nesting and
  input beyond the documented 1 MiB limit produce a controlled error.
- Collection URL validation rejects unpaired Unicode surrogates, malformed percent escapes,
  invalid DNS labels and unsupported authority syntax instead of producing a traceback or
  accepting malformed output. This is deliberately a bounded syntax check, not a safety verdict.
- Application readiness detects missing or invalid data and unavailable styles. Invalid
  Unicode task titles are rejected; local filesystem paths are not returned in errors.
- Application testing instructions now disclose the temporary loopback listener. README
  and roadmap routes preserve all five starter types rather than replacing earlier additions.

### Research/data and test discovery — 2026-10-17

[Research/data starter (#13)](https://github.com/drevendev/BeautifulRepo/pull/13) adds a fully
fabricated CSV, deterministic analysis, fixture digest, README template, provenance/citation
advice and mandatory navigation tests. The example makes no scientific or data-rights claim.

[Library test discovery (#14)](https://github.com/drevendev/BeautifulRepo/pull/14) replaces a
fixed nested test count with successful nonempty discovery. Real temporary suites cover
legitimate growth, zero tests, test failures, import errors and missing execution summaries.

### Library starter and local audit — 2026-10-16

[Library starter (#10)](https://github.com/drevendev/BeautifulRepo/pull/10) provides a tested
checkout-only API example, guide and README template without advertising an unpublished package.

[Repository audit (#12)](https://github.com/drevendev/BeautifulRepo/pull/12) adds bounded,
read-only checks for reader entry points, actionable findings, text/JSON reports and a
before/after example. Empty image alternatives and absent dedicated contribution guidance
are informational, not universal failures; no beauty score or certification is produced.

### Release guidance and accessible front page — 2026-10-14

[Release-note guidance (#9)](https://github.com/drevendev/BeautifulRepo/pull/9) adds a guide,
editable draft and tests distinguishing tags, GitHub Releases and maintained changelogs.

[README accessibility (#11)](https://github.com/drevendev/BeautifulRepo/pull/11) replaces a
layout-only feature table with a list and preserves the visitor journey as real text next
to the Mermaid diagram. Tests guard these structural properties, not assistive-technology certification.

### Earlier handbook foundations — October 2026

The initial handbook introduced a reader-first front page, repository checklist, README
scaffold, annotated pattern studies, dated program guidance and an offline source catalog.
Later additions included the CLI row-counting starter, theme-aware PocketDiff before/after
example, public contribution guidance and explicit community reporting limitations.

The documentation-destination checker gained coverage for nested/escaped parentheses and
labels, character references, multiline links, equal-length inline code delimiters,
indented/fenced code and list/quote containers. It also handles invalid UTF-8 and NUL paths
with controlled diagnostics. Its documented exclusions still apply: it is not an external
link crawler, reference-link parser or heading-anchor validator.

Visual regressions preserve theme switching, meaningful alt text, nearby text equivalence,
SVG title/description linkage and non-color labels. Historical source observations remain
qualified in their guides. Linked content keeps its original rights and trademarks.

The [MIT license](LICENSE) is unchanged.

[Unreleased]: https://github.com/drevendev/BeautifulRepo/compare/v0.2.0...HEAD
[v0.2.0]: https://github.com/drevendev/BeautifulRepo/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/drevendev/BeautifulRepo/releases/tag/v0.1.0
