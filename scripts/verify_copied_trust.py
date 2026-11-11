#!/usr/bin/env python3
"""Test a copied trust checker on synthetic repositories only, never user targets."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def snapshot(root: Path) -> dict[str, str]:
    result = {}
    for file in sorted(root.rglob("*")):
        if file.is_symlink():
            raise ValueError("redirected fixture")
        if file.is_file():
            result[file.relative_to(root).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return result


def verify(skill: Path) -> dict:
    checker = skill / "tools/repo_audit.py"
    if not checker.is_file() or checker.is_symlink():
        raise ValueError("missing/redirected copied checker")
    outcomes = {}
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        for case, license_present in (("missing-license", False), ("license-present", True)):
            target = base / case
            target.mkdir()
            (target / "README.md").write_text("# Fictional repository\n\nRead-only audit.\n", encoding="utf-8")
            (target / "SECURITY.md").write_text("# Draft\n\nNo verified intake route.\n", encoding="utf-8")
            (target / "do-not-run.py").write_text("raise RuntimeError('do not execute')\n", encoding="utf-8")
            if license_present:
                (target / "LICENSE").write_text("Synthetic license fixture, not legal advice.\n", encoding="utf-8")
            before = snapshot(target)
            ran = subprocess.run(
                [sys.executable, "-I", str(checker), str(target),
                 "--format", "json", "--fail-on", "never"],
                cwd=base, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=40, check=False,
            )
            if ran.returncode:
                raise AssertionError(f"{case}: exit {ran.returncode}: {ran.stderr[:250]}")
            report = json.loads(ran.stdout)
            if report.get("documents", {}).get("readme") != "README.md":
                raise AssertionError("copied checker did not inspect fixture")
            found = {x["rule_id"] for x in report["findings"]}
            if ("license.missing" in found) == license_present:
                raise AssertionError(f"{case}: missing-license diagnosis does not match fixture")
            if snapshot(target) != before:
                raise AssertionError("copied checker modified fixture")
            outcomes[case] = {"exit": ran.returncode, "missing_license": "license.missing" in found,
                              "before_sha256": before}
    return {"passed": True, "cases": outcomes, "limitations": (
        "Local synthetic checker execution only, not model-host discovery, "
        "a verified reporting inbox or legal analysis."
    )}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.skill_root)
    except (AssertionError, OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"copied trust checker trial failed: {error}", file=sys.stderr)
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
