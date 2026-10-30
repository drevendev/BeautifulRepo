# Trade simulation: a shipped milestone described as pending

**Case status, 2026-10-30: in progress.** This is a pinned, source-level before/after
study of a real repository. The README correction happened in the target's own
merged PR; BeautifulRepo documents rather than repeats that target change.
Pinned before/after offline audits and a saved-data first success from fresh
Git clones were exercised in GitHub Actions on 2026-10-29. The target's historical
CI and a separate isolated fixture run are also recorded. Live 320 CSS px Chromium
observations check served saved data, light/dark rendering and a bounded
keyboard entrance path. A separate headful Chromium run also exercised actual
400% browser zoom. Neither establishes HTML/JS deployment provenance,
whole-page accessibility or a fresh economic simulation; the case is incomplete.

## Repository and exact evidence

- Target: [drevendev/trade_simulation](https://github.com/drevendev/trade_simulation)
  (MIT; [licence at the inspected revision](https://github.com/drevendev/trade_simulation/blob/36bd70ea399813accf21d350aa5a0067f059757e/LICENSE)).
- Before: [README at `59801a2ab5a38a161d45cb67e8c4b449f2e0a8ec`](https://github.com/drevendev/trade_simulation/blob/59801a2ab5a38a161d45cb67e8c4b449f2e0a8ec/README.md),
  the baseline of [target PR #796](https://github.com/drevendev/trade_simulation/pull/796).
  README Git blob: `0da676fee4fede53c2b0bd0d8647ec47e00a190c`.
- Main correction: [PR #796](https://github.com/drevendev/trade_simulation/pull/796),
  merged 2026-10-23 as `b6e1f8f602b8735aee63eab8514581486096d06e`.
  It corrected the released-M4 claim and added a native README conformance regression.
- Later source updates:
  [`75204bb`](https://github.com/drevendev/trade_simulation/commit/75204bb8ed59b5b9b74883338f1de0b98609756c)
  and [`ec9cd6e`](https://github.com/drevendev/trade_simulation/commit/ec9cd6ef98bdfd9455a82c5811e048cce72bf352)
  on 2026-10-26, explaining the saved-run M4/M3 viewer more precisely.
- After snapshot: [`36bd70ea399813accf21d350aa5a0067f059757e`](https://github.com/drevendev/trade_simulation/tree/36bd70ea399813accf21d350aa5a0067f059757e),
  inspected 2026-10-29; [README](https://github.com/drevendev/trade_simulation/blob/36bd70ea399813accf21d350aa5a0067f059757e/README.md)
  Git blob `ba1ec400ced641596d2ca7fa41892caa4b5c41ec`.
  This is a **source snapshot**, not a claim about the current deployed Pages build.

## Before: where the reader could be misled

At the pinned baseline, the README described the Pages entrance as an M3
LocalMarket experience and M4 as becoming implementation-complete only when
the pull request landed. Both were stale relative to repository evidence:

- The target's [`v0.4.0` GitHub Release](https://github.com/drevendev/trade_simulation/releases/tag/v0.4.0)
  was actually published **2026-09-30**, not waiting for a future merge.
- The checked-in viewer had moved toward an M4 first-level presentation.
  A statement about the **deployed** website cannot be proved by reading
  `docs/index.html`, so deployment freshness must be checked separately.

The reader consequence is specific: someone deciding whether to explore M4
could mistake a published milestone for pending work, or expect the wrong
first screen from a static viewer. The smallest fix was to reconcile the
README against the release and checked-in viewer, **without** pretending
that static Pages executes the canonical TypeScript simulation.

## After: better boundaries and a useful source-first result

At the pinned after revision, the README says M4 shipped as `v0.4.0`,
describes the saved-run M4 spotlight and selectable M3 view, and explicitly
does **not** claim the deployed Pages site was refreshed. The checked-in
[`docs/index.html`](https://github.com/drevendev/trade_simulation/blob/36bd70ea399813accf21d350aa5a0067f059757e/docs/index.html)
uses the title *Trade simulation — M4 one-region closed economy* and a
recorded-economy first screen. This is evidence about **source**, not a
screenshot or observed live interaction.

A maintainer can offer a modest, reproducible **data inspection** before
asking readers to install the full simulation toolchain. From a checkout
of the pinned after revision, using only Python's standard library:

```bash
python -c "import json; d=json.load(open('docs/m4-preview.json', encoding='utf-8')); print('Seed:', d['scenario']['seed'], 'Ticks:', d['scenario']['ticksExecuted'], 'Capital @ tick 59:', round(d['samples'][-1]['installedCapital'], 2))"
```

Expected output from the pinned JSON source, observed first from an
**isolated byte-identical local fixture copy** and subsequently from a
**fresh Git clone on a GitHub Actions runner** on 2026-10-29 (see the
[pinned CI reproduction](#pinned-beforeafter-ci-reproduction-observed-2026-10-29)):

```text
Seed: 42 Ticks: 60 Capital @ tick 59: 78.04
```

The pinned [`docs/m4-preview.json`](https://github.com/drevendev/trade_simulation/blob/36bd70ea399813accf21d350aa5a0067f059757e/docs/m4-preview.json)
(blob `4ec090eb19cc58ec63058f2a49f48c573a036674`) specifies
seed **42**, **60 executed ticks**, **13 sampled records**, first sampled
tick **0** and last **59**. Installed capital in the last sample is
`78.03677092437883`; the display rounds it to `78.04`. These numbers
are from a **checked-in saved run**. This read-only example does **not**
rerun, validate or prove any simulation behavior.

For the real TypeScript engine the target's
[`package.json`](https://github.com/drevendev/trade_simulation/blob/36bd70ea399813accf21d350aa5a0067f059757e/package.json)
requires Node **22+**, and `npm test` has a `pretest` hook that installs
Playwright Chromium (potentially a network download). Its private
`0.0.0` package version is not the project's `v0.4.0` GitHub Release.
These are onboarding prerequisites worth disclosing before suggesting the
full test suite.

## Recorded local artifact run (2026-10-29)

A copy of the GitHub-fetched `docs/m4-preview.json` was reconstructed in an
**isolated local directory**, not a Git checkout. Before execution,
`git hash-object docs/m4-preview.json` returned
`4ec090eb19cc58ec63058f2a49f48c573a036674`, matching the exact pinned
Git blob above. From that directory, the **exact** Python one-liner shown here
exited 0 and printed:

```text
Seed: 42 Ticks: 60 Capital @ tick 59: 78.04
```

For a failure-path check, the fixture was temporarily renamed and the **same**
one-liner run again. It exited **1**, produced no stdout, and raised
`FileNotFoundError: [Errno 2] No such file or directory: 'docs/m4-preview.json'`.
The fixture was restored and its blob hash matched again. This verifies the
single-file command and its missing-file failure behavior against identical
content. It does **not** prove a fresh Git clone, a live simulation, the
browser viewer, or any target-native test suite.

## Target-native CI evidence (verified 2026-10-29)

The target's [GitHub Actions CI run #39926661147](https://github.com/drevendev/trade_simulation/actions/runs/39926661147)
was a **push to `master`** on **2026-10-23**, at the exact README-correction
merge commit `b6e1f8f602b8735aee63eab8514581486096d06e`.
GitHub reports the run **completed successfully**. Its job/step records show:

- `typescript` — success, including `npm ci`, `npm run typecheck`,
  `npm test` and `npm run build`.
- `build-and-test` — success, including `dotnet restore`,
  `dotnet build --configuration Release --no-restore` and
  `dotnet test --configuration Release --no-build`.
- `policy-guard` — success, although some PR-only steps were skipped on
  this push event. A green job does not mean every conditional step ran.

The same SHA has a successful
[GitHub Pages build/deploy run #39926660759](https://github.com/drevendev/trade_simulation/actions/runs/39926660759),
with `build`, `deploy` and `report-build-status` jobs marked successful.
These are **GitHub-native historical results**, not commands that BeautifulRepo
executed locally. The Pages result does not prove what a visitor currently
sees, and these specific runs are for the **merge commit**, not the later
after-snapshot `36bd70ea399813accf21d350aa5a0067f059757e`.
No test totals, screenshots, browser observations or present-day deployment
freshness are inferred from the green status.

## Repository metadata and trust surfaces (observed 2026-10-29)

This is a **dated, read-only inspection**, not a change to the target and not
part of either pinned Git revision. Repository description, topics, homepage
and security settings can change independently of a commit; the public
[GitHub repository metadata](https://api.github.com/repos/drevendev/trade_simulation)
was read on **2026-10-29**, while the tracked-file tree below is pinned to
the after snapshot `36bd70ea399813accf21d350aa5a0067f059757e`.

| Surface | Observed evidence | Reader impact / bounded decision |
| --- | --- | --- |
| About description | `null` in the public repository metadata | A GitHub search visitor lacks a one-line explanation there. Recommend a concise, factual TypeScript-economy description **for target maintainers to consider**, not a claim that one was applied. |
| Topics | Empty `topics` array | No repository-specific topic navigation is advertised. Suggest only accurate, verified subjects rather than maximizing tags. |
| Homepage | `https://drevendev.github.io/trade_simulation/` | The metadata **does** point to Pages. It does not establish the current deployment SHA or rendered viewer contents. |
| License and contributor route | Public metadata reports MIT; the pinned tree includes `LICENSE` and `CONTRIBUTING.md` | Those discoverable trust surfaces exist; they do not independently certify build quality or response times. |
| Target security-policy file | The pinned recursive Git tree completed without truncation (400 entries) and contains **no tracked `SECURITY.md`** | No target-tracked `SECURITY.md` was found; this does not rule out guidance elsewhere, an owner-level inherited policy, or private reporting configured outside the tree. |
| Private vulnerability reporting | **Unknown**: the public metadata read does not expose a verified enabled/disabled result; the dedicated settings route was unavailable to this inspection | Do **not** send vulnerability details to public issues on the assumption that they are private, and do not invent an email or reporting form. GitHub distinguishes an optional `SECURITY.md` from its separately configured private reporting feature. |

The relevant [GitHub security-policy documentation](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy)
and [private-reporting documentation](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately)
were checked on **2026-10-29**. These are recommendations and scope
limitations for a future authorized target maintainer review. BeautifulRepo
did **not** edit target files, description, topics, security settings,
license or release. No confidential reporting capability is asserted.

## Editorial decision and trade-off

**Adopt:** tie milestone status to a real release, describe a saved-run UI
as a viewer rather than a running engine, and put one source-derived result
next to a command a reader can inspect. The trade-off is that the small JSON
inspection proves only artifact accessibility; it does not replace a full
runtime demo, tests or production verification.

The issue [#82](https://github.com/drevendev/BeautifulRepo/issues/82)
also tracks target metadata and security reporting. These were **assessed
read-only**, with unknown settings explicitly left unknown; no target
repository changes were made.
This source-only write-up does not close
[#82](https://github.com/drevendev/BeautifulRepo/issues/82) or the
[real-case epic #88](https://github.com/drevendev/BeautifulRepo/issues/88).

## Pinned before/after CI reproduction (observed 2026-10-29)

The [source-only workflow](../.github/workflows/trade-case-evidence.yml)
completed successfully in
[GitHub Actions run #40957829865](https://github.com/drevendev/BeautifulRepo/actions/runs/40957829865),
[job #123742449748](https://github.com/drevendev/BeautifulRepo/actions/runs/40957829865/job/123742449748),
on the workflow's exact commit
[`acd04cab0993244c1c948137696ea9319ee49ed3`](https://github.com/drevendev/BeautifulRepo/commit/acd04cab0993244c1c948137696ea9319ee49ed3).
The workflow checks out BeautifulRepo's audit tools at the **single immutable
commit**
[`83cf280c7242791c7b9601c8f8069ea72f4a5a13`](https://github.com/drevendev/BeautifulRepo/commit/83cf280c7242791c7b9601c8f8069ea72f4a5a13).
The runner used two separate fresh, shallow Git clones of the target,
fetched exact before/after commits and asserted the resulting HEAD values.

Observed results from that job's logs:

- **Before** `59801a2ab5a38a161d45cb67e8c4b449f2e0a8ec`:
  `repo_audit.py --format json --fail-on never` found **0 errors,
  0 warnings, 0 informational findings** (exit 0);
  `docs_links.py` checked **37** relative Markdown destinations across
  **49** Markdown files (exit 0);
  `html_navigation.py` checked **39** local HTML/fragment destinations
  across **49** Markdown files (exit 0).
- **After** `36bd70ea399813accf21d350aa5a0067f059757e`:
  the same audit found **0 errors, 0 warnings, 0 informational findings**
  (exit 0); the link checker examined **38** relative destinations across
  **49** files (exit 0); HTML navigation examined **40** local destinations
  across **49** files (exit 0).
- From the fresh **after** clone, the documented `python -c` saved-JSON
  one-liner exited **0** and printed
  `Seed: 42 Ticks: 60 Capital @ tick 59: 78.04`. The step used
  `PYTHONSAFEPATH=1` to prevent importing modules from the inspected
  working directory. From a separate empty working directory the same
  one-liner exited **1**, produced no stdout, and raised
  `FileNotFoundError`; all three assertions were checked by the job.

**Interpretation:** the zero-finding audit results **did not detect the stale
M4 release claim** in the original README. These tools inspect structural
entry points and local destinations, not release truth. The extra destination
counts after the correction are inventory differences, **not quality scores
or an accessibility improvement**. Manual comparison with the actual
release and target-native CI was necessary to find the editorial defect.

The runner performed only Git source retrieval, BeautifulRepo's read-only
tools and standard-library JSON inspection. No TypeScript/.NET target code
or dependency installation was run. The workflow is PR-path-scoped or
manually dispatched, not scheduled. Its successful result is valid for the
specific workflow, tool and target SHAs above; it is not a live deployment,
browser test or broader security certification.

## Live Pages browser observations (2026-10-30 Cyprus time)

The [read-only Chromium probe](trade-pages-probe.mjs) ran against the
**served** [public Pages viewer](https://drevendev.github.io/trade_simulation/)
in [GitHub Actions #40973430007](https://github.com/drevendev/BeautifulRepo/actions/runs/40973430007).
Its exact-head source is
[PR #200](https://github.com/drevendev/BeautifulRepo/pull/200)
(commit `9d95f271700742edff2d9d932af1228efaa1388c`).
The run completed **successfully** at 2026-10-29 23:29 UTC
(2026-10-30 in Cyprus). The runner used Chromium
**153.0.8010.12**, the target's pinned source
`36bd70ea399813accf21d350aa5a0067f059757e`, its npm lockfile,
a **320 CSS px** viewport, and separate emulated light/dark preferences.
Target package scripts were disabled during dependency installation.
Only browser rendering and saved artifact inspection were executed:
**no target economic simulation was run**.

Observed in **both** color schemes:

- The served HTML and `m4-preview.json` returned **HTTP 200**.
- The served saved JSON SHA-256 was
  `f10fc8b9f67c55ed17158346c46ad686c6f3409dd08f379bda7a96055a880980`,
  **byte-identical** to the checked-in JSON from the pinned source snapshot.
- The browser displayed `tick 59 · sample 13 of 13` and
  `78.04 capital units`, matching the pinned saved sample
  (`78.03677092437883` before rounding).
- The page title was `Trade simulation — M4 one-region closed economy`;
  the lead heading read **Watch an economy find its rhythm.**
- `document.documentElement.scrollWidth` was **320 CSS px** and its
  `clientWidth` was **320 CSS px** (zero document-level horizontal overflow).
  This alone does not rule out clipping inside individual containers.
- No uncaught page errors were logged. Computed body backgrounds differed:
  light `rgb(251, 250, 247)`, dark `rgb(20, 20, 15)`.

The job uploaded
[the JSON observation record and two full-page screenshots](https://github.com/drevendev/BeautifulRepo/actions/runs/40973430007/artifacts/12941750856)
(`pages-light-320.png`, `pages-dark-320.png`, `observations.json`;
artifact **12941750856**, retention through **2026-11-12 UTC**).
The browser log, saved observation JSON and both full-page **320 × 3534 px**
PNG images were read and visually inspected after the run.

**Screenshot text alternative and editorial assessment.** In both themes
the viewer uses a single narrow column: a prominent three-line headline,
a two-link milestone chooser, a saved-M4 summary and tick slider, five
stacked metric cards, six collapsed milestone chapters, and a footer
with the source/run command. The cards' final recorded sample shows
zero current output, employment, needs coverage and wages but **78.04**
installed capital. **The probe deliberately selected tick 59** to verify
the saved data; these screenshots do *not* show the page's initial default
working-tick selection. The dark version replaces the pale backgrounds
with near-black panels and light text. No horizontally cut-off cards,
chapters or footer text were apparent in the captured images. The
secondary annotations, units and footer command use much smaller type
than the headline; at 320 px they deserve a separate legibility and
contrast assessment before making an accessibility claim. The collapsed
chapter contents, mobile touch behavior and keyboard focus states are
not evidenced by these static images.

The matching served data establishes **saved JSON agreement at observation
time**, not the deployed HTML/JavaScript commit SHA or a general guarantee
that Pages is current. Theme emulation is not a physical phone. Real
**400% browser zoom, screen-reader behavior, contrast measurements and
expanded-chart inspection remain NOT RUN**. Only a bounded keyboard entrance
path was subsequently tested; full keyboard traversal remains unverified.
The 320 px screenshot observations and text equivalent are now recorded,
but the case is still **in progress** because deployed HTML/JS provenance
and broader accessibility behavior remain unverified.

## Sampled keyboard entrance (observed 2026-10-30)

The [follow-up Chromium job #40985815887](https://github.com/drevendev/BeautifulRepo/actions/runs/40985815887)
completed **PASS** on the exact code commit
[`1ebd016`](https://github.com/drevendev/BeautifulRepo/commit/1ebd016368f9d368d165049066c3f11f140105ae).
The [read-only browser probe](trade-pages-probe.mjs) exercised real
Tab, ArrowLeft, ArrowRight and Enter keypresses at **320 CSS px**,
separately with light/dark preference emulation. The job log's
`keyboard` observation objects showed the same results in both modes:

- The first five sequential Tab stops were the M4 and M3 entrance links,
  saved-milestone selector, saved-tick range slider and M4 chapter summary.
  All five matched their intended DOM elements and matched
  `:focus-visible` with computed `solid 2px` outlines.
- ArrowLeft from the last sample moved the focused slider to index **11**
  with the text readout **tick 55 · sample 12 of 13**. ArrowRight restored
  index **12**, **tick 59 · sample 13 of 13**.
- Enter on the keyboard-focused native M4 summary changed its
  `details.open` state from **false** to **true**.
- Both modes retained HTTP 200, the exact SHA-256 match for the served
  saved-run JSON, the expected last-tick/capital text, zero document-level
  overflow and no uncaught page errors.

The [workflow artifact](https://github.com/drevendev/BeautifulRepo/actions/runs/40985815887/artifacts/12946517627)
contains `observations.json` plus light/dark full-page screenshots
(retention through **2026-11-13 UTC**). The screenshots were taken
**before** keyboard traversal, so they do **not** depict the focus ring
or expanded chapter. The focus outlines above are **computed-style
observations**, not pixel-level contrast or visibility measurements.
The logs were inspected; these follow-up screenshots were not manually
re-reviewed in this run.

This establishes a **small first-screen keyboard path only**.
Full tab traversal, keyboard behavior within expanded charts,
screen-reader usability, real 400% browser zoom, color contrast,
physical mobile interaction and deployed HTML/JS revision provenance
remain **unverified**. [Issue #82](https://github.com/drevendev/BeautifulRepo/issues/82)
remains open; integration requires separate later-run acceptance.

## Bounded text contrast (observed 2026-10-30)

The [Chromium probe](trade-pages-probe.mjs) now samples nine named,
visible text roles on the **served** saved-run viewer, separately in light and
dark emulated color schemes: eyebrow, lead, primary entrance, provenance,
tick label, metric label, metric unit, chapter hint and footer. The
[standalone metric](contrast-metrics.mjs) computes relative luminance from
computed RGB text and the first opaque, solid ancestor background. Its
[offline regressions](contrast-metrics.test.mjs) cover known ratios,
normal/large text thresholds, and conservative unknown states.

This is a **diagnostic sample**, not a whole-page WCAG pass. It uses the
[W3C WCAG 2.2 SC 1.4.3 text contrast thresholds](https://www.w3.org/TR/WCAG22/#contrast-minimum)
of **4.5:1 for normal** and **3:1 for large** text. Decisions use the
unrounded ratio. The report preserves exact foreground/background
colors, font size/weight, threshold, measured ratio and classification.
Unsupported gradients/images, alpha, blending, hidden or absent content
are **NOT MEASURABLE**, not successes. A probe with fewer than six
measurable roles fails its **instrumentation minimum**, but low measured
contrast is recorded as a finding rather than silently failing the browser
evidence workflow. Future inspection must decide actual reader impact.

**Actual evidence:** [GitHub Actions #40997307803](https://github.com/drevendev/BeautifulRepo/actions/runs/40997307803)
ran this probe successfully at exact implementation HEAD
[`c163aeed`](https://github.com/drevendev/BeautifulRepo/commit/c163aeed699ed71ed4da8e68a7e5e289181dd055).
All **7/7 offline metric regressions passed**. In the live Chromium log,
all **9/9 named roles were measurable in each theme** (18 of 18 samples).
Every sampled pair was at or above its applicable **4.5:1 normal-text**
threshold; none was classified below threshold or unknown. Recorded ratios:
light **5.17–17.40:1**, dark **5.47–13.97:1**. In particular, the
small **11.52 CSS px** metric-unit text measured **5.17:1 light** /
**5.91:1 dark**, and the small provenance annotation measured
**5.40:1 light** / **5.47:1 dark**. All comparisons were against actual
computed solid backgrounds on the served viewer, not assumed theme
variables. The run also rechecked the prior saved-JSON and sampled
keyboard observations. Its artifact contains machine-readable measurements
and screenshots; the **new screenshots were not manually re-reviewed** here.

This is a bounded **computed-style observation, not certification** of
WCAG 2.2 AA across the page. It omits other labels, SVG/chart data,
focus-ring contrast, alpha compositing, collapsed chapters, physical mobile,
real 400% zoom, screen reader and deployed HTML/JS provenance. A threshold
pass is not a general legibility judgement; the small unit sizes remain
an editorial concern.

## Native 400% Chromium browser zoom (observed 2026-10-30)

The [separate native-zoom workflow](../.github/workflows/trade-pages-zoom.yml)
completed successfully on [GitHub Actions #41015344993](https://github.com/drevendev/BeautifulRepo/actions/runs/41015344993)
using code HEAD
[`7e5d81f`](https://github.com/drevendev/BeautifulRepo/commit/7e5d81fcf2c4073536f4a724fd71b68faba700ca).
This test ran **headful Chromium inside an isolated 1440 × 1200 px Xvfb desktop**.
The [native zoom helper](native-page-zoom.py) sent eight genuine
`Ctrl+plus` keyboard shortcuts to the focused Chromium window after
checking its X11 `WM_CLASS`. This is **browser page zoom**, not CSS
`zoom`, a Playwright device scale override, a CSS-width-only viewport
emulation or pinch simulation.

The [live probe](trade-zoom-probe.mjs) independently measured the
following in **both** emulated light/dark schemes:

- `window.devicePixelRatio` increased **1 → 4** and
  `window.innerWidth` contracted **1280 → 320 CSS px**.
  `visualViewport.scale` remained **1**, and computed body
  `zoom` remained **1**.
- `document.documentElement.scrollWidth` and `clientWidth` were
  both **316 CSS px** after zoom; observed document-level horizontal
  overflow was **0 CSS px**. This does not prove that no nested chart
  or hidden section can clip.
- Served HTML and saved JSON returned **HTTP 200**. Served JSON was
  byte-identical to the pinned `36bd70e` fixture, SHA-256
  `f10fc8b9f67c55ed17158346c46ad686c6f3409dd08f379bda7a96055a880980`.
  The saved-viewer readout remained `tick 59 · sample 13 of 13`
  and `78.04 capital units`.
- Four actual Tab presses reached the saved-tick slider, which matched
  `:focus-visible`. Both themes showed distinct computed backgrounds,
  no uncaught page errors, and **zero probe failures**.

The job retained a [JSON observation report and physical Xvfb viewport
screenshots](https://github.com/drevendev/BeautifulRepo/actions/runs/41015344993/artifacts/12959601046)
(`pages-light-native-400-viewport.png`,
`pages-dark-native-400-viewport.png`; **1440 × 1200 physical px**,
retention through **2026-11-13 UTC**). Both captures were downloaded
and visually inspected. They show the browser's **400%** zoom indicator,
the light or dark first-screen hero and a headline wrapped to three
lines without visible cut-off. Only the **first viewport** is visible;
the enlarged page continues below the fold, so these images do not
prove every later section is visually usable.

**Instrumentation lesson:** Playwright's full-page screenshot API on
this Chromium version produced a misleading **316 px clipped PNG**
under native zoom even though browser DOM measurements showed no
document overflow. The final workflow therefore captures the actual
isolated desktop framebuffer through [Xlib](native-x11-capture.py),
rejecting blank/unpainted frames rather than treating cropped
screenshots as successful visual evidence. The first X11 capture
itself exposed an unpainted frame; a paint-frame wait and nonblank
pixel check resolved that false positive. This is a reusable distinction
between **measured browser layout**, **actual screen pixels** and
**screenshot-tool artifacts**.

The case still does **not** establish deployed HTML/JS commit
provenance, full keyboard or expanded-chart traversal, screen-reader
usability, a physical phone, other browser engines, or whole-page WCAG
conformance. This PR remains subject to separate later-run acceptance.

## What remains unverified

- The **offline source-only** auditors did run on both clean Git clones, but
  their zero-finding reports do **not** validate milestone/release claims,
  repository quality, source truth or rendered accessibility. No broader
  semantic validation is implied by the PASS workflow.
- The `python -c` saved-data command and missing-file path ran on Ubuntu
  Python 3.11 under `PYTHONSAFEPATH=1`. It reads a static source artifact;
  it does **not** execute a simulation or test Windows, macOS or published Pages.
- No `npm ci`, TypeScript typecheck, Vitest, Vite build or legacy .NET
  build/test was run **locally for this case**. Target-native GitHub CI was
  checked at the correction's merge SHA as recorded above; the later
  after-snapshot has not been independently re-tested as a target runtime.
- The **served Pages viewer was actually observed** at 320 CSS px in emulated
  light/dark Chromium and under actual Chromium **400% page zoom**,
  with matching saved JSON and reviewed first-viewport captures.
  Deployed HTML/JS revision, **full** keyboard traversal,
  screen-reader behavior and **whole-page** contrast remain **unverified**.
  A limited first-screen keyboard path and nine-role computed-style
  light/dark contrast sampling were exercised on 2026-10-30 as above.
- Description, topics, homepage and tracked security-policy presence were
  inspected on 2026-10-29. Private reporting enablement, inherited policies,
  current-release follow-on milestones and performance metrics remain
  **unverified**; no target settings or files were changed.

The pinned-tool source audit and the fresh-clone saved-data command/failure
path are now reproducible and observed. To mark this a **complete case**
under the [five-step procedure](README.md), the 320 px light/dark
screenshots and editorial observations now exist with honest limits.
The live JSON matches the source snapshot, and native Chromium 400%
page zoom has been directly observed. Current Pages HTML/JS provenance,
complete keyboard navigation, expanded charts, other browser engines and
screen-reader coverage remain explicitly unknown unless actually tested. The historical target-native CI
covers the correction merge, not the later after-snapshot runtime.
This remains a useful partial case, not a fully accepted one.
