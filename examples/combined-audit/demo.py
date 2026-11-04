#!/usr/bin/env python3
"""Reproduce a synthetic broken-link repair using the real combined audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "tools" / "audit_bundle.py"
LINK_CHECKS = ("markdown_links", "html_navigation")


def make_fixture(folder: Path, *, broken: bool) -> None:
    """Create a tiny fictional checkout; never touch a real project."""
    folder.mkdir()
    (folder / "docs").mkdir()
    destination = "docs/setup.md" if broken else "docs/guide.md"
    (folder / "README.md").write_text(
        "# Pocket Trails\n\n"
        "Pocket Trails is a fictional offline trail-notes project.\n\n"
        "## First success\n\n"
        f"Read the [setup guide]({destination}) to begin.\n\n"
        "## Contribute\n\n"
        "See [CONTRIBUTING.md](CONTRIBUTING.md).\n",
        encoding="utf-8",
    )
    (folder / "docs" / "guide.md").write_text(
        "# Setup guide\n\nThis is deliberately fictional documentation.\n",
        encoding="utf-8",
    )
    (folder / "LICENSE").write_text(
        "MIT License\n\nThis is a synthetic test fixture, not a real release.\n",
        encoding="utf-8",
    )
    (folder / "CONTRIBUTING.md").write_text(
        "# Contributing\n\nOpen a small, reproducible change.\n", encoding="utf-8"
    )


def file_bytes(folder: Path) -> dict[str, bytes]:
    return {
        file.relative_to(folder).as_posix(): file.read_bytes()
        for file in folder.rglob("*") if file.is_file()
    }


def run_audit(folder: Path) -> dict:
    original = file_bytes(folder)
    completed = subprocess.run(
        [sys.executable, "-I", str(BUNDLE), str(folder), "--format", "json",
         "--fail-on", "never"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        check=False, timeout=75,
    )
    if not completed.stdout:
        raise RuntimeError("combined audit produced no JSON: " +
                           completed.stderr.strip()[:250])
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("combined audit did not produce valid JSON") from exc
    if (not isinstance(report, dict) or report.get("schema_version") != 1
            or report.get("exit_code") != completed.returncode):
        raise RuntimeError("combined audit exit status does not match its report")
    if file_bytes(folder) != original:
        raise RuntimeError("combined audit modified the synthetic checkout")
    return report


def demonstrate() -> dict:
    with tempfile.TemporaryDirectory(prefix="beautifulrepo-demo-") as temporary:
        root = Path(temporary)
        before, after = root / "before", root / "after"
        make_fixture(before, broken=True)
        make_fixture(after, broken=False)
        results = {"before": run_audit(before), "after": run_audit(after)}
    for label, expected in (("before", 1), ("after", 0)):
        result = results[label]
        if result["exit_code"] != expected:
            raise RuntimeError(f"{label} audit exited {result['exit_code']}, expected {expected}")
        if any(item["state"] != "complete" for item in result["checks"].values()):
            raise RuntimeError(f"{label} audit is incomplete, not a valid demonstration")
    for checker in LINK_CHECKS:
        broken = results["before"]["checks"][checker]
        fixed = results["after"]["checks"][checker]
        if (broken["exit_code"] != 1 or fixed["exit_code"] != 0
                or not any("docs/setup.md" in line for line in broken["diagnostics"])):
            raise RuntimeError(f"{checker} did not reproduce the expected link repair")
    return {"fixture_kind": "synthetic", "reports": results,
            "verification": "Both link checkers found the missing path before and cleared after; no fixture writes by the audit."}


def text_report(result: dict) -> str:
    lines = ["Synthetic Pocket Trails — real BeautifulRepo combined audit output",
             "The repair changes one README link to an existing local guide."]
    for label in ("before", "after"):
        report = result["reports"][label]
        lines.append(f"\n{label.upper()}: combined exit {report['exit_code']}")
        for checker, item in report["checks"].items():
            if checker == "entry_points":
                counts = item["report"]["summary"]
                lines.append(
                    f"  {checker}: {counts['error']} errors, {counts['warning']} warnings, "
                    f"{counts['info']} informational findings"
                )
            else:
                lines.append(f"  {checker}: exit {item['exit_code']}, "
                             f"{item['inspected_markdown_files']} Markdown files inspected")
                if label == "before":
                    lines.extend(f"    {message}" for message in item["diagnostics"])
    lines.extend(("\n" + result["verification"],
                  "Synthetic exercise; not a real repository improvement, external link check, "
                  "rendering test or accessibility certificate."))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = demonstrate()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"Demo incomplete: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print(text_report(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
