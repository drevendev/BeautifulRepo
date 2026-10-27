"""Behavior and evidence checks for the release-note layout comparison."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "release-presentation" / "README.md"
CHECKER = ROOT / "tools" / "docs_links.py"


class ReleasePresentationTests(unittest.TestCase):
    def test_two_distinct_layouts_keep_the_same_real_evidence(self):
        text = CASE.read_text(encoding="utf-8")
        for marker in (
            "## Facts held constant",
            "## Treatment A — changelog entry",
            "## Treatment B — reader-facing release-note **draft**",
            "## Choose a presentation deliberately",
            "## Turn this into real release notes",
            "https://github.com/drevendev/BeautifulRepo/pull/179",
            "https://github.com/drevendev/BeautifulRepo/actions/runs/40550896841",
            "9468525f5c38c245bd6ccdcc9476dcdc467933e9",
            "Multiline",
            "Python 3.11+",
            "No release, tag, download",
            "Publication: not performed.",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        guide = (ROOT / "guides" / "release-notes.md").read_text(encoding="utf-8")
        visuals = (ROOT / "guides" / "readme-visuals.md").read_text(encoding="utf-8")
        self.assertIn("examples/release-presentation/README.md", guide)
        self.assertIn("examples/release-presentation/README.md", visuals)

    def test_documented_missing_reference_is_reported_at_use(self):
        # This deliberately reproduces the narrow real behavior used as evidence
        # by both editorial specimens, not a claimed model/browser interaction.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            readme = root / "README.md"
            readme.write_text("[Guide][docs]\n\n[docs]: absent.md\n",
                              encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-I", str(CHECKER), "--root", str(root)],
                capture_output=True, text=True, check=False, timeout=15,
            )
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("README.md:1: missing relative destination: 'absent.md'",
                          result.stderr)
            (root / "absent.md").write_text("# Guide\n", encoding="utf-8")
            fixed = subprocess.run(
                [sys.executable, "-I", str(CHECKER), "--root", str(root)],
                capture_output=True, text=True, check=False, timeout=15,
            )
            self.assertEqual(0, fixed.returncode, fixed.stderr)
            self.assertIn("checked 1 relative Markdown destination(s)", fixed.stdout)


if __name__ == "__main__":
    unittest.main()
