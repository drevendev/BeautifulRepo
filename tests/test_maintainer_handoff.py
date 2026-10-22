"""Structural contracts for the public maintainer handoff guide."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HandoffGuideTests(unittest.TestCase):
    def test_public_handoff_has_reproducible_first_steps(self):
        guide = (ROOT / "guides/maintainer-handoff.md").read_text(encoding="utf-8")
        for command in (
            "python -m unittest discover -s tests -v",
            "python tools/catalog.py",
            "python tools/docs_links.py",
            "python tools/html_navigation.py",
        ):
            with self.subTest(command=command):
                self.assertIn(command, guide)
        self.assertIn("Python 3.11", guide)
        self.assertIn("loopback HTTP listener", guide)

    def test_handoff_distinguishes_decisions_and_sensitive_information(self):
        guide = (ROOT / "guides/maintainer-handoff.md").read_text(encoding="utf-8")
        for required in (
            "**Before — insufficient:**", "**After — fictional public notice:**",
            "Contributor", "write access", "Owner/admin", "**Private:**",
            "**Public:**", "Release publishing is paused", "2026-10-21",
        ):
            with self.subTest(required=required):
                self.assertIn(required, guide)
        self.assertIn("not permission to transfer", guide)

    def test_reader_can_find_handoff_from_readme(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(guides/maintainer-handoff.md)", readme)


if __name__ == "__main__":
    unittest.main()
