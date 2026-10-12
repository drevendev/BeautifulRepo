"""Regression: decorative feature cards need list semantics, not layout tables."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


class FeatureOverviewAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = README.read_text(encoding="utf-8")
        cls.section = text.split("## What you get\n", 1)[1].split(
            "\n## See the difference", 1
        )[0]

    def test_six_features_are_semantic_list_items(self):
        labels = (
            "📋 Checklists", "🧱 Patterns", "🧰 Templates",
            "🔎 Tools", "🖼️ Visual guidance", "🧭 Community guidance",
        )
        items = [line for line in self.section.splitlines()
                 if line.startswith("- ")]
        self.assertEqual(len(items), len(labels))
        for label, item in zip(labels, items):
            with self.subTest(label=label):
                self.assertTrue(item.startswith(f"- **{label}** — "), item)
                self.assertGreater(len(item), len(label) + 8)

    def test_feature_overview_is_not_a_presentation_table(self):
        self.assertFalse(any(line.lstrip().startswith("|")
                             for line in self.section.splitlines()))


if __name__ == "__main__":
    unittest.main()
