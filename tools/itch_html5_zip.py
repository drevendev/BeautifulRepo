#!/usr/bin/env python3
"""Offline, metadata-only preflight for itch.io HTML5 ZIP uploads.

This never extracts entries or executes game code. Upload, asset loading,
case-sensitive links within HTML/JS/CSS, and actual browser play remain untested.
"""
from __future__ import annotations

import argparse
import json
import stat
import sys
import zipfile
from pathlib import Path

MAX_FILES = 1_000
MAX_PATH_CHARS = 240
MAX_TOTAL_BYTES = 500_000_000
MAX_FILE_BYTES = 200_000_000


def check_entries(entries: list[zipfile.ZipInfo]) -> tuple[int, int, list[dict[str, str]]]:
    """Inspect central-directory metadata; never read or unpack member data."""
    findings: list[dict[str, str]] = []
    seen: set[str] = set()
    files = 0
    total = 0
    has_index = False

    def report(rule: str, path: str, detail: str) -> None:
        findings.append({"rule": rule, "path": path, "detail": detail})

    for item in entries:
        name = item.filename
        # zipfile normalizes backslashes on Windows; inspect the original spelling.
        raw_name = item.orig_filename
        canonical_name = name.replace("\\", "/")
        if not item.is_dir():
            files += 1
            total += item.file_size
            if raw_name == "index.html":
                has_index = True
        if canonical_name in seen:
            report("duplicate_path", raw_name, "multiple ZIP members share this path or normalized alias")
        seen.add(canonical_name)
        if not raw_name or raw_name.startswith("/") or "\\" in raw_name or ":" in raw_name.split("/", 1)[0] or any(
            part in ("", ".", "..") for part in raw_name.rstrip("/").split("/")
        ):
            report("unsafe_path", raw_name, "member path is not a safe relative POSIX path")
        if any(ord(char) > 127 for char in raw_name) and not (item.flag_bits & 0x800):
            report("legacy_name_encoding", raw_name,
                   "non-ASCII ZIP member name lacks the UTF-8 flag; re-export with UTF-8 names")
        if len(name) > MAX_PATH_CHARS:
            report("path_length", name, f"path exceeds {MAX_PATH_CHARS} characters")
        if not item.is_dir() and item.file_size > MAX_FILE_BYTES:
            report("file_size", name, f"uncompressed file exceeds {MAX_FILE_BYTES} bytes")
        mode = item.external_attr >> 16
        if item.create_system == 3 and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
            report("special_entry", name, "symbolic links and special files are not accepted by this preflight")
        if item.flag_bits & 1:
            report("encrypted_entry", name, "encrypted ZIP members cannot be checked as ordinary game assets")

    if not has_index:
        report("missing_entrypoint", "index.html", "ZIP needs an index.html file at archive root (exact case)")
    if files > MAX_FILES:
        report("file_count", "", f"{files} files exceeds the {MAX_FILES}-file upload limit")
    if total > MAX_TOTAL_BYTES:
        report("total_size", "", f"{total} uncompressed bytes exceeds {MAX_TOTAL_BYTES}")
    return files, total, sorted(findings, key=lambda f: (f["rule"], f["path"], f["detail"]))


def inspect(path: Path) -> dict[str, object]:
    report: dict[str, object] = {
        "status": "incomplete", "archive": path.name, "files": 0,
        "uncompressed_bytes": 0, "findings": [],
    }
    try:
        if path.is_symlink() or not path.is_file():
            raise ValueError("archive must be an existing regular file, not a symlink")
        with zipfile.ZipFile(path, "r") as archive:
            files, total, findings = check_entries(archive.infolist())
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        report["error"] = f"cannot inspect ZIP central directory: {type(exc).__name__}"
        return report
    report.update(status="findings" if findings else "ok", files=files,
                  uncompressed_bytes=total, findings=findings)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="local itch.io HTML5 game ZIP")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    result = inspect(args.archive)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"HTML5 ZIP preflight: {result['status'].upper()} ({result['files']} files; "
              f"{result['uncompressed_bytes']} bytes unpacked, by ZIP metadata)")
        if "error" in result:
            print(result["error"])
        for item in result["findings"]:
            print(f"- {item['rule']} {ascii(item['path'])}: {item['detail']}")
    return {"ok": 0, "findings": 1, "incomplete": 2}[str(result["status"])]


if __name__ == "__main__":
    sys.exit(main())
