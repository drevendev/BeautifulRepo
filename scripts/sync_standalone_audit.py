#!/usr/bin/env python3
"""Keep the bundled standalone audit skill byte-identical to canonical sources."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "skills" / "audit-repo"
FILES = (
    "tools/repo_audit.py", "tools/docs_links.py", "tools/html_navigation.py",
    "checklists/repository.md", "checklists/first-success.md",
    "checklists/confidentiality.md", "guides/agent-safety.md",
    "guides/private-repositories.md",
)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    failures = []
    for name in FILES:
        source, dest = ROOT / name, BUNDLE / name
        if not source.is_file() or source.is_symlink():
            failures.append("unsafe/missing source: " + name)
            continue
        if args.write:
            if dest.is_symlink() or (dest.exists() and not dest.is_file()):
                failures.append("unsafe bundle destination: " + name)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        if dest.is_symlink() or not dest.is_file() or dest.read_bytes() != source.read_bytes():
            failures.append("missing/stale bundle: " + name)
    for problem in failures:
        print(problem, file=sys.stderr)
    if failures:
        return 1
    print(f"audit-repo bundle: {len(FILES)} files byte-identical")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
