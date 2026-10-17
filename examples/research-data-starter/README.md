# Fictional site counts: a reproducible data-repository example

This is a **fully fabricated** dataset for demonstrating a transparent
analysis path, not scientific observations or an operational dataset.
It contains no people, coordinates, access credentials or real measurements.

## Dataset and provenance

- `data/observations.csv`: six invented rows across two fictional sites,
  A and B, on three arbitrarily chosen dates. This file was authored directly
  for the BeautifulRepo documentation example; it was not obtained from an
  external data provider.
- CSV columns: `date` (valid calendar date in ASCII `YYYY-MM-DD` form),
  `site` (fictional identifier matching `[A-Z][A-Z0-9_-]*`), and `count`
  (nonnegative integer written with ASCII digits `0–9`). The column order is
  exactly `date,site,count`; missing values and surrounding whitespace are rejected.
- Primary key: (`date`, `site`) must be unique.
- Units: invented event counts; there is no sampling frame or real-world claim.
- Source terms: files are provided as part of BeautifulRepo's MIT-licensed
  example. The fixture does not imply that external datasets share this license.
- **Fixture integrity:** SHA-256 of the exact checked-in `data/observations.csv` bytes is
  `126286146ce550b525a0a7d995507a8c8c9db8155471fed79a1f4243483089e8`.
  The test suite verifies this digest to flag accidental changes to the teaching fixture.
  This is evidence for *these bytes only*, not a provenance record for real research.

## Reproduce the result

**Verified:** Python 3.13.5 on 2026-10-16 in the local example directory;
other environments have not been independently checked. Standard library only.

From `examples/research-data-starter`:

```bash
python analysis.py
python -m unittest discover -s tests -v
```

The analysis uses the checked-in CSV by default and emits JSON equivalent to:

```json
{
  "grand_total": 60,
  "rows": 6,
  "totals": {
    "A": 36,
    "B": 24
  }
}
```

Use `python analysis.py --input PATH` to inspect another *local* CSV with the
same schema. The tool does not fetch external data or modify input files.
Validation rejects duplicate (date, site) records, invalid calendar dates,
negative/noninteger counts, missing fields and unexpected columns.

The result is a toy sum, not research replication, scientific validation,
privacy certification or evidence that any external data was collected. The
sample does not have a DOI, public archive deposit or paper citation.

Read the [research-data repository guide](../../guides/research-data-repositories.md)
for the wider checklist. The source files here inherit the repository's
[MIT license](../../LICENSE).
