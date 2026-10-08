"""Structural checks for the BeautifulRepo public front page."""
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
README = ROOT / "README.md"


class FrontPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")

    def test_front_page_has_identity_proof_and_navigation(self):
        self.assertIn("<h1>✨ BeautifulRepo</h1>", self.text)
        self.assertIn("actions/workflows/quality.yml/badge.svg", self.text)
        self.assertIn("license-MIT", self.text)
        self.assertIn("python-3.11%2B", self.text)
        for link in (
            "checklists/repository.md",
            "guides/readme.md",
            "guides/readme-visuals.md",
            "templates/README.template.md",
            "CONTRIBUTING.md",
        ):
            self.assertIn(link, self.text)

    def test_visitor_journey_is_explicit_and_ordered(self):
        positions = [
            self.text.index("1 · Promise"),
            self.text.index("2 · Evidence"),
            self.text.index("3 · First success"),
            self.text.index("4 · Trust"),
            self.text.index("5 · Contribute"),
        ]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("flowchart LR", self.text)

    def test_self_check_commands_remain_visible(self):
        for command in (
            "python tools/catalog.py",
            "python tools/docs_links.py",
            "python -m unittest discover -s tests -v",
        ):
            self.assertIn(command, self.text)

    def test_front_page_keeps_reader_safety_and_accessibility_paths(self):
        self.assertIn(
            "[Community safety readiness](guides/community-safety.md)",
            self.text,
        )
        self.assertIn("accessibility", self.text.lower())
        self.assertIn(
            "examples/readme-visuals/README.md",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
