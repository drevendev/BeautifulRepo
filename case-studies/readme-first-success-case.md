# BeautifulRepo's README: from a directory to inspectable evidence

**Case status, 2026-10-23:** a full clean-clone run and selected GitHub-rendered observations were recorded at desktop and narrow widths. Light-theme contrast was measured at 1280 px and dark-theme contrast at 375 px; the available evidence does **not** cover both themes at every width. Screen readers, real 400% browser zoom, keyboard traversal and visible focus were **not** checked. This is a real-repository adaptation, not evidence of improved user conversion or a finished accessibility audit.

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

**Full clean clone, 2026-10-23.** The README since gained a copyable clone step (#66). A fresh `git clone` from GitHub of the README-update branch at commit `198b2e9ca94881075743805a930520ad8a81709c` was made on Windows 11 with Python 3.14.7 and Git's `core.autocrlf=true`. There, `rowcount.py` printed `Data rows: 3` and exited 0, and all five documented checks exited 0:

```bash
python tools/catalog.py
python tools/docs_links.py
python tools/html_navigation.py
python -m unittest discover -s tests -v
python tools/repo_audit.py .
```

The results were 11 catalog resources, 199 Markdown destinations, 210 HTML destinations, 301 tests (7 skipped) and an audit with 0 findings. The counts belong to that commit and will change as the handbook grows.

## Rendered review on GitHub, 2026-10-23

Checked on GitHub's own rendering of `README.md` on that branch, signed out, in the Chromium-based browser built into the Claude desktop app. Widths and colour schemes were set by viewport emulation, and layout and colours were measured in the page. These are not screenshots of a phone.

| Check | 1280 px | 375 px | 320 px |
| --- | --- | --- | --- |
| Page scrolls sideways | no | no | no |
| Blocks with their own horizontal scroll | none | 3 code blocks, `Start here` table (3 px) | 3 code blocks, `Start here` table |
| Text contrast, light theme | 15.8:1 (links 5.2:1) | NOT RECORDED | NOT RECORDED |
| Text contrast, dark theme | NOT RECORDED | 17.4:1 (links 6.1:1, code 15.9:1) | NOT RECORDED |

The first screen at 375 px shows the title, the one-sentence promise, the four badges in two rows and the four navigation links, without overlap. Every image has alt text: the four badges are named `CI status`, `License: MIT`, `Python 3.11+` and `Runtime dependencies: zero`. The Mermaid journey keeps its adjacent text alternative. The recorded DOM inspection found no negative `tabindex` on 72 README links, and the four section anchors the navigation uses exist. **This does not prove keyboard focusability or visible focus:** actual Tab/Shift+Tab traversal and activation were **NOT RUN**.

Long commands scroll inside their code blocks rather than widening the page. That is acceptable for copyable commands, and the copy button stays available. The three-column `Start here` table scrolls inside its own container at 320 px; WCAG 1.4.10 allows two-dimensional layouts such as data tables to do so.

**Not checked or not recorded:** a screen reader, actual keyboard focus traversal and visible focus styles, real phones, 400% browser zoom as opposed to a 320 px viewport, contrast for the other width/theme combinations, and the earlier `e1c3123` revision's rendering. The before/after comparison above stays source-level. Blank contrast cells in the earlier case-study table were missing evidence, not implicit passes.

A different issue, [#28](https://github.com/drevendev/BeautifulRepo/issues/28), tracks Pocket Board controls and is not settled by this README review.

## Decision and limits

**Adoptable pattern:** lead with a small, reproducible piece of product evidence, then offer a few audience-specific routes and leave full reference navigation discoverable. Cite exact files and outputs; label demonstrations and hypotheses.

**What is verified:**

- immutable README differences and links to the actual implementation and sample;
- byte-identity of two runnable files and isolated Python output;
- a full clean-clone run of the first success and the five checks;
- provider CI on the PR head;
- GitHub-rendered horizontal reflow at three emulated viewport widths, plus **selected** contrast observations (light at 1280 px; dark at 375 px). The other width/theme combinations are not documented as tested.

**What is not verified:** improved traffic or conversion, time to first success for actual users, screen-reader and visible-focus behaviour, and real devices.

### Primary guidance consulted (2026-10-22)

- [GitHub Docs, About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes): README scope, first-use/help/contribution information and relative links.
- [Open Source Guides, Starting an Open Source Project](https://opensource.guide/starting-a-project/): project audience, basic documentation and expectations.

The guidance supports the *decision criteria*, while the GitHub revisions and actual command above support the *specific outcome*. This case is original narrative and measurements; it copies no unrelated project's artwork or README.