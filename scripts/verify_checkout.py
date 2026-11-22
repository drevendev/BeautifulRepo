"""Run BeautifulRepo's Python Quality CI steps locally, in their workflow order.

This deliberately targets *this tool's checkout*, not a foreign repository under
review. The GitHub Actions matrix, self-test jobs and linter remain separate.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
# Keep this fixed inventory aligned with .github/workflows/quality.yml's catalog job.
# Each argv is literal; no shell, command interpolation or input repository scripts.
CHECKS = (
    ("first-minute demo", ("-I", "examples/combined-audit/demo.py")),
    ("combined audit", ("-I", "tools/audit_bundle.py", ".", "--fail-on", "never")),
    ("unit tests", ("-m", "unittest", "discover", "-s", "tests", "-v")),
    ("catalog", ("tools/catalog.py",)),
    ("Markdown destinations", ("tools/docs_links.py",)),
    ("HTML navigation", ("tools/html_navigation.py",)),
    ("Action SHA pins", ("-I", "tools/action_pins.py", "--root", ".")),
    (
        "README badge",
        ("-I", "tools/workflow_badges.py", "--root", ".", "--repo", "drevendev/BeautifulRepo", "--require-badge"),
    ),
    ("repository entry points", ("tools/repo_audit.py", ".")),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the Python portion of BeautifulRepo Quality CI on this checkout."
    )
    parser.add_argument("--list", action="store_true", help="Print the fixed checks; do not execute them")
    parser.add_argument("--keep-going", action="store_true", help="Continue with independent checks after a failure")
    args = parser.parse_args(argv)

    if args.list:
        for label, command in CHECKS:
            print(f"{label}: python {' '.join(command)}")
        return 0

    failed: list[str] = []
    for index, (label, command) in enumerate(CHECKS, start=1):
        print(f"\n[{index}/{len(CHECKS)}] {label}: python {' '.join(command)}", flush=True)
        try:
            result = subprocess.run([sys.executable, *command], cwd=ROOT, check=False)
            status = result.returncode
        except OSError as exc:
            print(f"ERROR: could not launch {label}: {exc}", file=sys.stderr, flush=True)
            status = 2
        if status != 0:
            failed.append(f"{label} (exit {status})")
            print(f"FAIL: {label} (exit {status})", file=sys.stderr, flush=True)
            if not args.keep_going:
                break

    if failed:
        print(f"FAIL: {len(failed)} check(s): {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"OK: all {len(CHECKS)} local Python checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
