"""Ensure the visual-design brief stays reusable and its filled case stays factual."""

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "DESIGN_INTENT.template.md"
CASE = ROOT / "examples" / "readme-visuals" / "rowcount"
EXAMPLE = CASE / "DESIGN_INTENT.md"
CLI = ROOT / "examples" / "cli-starter"
REVISION = "1db96d552d4e2ba6e9893cbd348d8f67eb3507fe"


class DesignIntentBriefTests(unittest.TestCase):
    def test_reusable_template_covers_evidence_and_review(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for heading in (
            "## Scope and reader",
            "## Evidence boundary",
            "## First-screen alternatives",
            "## Visual and interaction decisions",
            "## Rejected approaches",
            "## Verification and decision",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
        for marker in ("{exact commit or file", "illustrative",
                       'alt=""', "NOT CHECKED", "screen reader",
                       "two materially different"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertIn("www.w3.org/WAI/tutorials/images/", text)

    def test_filled_case_is_revision_bound_and_discloses_limits(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        for detail in (
            REVISION, "Data rows: 3", "Python 3.11+",
            "editorial.md", "terminal-led.md",
            "not screenshots", "not a released Python package",
            "not tested", "400% zoom", "screen reader",
            "no new", "illustrative",
        ):
            with self.subTest(detail=detail):
                self.assertIn(detail.casefold(), text.casefold())
        self.assertNotIn("{repository or document surface}", text)
        for page in ("editorial.md", "terminal-led.md"):
            source = (CASE / page).read_text(encoding="utf-8")
            self.assertIn("Data rows: 3", source)

    def test_brief_output_agrees_with_real_command(self):
        result = subprocess.run(
            [sys.executable, str(CLI / "rowcount.py"), str(CLI / "sample.csv")],
            cwd=ROOT, capture_output=True, text=True, check=False, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Data rows: 3\n")
        self.assertEqual(result.stderr, "")
        self.assertIn(result.stdout.strip(), EXAMPLE.read_text(encoding="utf-8"))

    def test_all_reader_paths_link_the_template_and_case(self):
        index = (ROOT / "templates" / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "guides" / "readme-visuals.md").read_text(encoding="utf-8")
        compare = (CASE / "README.md").read_text(encoding="utf-8")
        self.assertIn("(DESIGN_INTENT.template.md)", index)
        self.assertIn("(../examples/readme-visuals/rowcount/DESIGN_INTENT.md)", index)
        self.assertIn("(../templates/DESIGN_INTENT.template.md)", guide)
        self.assertIn("(../examples/readme-visuals/rowcount/DESIGN_INTENT.md)", guide)
        self.assertIn("(DESIGN_INTENT.md)", compare)
        self.assertIn("(../../../templates/DESIGN_INTENT.template.md)", compare)
        self.assertTrue(TEMPLATE.is_file())
        self.assertTrue(EXAMPLE.is_file())


if __name__ == "__main__":
    unittest.main()
