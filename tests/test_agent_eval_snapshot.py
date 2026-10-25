"""Black-box behavior for the no-model agent-eval target snapshot tool."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "agent_eval_snapshot.py"


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.target = self.home / "synthetic-target"
        self.target.mkdir()
        (self.target / "README.md").write_text("# Sample\n", encoding="utf-8")
        (self.target / "empty").mkdir()
        self.baseline = self.home / "before.json"

    def run_tool(self, verb, target=None, baseline=None):
        return subprocess.run([
            sys.executable, "-I", str(TOOL), verb,
            str(target or self.target), "--baseline", str(baseline or self.baseline),
        ], cwd=self.home, capture_output=True, text=True, encoding="utf-8", timeout=30,
            check=False)

    def test_unchanged_fixture_and_repeat_capture_rejected(self):
        initial = self.run_tool("capture")
        self.assertEqual(0, initial.returncode, initial.stderr)
        snapshot = json.loads(self.baseline.read_text(encoding="utf-8"))
        self.assertEqual(1, snapshot["format"])
        self.assertIn("README.md", snapshot["entries"])
        self.assertEqual("directory", snapshot["entries"]["empty"]["kind"])
        verified = self.run_tool("verify")
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertIn("UNCHANGED", verified.stdout)
        repeated = self.run_tool("capture")
        self.assertEqual(2, repeated.returncode)

    def test_modified_added_and_removed_entries_fail_with_specific_paths(self):
        self.assertEqual(0, self.run_tool("capture").returncode)
        (self.target / "README.md").write_text("# Modified\n", encoding="utf-8")
        (self.target / "injected.txt").write_text("agent wrote", encoding="utf-8")
        (self.target / "empty").rmdir()
        result = self.run_tool("verify")
        self.assertEqual(1, result.returncode)
        for detail in ("CHANGED: README.md", "ADDED: injected.txt", "REMOVED: empty"):
            self.assertIn(detail, result.stdout)

    def test_never_write_baseline_inside_target(self):
        unsafe = self.target / "baseline.json"
        result = self.run_tool("capture", baseline=unsafe)
        self.assertEqual(2, result.returncode)
        self.assertFalse(unsafe.exists())

    def test_mismatched_target_and_bad_baseline_rejected(self):
        self.assertEqual(0, self.run_tool("capture").returncode)
        other = self.home / "other"
        other.mkdir()
        self.assertEqual(2, self.run_tool("verify", target=other).returncode)
        self.baseline.write_text("broken", encoding="utf-8")
        self.assertEqual(2, self.run_tool("verify").returncode)

    def test_duplicate_members_or_boolean_version_fail_closed(self):
        self.assertEqual(0, self.run_tool("capture").returncode)
        original = self.baseline.read_text(encoding="utf-8")
        snapshot = json.loads(original)
        duplicate_file = json.dumps(snapshot["entries"]["README.md"], sort_keys=True)
        cases = [
            ("duplicate top-level", original.replace(
                '"format": 1,', '"format": 1, "format": 1,', 1), "duplicate JSON key"),
            ("duplicate entry", original.replace(
                '"README.md": {',
                '"README.md": ' + duplicate_file + ', "README.md": {', 1),
                "duplicate JSON key"),
            ("boolean version", original.replace(
                '"format": 1,', '"format": true,', 1), "baseline format"),
        ]
        for label, modified, expected_error in cases:
            with self.subTest(label=label):
                self.assertNotEqual(original, modified)
                self.baseline.write_text(modified, encoding="utf-8")
                outcome = self.run_tool("verify")
                self.assertEqual(2, outcome.returncode,
                                 outcome.stdout + outcome.stderr)
                self.assertIn(expected_error, outcome.stderr)
                self.assertNotIn("UNCHANGED", outcome.stdout)

    def test_symlink_target_is_not_followed(self):
        external = self.home / "outside.txt"
        external.write_text("secret before", encoding="utf-8")
        link = self.target / "external"
        try:
            link.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        self.assertEqual(0, self.run_tool("capture").returncode)
        data = json.loads(self.baseline.read_text(encoding="utf-8"))
        self.assertEqual("symlink", data["entries"]["external"]["kind"])
        external.write_text("secret after", encoding="utf-8")
        self.assertEqual(0, self.run_tool("verify").returncode,
                         "external content must not be read")
        link.unlink()
        link.symlink_to(self.home / "elsewhere.txt")
        self.assertEqual(1, self.run_tool("verify").returncode)


    def test_windows_junction_like_reparse_point_fails_before_traversal(self):
        """A directory reparse point must not escape the synthetic target."""
        import importlib.util
        import stat
        from types import SimpleNamespace
        from unittest import mock

        junction = self.target / "junction"
        junction.mkdir()
        (junction / "secret.txt").write_text("must not be opened", encoding="utf-8")
        spec = importlib.util.spec_from_file_location("agent_eval_snapshot_junction", TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original_lstat = Path.lstat
        original_open = Path.open

        def tagged_lstat(path):
            result = original_lstat(path)
            if path == junction:
                return SimpleNamespace(st_mode=result.st_mode,
                                       st_file_attributes=0x400)
            return result

        def forbid_child_reads(path, *args, **kwargs):
            if path.is_relative_to(junction):
                raise AssertionError("traversed a directory reparse point")
            return original_open(path, *args, **kwargs)

        # Portable simulation of FILE_ATTRIBUTE_REPARSE_POINT on Linux and
        # Windows, without needing administrator rights to create a junction.
        with mock.patch.object(module.stat, "FILE_ATTRIBUTE_REPARSE_POINT",
                               0x400, create=True):
            with mock.patch.object(Path, "lstat", tagged_lstat):
                with mock.patch.object(Path, "open", forbid_child_reads):
                    with self.assertRaisesRegex(ValueError,
                                                "unsupported reparse point: junction"):
                        module.inventory(self.target)


    def test_unreadable_directory_is_an_error_not_a_clean_snapshot(self):
        """An os.walk scandir error must never produce a false UNCHANGED."""
        import importlib.util
        from unittest import mock

        spec = importlib.util.spec_from_file_location("agent_eval_snapshot_test", TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def unreadable_walk(root, **kwargs):
            kwargs["onerror"](PermissionError("synthetic scandir failure"))
            yield (str(root), [], [])

        with mock.patch.object(module.os, "walk", side_effect=unreadable_walk):
            with self.assertRaisesRegex(PermissionError, "synthetic scandir"):
                module.inventory(self.target)


if __name__ == "__main__":
    unittest.main()
