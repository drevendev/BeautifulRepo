# Rowcount — decide from a concise contract

**Count nonblank CSV data records locally, after a required header.** This
checkout-only Python example is not a packaged utility or hosted service.
It needs Python 3.11+ and no third-party dependencies.

## Contract at a glance

| Question | Actual behavior |
| --- | --- |
| What counts? | Nonblank data records after the header; the header and wholly blank records do not count. |
| What is checked? | A nonblank CSV header and the column count of each nonblank data record. |
| What is **not** checked? | Data types, schemas, application-specific CSV dialects or semantic correctness. |
| Where does it run? | Locally on a file you name. There is no upload or network service. |

## Reproduce the result

From the BeautifulRepo repository root:

```bash
python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv
```

Verified stdout for the checked-in [sample.csv](../../cli-starter/sample.csv):

```text
Data rows: 3
```

The file contains a header and three data records. Inspect the
[implementation](../../cli-starter/rowcount.py) and
[documented error behavior](../../cli-starter/README.md) before adapting it.
Mismatched row widths produce a nonzero exit and a diagnostic, not a count.

**Use this treatment when:** a technical reader needs to decide whether the
input contract and limitations fit before trying the command. It trades the
editorial opening and transcript illustration for a scannable decision card.

[Compare all three entrances](README.md) ·
[Read the design-intent brief](DESIGN_INTENT.md).

_This is a third first-screen arrangement of the same working example, not a
second implementation, independent benchmark or accessibility certification._
