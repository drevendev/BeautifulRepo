#!/usr/bin/env python3
"""Keep the bundled standalone release-note skill deterministically derived from canonical sources."""
from __future__ import annotations
import argparse
from pathlib import Path
import posixpath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "skills" / "draft-release-notes"
FILES = (
    "scripts/release_inventory.py", "guides/agent-safety.md",
    "guides/release-notes.md", "templates/RELEASE_NOTES.template.md",
)

LINK = re.compile(r"(\]\()([^\s)]+)(\))")

def render(name: str) -> bytes:
    """Rewrite only links to files intentionally omitted from the copied package."""
    raw = (ROOT / name).read_bytes()
    if not name.endswith(".md"):
        return raw
    def rewrite(match: re.Match[str]) -> str:
        uri = match.group(2)
        if uri.startswith(("https://", "http://", "mailto:", "#")):
            return match.group(0)
        link, marker, fragment = uri.partition("#")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), link))
        if resolved in FILES:
            return match.group(0)
        if resolved.startswith("../") or not (ROOT / resolved).is_file():
            raise ValueError("unresolved source link " + name + ": " + uri)
        url = "https://github.com/drevendev/BeautifulRepo/blob/master/" + resolved
        if marker:
            url += "#" + fragment
        return match.group(1) + url + match.group(3)
    return LINK.sub(rewrite, raw.decode("utf-8")).encode("utf-8")


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
        try:
            expected = render(name)
        except (OSError, UnicodeError, ValueError) as exc:
            failures.append("cannot generate: " + name + ": " + str(exc))
            continue
        if args.write:
            if dest.is_symlink() or (dest.exists() and not dest.is_file()):
                failures.append("unsafe bundle destination: " + name)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(expected)
        if dest.is_symlink() or not dest.is_file() or dest.read_bytes() != expected:
            failures.append("missing/stale bundle: " + name)
    for problem in failures:
        print(problem, file=sys.stderr)
    if failures:
        return 1
    print(f"draft-release-notes bundle: {len(FILES)} deterministic copies match")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
