"""Fact-preserving variants of the same fictional README first screen."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "examples" / "readme-visuals" / "variants"
VARIANTS = ("editorial.md", "documentation-led.md", "playful-technical.md")
COMMAND = "pocketdiff january.csv february.csv --output changes.csv"


class VisualVariantsTests(unittest.TestCase):
    def test_all_variants_keep_identical_example_facts_and_disclose_fiction(self):
        for filename in VARIANTS:
            with self.subTest(filename=filename):
                text = (DIR / filename).read_text(encoding="utf-8")
                normalized = text.lower().replace("**", "")
                for fact in (COMMAND, "18 changed", "2 added", "1 removed",
                             "changes.csv", "no upload", "same key column"):
                    self.assertIn(fact, normalized)
                self.assertIn("fictional", normalized)
                self.assertIn("illustrative", normalized)
                self.assertIn("[compare the other first screens](readme.md)", normalized)
                self.assertNotIn("https://", text, "no offsite assets in specimens")

    def test_comparison_page_links_every_variant_and_states_limits(self):
        content = (DIR / "README.md").read_text(encoding="utf-8")
        for filename in VARIANTS:
            self.assertIn(f"]({filename})", content)
        self.assertIn("no implementation", content.lower())
        self.assertIn("not", content.lower())


if __name__ == "__main__":
    unittest.main()
