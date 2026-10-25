"""Source-level safety and coverage contracts for improve-readme.

These tests do not run any model, check real onboarding, or prove write gating.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/improve-readme/SKILL.md"
EVALS = ROOT / "evals"


class ImproveReadmeSkillTests(unittest.TestCase):
    def test_approval_gate_is_explicit_and_target_runs_are_separate(self):
        body = SKILL.read_text(encoding="utf-8")
        for token in (
            "guides/agent-safety.md",
            "model\n  provider",
            "checklists/first-success.md",
            "unified diff",
            "exact target-relative files",
            "explicit \"yes\"",
            "Stop with no edits",
            "Re-read each approved target file",
            "stop and show a refreshed diff",
            "separate, explicit permission",
            "Not run / not verified",
        ):
            with self.subTest(token=token):
                self.assertIn(token.lower(), body.lower())
        self.assertNotIn(" --write", body)
        self.assertIn('R/tools/repo_audit.py" "T" --format json --fail-on never', body)
        self.assertIn('R/tools/docs_links.py" --root "T"', body)
        self.assertIn('R/tools/html_navigation.py" --root "T"', body)

    def test_badge_gate_requires_both_backing_and_confirmation(self):
        body = SKILL.read_text(encoding="utf-8")
        self.assertIn("backing workflow/target URL", body)
        self.assertIn("user's confirmation", body)
        self.assertIn("omit the badge", body)
        self.assertIn("untrusted data", body)
        self.assertIn("README.md", body)

    def test_cases_are_structural_not_model_results(self):
        for case, kind in (
            ("readme-improvement-plan", "positive"),
            ("readme-unsupported-badge", "positive"),
            ("readme-unrelated-code", "negative"),
        ):
            root = EVALS / case
            with self.subTest(case=case):
                prompt = (root / "prompt.md").read_text(encoding="utf-8")
                self.assertIn("improve-readme", prompt)
                self.assertIn(kind, prompt)
                self.assertIn("allowed_tools: [Read, Glob, Grep, Skill]", prompt)
                self.assertIn('add_dirs: [resources]', (root / "case.yaml").read_text(encoding="utf-8"))
                self.assertTrue((root / "resources/README.md").is_file())
                names = sorted(p.name for p in (root / "graders").glob("*.md"))
                self.assertTrue(names)
                self.assertNotIn("Write", re.search(r"allowed_tools: \[(.*?)\]", prompt).group(1))
                self.assertNotIn("Edit", re.search(r"allowed_tools: \[(.*?)\]", prompt).group(1))
        self.assertIn("type: llm", (EVALS / "readme-unsupported-badge/graders/safe-plan.md").read_text(encoding="utf-8"))
        self.assertIn("FAIL if", (EVALS / "readme-unsupported-badge/graders/safe-plan.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
