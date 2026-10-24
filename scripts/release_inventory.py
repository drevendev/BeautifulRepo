#!/usr/bin/env python3
"""Read-only, offline commit inventory for an evidence-led release-note draft."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


class InventoryError(ValueError):
    """The requested history cannot be inventoried reliably."""


def git(target: Path, *args: str, allow_missing: bool = False) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "--no-pager", *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=20, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InventoryError(f"could not read local Git history: {exc}") from exc
    if result.returncode != 0:
        if allow_missing:
            return None
        raise InventoryError(f"git {args[0]} failed: {result.stderr.strip()[:300]}")
    return result.stdout.strip()


def inventory(target: Path, base: str | None = None, limit: int = 200) -> dict:
    if limit < 1 or limit > 500:
        raise InventoryError("--limit must be between 1 and 500")
    root = git(target, "rev-parse", "--show-toplevel")
    if not root:
        raise InventoryError("target must be inside a local Git checkout")
    target = Path(root)
    head = git(target, "rev-parse", "--verify", "HEAD^{commit}")
    assert head is not None
    tag = None
    if base is not None:
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", base):
            raise InventoryError("--base must be a hexadecimal commit SHA")
        base_sha = git(target, "rev-parse", "--verify", f"{base}^{{commit}}")
        base_kind = "explicit"
    else:
        tag = git(target, "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", "HEAD", allow_missing=True)
        if tag:
            base_sha = git(target, "rev-parse", "--verify", f"{tag}^{{commit}}")
            base_kind = "tag"
        else:
            roots = (git(target, "rev-list", "--max-parents=0", "HEAD") or "").splitlines()
            if len(roots) != 1:
                raise InventoryError("history has no unique root; pass --base with a commit SHA")
            base_sha = roots[0]
            base_kind = "root"
    assert base_sha is not None
    if git(target, "merge-base", "--is-ancestor", base_sha, head, allow_missing=True) is None:
        raise InventoryError("base is not an ancestor of HEAD")
    history = f"{base_sha}..{head}"
    count = int(git(target, "rev-list", "--count", history) or "0")
    if count > limit:
        raise InventoryError(f"{count} commits exceed --limit {limit}; choose a narrower --base")
    rows = (git(target, "log", "--no-show-signature", "--format=%H%x09%s", history) or "").splitlines()
    commits = []
    for row in rows:
        sha, separator, subject = row.partition("\t")
        if not separator or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise InventoryError("could not parse a commit record")
        commits.append({"sha": sha, "subject": subject})
    if len(commits) != count:
        raise InventoryError("commit inventory does not match the selected history count")
    return {
        "status": "unreleased_draft_only", "head_commit": head, "base_commit": base_sha,
        "base_kind": base_kind, "base_tag": tag, "commit_count": count,
        "commits": commits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="local Git repository path")
    parser.add_argument("--base", help="explicit ancestor commit SHA, otherwise nearest reachable v* tag or unique root")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    try:
        data = inventory(args.target, args.base, args.limit)
    except InventoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
