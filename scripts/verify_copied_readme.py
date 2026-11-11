#!/usr/bin/env python3
"""Check bundled README tools on a disposable synthetic target, not on user code."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run(tool: Path, root: Path, proposal: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(tool), "--root", str(root),
         "--proposal", str(proposal), *args],
        capture_output=True, text=True, encoding="utf-8", timeout=15,
    )


def verify(skill: Path) -> dict:
    preview = skill / "tools/readme_preview.py"
    apply = skill / "tools/readme_apply.py"
    for tool in (preview, apply):
        if not tool.is_file() or tool.is_symlink():
            raise ValueError(f"missing/redirected copied helper: {tool.name}")
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root = base / "fictional-target"
        root.mkdir()
        readme = root / "README.md"
        other = root / "do-not-run.py"
        proposal = base / "candidate.md"
        before = b"# Fictional project\n\nBefore.\n"
        after = b"# Fictional project\n\nAfter.\n"
        readme.write_bytes(before)
        proposal.write_bytes(after)
        other.write_text("raise RuntimeError('do not run me')\n", encoding="utf-8")
        other_bytes = other.read_bytes()

        shown = run(preview, root, proposal, "--expected-sha256", digest(before))
        if shown.returncode != 0 or "-Before." not in shown.stdout or "+After." not in shown.stdout:
            raise AssertionError("copied preview did not produce the expected unified diff")
        if readme.read_bytes() != before:
            raise AssertionError("preview modified README")
        stale = run(preview, root, proposal, "--expected-sha256", "0" * 64)
        if stale.returncode != 2 or readme.read_bytes() != before:
            raise AssertionError("stale README hash was accepted")
        no_hash = run(apply, root, proposal)
        if no_hash.returncode != 2 or readme.read_bytes() != before:
            raise AssertionError("apply wrote without approval hashes")
        wrong = run(apply, root, proposal, "--approved-current-sha256",
                    digest(before), "--approved-proposed-sha256", "0" * 64)
        if wrong.returncode != 2 or readme.read_bytes() != before:
            raise AssertionError("incorrect proposal hash accepted")
        # This is a synthetic authorized fixture, NOT an agent's permission to edit.
        good = run(apply, root, proposal, "--approved-current-sha256",
                   digest(before), "--approved-proposed-sha256", digest(after))
        if good.returncode != 0 or readme.read_bytes() != after:
            raise AssertionError("exact-hash fixture apply did not edit only README")
        if other.read_bytes() != other_bytes or proposal.read_bytes() != after:
            raise AssertionError("copied helper changed unrelated/proposal bytes")
    return {"passed": True, "fixture": "disposable synthetic target",
            "checks": ["diff/no-write", "stale-refusal", "missing-hashes-refusal",
                       "wrong-proposal-refusal", "exact-hash README-only apply"],
            "limitations": "No human approval/authentication or model invocation is tested."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = verify(args.skill_root)
    except (AssertionError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"copied README behavior failed: {exc}", file=sys.stderr)
        return 1
    result = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
