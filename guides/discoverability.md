# Make a repository discoverable without overpromising

A repository can be well documented and still hard to recognize in a search result
or link preview. Its GitHub **About description, topics, optional homepage, and
social preview** should help a new reader decide whether the project solves
their problem. They are *signposts*, not evidence of quality.

This recipe changes no repository settings. Adapting its suggestions requires
maintainer authority; a guide or a pull request does not authorize metadata,
hosting, or promotional changes.

## 1. Write the promise before choosing keywords

Read the opening of your current README and one verified first-success example.
Complete this sentence: **For [audience], this repository provides [thing] so
they can [outcome].** Remove claims the repository cannot demonstrate.

For BeautifulRepo, a possible About description is:

> Practical guides, runnable starters, templates and offline checks for maintainable GitHub repositories.

A poor alternative would be:

> The ultimate AI-powered toolkit guaranteed to make any repo viral and production-ready.

The second version makes unverifiable performance and completeness claims.
The first points to real [working examples](../examples/README.md) and
[offline checks](../tools/README.md), without promising packages, hosted
services, external reviews, or adoption.

**Quick test:** Can a visitor find the named deliverable within two clicks of
the [README](../README.md), and reproduce at least one relevant result?
If not, fix that path before polishing the metadata.

## 2. Choose topics for accurate classification

GitHub topics can help people explore repositories by subject. They are not a
substitute for explaining what the project actually does. Start with **three to
five** distinct, specific topics, and ask what each one describes:

- **Function:** `readme` or `documentation` only if README/documentation
  work is central, not merely present in every repository.
- **Audience or domain:** `repository-maintenance` if maintainers can really
  apply the materials to repository upkeep.
- **Implementation:** `python` only when Python is important for someone
  evaluating or using the project; a tiny maintenance script alone may not
  justify it.

For BeautifulRepo, a plausible *proposal to assess* is
`documentation`, `readme`, `open-source`, `repository-maintenance`.
Check the actual deliverables and existing topic usage before choosing any
subset. These are **not** claims that its live topics have been changed.

Do **not** add `hacktoberfest`, `good-first-issue`, a grant name, or a
popular framework to chase views if the repository has no genuine current
connection to it. Do not turn temporary event tags into evergreen metadata.

GitHub currently permits **at most 20 topics**, each up to **50 characters**,
using lowercase letters, numbers and hyphens; topic names are public even on
private repositories. These are platform rules, not a recommendation to fill
all available slots. Recheck them when editing metadata.

## 3. Decide whether you need a homepage

A repository URL can be the project's single, trustworthy home. Leave the
optional homepage field empty if you do not have a separate, maintained page
that offers something the README cannot.

Use a homepage only when it is real, accessible, and useful: for example a
working demo, a maintained documentation site, or a project website with a
clear route back to source. A link to a placeholder, dead demo, or unrelated
profile adds work for the reader. GitHub Pages and a custom domain are **not**
prerequisites for discoverability.

The [Open Source Guides discussion of finding users](https://opensource.guide/finding-users/)
supports a clear project message and a single recognizable destination; it
does not require buying a domain or operating another platform.

## 4. Decide whether an image will add evidence

A social preview is useful if it communicates the *specific* product:
for example, a legible screenshot of a real tool or a coherent diagram of a
demonstrated workflow. A generic gradient, fake analytics or unreadable
collage can make the link less informative.

GitHub's current guidance recommends PNG, JPG or GIF **under 1 MB**, at least
**640 × 320 px**, and ideally **1280 × 640 px**. Check that any text survives a
small preview, that the image looks acceptable on light and dark surfaces, and
that critical facts are also present in normal README text. Transparency is
supported, but a solid background may be safer across sharing platforms.

Leaving the preview unchanged is a valid decision. Do not upload images merely
to fill a customization field, and do not copy another project's branding.

## 5. Verify the result for free

Before proposing any metadata change:

1. Open the **public** repository page in a signed-out browser. Compare its
   README promise and first runnable example with the About description and
   topics. Check that a proposed homepage actually leads to a useful page.
2. Inspect the public GitHub REST endpoint
   `https://api.github.com/repos/OWNER/REPO` for `description`,
   `homepage`, and `topics`. This is **read-only** and can be requested
   without a token for a public repository; unauthenticated requests are
   rate-limited. Do not paste credentials into a web page or script.
3. If a social preview already exists, inspect an actual repository-link
   preview on a platform where you already have access. Sharing platforms
   cache previews: one appearance is not a guarantee of identical rendering
   everywhere. Do not publish a post just to run this check.
4. Note any discrepancies: misleading topic, unverified claim, dead homepage,
   unreadable image, missing first-success route. Fix the reader path first;
   edit settings only through an explicitly authorized maintainer workflow.
5. Repeat the same checks after an authorized change. Record the observation
   date, not stars, imagined click-through, or traffic you cannot measure.

**Example decision for BeautifulRepo (reviewed 2026-10-20):** its public
README describes a working handbook, starter examples, and offline tools. A
short About description and several relevant topics would help classify
those deliverables. A separate homepage is not necessary while the repository
itself provides the working entry point. Actual metadata changes are tracked
separately in [issue #20](https://github.com/drevendev/BeautifulRepo/issues/20);
this guide does **not** make them.

## Review checklist

- [ ] Description names a real audience, output, and use without superlatives.
- [ ] Each topic is relevant today, not borrowed for a temporary popularity boost.
- [ ] Homepage exists and helps—or is deliberately blank.
- [ ] Preview adds recognizable evidence—or stays unchanged.
- [ ] README and example provide the promised first success.
- [ ] Public metadata was read back; limits and review date are recorded.
- [ ] No settings, hosting, outreach, or release action is inferred from this guide.

## Primary sources and limits

Reviewed **2026-10-20**:

- [Open Source Guides: Finding Users](https://opensource.guide/finding-users/)
  — define a clear message and recognizable project home; audience outreach
  is a separate decision, not a step in this repository recipe.
- [GitHub Docs: Classifying with topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)
  — actual topic purpose, syntax, count, and visibility rules.
- [GitHub Docs: Social preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
  — optional image types, size, dimensions, and transparency limitations.
- [GitHub REST API: Get a repository](https://docs.github.com/en/rest/repos/repos#get-a-repository)
  — read-only public metadata inspection.

This is a reproducible editorial and metadata review, **not** a search-ranking
formula, SEO audit, traffic measurement, official endorsement, or permission to
alter someone else's repository settings.
