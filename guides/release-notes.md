# Release notes that help users upgrade

Release notes are not a dump of merged pull requests. They are a user-facing explanation of
one shipped state: what changed, who is affected, what action is required, and where to find
the exact history.

Reviewed 2026-10-04 against GitHub's release documentation and selected public repositories.

## Separate the artifacts

A **Git tag** marks a point in repository history. A **GitHub Release** is publication metadata
attached to a tag and can include notes and release assets. A **CHANGELOG** is durable project
history that may span many releases. They can support each other, but none is a substitute for
the others.

GitHub notes that a tag date and a release publication date can differ. When recording an
existing release, use the observed publication date (or say the release is not yet published);
do not substitute the tag date or infer availability from it.

## Start with reader impact

Lead with the changes a user needs to understand, not the order commits landed.

For each material change, answer:

- **What changed?** Name the behavior, interface, data format, workflow, or dependency.
- **Who is affected?** Distinguish all users from a narrow platform, integration, or use case.
- **What must they do?** State migration steps, configuration changes, or "no action required."
- **What can go wrong?** Call out known incompatibilities and important limitations.
- **Where is the evidence?** Link the relevant issue, pull request, documentation, or comparison.

Use headings such as **Breaking / upgrade required**, **Added**, **Changed**, **Fixed**,
**Deprecated**, and **Known issues** only when they make the release easier to scan. Empty
ceremonial sections add noise.

## Generated notes are an inventory, not the final explanation

GitHub's automatically generated release notes can include merged pull requests, contributors,
and a link to the full changelog. A repository may use `.github/release.yml` to categorize
entries by labels or exclude selected labels and users.

That automation is useful for completeness, but it cannot reliably decide user impact. Review
the generated list, promote consequential changes into a short narrative, remove internal-only
noise, and preserve links to the underlying work.

## Before publishing

- Verify the selected tag and target commit.
- Compare with the intended previous release or tag; do not assume "previous" from memory.
- Confirm the displayed version, release title, compatibility range, and upgrade instructions.
- Verify downloadable assets belong to the tagged source and record how they were produced.
- Link documentation for migrations or behavior changes that do not fit in the notes.
- If a release fixes a security vulnerability, coordinate the public note with the applicable
  security advisory rather than improvising disclosure in ordinary release prose.
- Render the draft and inspect headings, links, code samples, and long lines before publishing.

Drafts are useful review surfaces. A published release is a public project statement; generating
notes or creating a tag is not evidence that the release itself was reviewed.

## A practical note structure

Use [the release-note template](../templates/RELEASE_NOTES.template.md) as a starting point.
Keep the summary short enough to read before the detailed categories.

A good release note normally contains:

1. a one-paragraph outcome summary;
2. explicit upgrade or breaking-change guidance when needed;
3. grouped user-visible changes;
4. known issues or deferred fixes;
5. links to the exact tag/compare range and supporting work;
6. verification facts that were actually observed.

Do not invent download counts, compatibility claims, performance improvements, or test results.

## Observed repository patterns

### uv

At inspected revision `46b84fd0bfec23b72f29e8e2185ba68a65052f48`, uv keeps a
repository changelog with individual linked changes and archives older release lines into
versioned changelog files. Some entries add prose before the itemized changes when a release
needs a broader compatibility explanation.

**Apply:** keep detailed traceability while giving risky or consequential changes extra context.

**Not verified:** no uv release workflow, package artifact, or published binary was executed.

### GitHub CLI

At inspected revision `6fc1c29d5477bfe71da7af290eb481c0df7811f1`, GitHub CLI's
maintainer release documentation describes a release workflow that generates the changelog from
merged pull requests and then publishes release artifacts.

**Apply:** treat merged work as structured source material for notes, then review the resulting
release as a separate publication artifact.

**Not verified:** this inspection does not certify GitHub CLI's release infrastructure or signing
process.

## Primary sources

- GitHub, About releases:
  <https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases>
- GitHub, Automatically generated release notes:
  <https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes>
- GitHub, Managing releases:
  <https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository>
- uv changelog at inspected revision:
  <https://github.com/astral-sh/uv/blob/46b84fd0bfec23b72f29e8e2185ba68a65052f48/CHANGELOG.md>
- GitHub CLI release documentation at inspected revision:
  <https://github.com/cli/cli/blob/6fc1c29d5477bfe71da7af290eb481c0df7811f1/docs/releasing.md>

## Limits

This guide does not prescribe semantic versioning, create a release, verify release assets, or
assert that BeautifulRepo currently has a release automation pipeline.
