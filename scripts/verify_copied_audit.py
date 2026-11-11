#!/usr/bin/env python3
"""Exercise every copied standalone audit checker on disposable local fixtures.

This verifies observed checker behavior, not agent discovery, model invocation,
tool safety on arbitrary target repositories, or supported skills.sh distribution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

TOOLS = ("repo_audit.py", "docs_links.py", "html_navigation.py")
BROKEN = (
    "# Synthetic Repo\n\nAn unfinished TODO is visible.\n\n"
    "[missing guide](absent.md)\n\n<a href=\"absent.md#setup\">Unavailable</a>\n"
)
FIXED = (
    "# Synthetic Repo\n\n[setup guide](guide.md#setup)\n\n"
    "<a href=\"guide.md#setup\">View setup</a>\n"
)
GUIDE = "# Guide\n\n## Setup\n\nSynthetic instructions only.\n"


def snapshot(root: Path) -> dict[str, str]:
    """Capture every regular file's bytes and reject redirected fixture content."""
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("synthetic fixture contains a redirected entry")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def run_trial(skill_root: Path, output_dir: Path) -> dict:
    """Run all copied tools against both positive and negative synthetic cases."""
    skill_root = skill_root.resolve(strict=True)
    if not skill_root.is_dir():
        raise ValueError("installed skill root is not a directory")
    for name in TOOLS:
        tool = skill_root / "tools" / name
        if tool.is_symlink() or not tool.is_file():
            raise ValueError("copied checker missing or redirected: " + name)

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"cases": {}, "scope": "copied offline checkers on synthetic fixtures; not agent activation"}
    for case, readme in (("broken", BROKEN), ("fixed", FIXED)):
        target = output_dir / ("fixture-" + case)
        if target.exists():
            raise ValueError("refusing to reuse existing trial fixture: " + str(target))
        target.mkdir()
        (target / "README.md").write_text(readme, encoding="utf-8")
        if case == "fixed":
            (target / "guide.md").write_text(GUIDE, encoding="utf-8")
        original = snapshot(target)
        outcomes = {}
        for name in TOOLS:
            command = [sys.executable, "-I", str(skill_root / "tools" / name)]
            if name == "repo_audit.py":
                command += [str(target), "--format", "json", "--fail-on", "never"]
            else:
                command += ["--root", str(target)]
            completed = subprocess.run(
                command, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=40, check=False, cwd=output_dir,
            )
            stem = case + "-" + name.removesuffix(".py")
            (output_dir / (stem + ".stdout")).write_text(completed.stdout, encoding="utf-8")
            (output_dir / (stem + ".stderr")).write_text(completed.stderr, encoding="utf-8")
            outcomes[name] = completed.returncode

            expected = 0 if name == "repo_audit.py" or case == "fixed" else 1
            if completed.returncode != expected:
                raise AssertionError(
                    f"{case}/{name}: exit {completed.returncode}, expected {expected}; "
                    f"stderr={completed.stderr[:300]!r}"
                )
            if name == "repo_audit.py":
                report = json.loads(completed.stdout)
                if report.get("documents", {}).get("readme") != "README.md":
                    raise AssertionError("copied repo audit did not inspect fixture README")
                rules = {item["rule_id"] for item in report["findings"]}
                if "license.missing" not in rules:
                    raise AssertionError("copied repo audit did not report missing LICENSE")
                if ("readme.placeholder" in rules) != (case == "broken"):
                    raise AssertionError("copied repo audit did not distinguish TODO case")
            elif case == "broken" and "missing" not in completed.stderr.lower():
                raise AssertionError(f"{name} failed without a missing-destination diagnosis")
            elif case == "fixed" and "OK:" not in completed.stdout:
                raise AssertionError(f"{name} did not report a clean local link scan")
            if snapshot(target) != original:
                raise AssertionError(f"{name} modified the disposable target")

        result["cases"][case] = {"exits": outcomes, "fixture_sha256": original}
    (output_dir / "trial-summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = run_trial(args.skill_root, args.output_dir)
    except (OSError, ValueError, AssertionError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"copied audit behavioral trial failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
