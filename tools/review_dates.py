#!/usr/bin/env python3
"""List guide sources whose review dates are due for a recheck. No network or dependencies.

The handbook dates the moment someone actually re-read a source ("Reviewed
**2026-10-22**", "Checked: 2026-10-03"). This tool finds those dates in the
maintained documents and warns when one is older than its threshold. A warning
asks a person to re-read the source; it never claims the source changed, and
the fix is never to move the date without reading.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
# Maintained prose with dated source reviews. The generated catalog view and the
# changelog's history are excluded; catalog.py checks the catalog's own dates.
SOURCES = ("guides/*.md", "checklists/*.md", "CONTRIBUTING.md", "SECURITY.md", "tools/README.md")
DEFAULT_DAYS = 180
# Program rules change every season, like catalog entries in the "program" category.
DAYS_BY_FILE = {"guides/programs.md": 30}
REVIEW_DATE = re.compile(
    r"\b(?:[Rr]e)?(?:[Rr]eviewed|[Cc]hecked)\b(?: on)?:?[ \t\n*]*(\d{4}-\d{2}-\d{2})\b"
)
# Examples of the format in code are not reviews; blank them, keeping line numbers.
OPEN_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CLOSE_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
CODE_SPAN = re.compile(r"(`+)[^\n]*?\1")


def _blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group())


def mask_fenced_blocks(text: str) -> str:
    """Mask GFM-style fenced code while retaining source line numbers.

    A valid closer uses the same character and at least the opener width.
    An unclosed block lasts to EOF; neither case is a reviewed source.
    """
    active: tuple[str, int] | None = None
    result: list[str] = []
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if active is None:
            match = OPEN_FENCE.match(content)
            if match is None or (match[1][0] == "`" and "`" in match[2]):
                result.append(line)
                continue
            active = (match[1][0], len(match[1]))
        else:
            close = CLOSE_FENCE.fullmatch(content)
            if close and close[1][0] == active[0] and len(close[1]) >= active[1]:
                active = None
        result.append(re.sub(r"[^\n]", " ", line))
    return "".join(result)

def find_review_dates(root: Path) -> list[tuple[str, int, date | None, str]]:
    """Return (relative path, line, date or None if invalid, raw text) for each review date."""
    found = []
    paths = sorted({path for pattern in SOURCES for path in root.glob(pattern)})
    for path in paths:
        text = CODE_SPAN.sub(_blank, mask_fenced_blocks(path.read_text(encoding="utf-8")))
        relative = path.relative_to(root).as_posix()
        for match in REVIEW_DATE.finditer(text):
            line = text.count("\n", 0, match.start(1)) + 1
            try:
                observed = date.fromisoformat(match.group(1))
            except ValueError:
                observed = None
            found.append((relative, line, observed, match.group(1)))
    return found


def check(found, today: date) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the dates found."""
    errors, warnings = [], []
    for relative, line, observed, raw in found:
        where = f"{relative}:{line}"
        if observed is None:
            errors.append(f"{where}: {raw} is not a real date")
        elif observed > today:
            errors.append(f"{where}: review date {raw} is in the future")
        else:
            limit = DAYS_BY_FILE.get(relative, DEFAULT_DAYS)
            age = (today - observed).days
            if age > limit:
                warnings.append(f"{where}: reviewed {raw}, {age} days ago (recheck after "
                                f"{limit}); re-read the source, then update the date")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="repository root (default: this BeautifulRepo checkout)")
    parser.add_argument("--today", type=date.fromisoformat,
                        default=datetime.now(timezone.utc).date(),
                        help="date to measure against, YYYY-MM-DD (default: today, UTC)")
    parser.add_argument("--fail-on-warning", action="store_true",
                        help="exit 1 when a date is due for a recheck (for scheduled runs)")
    args = parser.parse_args(argv)

    found = find_review_dates(args.root)
    errors, warnings = check(found, args.today)
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors or (warnings and args.fail_on_warning):
        return 1
    print(f"OK: {len(found)} review date(s), {len(warnings)} due for a recheck")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
