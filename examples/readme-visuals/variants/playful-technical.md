# CSV changed. Here is the shape of the difference.

> Fictional README first-screen specimen—not an installed product.
> PocketDiff has no executable command; this sample report was invented.

## PocketDiff, in three numbers

**18 changed** rows. **2 added** rows. **1 removed** row.

`changes.csv` would hold that report. Two exports come in, one explanation
comes out. Everything happens locally: **no upload**.

**Try to picture the workflow (not a real command to run):**

```console
$ pocketdiff january.csv february.csv --output changes.csv
18 changed · 2 added · 1 removed
Wrote changes.csv
```

**The catch:** the sample assumes both CSV exports use the **same key column**.
The counts are illustrative, not performance or correctness evidence. If you
need executable code now, start with the
[tested Rowcount example](../../cli-starter/README.md).

[Compare the other first screens](README.md).
