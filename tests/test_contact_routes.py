"""The issue chooser routes questions, vulnerabilities and abuse to channels that exist."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContactRouteTests(unittest.TestCase):
    def test_chooser_offers_only_real_routes(self):
        config = (ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
        self.assertIn("blank_issues_enabled: false", config)
        for url in ("https://github.com/drevendev/BeautifulRepo/discussions",
                    "https://github.com/drevendev/BeautifulRepo/security/advisories/new",
                    "https://docs.github.com/en/communities/maintaining-your-safety-on-github/reporting-abuse-or-spam"):
            self.assertIn(f"url: {url}\n", config)
        self.assertNotIn("@", config.replace("@drevendev", ""), "no email contact")

    def test_forms_label_new_issues(self):
        for form, label in (("problem.yml", "bug"), ("improvement.yml", "enhancement")):
            text = (ROOT / ".github/ISSUE_TEMPLATE" / form).read_text(encoding="utf-8")
            self.assertIn(f'labels: ["{label}"]\n', text)

    def test_contributing_explains_questions_and_labels(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("## Ask a question", text)
        self.assertIn("## Find work by label", text)
        self.assertIn("`good first issue`", text)


if __name__ == "__main__":
    unittest.main()
