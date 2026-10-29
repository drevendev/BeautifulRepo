# Trade simulation: a shipped milestone described as pending

**Case status, 2026-10-29: in progress.** This is a pinned, source-level before/after
study of a real repository. The README correction happened in the target's own
merged PR; this BeautifulRepo change only documents it. The full case procedure's
fresh-clone tool runs, runtime first success, failure path and rendered checks
have **not** been completed.

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

Expected output **derived by parsing the pinned JSON source**, not by running
the command in a clean clone:

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

## Editorial decision and trade-off

**Adopt:** tie milestone status to a real release, describe a saved-run UI
as a viewer rather than a running engine, and put one source-derived result
next to a command a reader can inspect. The trade-off is that the small JSON
inspection proves only artifact accessibility; it does not replace a full
runtime demo, tests or production verification.

The issue [#82](https://github.com/drevendev/BeautifulRepo/issues/82)
also proposes metadata and security changes, but they were not executed
or assessed in this case. No new changes were made in `trade_simulation`.
This source-only write-up does not close
[#82](https://github.com/drevendev/BeautifulRepo/issues/82) or the
[real-case epic #88](https://github.com/drevendev/BeautifulRepo/issues/88).

## What remains unverified

- The BeautifulRepo `repo_audit.py`, `docs_links.py` and
  `html_navigation.py` **were not run** against before/after checkouts;
  no pinned-tool audit totals are claimed.
- The Python source-inspection one-liner **was not run in a fresh clone**;
  its displayed output is calculated from the inspected JSON.
  No failure-path execution was recorded.
- No `npm ci`, TypeScript typecheck, Vitest, Vite build or legacy
  .NET build/test was run for this case; no target CI result is attributed
  to this documentation work.
- The live GitHub Pages deployment, narrow-width light/dark rendering,
  400% zoom, keyboard and screen-reader behavior were **not observed**.
- No repository topics, description, reporting settings, current-release
  follow-on milestones or performance metrics were audited.

To mark this a **complete case**, follow the
[five-step procedure](README.md): same pinned tool checks before and after,
target-native CI evidence, a fresh-clone first-success and failure path,
and a documented 320 px visual review with its limitations. Until then,
its contribution is the exact-source reasoning, not a claimed full acceptance.
