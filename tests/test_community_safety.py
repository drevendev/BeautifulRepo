"""Structural regressions for BR-COMMUNITY-006 community-safety surfaces."""
from pathlib import Path
import re
import unittest

# Reserved example.com addresses are test data, not a public reporting contact.
PRIVATE_REPORTING_ROUTE_RE = re.compile(
    r"(?i)mailto:|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}"
)

ROOT = Path(__file__).parents[1]
PUBLIC_WARNING = (
    "Do not post secrets, security-vulnerability details, exploit steps, "
    "or personal data in this public issue."
)


class CommunitySafetyTests(unittest.TestCase):
    def test_readme_links_the_community_safety_guide(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "[Community safety readiness](guides/community-safety.md)",
            readme,
        )
        self.assertTrue((ROOT / "guides/community-safety.md").is_file())

    def test_public_issue_forms_warn_against_sensitive_reports(self):
        for relative in (
            ".github/ISSUE_TEMPLATE/problem.yml",
            ".github/ISSUE_TEMPLATE/improvement.yml",
        ):
            with self.subTest(relative=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(PUBLIC_WARNING, text)
                # Warn before any user input; a warning in the second field is too late.
                first_block = text.split("\nbody:\n", 1)[1]
                self.assertTrue(
                    first_block.startswith(
                        "  - type: markdown\n"
                        "    attributes:\n"
                        "      value: >-\n"
                        f"        {PUBLIC_WARNING}\n"
                    ),
                    f"{relative}: safety notice must precede the first input",
                )

    def test_contributing_keeps_public_safety_boundary(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        self.assertIn(
            "Do not post secrets, private logs or personal contact information in issues.",
            normalized,
        )
        self.assertIn(
            "A dedicated conduct policy and confirmed confidential reporting route remain on the roadmap",
            normalized,
        )
        self.assertIn(
            "use GitHub's platform reporting facilities rather than disclosing private details in an issue.",
            normalized,
        )

    def test_security_policy_template_stays_an_explicit_scaffold(self):
        path = ROOT / "templates/SECURITY.template.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Drafting template — not a live reporting policy.", text)
        self.assertIn("REPLACE_WITH_A_VERIFIED_PRIVATE_REPORTING_ROUTE", text)
        self.assertIn("STATE_ONLY_BEHAVIOR_THE_PROJECT_CAN_RELIABLY_PROVIDE", text)
        self.assertIsNone(
            PRIVATE_REPORTING_ROUTE_RE.search(text),
            "template must not invent an email reporting route",
        )
        self.assertIn(
            "[BeautifulRepo's community safety guide](../guides/community-safety.md)",
            text,
        )
        self.assertTrue((path.parent / "../guides/community-safety.md").resolve().is_file())

    def test_reporting_route_matcher_detects_real_email_addresses(self):
        self.assertIsNotNone(PRIVATE_REPORTING_ROUTE_RE.search("security@example.com"))
        self.assertIsNotNone(PRIVATE_REPORTING_ROUTE_RE.search("mailto:security@example.com"))
        self.assertIsNone(PRIVATE_REPORTING_ROUTE_RE.search("Use GitHub private vulnerability reporting"))


if __name__ == "__main__":
    unittest.main()
