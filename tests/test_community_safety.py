"""Structural checks for community-safety guidance and templates."""
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]


class CommunitySafetyTests(unittest.TestCase):
    def test_guide_keeps_reporting_lanes_distinct(self):
        text = (ROOT / "guides/community-safety.md").read_text(encoding="utf-8")
        for phrase in (
            "Ordinary bug or docs problem",
            "Security vulnerability",
            "Conduct complaint",
            "Private Vulnerability Reporting is a separate repository setting",
        ):
            self.assertIn(phrase, text)

    def test_security_template_cannot_masquerade_as_live_policy(self):
        template = ROOT / "templates/SECURITY.template.md"
        self.assertTrue(template.is_file())
        text = template.read_text(encoding="utf-8")
        self.assertIn("Template only", text)
        self.assertIn("{{VERIFIED_PRIVATE_REPORTING_ROUTE}}", text)
        self.assertFalse((ROOT / "SECURITY.md").exists())

    def test_conduct_material_is_adoption_checklist_not_policy(self):
        path = ROOT / "templates/CODE_OF_CONDUCT.adoption-checklist.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("intentionally not a code of conduct itself", text)
        self.assertIn("A private reporting route exists now", text)
        self.assertFalse((ROOT / "CODE_OF_CONDUCT.md").exists())

    def test_no_fake_live_contact_is_presented(self):
        joined = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in (
                "guides/community-safety.md",
                "templates/SECURITY.template.md",
                "templates/CODE_OF_CONDUCT.adoption-checklist.md",
            )
        )
        self.assertNotIn("@example.com", joined)
        self.assertIn("{{VERIFIED_PRIVATE_REPORTING_ROUTE}}", joined)


if __name__ == "__main__":
    unittest.main()
