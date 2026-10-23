"""README, CONTRIBUTING, the maintenance guide and CI name one and the same check list."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    "python tools/catalog.py",
    "python tools/docs_links.py",
    "python tools/html_navigation.py",
    "python -m unittest discover -s tests -v",
    "python tools/repo_audit.py .",
)


class CheckListConsistencyTests(unittest.TestCase):
    def test_documents_list_every_check_in_one_order(self):
        block = "\n".join(CHECKS) + "\n```"
        for page in ("README.md", "CONTRIBUTING.md", "guides/maintenance-workflow.md", "AGENTS.md"):
            with self.subTest(page=page):
                self.assertIn(block, (ROOT / page).read_text(encoding="utf-8"))

    def test_ci_runs_every_documented_check(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        for command in CHECKS:
            with self.subTest(command=command):
                self.assertIn(f"run: {command}\n", workflow)

    def test_agents_read_agents_md_without_a_root_claude_md(self):
        # A CLAUDE.md at the plugin root fails `claude plugin validate --strict`.
        self.assertFalse((ROOT / "CLAUDE.md").exists())
        self.assertEqual("@../AGENTS.md\n",
                         (ROOT / ".claude/CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("[AGENTS.md](AGENTS.md)", (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8"))

    def test_pr_template_points_to_the_five_checks(self):
        template = (ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
        self.assertIn("five local checks from CONTRIBUTING", template)
