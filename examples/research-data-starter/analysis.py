"""Reproduce an aggregate of a *synthetic* local CSV dataset.

The exercise never downloads data or imports code from a target repository.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import json
from pathlib import Path
import re

EXPECTED_COLUMNS = ["date", "site", "count"]
DEFAULT_INPUT = Path(__file__).resolve().parent / "data" / "observations.csv"


def summarize(path: Path) -> dict:
    """Return deterministic site totals after validating all input records."""
    totals: dict[str, int] = {}
    seen: set[tuple[str, str]] = set()
    rows = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(f"Expected exact CSV columns: {','.join(EXPECTED_COLUMNS)}")
        for number, row in enumerate(reader, start=2):
            if not isinstance(row, dict) or set(row) != set(EXPECTED_COLUMNS) or any(
                value is None for value in row.values()
            ):
                raise ValueError(f"Malformed CSV row {number}")
            day, site, count_text = (row[key] for key in EXPECTED_COLUMNS)
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", day):
                raise ValueError(f"Non-ISO date at CSV row {number}")
            try:
                date.fromisoformat(day)
            except ValueError:
                raise ValueError(f"Invalid date at CSV row {number}") from None
            if not re.fullmatch(r"[A-Z][A-Z0-9_-]*", site):
                raise ValueError(f"Invalid site identifier at CSV row {number}")
            if not re.fullmatch(r"[0-9]+", count_text):
                raise ValueError(f"Invalid nonnegative integer at CSV row {number}")
            key = (day, site)
            if key in seen:
                raise ValueError(f"Duplicate (date, site) at CSV row {number}")
            seen.add(key)
            totals[site] = totals.get(site, 0) + int(count_text)
            rows += 1
    if rows == 0:
        raise ValueError("No data rows")
    return {"rows": rows, "totals": dict(sorted(totals.items())), "grand_total": sum(totals.values())}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize fictional site counts from a local CSV")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="local UTF-8 CSV input")
    args = parser.parse_args(argv)
    try:
        report = summarize(args.input)
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        # Demonstration data is fictional, but avoid echoing arbitrary CSV cell contents.
        parser.exit(1, f"Data validation failed: {type(exc).__name__}\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
