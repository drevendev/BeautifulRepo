#!/usr/bin/env python3
"""Check whether one installed BeautifulRepo skill has its required sibling files.

Read-only filesystem presence check. It is not a skills CLI, an integrity attestation,
or evidence that an agent discovered, selected or ran a skill.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

REQUIRED = {
    "audit-repo": (
        "tools/repo_audit.py", "tools/docs_links.py", "tools/html_navigation.py",
        "checklists/repository.md", "checklists/first-success.md",
        "guides/agent-safety.md",
    ),
    "improve-readme": (
        "tools/repo_audit.py", "tools/docs_links.py", "tools/html_navigation.py",
        "tools/readme_preview.py", "tools/readme_apply.py",
        "checklists/repository.md", "checklists/first-success.md",
        "checklists/confidentiality.md", "guides/agent-safety.md",
        "guides/cli-repositories.md", "templates/README.template.md",
        "templates/LIBRARY_README.template.md", "templates/APPLICATION_README.template.md",
        "templates/RESEARCH_DATA_README.template.md", "templates/CURATED_README.template.md",
        "templates/INTERNAL_README.template.md",
    ),
    "trust-surfaces": (
        "tools/repo_audit.py", "guides/agent-safety.md",
        "guides/community-safety.md", "guides/private-repositories.md",
        "checklists/repository.md", "checklists/confidentiality.md",
        "templates/SECURITY.template.md",
    ),
    "draft-release-notes": (
        "scripts/release_inventory.py", "guides/agent-safety.md",
        "guides/release-notes.md", "templates/RELEASE_NOTES.template.md",
    ),
}


MAX_COMPARE_BYTES = 2 * 1024 * 1024


class ProbeError(ValueError):
    """Cannot assess an installed skill definition safely."""


def _ordinary_directory_chain(path: Path) -> bool:
    """Refuse redirected directory ancestors, including prefixes before '..'.

    Inspect the lexical route before abspath() normalizes it; otherwise a
    symlinked directory followed by '..' can disappear from the checked path.
    """
    lexical = path if path.is_absolute() else Path.cwd() / path
    cursor = Path(lexical.anchor)
    try:
        for part in lexical.parts[1:]:
            if part == "..":
                cursor = cursor.parent
                continue
            if part == ".":
                continue
            cursor = cursor / part
            info = cursor.lstat()
            if (
                not stat.S_ISDIR(info.st_mode)
                or stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_reparse_tag", 0)
            ):
                return False
        return True
    except OSError:
        return False


def _ordinary(root: Path, relative: Path) -> bool:
    """Refuse links/reparse points at every descendant component."""
    cursor = root
    try:
        info = cursor.lstat()
        if not stat.S_ISDIR(info.st_mode) or getattr(info, "st_reparse_tag", 0):
            return False
        for part in relative.parts:
            if part in (".", ".."):
                return False
            cursor = cursor / part
            info = cursor.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0):
                return False
        return stat.S_ISREG(info.st_mode)
    except OSError:
        return False


def _digest_file(path: Path) -> bytes:
    """Compare bounded file bytes; do not execute or parse installed content."""
    digest = hashlib.sha256()
    read_bytes = 0
    try:
        with path.open("rb") as source:
            while chunk := source.read(65536):
                read_bytes += len(chunk)
                if read_bytes > MAX_COMPARE_BYTES:
                    raise ProbeError("comparison file exceeds 2 MiB limit")
                digest.update(chunk)
    except OSError as exc:
        raise ProbeError("comparison file could not be read") from exc
    return digest.digest()


def inspect(path: Path, *, source_root: Path | None = None) -> dict:
    """Report required sibling files, optionally comparing a pinned local source."""
    lexical_skill_dir = path.parent if path.name == "SKILL.md" else path
    if lexical_skill_dir.name not in REQUIRED:
        raise ProbeError("expected one of the four BeautifulRepo skill directories")
    # Check every lexical ancestor before abspath() erases '..' components.
    # This includes parents above the assumed two-up root, not just its files.
    if not _ordinary_directory_chain(lexical_skill_dir):
        raise ProbeError("installed skill path is missing or redirected through an ancestor")
    skill_dir = Path(os.path.abspath(lexical_skill_dir))
    plugin_root = skill_dir.parent.parent
    # A relocated skill may be discoverable, but a redirected definition is not
    # acceptable evidence for this structural check.
    if not _ordinary(skill_dir.parent, Path(skill_dir.name) / "SKILL.md"):
        raise ProbeError("installed SKILL.md is missing, redirected or not an ordinary file")
    needed = REQUIRED[skill_dir.name]
    plugin_ready = all(_ordinary(plugin_root, Path(name)) for name in needed)
    # Three skills now provide self-contained copies. Prefer a full plugin
    # if complete; otherwise probe the copied skill folder.
    bundled_hint = skill_dir.name in ("audit-repo", "draft-release-notes", "improve-readme") and any(
        (skill_dir / name).exists() or (skill_dir / name).is_symlink()
        for name in needed
    )
    root = skill_dir if bundled_hint and not plugin_ready else plugin_root
    missing = [name for name in needed if not _ordinary(root, Path(name))]
    report = {
        "skill": skill_dir.name,
        "assumed_root": str(root),
        "layout": "self-contained" if root == skill_dir else "full-repository",
        "checked_required_files": len(needed),
        "missing_or_redirected": missing,
        "state": "present" if not missing else "incomplete",
        "limitations": (
            "Presence of named sibling files only. Not their bytes or safety, a skills.sh "
            "installation result, execution, discovery, model behavior or privacy guarantee."
        ),
    }
    if source_root is not None:
        # A separate, verified immutable checkout must be selected by the caller.
        # These bytes alone cannot authenticate that checkout or certify safety.
        if not _ordinary_directory_chain(source_root):
            raise ProbeError("source root is missing or redirected through an ancestor")
        reference_root = Path(os.path.abspath(source_root))
        if reference_root == root:
            raise ProbeError("source root must differ from installed skill root")
        relative_files = (f"skills/{skill_dir.name}/SKILL.md", *needed)
        bundled = root == skill_dir
        for relative in relative_files:
            source_relative = (
                f"skills/{skill_dir.name}/{relative}" if bundled and
                relative != f"skills/{skill_dir.name}/SKILL.md" else relative
            )
            if not _ordinary(reference_root, Path(source_relative)):
                raise ProbeError(f"source reference missing or redirected: {source_relative}")
        mismatched = []
        for relative in relative_files:
            # The copied SKILL.md lives directly in the installed skill folder.
            installed_path = (
                skill_dir / "SKILL.md"
                if relative == f"skills/{skill_dir.name}/SKILL.md"
                else root / relative
            )
            if (
                (relative.startswith("skills/") or _ordinary(root, Path(relative)))
                and _digest_file(installed_path) != _digest_file(
                    reference_root / (
                        f"skills/{skill_dir.name}/{relative}" if bundled and
                        relative != f"skills/{skill_dir.name}/SKILL.md" else relative
                    )
                )
            ):
                mismatched.append(relative)
        report["limitations"] = (
            "Presence and local byte equality only. Not source authentication, "
            "execution, discovery, model behavior or privacy guarantees."
        )
        report["source_comparison"] = {
            "checked_files": len(relative_files),
            "mismatched": mismatched,
            "limitations": (
                "Compares local bytes to a caller-selected source directory. "
                "Does not verify its commit, trust, provenance, execution or host discovery."
            ),
        }
        if mismatched and not missing:
            report["state"] = "mismatch"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path, help="installed skill directory or its SKILL.md")
    parser.add_argument(
        "--source-root", type=Path,
        help="separate locally verified pinned BeautifulRepo checkout for byte comparison",
    )
    args = parser.parse_args(argv)
    try:
        result = inspect(args.skill, source_root=args.source_root)
    except ProbeError as exc:
        print(json.dumps({"state": "invalid", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["state"] == "present" else 1


if __name__ == "__main__":
    raise SystemExit(main())
