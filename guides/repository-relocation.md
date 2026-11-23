# Move or rename a repository without losing its readers

A GitHub redirect is not proof that a repository still works. The old README
may open, while a downstream GitHub Action, Pages site, package coordinate or
first-run instruction fails. This is an **evidence-led preparation recipe**,
not authorization to rename, transfer or change BeautifulRepo's settings.

Use the [editable verification record](../templates/REPOSITORY_MOVE.template.md)
for a specific project. Keep private credentials and confidential contacts out
of public migration notes.

## What GitHub actually promises

For a **same-owner repository rename**, GitHub redirects ordinary repository
links and Git clone/fetch/push traffic. However, it explicitly **does not
redirect calls to a GitHub Action hosted in the renamed repository**:
`uses: OLD-OWNER/OLD-REPO@...` consumers can fail with `repository not found`.
Project-site Pages URLs are excluded from repository redirects. Reusing the
old name later disables the old redirect.

For a **repository transfer** to another owner, GitHub documents web and Git
redirects, but not Pages site redirects. Transfers have permission and
destination constraints; packages may transfer or lose their repository link
depending on their registry. Do not infer an Action or package PASS from an
ordinary web redirect. Account/organization username changes are distinct
operations with different rules.

Primary sources (reviewed **2026-11-23**, GitHub.com, not Enterprise Server):
[renaming a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)
and [transferring a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository).
These are provider promises, **not** an observed migration test.

## Before the authorized change

1. Record exact old/new `OWNER/REPO`, change type, date, decision authority,
   default branch and full last-known-good source SHA. Confirm actual
   destination permissions and policy separately.
2. Inventory **consumers**, not just hyperlinks: README and badges; docs;
   `.github/workflows` references (`uses:`); Actions published to others;
   Pages; packages and image registries; releases and downloads; external
   installation snippets and pinned source links. Unknown external consumers
   remain **UNKNOWN**, not absent.
3. Preserve a reader's **first success**: prerequisites, exact command,
   expected observable result, tested OS and source revision. Say *NOT RUN*
   for an old command that has not been reproduced.
4. Plan changes to downstream Action workflows, Pages URLs, package
   coordinates, private reporting and contribution routes. GitHub recommends
   a **new Action repository plus an archived old repository** rather than
   relying on a rename redirect for a published Action; archiving itself
   requires separate owner authorization.
5. Prepare truthful migration copy. Do not imply that redirects prove
   downloads, package availability, support or security reporting.

To locate *some* tracked literal references without modifying the checkout:

```sh
git grep -n -F 'OLD-OWNER/OLD-REPO' -- README.md guides templates .github
```

Replace the placeholders and adjust paths to the real checkout. No results
only means no matching literal in those tracked paths. It does not inspect
third-party repositories, hidden configuration, generated output or remote
users. Do not publish secret-bearing search results.

For an optional **Git-free, read-only** inventory with deterministic JSON output,
use the [repository reference preflight](../tools/README.md#inventory-old-repository-references-before-a-move):

```sh
python -I tools/repo_references.py --root ../target-checkout --old orchard-labs/maple-lint --format json
```

Run it from a BeautifulRepo checkout and set `--root` to the separate
repository you are reviewing. The example pair is fictional. It searches
selected local UTF-8 text files, case-insensitively, for the *literal*
`OWNER/REPO` substring; its line/column hits need human review, including
false matches inside longer names. It never runs the target's code or
shows surrounding source text. Exit **0** means no hits in the **scanned
subset**, **1** means hits, and **2** means incomplete evidence or invalid
input. Excluded folders, binary files, third-party consumers, remote
integrations, redirection behavior and actual workflow success are **not
verified**. Preserve these as UNKNOWN until separately checked. Review
filenames before sharing output from a private checkout.

The preflight checks the opened file's type, link count and identity against
its no-follow metadata before reading bytes; a changed file produces
**incomplete**, not a false clean scan. This is a best-effort local inventory,
**not** an atomic filesystem snapshot or protection against every concurrent
ancestor-directory replacement or in-place edit. Do not scan a maliciously
mutable tree as if it were a sandbox.

## Verify after the authorized move

Capture dated evidence for **each** applicable surface:

- **Landing route:** open the new repository URL directly. Check the README
  promise, accessible text alternatives, local images/links, issue/PR
  navigation and actual CONTRIBUTING and SECURITY routes.
- **Git and first success:** in an authorized networked environment, test
  `git ls-remote https://github.com/NEW-OWNER/NEW-REPO.git HEAD`.
  In a **disposable** clone, run the documented first command and compare
  its observed result. Do not execute untrusted repo code on valuable machines.
- **Existing clones:** inspect `git remote -v`; when appropriate, update
  that local clone via
  `git remote set-url origin https://github.com/NEW-OWNER/NEW-REPO.git`.
  This does not rename or transfer anything on GitHub.
- **Downstream workflows:** actually run representative `uses:` consumers
  against the new Action coordinate. Verify separately Pages, package
  installation, published docs, badges, assets and releases; a working
  repository redirect cannot establish these outcomes.
- **Continuity:** publish only observed results and known breakages. Leave
  owner/next-check/date for anything **FAIL**, **NOT RUN** or **INCONCLUSIVE**.
  Avoid reusing the old name without understanding redirect consequences.

## Worked fictional example

Suppose `orchard-labs/maple-lint` is renamed
`orchard-labs/spruce-lint`. Old issue links may redirect, but a customer
workflow with `uses: orchard-labs/maple-lint@<full-commit-SHA>` can fail
under GitHub's documented Action exception. The maintainer must identify
and verify new consumer references rather than claiming compatibility
from the redirect. A former Pages URL is **NOT RUN** until directly checked.
This is an illustration, **not** an actual move, test or published project.

**Acceptance:** preserve the path from promise → evidence → first success →
trust → contribution at the *new* location, with external exceptions named.
