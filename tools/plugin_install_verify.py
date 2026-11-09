#!/usr/bin/env python3
"""Verify the four BeautifulRepo Agent Skill files in an installed plugin cache.

An offline, read-only byte comparison, not a Claude Code/Codex discovery or model test.
The source must be a Git checkout at the user-supplied full commit SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

SKILLS = ("audit-repo", "improve-readme", "trust-surfaces", "draft-release-notes")
MAX_SKILL_BYTES = 256 * 1024
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")


class VerificationError(ValueError):
    """An input cannot be verified safely or completely."""


def _regular_bytes(root: Path, relative: Path) -> bytes:
    """Read a bounded file and reject redirecting path components."""
    path = root
    for part in relative.parts:
        path = path / part
        try:
            info = path.lstat()
        except OSError as exc:
            raise VerificationError("required skill file or directory is missing") from exc
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0):
            raise VerificationError("skill path contains a symbolic link or reparse point")
        if path != root / relative and not stat.S_ISDIR(info.st_mode):
            raise VerificationError("skill path has a non-directory component")
    if not stat.S_ISREG(info.st_mode):
        raise VerificationError("skill definition is not a regular file")
    if info.st_size > MAX_SKILL_BYTES:
        raise VerificationError("skill definition exceeds 256 KiB")
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_SKILL_BYTES + 1)
    except OSError as exc:
        raise VerificationError("skill definition could not be read") from exc
    if len(data) > MAX_SKILL_BYTES:
        raise VerificationError("skill definition exceeds 256 KiB")
    return data


def _skill_names(root: Path) -> set[str]:
    directory = root / "skills"
    try:
        if not directory.is_dir() or directory.is_symlink():
            raise VerificationError("skills directory is missing or redirected")
        return {entry.name for entry in directory.iterdir() if entry.is_dir()}
    except OSError as exc:
        raise VerificationError("skills directory cannot be listed") from exc


def _source_commit(root: Path) -> str:
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel", "HEAD"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, timeout=10, check=False, env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VerificationError("cannot inspect pinned source Git checkout") from exc
    lines = result.stdout.strip().splitlines()
    if result.returncode != 0 or len(lines) != 2:
        raise VerificationError("source is not a readable Git checkout")
    if Path(lines[0]).resolve() != root.resolve() or not SHA_RE.fullmatch(lines[1]):
        raise VerificationError("source is not the expected top-level Git checkout")
    return lines[1]


def verify(source: Path, installed: Path, expected_commit: str) -> dict:
    if not SHA_RE.fullmatch(expected_commit):
        raise VerificationError("expected commit must be a full lowercase 40-digit SHA")
    for root in (source, installed):
        if not root.is_absolute() or not root.is_dir() or root.is_symlink():
            raise VerificationError("source and installed roots must be ordinary absolute directories")
    actual_commit = _source_commit(source)
    if actual_commit != expected_commit:
        raise VerificationError("source checkout HEAD differs from the expected commit")
    required = set(SKILLS)
    if _skill_names(source) != required:
        raise VerificationError("source checkout does not contain exactly the four candidate skills")
    if _skill_names(installed) != required:
        raise VerificationError("installed plugin does not contain exactly the four candidate skills")
    mismatch = []
    for skill in SKILLS:
        relative = Path("skills") / skill / "SKILL.md"
        if hashlib.sha256(_regular_bytes(source, relative)).digest() != hashlib.sha256(
                _regular_bytes(installed, relative)).digest():
            mismatch.append(skill)
    return {
        "state": "match" if not mismatch else "mismatch",
        "source_commit": actual_commit,
        "checked_skill_definitions": list(SKILLS),
        "different_skill_definitions": mismatch,
        "limitations": "Byte match only; does not prove plugin installation, discovery, invocation or model behavior.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="clean pinned Git source checkout")
    parser.add_argument("--installed", type=Path, required=True, help="installed plugin cache root")
    parser.add_argument("--expected-commit", required=True, help="full 40-character source commit SHA")
    args = parser.parse_args(argv)
    try:
        report = verify(args.source, args.installed, args.expected_commit)
    except VerificationError as exc:
        print(json.dumps({"state": "incomplete", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["state"] == "match" else 1


if __name__ == "__main__":
    raise SystemExit(main())
