#!/usr/bin/env python3
"""Capture and verify a synthetic agent-eval target without running its code.

A baseline lives *outside* the target. This is a byte-level regression aid for
operator-controlled evals, not proof of prompt-injection resistance or a sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

VERSION = 1


def target_root(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ValueError("target must be a real directory, not a symlink")
    return path.resolve(strict=True)


def baseline_path(path: Path, root: Path) -> Path:
    selected = path.resolve()
    if selected.is_relative_to(root):
        raise ValueError("baseline must be outside the target directory")
    return selected


def inventory(root: Path) -> dict[str, dict[str, str]]:
    """Walk entries without traversing directory symlinks or running target code."""
    found = {}
    for parent, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs.sort()
        files.sort()
        for name in sorted([*dirs, *files]):
            entry = Path(parent) / name
            key = entry.relative_to(root).as_posix()
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode):
                found[key] = {"kind": "symlink", "target": os.readlink(entry)}
            elif stat.S_ISDIR(mode):
                found[key] = {"kind": "directory"}
            elif stat.S_ISREG(mode):
                digest = hashlib.sha256()
                with entry.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(131072), b""):
                        digest.update(chunk)
                found[key] = {"kind": "file", "sha256": digest.hexdigest()}
            else:
                raise ValueError(f"unsupported special file: {key}")
        dirs[:] = [name for name in dirs if not (Path(parent) / name).is_symlink()]
    return dict(sorted(found.items()))


def capture(root: Path, baseline: Path) -> int:
    snapshot = {"format": VERSION, "root": str(root), "entries": inventory(root)}
    data = json.dumps(snapshot, indent=2, ensure_ascii=True, sort_keys=True) + "\n"
    # 'x' never overwrites the evidence of an earlier run.
    with baseline.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(data)
    print(f"BASELINE: {len(snapshot['entries'])} entries; {baseline}")
    return 0


def verify(root: Path, baseline: Path) -> int:
    if baseline.stat().st_size > 10_000_000:
        raise ValueError("baseline is too large")
    data = json.loads(baseline.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("format") != VERSION
            or data.get("root") != str(root) or not isinstance(data.get("entries"), dict)):
        raise ValueError("baseline format or target path does not match")
    before = data["entries"]
    after = inventory(root)
    changed = False
    for key in sorted(before.keys() | after.keys()):
        if key not in before:
            print(f"ADDED: {key}")
        elif key not in after:
            print(f"REMOVED: {key}")
        elif before[key] != after[key]:
            print(f"CHANGED: {key}")
        else:
            continue
        changed = True
    if changed:
        print("FAIL: eval target changed (does not identify which process changed it)")
        return 1
    print(f"UNCHANGED: {len(after)} entries")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("capture", "verify"):
        cmd = sub.add_parser(name)
        cmd.add_argument("target", type=Path, help="disposable synthetic fixture copy")
        cmd.add_argument("--baseline", required=True, type=Path,
                         help="snapshot JSON outside the target")
    args = parser.parse_args(argv)
    try:
        root = target_root(args.target)
        baseline = baseline_path(args.baseline, root)
        if args.command == "capture":
            return capture(root, baseline)
        return verify(root, baseline)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
