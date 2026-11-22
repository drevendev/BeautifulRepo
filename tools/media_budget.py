#!/usr/bin/env python3
"""Offline, bounded inventory of repository-owned image file sizes.

This tool does not render images, fetch external URLs or estimate page-load bytes.
Budgets are project decisions, never GitHub, WCAG or web-performance limits.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat

IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".apng"})
IGNORED_DIRECTORIES = frozenset({".git", ".venv", "venv", "node_modules", "__pycache__"})
MAX_ENTRIES = 10_000
MAX_DEPTH = 32
KIB = 1024


def _positive_kib(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("budget must be a positive integer KiB value") from error
    if not 1 <= number <= 1_000_000:
        raise argparse.ArgumentTypeError("budget must be between 1 and 1000000 KiB")
    return number


def inspect(root: Path, max_file_bytes: int, max_total_bytes: int) -> dict[str, object]:
    """Inventory file *metadata* only; redirects are never followed.

    A non-regular media path, an unreadable directory, or a scan limit produces
    an incomplete result rather than a misleading PASS. The total is the sum
    of encountered regular image file sizes, not a browser transfer estimate.
    """
    report: dict[str, object] = {
        "status": "incomplete", "files": 0, "total_bytes": 0,
        "max_file_bytes": max_file_bytes, "max_total_bytes": max_total_bytes,
        "largest": [], "findings": [], "errors": [],
    }
    errors: list[str] = []
    findings: list[dict[str, object]] = []
    sizes: list[tuple[str, int]] = []
    try:
        root_info = root.lstat()
        if not stat.S_ISDIR(root_info.st_mode) or root.is_symlink():
            raise OSError("root must be an ordinary directory, not a redirect")
    except OSError:
        report["errors"] = ["Cannot inspect root as an ordinary directory"]
        return report

    stack: list[tuple[Path, int]] = [(root, 0)]
    entries_seen = 0
    while stack:
        directory, depth = stack.pop()
        try:
            with os.scandir(directory) as stream:
                entries = []
                for entry in stream:
                    if entries_seen + len(entries) >= MAX_ENTRIES:
                        raise ValueError("Scan exceeds entry inventory limit")
                    entries.append(entry)
                entries.sort(key=lambda entry: entry.name)
        except ValueError:
            errors.append(f"Scan exceeds {MAX_ENTRIES} directory entries")
            stack.clear()
            continue
        except OSError:
            errors.append(f"Cannot inspect directory: {directory.relative_to(root).as_posix() or '.'}")
            continue
        for entry in entries:
            entries_seen += 1
            relative = entry.path[len(os.fspath(root).rstrip(os.sep)) + 1:].replace(os.sep, "/")
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError:
                errors.append(f"Cannot inspect entry: {relative}")
                continue
            mode = info.st_mode
            if stat.S_ISLNK(mode) or getattr(info, "st_reparse_tag", 0) == 0xA0000003:
                errors.append(f"Skipped redirect: {relative}")
            elif stat.S_ISDIR(mode):
                if entry.name in IGNORED_DIRECTORIES:
                    continue
                if depth >= MAX_DEPTH:
                    errors.append(f"Scan exceeds {MAX_DEPTH} directory levels: {relative}")
                else:
                    stack.append((Path(entry.path), depth + 1))
            elif Path(entry.name).suffix.lower() in IMAGE_EXTENSIONS:
                if stat.S_ISREG(mode):
                    sizes.append((relative, info.st_size))
                    if info.st_size > max_file_bytes:
                        findings.append({"rule": "file_budget", "path": relative, "bytes": info.st_size})
                else:
                    errors.append(f"Skipped non-regular media entry: {relative}")
    total = sum(size for _, size in sizes)
    if total > max_total_bytes:
        findings.append({"rule": "total_budget", "path": "", "bytes": total})
    findings.sort(key=lambda f: (str(f["rule"]), str(f["path"])))
    report.update(
        status="incomplete" if errors else "findings" if findings else "ok",
        files=len(sizes), total_bytes=total,
        largest=[{"path": path, "bytes": size} for path, size in
                 sorted(sizes, key=lambda item: (-item[1], item[0]))[:5]],
        findings=findings, errors=sorted(errors),
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="existing repository directory (default: current directory)")
    parser.add_argument("--max-file-kib", type=_positive_kib, default=1024,
                        help="per-image file-size budget in KiB (default: 1024)")
    parser.add_argument("--max-total-kib", type=_positive_kib, default=8192,
                        help="all inventoried images combined in KiB (default: 8192)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    report = inspect(args.root, args.max_file_kib * KIB, args.max_total_kib * KIB)
    if args.format == "json":
        print(json.dumps(report, sort_keys=True, ensure_ascii=True))
    else:
        print(f"Media budget: {str(report['status']).upper()} "
              f"({report['files']} files, {report['total_bytes']} bytes on disk)")
        for item in report["findings"]:
            print(f"- {item['rule']} {ascii(item['path'])}: {item['bytes']} bytes")
        for message in report["errors"]:
            print(f"- INCOMPLETE: {ascii(message)}")
        for item in report["largest"]:
            print(f"  largest: {ascii(item['path'])} ({item['bytes']} bytes)")
    return {"ok": 0, "findings": 1, "incomplete": 2}[str(report["status"])]


if __name__ == "__main__":
    raise SystemExit(main())
