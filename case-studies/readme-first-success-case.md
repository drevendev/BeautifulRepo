# BeautifulRepo's README: from a directory to inspectable evidence

**Case status, 2026-10-22:** reproducible source/command evidence captured; GitHub-native rendered desktop/narrow/light/dark and keyboard/assistive-technology checks **not yet completed**. This is a real-repository adaptation, not evidence of improved user conversion or a finished accessibility audit.

## The real repository and immutable baselines

- Project: [`drevendev/BeautifulRepo`](https://github.com/drevendev/BeautifulRepo), a public handbook with runnable examples.
- Before: [`README.md` at `e1c3123beeaa8911c109f57cd4cd55f3bb36df6c`](https://github.com/drevendev/BeautifulRepo/blob/e1c3123beeaa8911c109f57cd4cd55f3bb36df6c/README.md), source blob `cbdc20ce13fa739c56ef6cde53142cc13dcf4cd0`.
- After: [`README.md` at `baeb53dd1c89e309dd3abb6781f5f9869c8effca`](https://github.com/drevendev/BeautifulRepo/blob/baeb53dd1c89e309dd3abb6781f5f9869c8effca/README.md), source blob `716befb3c640e378fa75ca3c890b9f9aca13fa73`.
- Change: [PR #44, evidence-first showcase](https://github.com/drevendev/BeautifulRepo/pull/44), integrated 2026-10-22. The PR includes associated source tests, a design-intent brief and editorial examples.

These are source observations at fixed revisions; they do not imply a study of actual visitors.

## The reader obstacle

The old first screen described the mission and then immediately presented *choices*. Its centered navigation held **eight links** and its `Start here` table held **twelve destination rows**. There was no `Working proof` section before the table. A first-time reader had to choose a document before seeing what a runnable example actually prints.

This is a reproducible **source-structure obstacle**, not a measured accessibility defect, reading-time claim, or evidence that people failed to find the material.

## Change and tradeoffs

The revised page places `Working proof` before `Start here`, with an exact checkout command, a tiny input fixture and the expected output. The top navigation went from **eight** destinations to **four**, and the first decision table from **twelve** choices to **three**. The later handbook and [five-type example index](https://github.com/drevendev/BeautifulRepo/blob/baeb53dd1c89e309dd3abb6781f5f9869c8effca/examples/README.md) preserve deeper material without making it the first decision.

The new first step is deliberately small: count three CSV records from a checked-in file. It proves that *one working path* exists; it cannot prove that the entire handbook or all examples are correct. The README distinguishes the fictional PocketDiff visual study and the synthetic repository-audit demo from this real command. The compact first screen trades immediate exposure of many sections for reduced initial choice: readers seeking advanced templates need to follow the broader handbook/index.

### Textual before/after equivalents

**Before:** title and value proposition → status/metadata badges → eight navigation links → principle callout → twelve-row `Start here` table → visitor-journey explanation.

**After:** title and value proposition → status/metadata badges → four navigation links → principle callout → `Working proof` with command and observed output → three-row `Start here` table → visitor-journey explanation and preserved deeper navigation.

This textual hierarchy is available without interpreting a screenshot. It is *not* a claim that GitHub's rendered page is correctly ordered for every assistive technology.

## Reproduce one real first success

From the repository root, with Python 3.11 or newer:

```bash
python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv
```

README expected stdout:

```text
Data rows: 3
```

**Observed separately on 2026-10-22:** Python **3.13.5**, command exited 0 and printed exactly `Data rows: 3`. The two source files were reconstructed verbatim from GitHub's current `master` and checked with `git hash-object`: `rowcount.py` blob `5d7a8f2996e5412f18438a970fc5f140c6ac4137`; `sample.csv` blob `7ef754ffa22bb69e50d926dbf4776bd235239615`. The verification used an isolated directory containing those exact two files, **not a clean full repository clone**. No network access or third-party Python packages were needed to run this command.

The original change's [GitHub Actions workflow run #39556116102](https://github.com/drevendev/BeautifulRepo/actions/runs/39556116102) completed successfully on the PR's exact head with Python 3.11 and 3.14. This is repository CI evidence, distinct from the isolated Python 3.13.5 reproduction above; it is not a substitute for the visual inspection below.

To repeat the **full-checkout** acceptance, clone the fixed `baeb53dd...` revision, run the command, and separately execute:

```bash
python tools/catalog.py
python tools/docs_links.py
python tools/html_navigation.py
python -m unittest discover -s tests -v
```

**Not claimed as run locally here:** the full checkout or this four-command local suite. CI evidence is linked above, rather than converted into an invented local result.

## Visual and accessible acceptance: still open

The source-level counts above do not establish rendered layout, color contrast, horizontal reflow, landmark order, or keyboard focus visibility. To complete this case and inform [Issue #21](https://github.com/drevendev/BeautifulRepo/issues/21): capture GitHub's **actual rendered README** at both fixed revisions; inspect desktop and 320 CSS-pixel-equivalent/narrow or 400%-zoom viewports; inspect light and dark mode with a text equivalent; and record keyboard focus/link reachability and any necessary correction. Distinguish each observed PASS/FAIL from untested screen-reader or platform combinations. Do not pass off a locally styled Markdown approximation as a GitHub renderer screenshot.

A different issue, [#28](https://github.com/drevendev/BeautifulRepo/issues/28), tracks Pocket Board controls and must not be silently closed on the strength of this README source change.

## Decision and limits

**Adoptable pattern:** lead with a small, reproducible piece of product evidence, then offer a few audience-specific routes and leave full reference navigation discoverable. Cite exact files and outputs; label demonstrations and hypotheses.

**What is verified:** immutable README differences; links to the actual implementation and sample; byte-identity of two runnable files; isolated Python output; provider CI on the PR head.

**What is not verified:** improved traffic/conversion, time to first success for actual users, full clean-clone run locally, real GitHub visual checks and assistive-technology compatibility.

### Primary guidance consulted (2026-10-22)

- [GitHub Docs, About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes): README scope, first-use/help/contribution information and relative links.
- [Open Source Guides, Starting an Open Source Project](https://opensource.guide/starting-a-project/): project audience, basic documentation and expectations.

The guidance supports the *decision criteria*, while the GitHub revisions and actual command above support the *specific outcome*. This case is original narrative and measurements; it copies no unrelated project's artwork or README.