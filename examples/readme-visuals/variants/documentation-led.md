# PocketDiff: local CSV comparison

> Fictional README first-screen specimen. There is no PocketDiff package to
> install or run; the numbers and command are illustrative.

## Inputs and boundaries

| Item | Example contract |
| --- | --- |
| Input A | `january.csv` |
| Input B | `february.csv` |
| Prerequisite | Both CSV exports use the **same key column** |
| Data handling | Local comparison, **no upload** |
| Output | `changes.csv` |

## Expected shape of an example report

**18 changed** · **2 added** · **1 removed**. These are fictional counts, not
observations from a test run.

```console
$ pocketdiff january.csv february.csv --output changes.csv
18 changed · 2 added · 1 removed
Wrote changes.csv
```

**Status:** Specimen only—no executable PocketDiff or tested setup steps.
For an actual tested command with a fixture, use the
[Rowcount starter](../../cli-starter/README.md).

[Compare the other first screens](README.md).
