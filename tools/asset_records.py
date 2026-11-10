#!/usr/bin/env python3
"""Check the structure of BeautifulRepo asset provenance records, not the rights."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
import os
from pathlib import Path
import re
import stat
import sys

MAX_BYTES = 128 * 1024
FIELDS = (
    "Used at",
    "What it depicts/contains",
    "Creator/rightsholder",
    "Original source",
    "Source revision/acquired on",
    "Rights basis",
    "Allowed use checked",
    "Changes made",
    "Required credit/notice",
    "Text equivalent",
    "Decision",
    "Reviewed on / by",
    "Recheck when",
)
FIELD_PATTERN = re.compile(r"^- \*\*(.+?):\*\*\s*(.*?)\s*$")
DECISION_PATTERN = re.compile(r"^(APPROVED|PENDING|REMOVED)(?:\s*(?:[-—:]\s*|\(.*\)\s*).*)?$", re.I)
DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*/\s*(\S.*)$")
PLACEHOLDERS = {
    "ASSET_FILENAME_OR_GROUP", "REPOSITORY_PATHS_AND_EMBEDS",
    "PLAIN_LANGUAGE_DESCRIPTION", "VERIFIED_NAME_OR_UNVERIFIED",
    "EXACT_PUBLIC_URL_OR_PRIVATE_EVIDENCE_REFERENCE",
    "DATE_AND_VERSION_IF_AVAILABLE", "EXACT_LICENSE_NAME_VERSION_AND_LINK_OR_PERMISSION_SCOPE",
    "REDISTRIBUTION_MODIFICATION_AND_RELEVANT_LIMITS",
    "CROPPED_RECOLOURED_OR_UNCHANGED_WITH_DETAILS",
    "FULL_ACTUAL_ATTRIBUTION_AND_NOTICE_LOCATION",
    "CAPTION_ALT_TEXT_OR_ADJACENT_EXPLANATION_PATH",
    "APPROVED_WITH_EVIDENCE_OR_PENDING_DO_NOT_PUBLISH_OR_REMOVED",
    "DATE_AND_REVIEWER", "SOURCE_OR_ASSET_LICENSE_DISTRIBUTION_CHANGES",
}


class RecordError(ValueError):
    """Invalid or incomplete file structure."""


def read_text(path: Path) -> str:
    """Read only bounded ordinary files. Never follow a symlink at the leaf."""
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise RecordError("input must be an ordinary file, not a link")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as file:
            if not stat.S_ISREG(os.fstat(file.fileno()).st_mode):
                raise RecordError("input must be an ordinary file")
            raw = file.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES or b"\x00" in raw:
            raise RecordError("input exceeds 128 KiB or contains NUL")
        return raw.decode("utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise RecordError("cannot read a bounded UTF-8 file") from exc


def validate(text: str, *, today: date | None = None) -> dict:
    """Return non-sensitive record counts or fail with a numbered structural error."""
    today = today or date.today()
    records: list[tuple[int, str, dict[str, str]]] = []
    current: dict[str, str] | None = None
    heading = ""
    start = 0
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            if current is not None:
                records.append((start, heading, current))
            start = number
            heading = line[3:].strip()
            if not heading or heading in PLACEHOLDERS:
                raise RecordError(f"line {number}: missing concrete asset name")
            current = {}
        elif line.startswith("- **"):
            if current is None:
                raise RecordError(f"line {number}: field outside an asset section")
            match = FIELD_PATTERN.fullmatch(line)
            if match is None:
                raise RecordError(f"line {number}: invalid record field")
            key, value = match.groups()
            if key not in FIELDS:
                raise RecordError(f"line {number}: unknown field")
            if key in current:
                raise RecordError(f"line {number}: repeated field")
            if not value or value in PLACEHOLDERS or value.casefold() in ("todo", "tbd", "placeholder"):
                raise RecordError(f"line {number}: blank or template value")
            current[key] = value
    if current is not None:
        records.append((start, heading, current))
    if not records:
        raise RecordError("no asset sections found (expected '## asset-name')")
    names: set[str] = set()
    decisions = Counter()
    for line, name, fields in records:
        if name in names:
            raise RecordError(f"line {line}: duplicate asset section")
        names.add(name)
        missing = set(FIELDS) - set(fields)
        if missing:
            # Output only the canonical field name; never echo user values.
            raise RecordError(f"line {line}: missing field '{sorted(missing)[0]}'")
        decision = DECISION_PATTERN.fullmatch(fields["Decision"])
        if decision is None:
            raise RecordError(f"line {line}: decision must begin APPROVED, PENDING or REMOVED")
        choice = decision.group(1).lower()
        reviewed = DATE_PATTERN.fullmatch(fields["Reviewed on / by"])
        if reviewed is None:
            raise RecordError(f"line {line}: use YYYY-MM-DD / reviewer for review date")
        try:
            day = date.fromisoformat(reviewed.group(1))
        except ValueError as exc:
            raise RecordError(f"line {line}: invalid review date") from exc
        if day > today:
            raise RecordError(f"line {line}: review date is in the future")
        if choice == "approved":
            for key in ("Creator/rightsholder", "Original source", "Rights basis", "Allowed use checked", "Required credit/notice"):
                if fields[key].strip().casefold() in ("unknown", "unverified", "n/a", "not checked"):
                    raise RecordError(f"line {line}: approved record has unresolved '{key}'")
        decisions[choice] += 1
    return {
        "schema_version": 1,
        "records": len(records),
        "decisions": {choice: decisions[choice] for choice in ("approved", "pending", "removed")},
        "has_pending_decisions": decisions["pending"] > 0,
        "notice": "Structural evidence inventory only; no asset source, ownership, permission, or legal compatibility verified.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Markdown asset provenance record file")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = validate(read_text(Path(args.file)))
    except RecordError as exc:
        print(f"asset_records: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        counts = result["decisions"]
        print(f"Asset records: {result['records']} (approved {counts['approved']}, pending {counts['pending']}, removed {counts['removed']})")
        print("No PENDING decisions recorded (rights NOT verified)." if not result["has_pending_decisions"] else "PENDING decisions recorded: do not publish unresolved assets.")
        print(result["notice"])
    return 1 if result["has_pending_decisions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
