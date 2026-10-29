#!/usr/bin/env python3
"""Offline consistency check for reviewed SHA-pinned GitHub Actions workflow steps.

The manifest is a local review record, not a remote tag/signature verifier.
No YAML dependency, network, subprocess, target-code execution, or file writes.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import stat
import sys

MAX_FILE_BYTES = 256 * 1024
MAX_MANIFEST_BYTES = 64 * 1024
MAX_WORKFLOWS = 100
ACTION_NAME = r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+"
ACTION_REFERENCE = re.compile(rf"({ACTION_NAME})@([0-9a-f]{{40}})\Z")
USE_LINE = re.compile(r"^[ \t]*(?:-[ \t]+)?uses[ \t]*:[ \t]*([^#\r\n]*?)[ \t]*(?:#[ \t]*(.*))?$", re.M)
VERSION = re.compile(r"v[0-9]+(?:\.[0-9]+){1,2}(?:[-+][0-9A-Za-z.+-]+)?\Z")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


class InputError(ValueError):
    """Malformed or redirected repository-owned input."""


def read_regular(path: Path, limit: int) -> str:
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            raise InputError(f"{path}: not an ordinary file")
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            raise InputError(f"{path}: exceeds {limit} bytes")
        result = raw.decode("utf-8-sig")
        if "\x00" in result:
            raise InputError(f"{path}: contains NUL")
        return result
    except (OSError, UnicodeError) as exc:
        raise InputError(f"{path}: cannot read UTF-8 file ({type(exc).__name__})") from None


def pairs_without_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    try:
        data = json.loads(read_regular(path, MAX_MANIFEST_BYTES),
                          object_pairs_hook=pairs_without_duplicates)
    except (ValueError, TypeError) as exc:
        raise InputError(f"{path}: invalid manifest: {exc}") from None
    if not isinstance(data, dict) or not data:
        raise InputError("action pin manifest must be a nonempty object")
    for name, item in data.items():
        if not isinstance(name, str) or not re.fullmatch(ACTION_NAME, name):
            raise InputError(f"invalid action name in manifest: {name!r}")
        if not isinstance(item, dict) or set(item) != {"sha", "version", "reviewed"}:
            raise InputError(f"{name}: expected sha, version and reviewed")
        if not all(isinstance(v, str) for v in item.values()):
            raise InputError(f"{name}: manifest values must be strings")
        if not re.fullmatch(r"[0-9a-f]{40}", item["sha"]):
            raise InputError(f"{name}: sha must be 40 lowercase hex characters")
        if not VERSION.fullmatch(item["version"]):
            raise InputError(f"{name}: invalid version")
        reviewed = item["reviewed"]
        if not DATE.fullmatch(reviewed):
            raise InputError(f"{name}: reviewed must be YYYY-MM-DD")
        try:
            date.fromisoformat(reviewed)
        except ValueError:
            raise InputError(f"{name}: invalid review date") from None
    return data


def check_repo(root: Path) -> tuple[list[str], int, int]:
    root = root.resolve()
    directory = root / ".github" / "workflows"
    if not directory.is_dir() or directory.is_symlink():
        raise InputError(".github/workflows must be an ordinary directory")
    pins = load_manifest(root / ".github" / "action-pins.json")
    paths = sorted(path for path in directory.iterdir()
                   if path.suffix.lower() in {".yml", ".yaml"})
    if not paths or len(paths) > MAX_WORKFLOWS:
        raise InputError("expected 1 to 100 workflow files")
    errors = []
    used = set()
    seen = 0
    for path in paths:
        source = read_regular(path, MAX_FILE_BYTES)
        for match in USE_LINE.finditer(source):
            line = source.count("\n", 0, match.start()) + 1
            ref = match.group(1).strip()
            comment = (match.group(2) or "").strip()
            if ref.startswith("./") or ref.startswith("docker://"):
                continue  # Local and container actions have no GitHub commit SHA.
            seen += 1
            pinned = ACTION_REFERENCE.fullmatch(ref)
            if not pinned:
                errors.append(f"{path.relative_to(root)}:{line}: external uses must pin a 40-character commit SHA: {ref!r}")
                continue
            name, sha = pinned.groups()
            item = pins.get(name)
            if item is None:
                errors.append(f"{path.relative_to(root)}:{line}: no reviewed manifest entry for {name}")
                continue
            used.add(name)
            if sha != item["sha"]:
                errors.append(f"{path.relative_to(root)}:{line}: {name} SHA differs from reviewed manifest")
            wanted = f"{item['version']} ref inspected {item['reviewed']}"
            if comment != wanted:
                errors.append(f"{path.relative_to(root)}:{line}: {name} annotation must be '# {wanted}'")
    if seen == 0:
        errors.append("no external action references found")
    for name in sorted(set(pins) - used):
        errors.append(f"manifest entry is not used by any workflow: {name}")
    return errors, seen, len(paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="repository to check")
    args = parser.parse_args(argv)
    try:
        errors, references, workflows = check_repo(args.root)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"ERROR: {len(errors)} action pin inconsistency/ies", file=sys.stderr)
        return 1
    print(f"OK: {references} reviewed external action references across {workflows} workflow(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
