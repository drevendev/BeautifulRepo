# Repository audit: fix observations, not a score

This fictional before/after example shows how the [entry-point audit](../../guides/repository-audit.md)
turns visible README problems into specific changes. It does not create a real project,
choose a license, or modify the checkout you run it from.

From the BeautifulRepo root:

```bash
python examples/repository-audit/demo.py
```

The demonstration creates one temporary directory, writes two fictional README variants
there in sequence, audits each, prints JSON, and removes the temporary directory.
Only this demonstration writes its disposable fixture; the audit tool itself is read-only.

## Before

The first README has unfinished prose, a heading jump, and a layout table with empty
headers. The audit reports four warnings: those three observations plus a missing local
license file. Missing dedicated contribution guidance is informational.

## After

The revised README describes the fictional project, uses a level-two subsection, and
replaces the layout table with a list. The report now has one warning and one informational
finding. The license and contribution observations remain intentionally unresolved.

Expected summary:

```text
before: 0 errors, 4 warnings, 1 informational finding
after:  0 errors, 1 warning,  1 informational finding
```

The demonstration's output and expected observations are regression-tested. No license is
invented merely to make a checker green, and no numeric quality or accessibility rating is
produced. A maintainer still needs to assess the real project's publishing and contribution
arrangements before deciding what to add.

See the [tool contract](../../guides/repository-audit.md#scope-and-reading-boundaries)
and [source code](demo.py). The example inherits the repository's [MIT license](../../LICENSE).
