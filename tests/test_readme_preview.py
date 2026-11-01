"""Read-only README proposal preview and stale-content guard regressions."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "readme_preview.py"


class ReadmePreviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)
        self.repo = self.tmp / "target repo"
        self.repo.mkdir()
        self.readme = self.repo / "README.md"
        self.proposal = self.tmp / "candidate.md"
        self.readme.write_text("# Example\n\nBefore.\n", encoding="utf-8")
        self.proposal.write_text("# Example\n\nAfter.\n", encoding="utf-8")

    def command(self, *extra):
        return subprocess.run(
            [sys.executable, "-I", str(TOOL), "--root", str(self.repo),
             "--proposal", str(self.proposal), *extra],
            cwd=self.tmp, capture_output=True, text=True, encoding="utf-8", timeout=10,
        )

    def test_diff_hashes_no_target_writes_and_foreign_cwd(self):
        old = self.readme.read_bytes()
        new = self.proposal.read_bytes()
        result = self.command("--expected-sha256", hashlib.sha256(old).hexdigest())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--- a/README.md", result.stdout)
        self.assertIn("+++ b/README.md", result.stdout)
        self.assertIn("-Before.", result.stdout)
        self.assertIn("+After.", result.stdout)
        self.assertIn(hashlib.sha256(old).hexdigest(), result.stdout)
        self.assertIn(hashlib.sha256(new).hexdigest(), result.stdout)
        self.assertNotIn(str(self.tmp), result.stdout)
        self.assertEqual(old, self.readme.read_bytes())
        self.assertEqual(new, self.proposal.read_bytes())

    def test_same_bytes_has_no_diff(self):
        self.proposal.write_bytes(self.readme.read_bytes())
        result = self.command()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("No differences.", result.stdout)
        self.assertNotIn("--- a/README.md", result.stdout)

    def test_stale_hash_fails_closed_without_diff(self):
        result = self.command("--expected-sha256", "0" * 64)
        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("changed since", result.stderr)

    def test_bad_hash_is_usage_error(self):
        result = self.command("--expected-sha256", "not-a-hash")
        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)

    def test_invalid_utf8_and_terminal_control_are_rejected(self):
        for content in (b"\xff", b"# X\n\x1b[31mRed\n", b"# X\x00"):
            with self.subTest(content=content):
                self.proposal.write_bytes(content)
                result = self.command()
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)

    def test_bounded_and_missing_input(self):
        self.proposal.write_bytes(b"a" * (256 * 1024 + 1))
        result = self.command()
        self.assertEqual(2, result.returncode)
        self.assertIn("256 KiB", result.stderr)
        self.proposal.unlink()
        self.assertEqual(2, self.command().returncode)

    def test_symlinked_root_readme_and_proposal_are_rejected(self):
        target = self.tmp / "real.md"
        target.write_text("# Real\n", encoding="utf-8")
        self.proposal.unlink()
        try:
            self.proposal.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.assertEqual(2, self.command().returncode)
        self.proposal.unlink()
        self.proposal.write_text("# Proposed\n", encoding="utf-8")
        self.readme.unlink()
        try:
            self.readme.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("README symlinks unavailable")
        self.assertEqual(2, self.command().returncode)
        self.readme.unlink()
        self.readme.write_text("# Original\n", encoding="utf-8")
        linked = self.tmp / "linked"
        try:
            linked.symlink_to(self.repo, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        self.repo = linked
        self.assertEqual(2, self.command().returncode)

    def test_missing_final_newline_and_line_endings_reported(self):
        self.readme.write_bytes(b"# X\r\nBefore")
        self.proposal.write_bytes(b"# X\nAfter\n")
        result = self.command()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("current=CRLF proposed=LF", result.stdout)
        self.assertIn("No newline at end of file", result.stdout)
        self.assertIn("+After", result.stdout)

    def test_bare_carriage_return_is_rejected_in_both_inputs(self):
        for path in (self.readme, self.proposal):
            with self.subTest(path=path.name):
                before = path.read_bytes()
                path.write_bytes(b"# Example\rHide earlier output\n")
                result = self.command()
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertIn("bare carriage return", result.stderr)
                path.write_bytes(before)

    def test_unicode_c1_and_bidi_controls_are_rejected_in_both_inputs(self):
        for ch in ("\u009b", "\u0085", "\u061c", "\u200e", "\u200f", "\u202a", "\u202e", "\u202c", "\u2066", "\u2069"):
            for path in (self.readme, self.proposal):
                with self.subTest(codepoint=hex(ord(ch)), path=path.name):
                    before = path.read_bytes()
                    path.write_text("# Example\n" + ch + "Hidden claim\n", encoding="utf-8")
                    result = self.command()
                    self.assertEqual(2, result.returncode)
                    self.assertEqual("", result.stdout)
                    self.assertIn("display control", result.stderr)
                    path.write_bytes(before)

    def test_unicode_line_separators_cannot_forge_diff_lines(self):
        # splitlines(keepends=True) treats these as newlines even without LF.
        for separator in ("\u2028", "\u2029"):
            for path in (self.readme, self.proposal):
                with self.subTest(codepoint=hex(ord(separator)), path=path.name):
                    original = path.read_bytes()
                    path.write_text("A" + separator + "B\n", encoding="utf-8")
                    result = self.command()
                    self.assertEqual(2, result.returncode)
                    self.assertEqual("", result.stdout)
                    self.assertIn("display control", result.stderr)
                    self.assertNotIn("@@ -1,2 +1,2 @@", result.stdout)
                    self.assertNotIn("No newline at end of file", result.stdout)
                    path.write_bytes(original)

        # A physical LF line really is one diff line, with no invented marker.
        self.readme.write_text("A Пример\n", encoding="utf-8")
        self.proposal.write_text("A Другое\n", encoding="utf-8")
        result = self.command()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("@@ -1 +1 @@", result.stdout)
        self.assertNotIn("No newline at end of file", result.stdout)

    def test_utf8_output_when_parent_requests_legacy_encoding(self):
        self.proposal.write_text("# Пример\n\nשלום  مرحبا\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-I", str(TOOL), "--root", str(self.repo),
             "--proposal", str(self.proposal)],
            cwd=self.tmp, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "cp1252"}, timeout=10,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Пример", result.stdout)
        self.assertIn("مرحبا", result.stdout)

    def test_regular_non_ascii_text_is_allowed(self):
        self.proposal.write_text("# Пример\n\nשלום  مرحبا\n", encoding="utf-8")
        result = self.command()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Пример", result.stdout)


if __name__ == "__main__":
    unittest.main()
