"""Structural contract for the GitHub Action other repositories pin."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ActionContractTests(unittest.TestCase):
    def setUp(self):
        self.action = (ROOT / "action.yml").read_text(encoding="utf-8")

    def test_action_runs_bundled_tools_with_the_callers_python(self):
        self.assertIn("using: composite", self.action)
        for tool in ("repo_audit.py", "docs_links.py", "html_navigation.py"):
            with self.subTest(tool=tool):
                self.assertIn(f'"$GITHUB_ACTION_PATH/tools/{tool}"', self.action)
        self.assertNotIn("uses:", self.action)  # no nested actions such as setup-python
        self.assertIn("sys.version_info < (3, 11)", self.action)

    def test_inputs_reach_scripts_through_environment_only(self):
        self.assertEqual(re.findall(r"^ +run: (?!\|$).*", self.action, re.MULTILINE), [])
        for block in re.findall(r"run: \|\n((?:        .*\n|\n)+)", self.action):
            with self.subTest(block=block.splitlines()[0]):
                self.assertNotIn("${{", block)

    def test_documented_inputs_match_the_action(self):
        guide = (ROOT / "guides/adopting-the-checks.md").read_text(encoding="utf-8")
        declared = re.findall(r"^  ([a-z-]+):\n    description:", self.action, re.MULTILINE)
        self.assertEqual(declared, ["path", "checks", "audit-fail-on", "exclude"])
        for name in declared:
            with self.subTest(input=name):
                self.assertIn(f"| `{name}` |", guide)
        self.assertIn("audit|docs-links|html-navigation) ;;", self.action)
        for check in ("audit", "docs-links", "html-navigation"):
            with self.subTest(check=check):
                self.assertIn(f"' {check} ')", self.action)
                self.assertIn(f"| `{check}` |", guide)

    def test_guide_pins_a_commit_and_is_linked(self):
        guide = (ROOT / "guides/adopting-the-checks.md").read_text(encoding="utf-8")
        self.assertRegex(guide, r"uses: drevendev/BeautifulRepo@[0-9a-f]{40} # v\d+\.\d+\.\d+\n")
        for page in ("README.md", "tools/README.md"):
            with self.subTest(page=page):
                text = (ROOT / page).read_text(encoding="utf-8")
                self.assertIn("guides/adopting-the-checks.md", text)

    def test_ci_self_test_exercises_failure_cases(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("uses: ./", workflow)
        self.assertIn('test "$BROKEN" = failure', workflow)
        self.assertIn('test "$TYPO" = failure', workflow)


if __name__ == "__main__":
    unittest.main()
