"""Offline subprocess tests for fixture-read evidence; no model is invoked."""
from __future__ import annotations

import json
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
                     "content": self.fixture.read_text(encoding="utf-8")}, **changes)

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


if __name__ == "__main__":
    unittest.main()
