# Three ways to open the same README

**A controlled layout experiment, not three products.** These first screens all
describe the *same fictional* `PocketDiff` command. No PocketDiff package or
command was released or executed. The example report is invented. The point is
to choose a hierarchy for a reader rather than generate a generic hero.

## Fixed facts: do not change the story to flatter the layout

- **Job:** compare January and February CSV exports locally, by the same key column.
- **Promise:** no upload; the imagined data stays on the reader's computer.
- **Illustrative command:** `pocketdiff january.csv february.csv --output changes.csv`.
- **Illustrative report:** **18 changed**, **2 added**, **1 removed**; saved to `changes.csv`.
- **Evidence limit:** no implementation, benchmark, installed package or verified
  terminal run exists. Numbers and output are part of a fictional brief.

Each linked file is a self-contained **first-screen specimen** with an explicit
fictional disclaimer. Compare its opening from the top, not a screenshot crop:

1. [Editorial](editorial.md) — quiet prose and the result up front, for someone
   asking whether the tool addresses their job.
2. [Documentation-led](documentation-led.md) — inputs and constraints first,
   for an evaluator who needs operational boundaries before a preview.
3. [Playful technical](playful-technical.md) — a memorable, text-only
   change summary first, for an exploratory maker audience.

## Why the differences matter

| Decision | Editorial | Documentation-led | Playful technical |
| --- | --- | --- | --- |
| First question | What problem does it solve? | Can I use it with my data? | What will I see? |
| Main device | One measured sentence | A compact input/output specification | Three labelled change counts |
| Primary next move | Inspect sample command | Check constraints then command | Read the example transcript |
| Design risk | Too little context | Feels like a manual before a promise | Decoration displaces trust |

None is a universal winner. The presentation is a choice about reader priority,
not a grading rubric or evidence that a layout is accessible in every renderer.
The outputs remain explanatory **text** rather than color or an external image.

## Adapt without copying a generic layout

Write your own [design-intent brief](../DESIGN_INTENT.md): audience, their next
question, verifiable output, constraints, typography/hierarchy, owned assets,
light/dark and narrow-screen alternatives, accessible states and an explicit
list of rejected embellishments. In a real project replace these invented numbers
with an observed result at an exact revision, link working code, and test the
shortest first-success command. Do not paste the fictional transcript as proof.

To review, open each variant in GitHub's Markdown renderer at wide and narrow
widths and both themes, then inspect heading navigation and text-only reading.
That manual review has **not** been performed here; source and link checks
are necessary but insufficient. See the [visual README guide](../../../guides/readme-visuals.md)
and the [original before/after specimen](../README.md).
