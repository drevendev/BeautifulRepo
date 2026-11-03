"""Guard the portable, intentionally non-live repository status template."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates/REPOSITORY_STATUS_NOTICE.template.md"
GUIDE = ROOT / "guides/repository-retirement.md"


class RetirementNoticeTests(unittest.TestCase):
    def test_template_does_not_embed_location_dependent_links(self):
        # These instructions are often copied into an unrelated root README.
        # A link valid below BeautifulRepo/templates/ may be broken there.
        text = TEMPLATE.read_text(encoding="utf-8")
        destinations = re.findall(r"\]\(([^)]+)\)", text)
        self.assertTrue(destinations, "Keep a useful source reference")
        for destination in destinations:
            with self.subTest(destination=destination):
                self.assertTrue(
                    destination.startswith(("https://", "http://", "#")),
                    f"Template link depends on source directory: {destination}",
                )

    def test_both_states_have_separate_copyable_notices(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for heading in ("## PAUSED", "## PRE-ARCHIVE"):
            with self.subTest(heading=heading):
                self.assertIn(heading, text)
        paused = text.split("## PAUSED", 1)[1].split("## PRE-ARCHIVE", 1)[0]
        pre_archive = text.split("## PRE-ARCHIVE", 1)[1].split(
            "After GitHub archival", 1
        )[0]
        for notice in (paused, pre_archive):
            quoted = [line for line in notice.splitlines() if line.startswith(">")]
            self.assertGreater(len(quoted), 3)
            self.assertIn("Last documented revision:", "\n".join(quoted))
            self.assertIn("Last verified first success:", "\n".join(quoted))
        self.assertIn("has **not** been archived on GitHub", paused)
        self.assertIn("being", pre_archive)
        self.assertIn("prepared for GitHub archival", pre_archive)

    def test_copy_instructions_cover_destination_and_permissions(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertIn("only the blockquoted notice", template)
        self.assertIn("destination README", template)
        self.assertIn("Copy **only one blockquoted notice**", guide)
        self.assertIn("relative Markdown links", guide)
        self.assertIn("cannot be edited without unarchiving", guide)


if __name__ == "__main__":
    unittest.main()
