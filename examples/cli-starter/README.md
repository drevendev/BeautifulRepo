# Rowcount: a small CLI README that proves its example

**Count nonblank data records in a UTF-8 CSV file without uploading the data.**

This is a deliberately small, working **documentation example** for
[BeautifulRepo's CLI repository guide](../../guides/cli-repositories.md), not a packaged
application or a recommendation for production CSV validation. It uses only Python's
standard library.

## Try it in a checkout

Prerequisite: **Python 3.11+**. From the BeautifulRepo repository root:

```bash
python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv
```

Expected stdout (tested, no color or network required):

```text
Data rows: 3
```

The input is [sample.csv](sample.csv). The tool counts records *after* the first header
record, ignores fully blank records, and preserves quoted CSV newlines. It reports an
error when a nonblank record has a different number of columns than the header. This is
not a schema, type, delimiter, or adversarial-data validator.

## Commands and results

| Command | Result |
| --- | --- |
| `python examples/cli-starter/rowcount.py --help` | Usage and argument details; exit 0 |
| `python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv` | Prints `Data rows: 3`; exit 0 |
| `python examples/cli-starter/rowcount.py missing.csv` | Prints a plain error to stderr; exit 1 |
| `python examples/cli-starter/rowcount.py` | Prints usage to stderr; exit 2 |

**Privacy:** the script reads only the explicitly supplied local file. No network calls,
telemetry, credentials or environment configuration are needed.

## Run the example's tests

```bash
python -m unittest discover -s tests -p 'test_cli_starter.py' -v
```

The tests exercise the advertised sample, help, usage errors and common malformed inputs.
They do not prove portability across every Python version, shell, CSV dialect or platform.

## Adapt for a real CLI project

Keep the concise promise, first working command, expected result and truthful limitations.
Replace this direct `python path/to/script.py` workflow with a **verified** installation or
executable command only after packaging or distribution exists. Add supported operating
systems, an uninstall/update path, versioning, support status and security guidance where
appropriate. Do not present fictitious `pipx`, Homebrew or package-registry commands as
published releases.
