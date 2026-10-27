# Release notes that help users upgrade

A release note is a **user-facing explanation of one shipped state**: what changed,
who is affected, whether action is required, and where to verify the details.
It is not a pasted list of commits, internal tickets, or pull request titles.

## Do not confuse the artifacts

- A **Git tag** identifies a commit in the repository history.
- A **GitHub Release** is a separately published record attached to a tag, which may
  have human-readable notes and downloadable assets.
- A **CHANGELOG** is durable project history; it need not imply a release exists.

The tag date and the release publication date can differ. Never infer that
downloadable software exists from a tag or a draft note alone.

## Write for the person upgrading

Start with the result and the affected audience. A useful note answers:

1. What behavior changed, and who will notice it?
2. Is an upgrade step needed? Provide a command or precise configuration change.
3. Which incompatibilities and limitations remain?
4. Which tag, previous release, and comparison establish the exact scope?
5. Which checks and platforms were actually verified?

Use headings such as **Breaking changes**, **Added**, **Changed**, **Fixed**, and
**Known issues** when they improve scanning. Leave out empty ceremonial sections.

## Before and after: a fictional CLI release

**Weak:** “0.4.0: merged #42, #43; refactored parsing and fixed CSV.”

**Better, illustrative only (not a real release):**

> **ExampleCLI 0.4.0 — clearer CSV reports.**
>
> **Upgrade action:** rename `--csv-output` to `--output` in automation scripts.
> The old option is no longer accepted.
>
> **Fixed:** malformed CSV now produces exit code 1 and a plain stderr error.
>
> **Known limitation:** PowerShell behavior has not been verified.
>
> **Evidence before publishing:** add the real tag and target commit, the exact
> previous-tag comparison, relevant PRs, and actual test results.

The second example explains impact and an action instead of treating engineering
activity as the product. Its evidence remains visibly unverified.

## Announce the same change without launch filler

These two **illustrative announcements** use the same fictional ExampleCLI 0.4.0
facts as the release note above. They do not describe a real release,
a downloadable package, or tests performed by BeautifulRepo.

**Weak announcement:**

> Exciting ExampleCLI 0.4.0 update! `--csv-output` was renamed to `--output`
> and the old option is no longer accepted. Malformed CSV now exits with code 1.
> PowerShell behavior has not been verified. Enjoy these amazing improvements!

**Useful announcement:**

> **ExampleCLI 0.4.0 (fictional): update your CSV option.**
> If a script uses `--csv-output`, replace it with `--output` before upgrading;
> the old option is no longer accepted. Malformed CSV now exits with code 1,
> so scripts can handle that failure explicitly. PowerShell behavior has not
> been verified.

The facts did not change; the wording and reader path did:

- **Claim:** replace "amazing improvements" with the specific option rename and
  CSV error behavior. Neither superlatives nor an invented success metric prove value.
- **Evidence:** keep the unverified PowerShell limitation and the fictional status
  visible. Before a *real* announcement, link the tag, diff and actual test evidence.
  This example provides none of those artifacts.
- **Reader impact:** tell maintainers which flag to replace and what exit code
  to handle instead of asking them to "enjoy" an unspecified improvement.

A short announcement can prioritize the next action; the release note should
carry the detailed migration, known limitations and verification references.

## Generated notes are a starting inventory
## Two layouts using a real merged change

The [evidence-bound release presentation](../examples/release-presentation/README.md)
compares a short **Unreleased changelog entry** with a more explanatory
**unpublished release-note draft**. Both reuse the *same real* Markdown link
checker change, pinned merge commit and PR-head CI evidence; neither implies
a new tag, downloadable artifact or published release. The example shows how
reader priority, not an invented version number, determines the layout.


GitHub-generated notes can list merged pull requests, contributors and comparisons.
A `.github/release.yml` file can categorize changes by labels. These tools help
collect facts but cannot reliably decide user impact: **review the generated list**
and remove internal-only noise. Keep a Changelog 2.0 likewise cautions that a
commit message and a reader-facing changelog entry serve different audiences.

Do not make a changelog entry mandatory on every tiny PR merely to satisfy a CI
check. That turns a useful communication artifact into low-signal bookkeeping.

## Publication checklist

- [ ] Resolve the actual tag, target commit, preceding version and diff.
- [ ] Verify version name, affected platforms and prerequisite versions.
- [ ] Confirm that stated downloads and install commands really exist.
- [ ] Test the upgrade path on the platforms you claim to support.
- [ ] Link migrations and caveats rather than burying them in vague prose.
- [ ] Review generated notes manually; verify links and render formatting.
- [ ] Keep drafts clearly identified; publishing a release is a separate action.

Start from the [release-note template](../templates/RELEASE_NOTES.template.md).
Do not invent version numbers, performance gains, test results or asset verification.

## Sources and limits

Reviewed **2026-10-09**:

- [GitHub — About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [GitHub — Automatically generated release notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes)
- [GitHub — Managing releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Keep a Changelog 2.0](https://keepachangelog.com/en/2.0.0/)

This guide is writing advice, not a release tool. No release, tag, artifact
verification or deployment is performed by following it. BeautifulRepo's own
tagged versions are listed on its [Releases page](https://github.com/drevendev/BeautifulRepo/releases).
