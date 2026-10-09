#!/usr/bin/env python3
"""Small, dependency-free CSV row counter for a CLI README example."""

import argparse
import csv
import sys
from pathlib import Path


def count_records(path: Path) -> int:
    """Count nonblank data records after a required header row."""
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, None)
        if header is None or not any(cell.strip() for cell in header):
            raise ValueError("missing a CSV header")
        total = 0
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            if len(row) != len(header):
                raise ValueError(
                    f"record ending at line {reader.line_num}: "
                    f"expected {len(header)} columns, got {len(row)}"
                )
            total += 1
        return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Count nonblank CSV data records (excluding the header)."
    )
    parser.add_argument("csv_file", type=Path, help="path to a UTF-8 CSV file")
    args = parser.parse_args(argv)
    try:
        total = count_records(args.csv_file)
    except OSError as exc:
        # OSError may contain the full local input path.
        reason = exc.strerror or "file access failed"
        print(f"rowcount: cannot read CSV: {reason}", file=sys.stderr)
        return 1
    except (UnicodeError, csv.Error, ValueError) as exc:
        print(f"rowcount: {exc}", file=sys.stderr)
        return 1
    print(f"Data rows: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
