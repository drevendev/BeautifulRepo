"""Verify that the AI-copy review's worked example is real, not marketing copy."""

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).parents[1]
GUIDE = ROOT / "guides" / "ai-readme-review.md"
COMMAND = "python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv"


class AiReadmeReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GUIDE.read_text(encoding="utf-8")

    def test_first_success_runs_against_real_csv(self):
        self.assertIn(f"```bash\n{COMMAND}\n```", self.guide)
        completed = subprocess.run(
            [
                sys.executable,
                "examples/cli-starter/rowcount.py",
                "examples/cli-starter/sample.csv",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "Data rows: 3\n")
        self.assertEqual(completed.stderr, "")
        self.assertIn("```text\nData rows: 3\n```", self.guide)

    def test_invented_claims_are_clearly_marked_as_negative_example(self):
        prose = " ".join(self.guide.split())
        for required in (
            "Candidate first screen — deliberately invented bad copy",
            "fabricated negative example, not a product description",
            "Replacement — quiet, command-first treatment",
            "**Unverified — withhold**",
            "not a published Python package",
            "not a judgment that the author's voice is",
            "Source check",
        ):
            with self.subTest(required=required):
                self.assertIn(required, prose)

    def test_receipt_separates_source_checks_from_manual_testing(self):
        for required in (
            "Claims: verified | illustrative | unverified | false",
            "Manual rendering: widths | light/dark | zoom | keyboard | screen reader:",
            "Checks actually run:",
            "Do not fill an unperformed check",
            "1db96d552d4e2ba6e9893cbd348d8f67eb3507fe",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.guide)


if __name__ == "__main__":
    unittest.main()
