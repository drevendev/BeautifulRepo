# Rowcount — count CSV records locally

**How many data records are in this CSV?** Rowcount answers with one line,
without uploading the file.

It is a small, working Python example, **not an installable package**.
Start with the checked-in [sample.csv](../../cli-starter/sample.csv), which
contains a header and three data records.

## First success

From the BeautifulRepo root, with Python 3.11+:

```bash
python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv
```

Observed output for that exact sample:

```text
Data rows: 3
```

Rowcount excludes the header and fully blank rows. It checks the column count
of nonblank rows, but does **not** validate CSV types, schemas or arbitrary
dialects. No network call is required.

[Inspect the working implementation](../../cli-starter/rowcount.py) ·
[Read its test and error boundaries](../../cli-starter/README.md) ·
[Compare the terminal-led entrance](terminal-led.md).

_This page is an alternative README first screen, not a second product._
