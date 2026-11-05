"""Exercise the documented first-audit command against an untouched target.

Unlike an in-process unit test, this is the public CLI called from a separate
checkout on Linux/Windows CI runners, with a target path containing spaces.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools" / "audit_bundle.py"
LINK_CHECKS = ("markdown_links", "html_navigation")


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*") if path.is_file()
    }


class FirstVisitTests(unittest.TestCase):
    def check_checkout(self, target: Path, expected_exit: int, missing: bool) -> None:
        before = file_snapshot(target)
        completed = subprocess.run(
            [sys.executable, "-I", str(AUDIT), str(target),
             "--fail-on", "never", "--format", "json"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            timeout=90, check=False,
        )
        self.assertEqual(expected_exit, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(1, report["schema_version"])
        self.assertEqual(expected_exit, report["exit_code"])
        self.assertEqual("complete", report["checks"]["entry_points"]["state"])
        for checker in LINK_CHECKS:
            result = report["checks"][checker]
            self.assertEqual("complete", result["state"])
            self.assertEqual(int(missing), result["exit_code"])
            diagnostics = "\n".join(result["diagnostics"])
            if missing:
                self.assertIn("docs/setup.md", diagnostics)
            else:
                self.assertEqual("", diagnostics)
        self.assertEqual(before, file_snapshot(target), "audit changed target files")

    def test_copy_pastable_external_checkout_path_and_repair(self):
        with tempfile.TemporaryDirectory(prefix="beautifulrepo-first-visit-") as tmp:
            target = Path(tmp) / "a repository with spaces"
            (target / "docs").mkdir(parents=True)
            (target / "README.md").write_text(
                "# Test project\n\nRead the [setup guide](docs/setup.md).\n",
                encoding="utf-8",
            )
            (target / "docs" / "guide.md").write_text(
                "# Setup guide\n", encoding="utf-8",
            )
            (target / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (target / "CONTRIBUTING.md").write_text(
                "# Contributing\n", encoding="utf-8",
            )
            self.check_checkout(target, expected_exit=1, missing=True)
            (target / "README.md").write_text(
                "# Test project\n\nRead the [setup guide](docs/guide.md).\n",
                encoding="utf-8",
            )
            self.check_checkout(target, expected_exit=0, missing=False)


if __name__ == "__main__":
    unittest.main()
