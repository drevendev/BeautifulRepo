"""Contract for the tag-driven release draft workflow."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        cls.quality = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")

    def test_runs_only_for_version_tags_and_writes_only_contents(self):
        self.assertIn("on:\n  push:\n    tags: ['v*']\n", self.workflow)
        self.assertIn("permissions:\n  contents: write\n", self.workflow)
        self.assertNotIn("pull_request", self.workflow)

    def test_creates_a_draft_and_never_overwrites_a_release(self):
        self.assertIn("gh release create \"$TAG\" --draft --verify-tag", self.workflow)
        self.assertNotIn("gh release edit", self.workflow)
        self.assertIn('if gh release view "$TAG"', self.workflow)

    def test_refuses_tags_off_master_or_with_failed_required_checks(self):
        self.assertIn('git merge-base --is-ancestor "$sha" origin/master', self.workflow)
        self.assertIn("rules/branches/master", self.workflow)  # the ruleset is the one list
        self.assertIn('"$conclusion" = success', self.workflow)

    def test_fills_only_verifiable_placeholders(self):
        template = (ROOT / "templates/RELEASE_NOTES.template.md").read_text(encoding="utf-8")
        filled = set(re.findall(r'"(\{\{[A-Z_]+\}\})":', self.workflow))
        self.assertEqual(filled, {"{{VERSION}}", "{{TAG}}", "{{COMMIT_SHA}}",
                                  "{{PREVIOUS_TAG_OR_BASE}}", "{{VERIFICATION_FACTS}}",
                                  "{{RELEASE_PUBLICATION_DATE_OR_NOT_YET_PUBLISHED}}",
                                  "{{COMPARE_URL}}", "{{CHANGELOG_URL}}"})
        for placeholder in filled:
            with self.subTest(placeholder=placeholder):
                self.assertIn(placeholder, template)
        self.assertIn("{{ONE_PARAGRAPH_USER_OUTCOME}}", template)  # prose stays human

    def test_inputs_reach_scripts_through_environment_only(self):
        for block in re.findall(r"run: \|\n((?:          .*\n|\n)+)", self.workflow):
            with self.subTest(block=block.splitlines()[0]):
                self.assertNotIn("${{", block)

    def test_checkout_is_pinned_like_ci(self):
        pin = re.search(r"uses: actions/checkout@([0-9a-f]{40})", self.quality).group(1)
        self.assertIn(f"uses: actions/checkout@{pin}", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)


if __name__ == "__main__":
    unittest.main()
