"""Test installed release-note helper on real, disposable local Git fixtures."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts/verify_copied_release.py"


@unittest.skipUnless(shutil.which("git"), "git not installed")
class CopiedReleaseTests(unittest.TestCase):
    def test_copied_release_inventory_has_expected_boundary_and_no_target_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "draft-release-notes"
            shutil.copytree(ROOT / "skills/draft-release-notes", skill)
            process = subprocess.run(
                [sys.executable, "-I", str(TOOL), "--skill-root", str(skill)],
                capture_output=True, text=True,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn('"target_files_and_refs_unchanged": true', process.stdout)

    def test_missing_helper_is_a_failure_not_an_inconclusive_success(self):
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run(
                [sys.executable, "-I", str(TOOL), "--skill-root", directory],
                capture_output=True, text=True,
            )
            self.assertEqual(process.returncode, 1)
            self.assertIn("missing", process.stderr)
