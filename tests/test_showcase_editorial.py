"""Tests for public design and editorial examples without claiming voice scores."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EditorialShowcaseTests(unittest.TestCase):
    def test_design_intent_describes_existing_assets_and_limits(self):
        text = (ROOT / "examples/readme-visuals/DESIGN_INTENT.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "fictional", "hero-light.svg", "hero-dark.svg", "changes.csv",
            "18 changed", "2 added", "1 removed", "alt text",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)
        self.assertIn("not a shipped CLI", text)

    def test_visual_example_links_brief(self):
        example = (ROOT / "examples/readme-visuals/README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("(DESIGN_INTENT.md)", example)

    def test_editorial_examples_have_three_paired_fact_sets(self):
        text = (ROOT / "guides/editorial-evidence.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(text.count("**Before — generic:**"), 3)
        self.assertEqual(text.count("**After — specific:**"), 3)
        self.assertIn("verified", text)
        self.assertIn("expected", text)
        self.assertIn("unknown", text)
        self.assertIn("Data rows: 3", text)
        self.assertIn("Python 3.11", text)
        self.assertIn("three *different*", text)


if __name__ == "__main__":
    unittest.main()

