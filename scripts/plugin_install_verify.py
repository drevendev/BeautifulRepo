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
# Files the four skills explicitly require locally: executable helpers, safety
# and task guides, checklists and starter templates. This is intentionally not
# an attestation of the entire plugin tree or host-side skill discovery.
DEPENDENCIES = (
    "tools/repo_audit.py",
    "tools/docs_links.py",
    "tools/html_navigation.py",
    "tools/readme_preview.py",
    "tools/readme_apply.py",
    "scripts/release_inventory.py",
    "guides/agent-safety.md",
    "guides/cli-repositories.md",
    "guides/community-safety.md",
    "guides/private-repositories.md",
    "guides/release-notes.md",
    "checklists/repository.md",
    "checklists/first-success.md",
    "checklists/confidentiality.md",
    "templates/README.template.md",
    "templates/LIBRARY_README.template.md",
    "templates/APPLICATION_README.template.md",
    "templates/RESEARCH_DATA_README.template.md",
    "templates/CURATED_README.template.md",
    "templates/INTERNAL_README.template.md",
    "templates/SECURITY.template.md",
    "templates/RELEASE_NOTES.template.md",
)
# Installed plugin caches may omit marketplace metadata. Compare actual plugin
# manifests only when present; never infer their presence from a source checkout.
OPTIONAL_MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json")
MAX_SKILL_BYTES = 256 * 1024
MAX_TRACKED_SKILL_FILES = 512
MAX_SKILL_TREE_BYTES = 128 * 1024
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")


class VerificationError(ValueError):
    """An input cannot be verified safely or completely."""


def _is_redirected(path: Path, info: os.stat_result) -> bool:
    """Recognize links and Windows reparse points without following them."""
    return (
        stat.S_ISLNK(info.st_mode)
        or bool(getattr(info, "st_reparse_tag", 0))
        or bool(getattr(info, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
        or getattr(path, "is_junction", lambda: False)()
    )


def _ordinary_root(root: Path) -> None:
    """Reject redirected ancestors as well as a redirected final directory.

    A symlinked parent could otherwise make a cached plugin appear to be in
    a different location while reading bytes from somewhere else. This is
    a point-in-time preflight, not protection against concurrent replacement.
    """
    if not root.is_absolute():
        raise VerificationError("source and installed roots must be ordinary absolute directories")
    for component in reversed((root, *root.parents)):
        try:
            info = component.lstat()
        except OSError as exc:
            raise VerificationError("source or installed root cannot be inspected") from exc
        if _is_redirected(component, info):
            raise VerificationError("source or installed root has a redirected component")
        if not stat.S_ISDIR(info.st_mode):
            raise VerificationError("source and installed roots must be ordinary absolute directories")


def _regular_bytes(root: Path, relative: Path) -> bytes:
    """Read a bounded file and reject redirecting path components."""
    path = root
    for part in relative.parts:
        path = path / part
        try:
            info = path.lstat()
        except OSError as exc:
            raise VerificationError("required skill file or directory is missing") from exc
        if _is_redirected(path, info):
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


def _committed_bytes(root: Path, commit: str, relative: Path) -> bytes:
    """Read the immutable Git blob, never uncommitted source working-tree bytes."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    blob = f"{commit}:{relative.as_posix()}"
    try:
        size = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-s", blob],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, timeout=10, check=False, env=env,
        )
        if size.returncode != 0 or not size.stdout.strip().isdigit():
            raise VerificationError("skill is not present in pinned Git commit")
        if int(size.stdout.strip()) > MAX_SKILL_BYTES:
            raise VerificationError("pinned skill definition exceeds 256 KiB")
        content = subprocess.run(
            ["git", "-C", str(root), "show", blob],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=10, check=False, env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VerificationError("cannot read pinned skill definition") from exc
    if content.returncode != 0 or len(content.stdout) != int(size.stdout.strip()):
        raise VerificationError("pinned skill definition could not be verified")
    return content.stdout


def _committed_skill_assets(root: Path, commit: str) -> list[Path]:
    """Enumerate tracked files beyond SKILL.md from the immutable source tree.

    Verify actual copied scripts and references, not just their entry-point
    instructions. Host-generated untracked extras remain outside this check.
    """
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "-z", commit, "--", "skills"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=10, check=False, env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VerificationError("cannot enumerate pinned skill assets") from exc
    if result.returncode != 0 or len(result.stdout) > MAX_SKILL_TREE_BYTES:
        raise VerificationError("pinned skill inventory is unavailable or too large")
    files: list[Path] = []
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode, kind, _object_id = header.split(b" ")
            name = raw_path.decode("utf-8")
        except (ValueError, UnicodeError) as exc:
            raise VerificationError("pinned skill inventory contains an invalid entry") from exc
        parts = name.split("/")
        if (len(parts) < 3 or parts[0] != "skills" or parts[1] not in SKILLS
                or any(part in ("", ".", "..") or "\\" in part for part in parts)
                or mode not in (b"100644", b"100755") or kind != b"blob"):
            raise VerificationError("pinned skill inventory has an unsupported path or file type")
        if len(parts) == 3 and parts[2] == "SKILL.md":
            continue
        files.append(Path(name))
        if len(files) > MAX_TRACKED_SKILL_FILES:
            raise VerificationError("pinned skill inventory exceeds the file limit")
    return sorted(files, key=lambda path: path.as_posix())


def verify(source: Path, installed: Path, expected_commit: str) -> dict:
    if not SHA_RE.fullmatch(expected_commit):
        raise VerificationError("expected commit must be a full lowercase 40-digit SHA")
    for root in (source, installed):
        _ordinary_root(root)
    try:
        if source.samefile(installed):
            raise VerificationError("source and installed must be distinct physical directories")
    except OSError as exc:
        raise VerificationError("cannot establish distinct source and installed directories") from exc
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
        if hashlib.sha256(_committed_bytes(source, actual_commit, relative)).digest() != hashlib.sha256(
                _regular_bytes(installed, relative)).digest():
            mismatch.append(skill)
    skill_assets = _committed_skill_assets(source, actual_commit)
    different_assets = []
    for relative in skill_assets:
        if hashlib.sha256(_committed_bytes(source, actual_commit, relative)).digest() != hashlib.sha256(
                _regular_bytes(installed, relative)).digest():
            different_assets.append(relative.as_posix())
    dependency_mismatch = []
    for name in DEPENDENCIES:
        relative = Path(name)
        if hashlib.sha256(_committed_bytes(source, actual_commit, relative)).digest() != hashlib.sha256(
                _regular_bytes(installed, relative)).digest():
            dependency_mismatch.append(name)
    checked_manifests = []
    missing_manifests = []
    different_manifests = []
    for name in OPTIONAL_MANIFESTS:
        relative = Path(name)
        present = True
        path = installed
        for index, part in enumerate(relative.parts):
            path = path / part
            try:
                info = path.lstat()
            except FileNotFoundError:
                # A genuinely absent optional manifest is not host evidence.
                missing_manifests.append(name)
                present = False
                break
            except OSError as exc:
                raise VerificationError("optional plugin manifest could not be inspected") from exc
            # Inspect parents before classifying a missing file; a dangling
            # symlinked directory must never be reported as harmless absence.
            if _is_redirected(path, info):
                raise VerificationError("optional plugin manifest has a redirected component")
            if index < len(relative.parts) - 1 and not stat.S_ISDIR(info.st_mode):
                raise VerificationError("optional plugin manifest parent is not a directory")
        if not present:
            continue
        checked_manifests.append(name)
        if hashlib.sha256(_committed_bytes(source, actual_commit, relative)).digest() != hashlib.sha256(
                _regular_bytes(installed, relative)).digest():
            different_manifests.append(name)
    return {
        "state": "match" if not mismatch and not different_assets and not dependency_mismatch and not different_manifests else "mismatch",
        "source_commit": actual_commit,
        "checked_skill_definitions": list(SKILLS),
        "different_skill_definitions": mismatch,
        "checked_skill_assets": [path.as_posix() for path in skill_assets],
        "different_skill_assets": different_assets,
        "checked_plugin_dependencies": list(DEPENDENCIES),
        "different_plugin_dependencies": dependency_mismatch,
        "checked_present_manifests": checked_manifests,
        "missing_optional_manifests": missing_manifests,
        "different_present_manifests": different_manifests,
        "limitations": (
            "Byte match of pinned skill definitions, tracked skill assets, named "
            "shared dependencies and present optional manifests only. Missing "
            "manifests and untracked extra cache files are unverified; this is "
            "not a full plugin attestation or proof of installation, discovery, "
            "invocation or model behavior."
        ),
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
