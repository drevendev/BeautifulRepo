# Trade simulation: a shipped milestone described as pending

**Case status, 2026-10-29: in progress.** This is a pinned, source-level before/after
study of a real repository. The README correction happened in the target's own
merged PR; BeautifulRepo documents rather than repeats that target change.
Full before/after audits, fresh-clone first success and rendered accessibility
checks remain unverified. A byte-identical local fixture success/failure and
target-native CI at the correction's merge SHA are recorded below; neither
completes the full case.

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

Expected output from the pinned JSON source, **also observed from an isolated
local byte-identical fixture copy** on 2026-10-29. A clean clone was not run:

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

## What remains unverified

- The BeautifulRepo `repo_audit.py`, `docs_links.py` and
  `html_navigation.py` **were not run** against before/after checkouts;
  no pinned-tool audit totals are claimed.
- The Python source-inspection one-liner and a missing-file failure path
  **were run only against a hash-verified isolated fixture copy**, as documented
  above. A clean Git clone, its checkout steps and other failure paths remain
  **NOT RUN**.
- No `npm ci`, TypeScript typecheck, Vitest, Vite build or legacy .NET
  build/test was run **locally for this case**. Target-native GitHub CI was
  checked at the correction's merge SHA as recorded above; the later
  after-snapshot has not been independently re-tested here.
- The live GitHub Pages deployment, narrow-width light/dark rendering,
  400% zoom, keyboard and screen-reader behavior were **not observed**.
- Repository description, topics, homepage and tracked security-policy presence
  **were inspected** on 2026-10-29. Private reporting enablement, inherited
  policies, current-release follow-on milestones and performance metrics remain
  **unverified**; none of the target metadata or settings was changed.

To mark this a **complete case**, follow the
[five-step procedure](README.md): same pinned BeautifulRepo tool checks
before and after, a fresh-clone first success and failure path, and a
documented 320 px visual review with its limitations. The historical
target-native CI evidence above covers only the original correction merge;
it is not current-after-snapshot or browser acceptance. Until then this
remains a useful partial, not a fully accepted case.
