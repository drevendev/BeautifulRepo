"""Synthetic boundary and CLI regressions for read-only repository reference inventory."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import repo_references  # noqa: E402
from repo_references import inspect  # noqa: E402


class RepoReferencesTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def put(self, path: str, content: bytes) -> Path:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def cli(self, *args: str):
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools/repo_references.py"),
             "--root", str(self.root), "--old", "orchard-labs/maple-lint",
             "--format", "json", *args], capture_output=True, text=True, check=False)

    def test_finds_links_uses_and_case_variants_without_leaking_line_contents(self):
        self.put("README.md", b"secret=42 https://github.com/orchard-labs/maple-lint\n")
        self.put(".github/workflows/build.yml", b"uses: ORCHARD-LABS/MAPLE-LINT@v1\n")
        run = self.cli()
        self.assertEqual(run.returncode, 1, run.stderr)
        value = json.loads(run.stdout)
        self.assertEqual(value["status"], "findings")
        self.assertEqual(value["findings"], [
            {"path": ".github/workflows/build.yml", "line": 1, "column": 7},
            {"path": "README.md", "line": 1, "column": 30},
        ])
        self.assertNotIn("secret", run.stdout)
        self.assertEqual(value["files_scanned"], 2)

    def test_clean_tree_is_ok_but_not_a_consumer_check(self):
        self.put("README.md", b"nothing to see\n")
        self.assertEqual(json.loads(self.cli().stdout)["status"], "ok")
        self.assertEqual(self.cli().returncode, 0)

    def test_skips_nontext_and_dependency_trees(self):
        self.put("archive.zip", b"orchard-labs/maple-lint")
        self.put("node_modules/index.md", b"orchard-labs/maple-lint")
        self.put("scripts/tool.py", b"print(1)\n")
        report = inspect(self.root, "orchard-labs/maple-lint")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["files_scanned"], 1)

    def test_malformed_utf8_makes_scan_incomplete(self):
        self.put("docs/legacy.md", b"\xff")
        report = inspect(self.root, "orchard-labs/maple-lint")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["errors"])
        self.assertEqual(self.cli().returncode, 2)

    def test_oversize_file_is_not_treated_as_negative(self):
        self.put("docs/big.md", b"x" * (1_048_576 + 1))
        self.assertEqual(inspect(self.root, "orchard-labs/maple-lint")["status"], "incomplete")

    def test_symlink_file_is_not_followed(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            source = Path(elsewhere) / "outside.md"
            source.write_bytes(b"orchard-labs/maple-lint")
            try:
                (self.root / "alias.md").symlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            report = inspect(self.root, "orchard-labs/maple-lint")
            self.assertEqual(report["status"], "incomplete")
            self.assertEqual(report["findings"], [])

    def test_symlink_in_root_ancestor_is_rejected(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            target = Path(elsewhere) / "repo"
            target.mkdir()
            (target / "README.md").write_text("orchard-labs/maple-lint", encoding="utf-8")
            alias = self.root / "redirect"
            try:
                alias.symlink_to(Path(elsewhere), target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            report = inspect(alias / "repo", "orchard-labs/maple-lint")
            self.assertEqual(report["status"], "incomplete")
            self.assertEqual(report["findings"], [])

    def test_hardlink_is_not_read(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            target = Path(elsewhere) / "source.md"
            target.write_text("orchard-labs/maple-lint", encoding="utf-8")
            try:
                (self.root / "shared.md").hardlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("hard links unavailable")
            report = inspect(self.root, "orchard-labs/maple-lint")
            self.assertEqual(report["status"], "incomplete")
            self.assertEqual(report["findings"], [])

    def test_validation_errors_return_two_without_traceback(self):
        for input_value in ("https://github.com/org/repo", "../../repo", "org/", "org/repo/x"):
            with self.subTest(value=input_value):
                run = subprocess.run([sys.executable, "-I", str(ROOT / "tools/repo_references.py"),
                                      "--old", input_value], capture_output=True, text=True, check=False)
                self.assertEqual(run.returncode, 2)
                self.assertNotIn("Traceback", run.stderr)

    def test_directory_entry_limit_is_bounded_during_enumeration(self):
        for index in range(7):
            self.put(f"{index:02}.md", b"org/repo")

        real_scandir = repo_references.os.scandir
        entries_yielded = 0

        class CountingScan:
            def __init__(self, directory):
                self.iterator = real_scandir(directory)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                self.iterator.close()

            def __iter__(self):
                nonlocal entries_yielded
                for entry in self.iterator:
                    entries_yielded += 1
                    if entries_yielded > 4:
                        raise AssertionError("enumerated beyond budget + overflow sentinel")
                    yield entry

        with patch.object(repo_references, "MAX_ENTRIES", 3), \
                patch.object(repo_references.os, "scandir", CountingScan):
            report = inspect(self.root, "org/repo")
        self.assertEqual(entries_yielded, 4)
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(any("directory entries" in error for error in report["errors"]))

    def test_match_limit_never_reports_complete(self):
        self.put("README.md", b"org/repo " * 2000)
        result = inspect(self.root, "org/repo")
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(len(result["findings"]), 2000)
        self.assertTrue(any("match limit" in err for err in result["errors"]))

    def test_root_missing_is_incomplete(self):
        self.assertEqual(inspect(self.root / "missing", "org/repo")["status"], "incomplete")

    def test_multiline_and_repeated_hits(self):
        self.put("Makefile", b"A=org/repo\nB=org/repo org/repo\n")
        hits = inspect(self.root, "org/repo")["findings"]
        self.assertEqual([(item["line"], item["column"]) for item in hits],
                         [(1, 3), (2, 3), (2, 12)])


if __name__ == "__main__":
    unittest.main()
