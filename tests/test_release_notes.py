"""Structural checks for the release-notes guide and reusable template."""
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]


class ReleaseNotesTests(unittest.TestCase):
    def test_guide_distinguishes_tag_release_and_changelog(self):
        text = (ROOT / "guides/release-notes.md").read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in (
            "A **Git tag** marks a point in repository history.",
            "A **GitHub Release** is publication metadata",
            "A **CHANGELOG** is durable project history",
            "Generated notes are an inventory, not the final explanation",
        ):
            self.assertIn(phrase, normalized)

    def test_generated_notes_are_not_presented_as_acceptance(self):
        text = (ROOT / "guides/release-notes.md").read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        self.assertIn(".github/release.yml", text)
        self.assertIn("review the generated list", normalized.lower())
        self.assertIn(
            "creating a tag is not evidence that the release itself was reviewed",
            normalized,
        )

    def test_template_requires_evidence_and_upgrade_guidance(self):
        text = (ROOT / "templates/RELEASE_NOTES.template.md").read_text(encoding="utf-8")
        for token in (
            "{{VERSION}}",
            "{{UPGRADE_ACTION_OR_EXPLICIT_NO_ACTION_REQUIRED}}",
            "{{TAG}}",
            "{{COMMIT_SHA}}",
            "{{RELEASE_PUBLICATION_DATE_OR_NOT_YET_PUBLISHED}}",
            "{{VERIFICATION_FACTS}}",
            "{{COMPARE_URL}}",
        ):
            self.assertIn(token, text)
        self.assertIn("Draft template", text)

    def test_template_keeps_tag_and_publication_date_separate(self):
        guide = (ROOT / "guides/release-notes.md").read_text(encoding="utf-8")
        template = (ROOT / "templates/RELEASE_NOTES.template.md").read_text(encoding="utf-8")
        normalized = " ".join(guide.split())
        self.assertIn("tag date and a release publication date can differ", normalized)
        self.assertIn("Tag / target commit:", template)
        self.assertIn("Release publication date:", template)

    def test_template_does_not_claim_observed_results(self):
        text = (ROOT / "templates/RELEASE_NOTES.template.md").read_text(encoding="utf-8")
        self.assertNotIn("all tests passed", text.lower())
        self.assertNotIn("100% compatible", text.lower())


if __name__ == "__main__":
    unittest.main()
