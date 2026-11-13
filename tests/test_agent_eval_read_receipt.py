"""Offline subprocess tests for fixture-read evidence; no model is invoked."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "agent_eval_read_receipt.py"


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.home = Path(td.name)
        self.fixture = self.home / "fixture.md"
        self.fixture.write_text("# Synthetic\nToken: verified-example\n", encoding="utf-8")
        self.path = "/sandbox/synthetic/README.md"
        self.receipt = self.home / "read-receipt.json"

    def run_checker(self, obj=None, raw=None):
        if raw is None:
            raw = json.dumps(obj, ensure_ascii=False)
        self.receipt.write_text(raw, encoding="utf-8")
        return subprocess.run([
            sys.executable, "-I", str(TOOL),
            "--fixture", str(self.fixture),
            "--observed-path", self.path,
            "--receipt", str(self.receipt),
        ], cwd=self.home, capture_output=True, text=True, timeout=30, check=False)

    def item(self, **changes):
        return dict({"kind": "tool_result", "tool": "Read", "path": self.path,
                     "content": self.fixture.read_bytes().decode("utf-8")}, **changes)

    def test_exact_read_result_is_a_match_not_model_pass(self):
        result = self.run_checker({"format": 1, "reads": [self.item()]})
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("CONTENT_MATCH", result.stdout)
        self.assertIn("SHA-256", result.stdout)
        self.assertNotIn("PASS", result.stdout)

    def test_path_only_request_and_final_answer_do_not_count(self):
        for read in (
            {"kind": "tool_call", "tool": "Read", "path": self.path},
            {"kind": "assistant", "content": self.fixture.read_text(encoding="utf-8")},
            {"kind": "tool_result", "tool": "Glob", "path": self.path,
             "content": self.fixture.read_text(encoding="utf-8")},
        ):
            with self.subTest(read=read["kind"]):
                result = self.run_checker({"format": 1, "reads": [read]})
                self.assertEqual(1, result.returncode)
                self.assertIn("INCONCLUSIVE", result.stdout)

    def test_wrong_path_missing_content_or_truncation_is_inconclusive(self):
        cases = [
            [{"kind": "tool_result", "tool": "Read", "path": "/other/README.md",
              "content": self.fixture.read_text(encoding="utf-8")}],
            [{"kind": "tool_result", "tool": "Read", "path": self.path}],
            [self.item(content="# Synthetic\n")],
            [self.item(), self.item(content="stale")],
        ]
        for reads in cases:
            with self.subTest(reads=reads):
                result = self.run_checker({"format": 1, "reads": reads})
                self.assertEqual(1, result.returncode)
                self.assertIn("INCONCLUSIVE", result.stdout)

    def test_malformed_duplicate_key_boolean_version_and_huge_array(self):
        cases = [
            '{"format":1,"format":1,"reads":[]}',
            '{"format":true,"reads":[]}',
            '{"format":1,"reads":[null]}',
            json.dumps({"format": 1, "reads": [{}] * 10001}),
            "invalid",
        ]
        for raw in cases:
            with self.subTest(raw=raw[:40]):
                result = self.run_checker(raw=raw)
                self.assertEqual(2, result.returncode)
                self.assertIn("ERROR:", result.stderr)

    def test_crlf_fixture_must_not_match_lf_normalized_tool_output(self):
        self.fixture.write_bytes(b"first\r\nsecond\r\n")
        result = self.run_checker({"format": 1, "reads": [self.item(content="first\nsecond\n")]})
        self.assertEqual(1, result.returncode)
        self.assertIn("INCONCLUSIVE", result.stdout)

    def test_hard_linked_fixture_fails_before_reading(self):
        external = self.home / "external-fixture.md"
        try:
            os.link(self.fixture, external)
        except (OSError, NotImplementedError):
            self.skipTest("hard links unavailable")
        self.assertFalse(self.fixture.is_symlink())
        self.assertGreater(self.fixture.stat().st_nlink, 1)
        result = self.run_checker({"format": 1, "reads": [self.item()]})
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("fixture must not be a hard-linked file", result.stderr)
        self.assertNotIn("CONTENT_MATCH", result.stdout)

    def test_hard_linked_receipt_fails_before_parsing(self):
        self.assertEqual(0, self.run_checker(
            {"format": 1, "reads": [self.item()]}).returncode)
        external = self.home / "external-receipt.json"
        try:
            os.link(self.receipt, external)
        except (OSError, NotImplementedError):
            self.skipTest("hard links unavailable")
        self.assertFalse(self.receipt.is_symlink())
        self.assertGreater(self.receipt.stat().st_nlink, 1)
        # Invoke the existing receipt directly; do not rewrite its hard link.
        result = subprocess.run([
            sys.executable, "-I", str(TOOL),
            "--fixture", str(self.fixture),
            "--observed-path", self.path,
            "--receipt", str(self.receipt),
        ], cwd=self.home, capture_output=True, text=True, timeout=30,
            check=False)
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("receipt must not be a hard-linked file", result.stderr)
        self.assertNotIn("CONTENT_MATCH", result.stdout)

    def test_symlink_fixture_fails_closed(self):
        link = self.home / "link.md"
        try:
            link.symlink_to(self.fixture)
        except (NotImplementedError, OSError):
            self.skipTest("symlinks unavailable")
        result = self.run_checker({"format": 1, "reads": [self.item()]})
        self.assertEqual(0, result.returncode)
        self.fixture = link
        result = self.run_checker({"format": 1, "reads": [self.item()]})
        self.assertEqual(2, result.returncode)
        self.assertIn("non-symlink", result.stderr)


    def test_fixture_under_symlinked_parent_is_rejected(self):
        parent = self.home / "trusted-fixture"
        parent.mkdir()
        (parent / "README.md").write_text("# Synthetic\\n", encoding="utf-8")
        alias = self.home / "redirected-fixture"
        try:
            alias.symlink_to(parent, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        self.fixture = alias / "README.md"
        result = self.run_checker({"format": 1, "reads": [
            {"kind": "tool_result", "tool": "Read", "path": self.path,
             "content": "# Synthetic\\n"}
        ]})
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("fixture parent must not be a symlink", result.stderr)
        self.assertNotIn("CONTENT_MATCH", result.stdout)

    def test_receipt_under_symlinked_parent_is_rejected(self):
        # The fixture itself is ordinary; the JSON evidence path is redirected.
        real = self.home / "evidence"
        real.mkdir()
        alias = self.home / "redirected-evidence"
        try:
            alias.symlink_to(real, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        self.receipt = alias / "receipt.json"
        result = self.run_checker({"format": 1, "reads": [self.item()]})
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("receipt parent must not be a symlink", result.stderr)

    def test_simulated_windows_reparse_file_and_parent_fail_before_read(self):
        import importlib.util
        from types import SimpleNamespace
        from unittest import mock

        parent = self.home / "normal-parent"
        parent.mkdir()
        file = parent / "fixture.md"
        file.write_text("# Synthetic\\n", encoding="utf-8")
        spec = importlib.util.spec_from_file_location("agent_eval_receipt_guard", TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original_lstat = Path.lstat

        for redirected, label, expected in (
            (parent, "fixture", "fixture parent must not be a Windows reparse point"),
            (file, "fixture", "fixture must not be a Windows reparse point"),
        ):
            with self.subTest(redirected=str(redirected)):
                def tagged_lstat(path, redirected=redirected):
                    info = original_lstat(path)
                    if path == redirected:
                        return SimpleNamespace(st_mode=info.st_mode,
                                               st_file_attributes=0x400)
                    return info

                with mock.patch.object(module.stat, "FILE_ATTRIBUTE_REPARSE_POINT",
                                       0x400, create=True):
                    with mock.patch.object(Path, "lstat", tagged_lstat):
                        with mock.patch.object(
                            Path, "read_bytes",
                            side_effect=AssertionError("redirected file was read")
                        ):
                            with self.assertRaisesRegex(ValueError, expected):
                                module._text_file(file, label)

    def test_unredirected_lexical_dotdot_parent_remains_usable(self):
        ordinary = self.home / "ordinary"
        ordinary.mkdir()
        self.fixture = ordinary / ".." / "fixture.md"
        result = self.run_checker({"format": 1, "reads": [self.item()]})
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
