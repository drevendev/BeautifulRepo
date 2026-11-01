"""Black-box exact-consent-hash README application tests."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "readme_apply.py"


class ReadmeApplyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)
        self.root = self.tmp / "target repo"
        self.root.mkdir()
        self.readme = self.root / "README.md"
        self.readme.write_bytes(b"# Project\n\nBefore.\n")
        self.proposal = self.tmp / "candidate.md"
        self.proposal.write_bytes(b"# Project\n\nAfter.\n")
        self.other = self.root / "keep.txt"
        self.other.write_text("Do not touch", encoding="utf-8")

    @staticmethod
    def digest(content):
        return hashlib.sha256(content).hexdigest()

    def command(self, *extra, current=None, proposed=None):
        cmd = [sys.executable, "-I", str(TOOL), "--root", str(self.root),
               "--proposal", str(self.proposal)]
        if current is not None:
            cmd.extend(["--approved-current-sha256", current])
        if proposed is not None:
            cmd.extend(["--approved-proposed-sha256", proposed])
        cmd.extend(extra)
        return subprocess.run(cmd, cwd=self.tmp, capture_output=True,
                              text=True, encoding="utf-8", timeout=10)

    def approved(self, *extra):
        return self.command(*extra, current=self.digest(self.readme.read_bytes()),
                            proposed=self.digest(self.proposal.read_bytes()))

    def assert_clean(self):
        self.assertEqual("Do not touch", self.other.read_text(encoding="utf-8"))
        self.assertEqual([], list(self.root.glob(".beautifulrepo-readme-*")))

    def test_approval_hashes_are_required_and_missing_means_no_write(self):
        old = self.readme.read_bytes()
        result = self.command()
        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual(old, self.readme.read_bytes())
        self.assert_clean()

    def test_approved_hashes_apply_only_readme_and_preserve_candidate(self):
        before = self.readme.read_bytes()
        proposal = self.proposal.read_bytes()
        if os.name == "posix":
            self.readme.chmod(0o644)
        result = self.command(current=self.digest(before), proposed=self.digest(proposal))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Applied README.md", result.stdout)
        self.assertEqual(proposal, self.readme.read_bytes())
        self.assertEqual(proposal, self.proposal.read_bytes())
        if os.name == "posix":
            self.assertEqual(0o644, stat.S_IMODE(self.readme.stat().st_mode))
        self.assert_clean()

    def test_stale_original_rejected_with_no_write(self):
        old = self.readme.read_bytes()
        self.readme.write_text("# Edited by someone else\n", encoding="utf-8")
        result = self.command(current=self.digest(old), proposed=self.digest(self.proposal.read_bytes()))
        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("re-preview", result.stderr)
        self.assertEqual(b"# Edited by someone else\n", self.readme.read_bytes())
        self.assert_clean()

    def test_changed_candidate_rejected_with_no_write(self):
        old = self.readme.read_bytes()
        candidate = self.proposal.read_bytes()
        self.proposal.write_bytes(b"# Replaced candidate\n")
        result = self.command(current=self.digest(old), proposed=self.digest(candidate))
        self.assertEqual(2, result.returncode)
        self.assertEqual(old, self.readme.read_bytes())
        self.assertEqual("", result.stdout)
        self.assert_clean()

    def test_noop_when_approved_bytes_already_equal(self):
        self.proposal.write_bytes(self.readme.read_bytes())
        result = self.approved()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("No change", result.stdout)
        self.assert_clean()

    def test_rejects_candidate_inside_checkout(self):
        proposed = self.root / "candidate.md"
        proposed.write_bytes(self.proposal.read_bytes())
        self.proposal = proposed
        old = self.readme.read_bytes()
        result = self.approved()
        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("outside", result.stderr)
        self.assertEqual(old, self.readme.read_bytes())
        self.assert_clean()

    def test_rejects_invalid_utf8_and_controls(self):
        old = self.readme.read_bytes()
        for content in (b"\xff", b"# X\n\x1b[31m", "A\u2028B\n".encode("utf-8")):
            with self.subTest(content=content):
                self.proposal.write_bytes(content)
                result = self.approved()
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertEqual(old, self.readme.read_bytes())
                self.assert_clean()

    def test_symlinked_target_and_proposal_rejected_when_available(self):
        real = self.tmp / "real.md"
        real.write_bytes(self.readme.read_bytes())
        self.readme.unlink()
        try:
            self.readme.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        result = self.approved()
        self.assertEqual(2, result.returncode)
        self.assertEqual(real.read_bytes(), b"# Project\n\nBefore.\n")
        self.readme.unlink()
        self.readme.write_bytes(real.read_bytes())
        self.proposal.unlink()
        try:
            self.proposal.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("proposal symlinks unavailable")
        result = self.approved()
        self.assertEqual(2, result.returncode)
        self.assert_clean()

    def test_crlf_and_utf8_bom_proposal_bytes_preserved(self):
        proposed = b"\xef\xbb\xbf# Project\r\n\r\nAfter.\r\n"
        self.proposal.write_bytes(proposed)
        result = self.approved()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(proposed, self.readme.read_bytes())
        self.assert_clean()

    def test_does_not_execute_target_code(self):
        marker = self.tmp / "executed"
        script = self.root / "run-me.py"
        script.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('bad')\n",
                          encoding="utf-8")
        result = self.approved()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(marker.exists())
        self.assert_clean()


if __name__ == "__main__":
    unittest.main()
