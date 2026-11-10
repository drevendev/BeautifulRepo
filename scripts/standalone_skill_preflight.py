#!/usr/bin/env python3
"""Check whether one installed BeautifulRepo skill has its required sibling files.

Read-only filesystem presence check. It is not a skills CLI, an integrity attestation,
or evidence that an agent discovered, selected or ran a skill.
"""
from __future__ import annotations

import argparse
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


class ProbeError(ValueError):
    """Cannot assess an installed skill definition safely."""


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


def inspect(path: Path) -> dict:
    """Report required files at the exact two-level-up SKILL.md fallback root."""
    skill_dir = Path(os.path.abspath(path))
    if skill_dir.name == "SKILL.md":
        skill_dir = skill_dir.parent
    if skill_dir.name not in REQUIRED:
        raise ProbeError("expected one of the four BeautifulRepo skill directories")
    root = skill_dir.parent.parent
    # A relocated skill may be discoverable, but a redirected definition is not
    # acceptable evidence for this structural check.
    if not _ordinary(skill_dir.parent, Path(skill_dir.name) / "SKILL.md"):
        raise ProbeError("installed SKILL.md is missing, redirected or not an ordinary file")
    needed = REQUIRED[skill_dir.name]
    missing = [name for name in needed if not _ordinary(root, Path(name))]
    return {
        "skill": skill_dir.name,
        "assumed_root": str(root),
        "checked_required_files": len(needed),
        "missing_or_redirected": missing,
        "state": "present" if not missing else "incomplete",
        "limitations": (
            "Presence of named sibling files only. Not their bytes or safety, a skills.sh "
            "installation result, execution, discovery, model behavior or privacy guarantee."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path, help="installed skill directory or its SKILL.md")
    args = parser.parse_args(argv)
    try:
        result = inspect(args.skill)
    except ProbeError as exc:
        print(json.dumps({"state": "invalid", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["state"] == "present" else 1


if __name__ == "__main__":
    raise SystemExit(main())
