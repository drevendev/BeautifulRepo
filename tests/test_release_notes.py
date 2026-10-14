"""Structural checks for the reader-facing release notes starter."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "guides" / "release-notes.md"
TEMPLATE = ROOT / "templates" / "RELEASE_NOTES.template.md"


class ReleaseNotesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GUIDE.read_text(encoding="utf-8")
        cls.template = TEMPLATE.read_text(encoding="utf-8")

    def test_guide_distinguishes_three_artifacts(self):
        for phrase in ("**Git tag**", "**GitHub Release**", "**CHANGELOG**"):
            self.assertIn(phrase, self.guide)
        self.assertIn("tag date and the release publication date can differ", self.guide)

    def test_reader_impact_and_unpublished_example_are_explicit(self):
        for phrase in (
            "Upgrade action", "Known limitation", "illustrative only",
            "not a real release", "actual test results",
        ):
            self.assertIn(phrase, self.guide)

    def test_generated_notes_are_not_claimed_as_acceptance(self):
        self.assertIn(".github/release.yml", self.guide)
        self.assertIn("review the generated list", self.guide)
        self.assertIn("No release, tag, artifact", self.guide)

    def test_guide_links_template_and_dated_sources(self):
        self.assertIn("../templates/RELEASE_NOTES.template.md", self.guide)
        self.assertTrue(TEMPLATE.is_file())
        self.assertIn("2026-10-09", self.guide)
        self.assertIn("https://keepachangelog.com/en/2.0.0/", self.guide)

    def test_template_keeps_evidence_placeholders(self):
        for token in (
            "{{VERSION}}",
            "{{UPGRADE_ACTION_OR_EXPLICIT_NO_ACTION_REQUIRED}}",
            "{{TAG}}",
            "{{COMMIT_SHA}}",
            "{{RELEASE_PUBLICATION_DATE_OR_NOT_YET_PUBLISHED}}",
            "{{VERIFICATION_FACTS}}",
            "{{COMPARE_URL}}",
        ):
            self.assertIn(token, self.template)
        self.assertIn("Draft template", self.template)
        self.assertIn("Tag / target commit:", self.template)
        self.assertIn("Release publication date:", self.template)

    def test_template_does_not_invent_verification(self):
        lower = self.template.lower()
        self.assertNotIn("all tests passed", lower)
        self.assertNotIn("100% compatible", lower)

    def test_reader_navigation_contains_release_note_routes(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(guides/release-notes.md)", readme)
        self.assertIn("(templates/RELEASE_NOTES.template.md)", readme)



if __name__ == "__main__":
    unittest.main()
