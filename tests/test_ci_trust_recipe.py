"""Check the copyable fork-PR documentation workflow contract.

Static regression coverage, not a hosted-runner security assessment.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = (ROOT / "guides/adopting-the-checks.md").read_text(encoding="utf-8")
QUALITY = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class CiTrustRecipeTests(unittest.TestCase):
    def test_copyable_recipe_is_unprivileged_and_sha_pinned(self):
        section = GUIDE.split("## Add it to a workflow\n", 1)[1].split(
            "\n## ", 1
        )[0]
        workflow = section.split("```yaml\n", 1)[1].split("\n```", 1)[0]
        self.assertIn("on:\n  pull_request:\n", workflow)
        self.assertIn("permissions:\n  contents: read\n", workflow)
        self.assertIn("persist-credentials: false", workflow)
        for denied in ("pull_request_target:", "workflow_run:", "secrets.", "run:"):
            self.assertNotIn(denied, workflow)
        actions = re.findall(r"^\s*- uses: (\S+)", workflow, flags=re.MULTILINE)
        self.assertEqual(3, len(actions))
        for action in actions:
            with self.subTest(action=action):
                self.assertRegex(
                    action,
                    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$",
                )

    def test_actual_quality_workflow_keeps_same_basic_boundary(self):
        self.assertIn("  pull_request:\n", QUALITY)
        self.assertIn("permissions:\n  contents: read\n", QUALITY)
        self.assertIn("persist-credentials: false", QUALITY)
        self.assertNotIn("pull_request_target:", QUALITY)

    def test_reader_caveats_name_real_sources_and_unknowns(self):
        section = GUIDE.split("## Check the fork-PR trust boundary\n", 1)[1].split(
            "\n## ", 1
        )[0]
        for phrase in (
            "security sandbox", "pull_request_target", "workflow_run",
            "disposable PR", "Self-hosted runners",
            "Primary sources checked 2026-11-10",
            "docs.github.com/en/actions/reference/security/secure-use",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, section)


if __name__ == "__main__":
    unittest.main()
