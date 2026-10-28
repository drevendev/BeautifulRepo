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
import os
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
# Maintained prose with dated source reviews. The generated catalog view and the
# changelog's history are excluded; catalog.py checks the catalog's own dates.
SOURCES = ("guides/*.md", "checklists/*.md", "CONTRIBUTING.md", "SECURITY.md", "tools/README.md")
DEFAULT_DAYS = 180
MAX_SOURCE_BYTES = 256 * 1024
MAX_SOURCE_FILES = 4096
JUNCTION_REPARSE_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)
# Program rules change every season, like catalog entries in the "program" category.
DAYS_BY_FILE = {"guides/programs.md": 30}
REVIEW_DATE = re.compile(
    r"\b(?:[Rr]e)?(?:[Rr]eviewed|[Cc]hecked)\b(?: on)?:?[ \t\n*]*(\d{4}-\d{2}-\d{2})\b"
)
# Examples of the format in code are not reviews; blank them, keeping line numbers.
OPEN_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CLOSE_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
BACKTICK_RUN = re.compile(r"`+")


def mask_inline_inert(text: str) -> str:
    """Ignore same-line code spans and HTML comments; keep prose and line numbers.

    Markdown backtick runs close only at an equal-width run. Track comments
    across lines without interpreting backticks inside comments as code.
    This is a bounded source-date filter, not a complete GFM parser.
    """
    in_comment = False
    result: list[str] = []
    for line in text.splitlines(keepends=True):
        runs = list(BACKTICK_RUN.finditer(line))
        run_at = {match.start(): i for i, match in enumerate(runs)}
        following: dict[int, int] = {}
        next_by_width: dict[int, int] = {}
        for i in range(len(runs) - 1, -1, -1):
            width = len(runs[i].group())
            if width in next_by_width:
                following[i] = next_by_width[width]
            next_by_width[width] = i

        chars = list(line)
        offset = 0
        while offset < len(line):
            if in_comment:
                close = line.find("-->", offset)
                end = len(line) if close == -1 else close + 3
                chars[offset:end] = ["\n" if c == "\n" else " " for c in chars[offset:end]]
                offset = end
                in_comment = close == -1
                continue
            if line.startswith("<!--", offset):
                in_comment = True
                continue
            run_id = run_at.get(offset)
            if run_id is not None:
                closing_id = following.get(run_id)
                if closing_id is not None:
                    end = runs[closing_id].end()
                    chars[offset:end] = ["\n" if c == "\n" else " " for c in chars[offset:end]]
                    offset = end
                else:
                    offset = runs[run_id].end()
                continue
            offset += 1
        result.append("".join(chars))
    return "".join(result)


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


class ReviewInputError(ValueError):
    """The selected source cannot be scanned within the offline file bounds."""


def _source_text(path: Path, relative: str) -> str:
    """Read an ordinary bounded UTF-8 file; never intentionally follow a file link."""
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ReviewInputError(f"{relative}: source is not an ordinary file.")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise ReviewInputError(f"{relative}: source is not an ordinary file.")
            raw = handle.read(MAX_SOURCE_BYTES + 1)
        if len(raw) > MAX_SOURCE_BYTES:
            raise ReviewInputError(f"{relative}: source exceeds the 256 KiB scan limit.")
        text = raw.decode("utf-8-sig")
        if "\x00" in text:
            raise ReviewInputError(f"{relative}: NUL in source text.")
        return text
    except ReviewInputError:
        raise
    except (OSError, UnicodeError):
        raise ReviewInputError(f"{relative}: cannot read ordinary UTF-8 source.") from None


def find_review_dates(root: Path) -> list[tuple[str, int, date | None, str]]:
    """Return (relative path, line, date or None if invalid, raw text) for each review date."""
    try:
        root = root.resolve(strict=True)
        if not root.is_dir():
            raise ReviewInputError("--root must be an existing directory.")
    except (OSError, RuntimeError):
        raise ReviewInputError("--root must be an existing directory.") from None

    # The selected paths live only at root or one level below these directories.
    # Reject redirected directories before globbing, including NTFS junctions.
    for directory in ("guides", "checklists", "tools"):
        folder = root / directory
        try:
            info = folder.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            raise ReviewInputError(f"{directory}: cannot inspect source directory.") from None
        if not stat.S_ISDIR(info.st_mode) or (
            getattr(info, "st_reparse_tag", 0) == JUNCTION_REPARSE_TAG
        ):
            raise ReviewInputError(f"{directory}: redirected or non-directory source.")

    found = []
    paths = sorted({path for pattern in SOURCES for path in root.glob(pattern)})
    if len(paths) > MAX_SOURCE_FILES:
        raise ReviewInputError(f"too many source files (limit {MAX_SOURCE_FILES}).")
    for path in paths:
        relative = path.relative_to(root).as_posix()
        text = mask_inline_inert(mask_fenced_blocks(_source_text(path, relative)))
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

    try:
        found = find_review_dates(args.root)
    except ReviewInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
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
