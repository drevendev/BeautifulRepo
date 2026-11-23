#!/usr/bin/env python3
"""Inventory local literal OWNER/REPO references before a GitHub repository move.

Read-only, dependency-free and bounded; neither redirects nor third-party consumers
are checked. Results contain paths and positions, never surrounding source lines.
"""

from __future__ import annotations

import argparse
import json
from itertools import islice
import os
from pathlib import Path
import re
import stat

TEXT_SUFFIXES = frozenset({
    ".md", ".markdown", ".rst", ".txt", ".yml", ".yaml", ".toml",
    ".json", ".ini", ".cfg", ".html", ".sh", ".ps1", ".py",
})
IGNORED_DIRECTORIES = frozenset({".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"})
MAX_ENTRIES = 10_000
MAX_DEPTH = 32
MAX_FILE_BYTES = 1_048_576
MAX_TOTAL_BYTES = 25_165_824
MAX_MATCHES = 2_000
REPOSITORY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


def _source_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"Dockerfile", "Makefile", ".gitmodules"}


def inspect(root: Path, old: str) -> dict[str, object]:
    """Find case-insensitive literal occurrences in bounded local text files.

    Files with unsupported content or metadata make the inventory INCOMPLETE,
    never an apparent zero-findings PASS. No user-controlled source is executed.
    """
    if not REPOSITORY.fullmatch(old) or len(old) > 141:
        raise ValueError("expected OLD-OWNER/OLD-REPO, not a URL or path")
    report: dict[str, object] = {
        "status": "incomplete", "old": old, "files_scanned": 0,
        "findings": [], "errors": [],
    }
    absolute = Path(os.path.abspath(root))  # Normalize without resolving symbolic links.
    try:
        for component in (absolute, *absolute.parents):
            info = os.stat(component, follow_symlinks=False)
            if not stat.S_ISDIR(info.st_mode) or getattr(info, "st_reparse_tag", 0):
                raise OSError("root path includes a redirect or non-directory")
    except OSError:
        report["errors"] = ["Cannot inspect root without directory redirects"]
        return report

    literal = re.compile(re.escape(old), re.IGNORECASE | re.ASCII)
    errors: list[str] = []
    findings: list[dict[str, object]] = []
    stack: list[tuple[Path, int]] = [(absolute, 0)]
    entries_seen = 0
    bytes_seen = 0
    while stack:
        directory, depth = stack.pop()
        try:
            with os.scandir(directory) as scan:
                # Consume at most the remaining budget and one overflow sentinel.
                remaining = MAX_ENTRIES - entries_seen
                batch = list(islice(scan, remaining + 1))
        except OSError:
            errors.append(f"Cannot inspect directory: {directory.relative_to(absolute).as_posix() or '.'}")
            continue
        if len(batch) > remaining:
            errors.append(f"Scan exceeds {MAX_ENTRIES} directory entries")
            break
        entries = sorted(batch, key=lambda entry: entry.name)
        entries_seen += len(entries)
        for entry in entries:
            if entry.name in IGNORED_DIRECTORIES:
                continue
            relative = Path(entry.path).relative_to(absolute).as_posix()
            try:
                info = os.stat(entry.path, follow_symlinks=False)
            except OSError:
                errors.append(f"Cannot inspect entry: {relative}")
                continue
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0):
                errors.append(f"Skipped redirect: {relative}")
            elif stat.S_ISDIR(info.st_mode):
                if depth >= MAX_DEPTH:
                    errors.append(f"Scan exceeds {MAX_DEPTH} directory levels: {relative}")
                else:
                    stack.append((Path(entry.path), depth + 1))
            elif _source_file(Path(entry.name)):
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    errors.append(f"Skipped non-regular or hard-linked file: {relative}")
                    continue
                if info.st_size > MAX_FILE_BYTES or bytes_seen + info.st_size > MAX_TOTAL_BYTES:
                    errors.append(f"Text budget exceeded: {relative}")
                    continue
                bytes_seen += info.st_size
                try:
                    # Racy files and malformed content must not produce false completeness.
                    with open(entry.path, "rb") as handle:
                        data = handle.read(MAX_FILE_BYTES + 1)
                    if len(data) > MAX_FILE_BYTES:
                        raise ValueError("file grew beyond limit")
                    content = data.decode("utf-8-sig")
                except (OSError, UnicodeError, ValueError):
                    errors.append(f"Cannot decode bounded text file: {relative}")
                    continue
                report["files_scanned"] = int(report["files_scanned"]) + 1
                for line_number, line in enumerate(content.splitlines(), 1):
                    for match in literal.finditer(line):
                        findings.append({"path": relative, "line": line_number, "column": match.start() + 1})
                        if len(findings) >= MAX_MATCHES:
                            errors.append(f"Scan reached {MAX_MATCHES} match limit")
                            stack.clear()
                            break
                    if len(findings) >= MAX_MATCHES:
                        break
            # Stop the enclosing directory loop too: another file must not
            # push a previously reached match budget past MAX_MATCHES.
            if len(findings) >= MAX_MATCHES:
                break
            # Non-text and non-regular non-source files do not belong to this inventory.
        if len(findings) >= MAX_MATCHES:
            break
    findings.sort(key=lambda item: (str(item["path"]), int(item["line"]), int(item["column"])))
    report.update(status="incomplete" if errors else "findings" if findings else "ok",
                  findings=findings, errors=sorted(errors))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="checkout to inspect")
    parser.add_argument("--old", required=True, help="old OWNER/REPO pair (not a URL)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = inspect(args.root, args.old)
    except ValueError as error:
        parser.error(str(error))
    if args.format == "json":
        print(json.dumps(result, sort_keys=True, ensure_ascii=True))
    else:
        print(f"Repository references: {str(result['status']).upper()} "
              f"({result['files_scanned']} files, {len(result['findings'])} occurrences)")
        for item in result["findings"]:
            print(f"- {ascii(item['path'])}:{item['line']}:{item['column']}")
        for error in result["errors"]:
            print(f"- INCOMPLETE: {ascii(error)}")
    return {"ok": 0, "findings": 1, "incomplete": 2}[str(result["status"])]


if __name__ == "__main__":
    raise SystemExit(main())
