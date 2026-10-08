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

## Generated notes are a starting inventory

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
verification or deployment is performed or claimed by BeautifulRepo.
