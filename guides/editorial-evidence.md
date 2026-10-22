# Editorial evidence kit: accurate words with a recognizable voice

A repository README, changelog, and announcement make promises readers may
rely on. Edit them around **claim → evidence → consequence**, not repeated
superlatives. This is a manual editorial method; it does not assign an
originality score, detect AI authorship, or make a generic tone into a voice.

## A four-pass review

1. **Audience and job.** Name the concrete person and decision. "Maintainers
   looking for a local check" is more useful than "everyone."
2. **Claim and evidence.** Pair every measurable or categorical claim with a
   file, command, fixture, test, or qualification a reader can inspect.
   If the evidence is missing, remove the claim or label it as expected.
3. **Reader consequence.** Explain what changes for the reader: the next
   command, the shape of the output, the remaining risk, or the migration step.
4. **Voice and reduction.** Replace stock words with project-specific nouns
   and verbs. Remove duplicate promises, unsupported numbers, invented impact,
   and calls to action pointing nowhere. Retain deliberate humor or simplicity
   when it helps *this* audience.

Classify each sentence as **verified**, **expected**, or **unknown**.
"CI passed on Python 3.11 and 3.14" needs an actual run.
"This should reduce onboarding questions" is a hypothesis, not an outcome.
"We saw 40% higher conversion" is inadmissible without the actual measurement.

## Same facts, different copy: README first screen

**Facts held constant:** BeautifulRepo is a source-available handbook with
small offline Python checks and five starter categories; it is not a hosted
service, an official GitHub standard, or a distribution on PyPI.

**Before — generic:**

> BeautifulRepo is the ultimate modern toolkit that supercharges every
> repository. Dive in to experience the future of open source!

**After — specific:**

> Make a repository easier to understand and maintain. Use a tested CLI example,
> five starter types, and offline documentation checks from a checkout with
> Python 3.11+.

**Why:** the revision identifies a job, actual artifacts, and a prerequisite.
It does not pretend that the tools can measure beauty. Its first command belongs
next to a real example, not behind a promotional banner.

## Same facts, different copy: patch announcement

**Facts held constant:** the repository has a documentation checker for local
HTML links and section anchors; Python 3.11 and 3.14 jobs passed on the PR head.
It does not fetch external URLs or certify assistive-technology behavior.

**Before — generic:**

> Huge quality update! Our flawless link validation is now smarter than ever.

**After — specific:**

> The offline documentation check now catches missing local HTML assets and
> section anchors alongside the existing Markdown destination checks.
> The PR ran successfully on Python 3.11 and 3.14. External sites and
> screen-reader behavior remain outside this check.

**Why:** "flawless" could mislead maintainers about untested coverage.
The revision says what the check catches, what ran, and what it cannot claim.
A future announcement must update the CI reference and describe any
changed behavior; this paragraph is an example, not a release notice.

## Same facts, different copy: changelog entry

**Facts held constant:** the tested `rowcount.py` example counts three
nonblank data records in `sample.csv`; it does not validate CSV schemas.

**Before — generic:**

> Improved CLI example with major performance and usability enhancements.

**After — specific:**

> Documented `python examples/cli-starter/rowcount.py
> examples/cli-starter/sample.csv` and its expected `Data rows: 3`
> output. Clarified that the example counts data records but does not
> validate column types or file schemas.

**Why:** there is no benchmark or performance change in the facts. A good
entry names the visible behavior and the boundary without inventing impact.

## Generate three *different* opening angles

For the same facts above, try three distinct leads before selecting one:

- **Task-first:** "Find the first broken step between your README and a
  reader's successful command." Useful for maintainers actively debugging
  onboarding.
- **Artifact-first:** "Five runnable starter categories and offline checks,
  documented from source." Useful for readers evaluating deliverables.
- **Constraint-first:** "Improve your repository without publishing a package
  or installing third-party Python dependencies." Useful for maintainers
  avoiding extra infrastructure.

These are **alternatives**, not three paragraphs to combine. Check each
against the actual source and audience, then delete the two that do not fit.
An anti-duplication pass should catch repeated first-sentence shape,
generic "seamless / revolutionary / game-changing" adjectives, and identical
calls to action. Choosing voice remains a human judgement.

## Lint only what a machine can decide

The repository's standard-library checks can verify local paths, syntax and
example contracts. They cannot verify truth, intent, humor or original voice.
Optional prose linters such as [Vale](https://vale.sh/) are worth evaluating
**only** when a project has written language-specific rules and accepts that
extra tooling; no Vale install or enforced English-only rules are added here.
Research projects and multilingual documents should not inherit arbitrary
English clichés as a blocking CI policy.

## Final editorial gate

- [ ] The opening sentence names an actual job and artifact.
- [ ] Every result claim links to a reproducible check or carries a limitation.
- [ ] Expectations and unknowns are not presented as measured benefits.
- [ ] The example uses the same facts before and after.
- [ ] The next action names a working path, not an unpublished product.
- [ ] A reader can recover the essential information without an image.
- [ ] An editor has chosen tone and removed repeated filler manually.

**Primary references, reviewed 2026-10-21:**
[GitHub — About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
and [Open Source Guides — Starting a Project](https://opensource.guide/starting-a-project/).
Those sources guide reader-first structure; this kit's three angles and
claim/evidence procedure are original editorial recommendations, not
official GitHub policy.

