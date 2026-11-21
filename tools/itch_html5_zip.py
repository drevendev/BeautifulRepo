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

# Local Windows extraction portability rules, NOT itch.io upload requirements.
# https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in "123456789¹²³"
}
WINDOWS_INVALID = '<>:"|?*'


def nonportable_windows_component(component: str) -> bool:
    """Reject names Windows shell/tools cannot reliably create or preserve."""
    return bool(component) and (
        component.endswith((" ", "."))
        or any(char in WINDOWS_INVALID for char in component)
        or component.split(".", 1)[0].rstrip(" ").upper() in WINDOWS_RESERVED
    )


def check_entries(entries: list[zipfile.ZipInfo]) -> tuple[int, int, list[dict[str, str]]]:
    """Inspect central-directory metadata; never read or unpack member data."""
    findings: list[dict[str, str]] = []
    seen: set[str] = set()
    seen_casefold: dict[str, str] = {}
    file_paths: set[str] = set()
    directory_paths: set[str] = set()
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
        mode = item.external_attr >> 16
        unix_type = stat.S_IFMT(mode) if item.create_system == 3 else 0
        # ZipInfo.is_dir() checks only the trailing slash, not Unix mode bits.
        # A directory masquerading as "index.html" is not a usable entry point.
        name_is_dir = item.is_dir()
        unix_is_dir = unix_type == stat.S_IFDIR
        if unix_type in (stat.S_IFDIR, stat.S_IFREG) and name_is_dir != unix_is_dir:
            report("entry_type_mismatch", raw_name,
                   "Unix file type disagrees with directory path spelling")
        if not (name_is_dir or unix_is_dir):
            files += 1
            total += item.file_size
            if raw_name == "index.html":
                has_index = True
                if item.file_size == 0:
                    report("empty_entrypoint", raw_name,
                           "root index.html has zero bytes; it cannot serve as a game entry document")
        already_seen = canonical_name in seen
        if already_seen:
            report("duplicate_path", raw_name, "multiple ZIP members share this path or normalized alias")
        seen.add(canonical_name)
        # Case-distinct ZIP members can overwrite each other in a Windows extraction.
        folded = canonical_name.casefold()
        prior = seen_casefold.get(folded)
        if prior is not None and prior != canonical_name and not already_seen:
            report("windows_case_collision", raw_name,
                   "case-distinct members may collide on case-insensitive filesystems")
        seen_casefold.setdefault(folded, canonical_name)
        # ZIP can contain incompatible file/directory paths; extracted filesystems cannot.
        key = canonical_name.rstrip("/")
        if key:
            (directory_paths if (name_is_dir or unix_is_dir) else file_paths).add(key)
        # Control characters can be present in ZIP names but make extracted
        # paths and diagnostic logs ambiguous. This is a conservative
        # portability preflight, not a published itch.io-specific limit.
        if (
            not raw_name
            or raw_name.startswith("/")
            or "\\" in raw_name
            or ":" in raw_name.split("/", 1)[0]
            or any(part in ("", ".", "..") for part in raw_name.rstrip("/").split("/"))
            or any(ord(char) < 0x20 or 0x7f <= ord(char) <= 0x9f for char in raw_name)
        ):
            report("unsafe_path", raw_name, "member path is not a safe relative POSIX path")
        if any(nonportable_windows_component(part)
               for part in raw_name.rstrip("/").split("/")):
            report("windows_path", raw_name,
                   "member name uses Windows-reserved characters, device names or trailing dot/space")
        if any(ord(char) > 127 for char in raw_name) and not (item.flag_bits & 0x800):
            report("legacy_name_encoding", raw_name,
                   "non-ASCII ZIP member name lacks the UTF-8 flag; re-export with UTF-8 names")
        if len(name) > MAX_PATH_CHARS:
            report("path_length", name, f"path exceeds {MAX_PATH_CHARS} characters")
        if not item.is_dir() and item.file_size > MAX_FILE_BYTES:
            report("file_size", name, f"uncompressed file exceeds {MAX_FILE_BYTES} bytes")
        if item.create_system == 3 and unix_type not in (0, stat.S_IFREG, stat.S_IFDIR):
            report("special_entry", name, "symbolic links and special files are not accepted by this preflight")
        if item.flag_bits & 1:
            report("encrypted_entry", name, "encrypted ZIP members cannot be checked as ordinary game assets")

    # An explicit directory cannot also be a file; a nested member cannot
    # use a file as its implicit parent directory. Explicit directory records
    # are optional in ZIPs, so their absence is not a finding.
    for path in sorted(file_paths & directory_paths):
        report("path_type_conflict", path, "ZIP contains both a file and a directory at this path")
    for path in sorted(file_paths | directory_paths):
        pieces = path.split("/")
        for depth in range(1, len(pieces)):
            parent = "/".join(pieces[:depth])
            if parent in file_paths:
                report("path_type_conflict", path,
                       f"member needs a directory at '{parent}', but ZIP contains a file there")
                break

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
        # Keep JSON ASCII-only so legacy ZIP paths survive narrow Windows consoles.
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
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
