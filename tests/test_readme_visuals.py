"""Structural checks for the visual README example."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/readme-visuals/README.md"
ASSETS = [
    ROOT / "examples/readme-visuals/hero-light.svg",
    ROOT / "examples/readme-visuals/hero-dark.svg",
]


class ReadmeVisualExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = EXAMPLE.read_text(encoding="utf-8")

    def test_theme_aware_picture_has_default_and_alt_text(self):
        self.assertIn('media="(prefers-color-scheme: dark)" srcset="./hero-dark.svg"', self.text)
        self.assertIn('media="(prefers-color-scheme: light)" srcset="./hero-light.svg"', self.text)
        match = re.search(r'<img alt="([^"]+)"\s+src="\./hero-light\.svg">', self.text)
        self.assertIsNotNone(match)
        self.assertGreater(len(match.group(1).split()), 8)

    def test_text_equivalent_preserves_visual_facts(self):
        for fact in ("18 changed", "2 added", "1 removed", "changes.csv"):
            self.assertIn(fact, self.text)

    def test_assets_are_local_and_present(self):
        for name in ("./hero-dark.svg", "./hero-light.svg"):
            self.assertIn(name, self.text)
        for path in ASSETS:
            self.assertTrue(path.is_file(), path)

    def test_svg_assets_have_title_description_and_viewbox(self):
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for path in ASSETS:
            root = ET.parse(path).getroot()
            self.assertEqual(root.attrib.get("viewBox"), "0 0 960 360")
            self.assertEqual(root.attrib.get("role"), "img")
            title = root.find("svg:title", ns)
            desc = root.find("svg:desc", ns)
            self.assertIsNotNone(title)
            self.assertIsNotNone(desc)
            self.assertTrue((title.text or "").strip())
            self.assertIn("18 changed rows", (desc.text or ""))

    def test_status_not_conveyed_by_color_only(self):
        for path in ASSETS:
            text = path.read_text(encoding="utf-8")
            for label in ("CHANGED", "ADDED", "REMOVED", "18 rows", "2 rows", "1 row"):
                self.assertIn(label, text)


if __name__ == "__main__":
    unittest.main()
