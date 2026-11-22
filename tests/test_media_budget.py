"""Synthetic, offline regression cases for advisory media file-size budgets."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from media_budget import inspect  # noqa: E402


class MediaBudgetTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)

    def put(self, name: str, size: int) -> None:
        file = self.root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(b"x" * size)

    def check(self, *args: str):
        return subprocess.run([sys.executable, "-I", str(ROOT / "tools/media_budget.py"),
                               "--root", str(self.root), "--format", "json", *args],
                              capture_output=True, text=True, check=False)

    def test_empty_repository_is_a_real_zero_result(self):
        result = inspect(self.root, 1024, 2048)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["files"], 0)
        self.assertEqual(result["largest"], [])

    def test_nested_images_are_counted_by_size_without_decoding(self):
        self.put("assets/icon.PNG", 8)
        self.put("doc/pic.svg", 15)
        self.put("doc/source.txt", 999)
        result = inspect(self.root, 20, 40)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["total_bytes"], 23)
        self.assertEqual(result["largest"][0], {"path": "doc/pic.svg", "bytes": 15})
        self.assertEqual(result["files"], 2)

    def test_single_and_total_budget_report_distinct_findings(self):
        self.put("a.png", 1200)
        self.put("b.avif", 1000)
        run = self.check("--max-file-kib", "1", "--max-total-kib", "2")
        self.assertEqual(run.returncode, 1, run.stderr)
        data = json.loads(run.stdout)
        self.assertEqual(data["status"], "findings")
        self.assertEqual([(v["rule"], v["path"]) for v in data["findings"]],
                         [("file_budget", "a.png"), ("total_budget", "")])

    def test_exact_threshold_passes(self):
        self.put("icon.webp", 1024)
        self.assertEqual(self.check("--max-file-kib", "1", "--max-total-kib", "1").returncode, 0)

    def test_ignore_dependency_directories_but_not_normal_assets(self):
        self.put("node_modules/huge.png", 3000)
        self.put(".git/objects/image.jpg", 3000)
        self.put("assets/good.jpeg", 10)
        result = inspect(self.root, 15, 15)
        self.assertEqual(result["files"], 1)
        self.assertEqual(result["status"], "ok")


    def test_ignored_dependency_directory_redirect_does_not_fail_inventory(self):
        self.put("assets/kept.png", 20)
        with tempfile.TemporaryDirectory() as elsewhere:
            outside = Path(elsewhere)
            (outside / "external.png").write_bytes(b"x" * 4096)
            for name in ("node_modules", ".venv"):
                try:
                    (self.root / name).symlink_to(outside, target_is_directory=True)
                except (OSError, NotImplementedError):
                    self.skipTest("directory symlinks unavailable")
            result = inspect(self.root, 64, 64)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["files"], 1)
            self.assertEqual(result["total_bytes"], 20)
            self.assertEqual(result["errors"], [])

    def test_ignored_broken_directory_redirect_does_not_fail_inventory(self):
        try:
            (self.root / "node_modules").symlink_to(
                self.root / "missing-target", target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        result = inspect(self.root, 64, 64)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["files"], 0)

    def test_symlinks_are_incomplete_and_not_followed(self):
        self.put("a.png", 100)
        try:
            (self.root / "b.png").symlink_to(self.root / "a.png")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        data = json.loads(self.check().stdout)
        self.assertEqual(data["status"], "incomplete")
        self.assertEqual(data["files"], 1)
        self.assertTrue(any("Skipped redirect" in err for err in data["errors"]))
        self.assertEqual(self.check().returncode, 2)

    def test_directory_symlink_is_incomplete_and_does_not_escape(self):
        other = self.root / "assets"
        other.mkdir()
        self.put("assets/screenshot.png", 100)
        try:
            (self.root / "alias").symlink_to(other, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        data = json.loads(self.check().stdout)
        self.assertEqual(data["files"], 1)
        self.assertEqual(data["status"], "incomplete")

    def test_invalid_budgets_are_rejected(self):
        for value in ("0", "-1", "abc", "1000001"):
            with self.subTest(value=value):
                run = self.check("--max-file-kib", value)
                self.assertEqual(run.returncode, 2)
                self.assertIn("budget must", run.stderr)

    def test_missing_root_is_not_success(self):
        self.root = self.root / "does-not-exist"
        data = json.loads(self.check().stdout)
        self.assertEqual(data["status"], "incomplete")
        self.assertEqual(self.check().returncode, 2)

    def test_order_is_deterministic_for_equal_sizes(self):
        self.put("b.gif", 40)
        self.put("a.gif", 40)
        data = json.loads(self.check().stdout)
        self.assertEqual([v["path"] for v in data["largest"]], ["a.gif", "b.gif"])

    def test_filename_with_unicode_survives_json(self):
        self.put("écran.png", 22)
        data = json.loads(self.check().stdout)
        self.assertEqual(data["largest"][0]["path"], "écran.png")

    def test_hardlinked_external_image_is_incomplete_and_not_counted(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            source = Path(elsewhere) / "external.png"
            source.write_bytes(b"x" * 2048)
            try:
                (self.root / "poster.png").hardlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("hard links unavailable")
            run = self.check()
            self.assertEqual(run.returncode, 2, run.stderr)
            data = json.loads(run.stdout)
            self.assertEqual(data["status"], "incomplete")
            self.assertEqual(data["files"], 0)
            self.assertEqual(data["total_bytes"], 0)
            self.assertTrue(any("Skipped hard-linked media entry: poster.png" in
                                error for error in data["errors"]))
            self.assertEqual(source.read_bytes(), b"x" * 2048)

    def test_hardlinked_image_inside_root_is_also_incomplete(self):
        self.put("original.png", 32)
        try:
            (self.root / "alias.png").hardlink_to(self.root / "original.png")
        except (OSError, NotImplementedError):
            self.skipTest("hard links unavailable")
        data = inspect(self.root, 1024, 1024)
        self.assertEqual(data["status"], "incomplete")
        self.assertEqual(data["files"], 0)
        self.assertEqual(len([error for error in data["errors"]
                              if "hard-linked media entry" in error]), 2)

    def test_hardlinked_non_image_does_not_block_media_inventory(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            source = Path(elsewhere) / "outside.txt"
            source.write_text("not a media asset", encoding="utf-8")
            try:
                (self.root / "readme.txt").hardlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("hard links unavailable")
            data = inspect(self.root, 1024, 1024)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["files"], 0)

    def test_symlink_in_root_parent_is_incomplete_without_external_inventory(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            external = Path(elsewhere) / "repo"
            external.mkdir()
            (external / "outside.png").write_bytes(b"x" * 4096)
            alias = self.root / "redirected_parent"
            try:
                alias.symlink_to(Path(elsewhere), target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("directory symlinks unavailable")
            indirect_root = alias / "repo"
            self.assertFalse(indirect_root.is_symlink())
            data = inspect(indirect_root, 1024, 1024)
            self.assertEqual(data["status"], "incomplete")
            self.assertEqual(data["files"], 0)
            self.assertEqual(data["total_bytes"], 0)
            run = subprocess.run(
                [sys.executable, "-I", str(ROOT / "tools/media_budget.py"),
                 "--root", str(indirect_root), "--format", "json"],
                capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 2, run.stderr)
            self.assertEqual(json.loads(run.stdout)["files"], 0)
            self.assertEqual((external / "outside.png").read_bytes(), b"x" * 4096)

    def test_root_symlink_is_not_followed(self):
        try:
            alias = self.root / "alias"
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.assertEqual(inspect(alias, 1024, 1024)["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
