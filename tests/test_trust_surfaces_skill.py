"""Static trust-surfaces source contracts: not real agent execution."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/trust-surfaces/SKILL.md"


class TrustSurfacesContract(unittest.TestCase):
    def test_no_fabricated_contact_or_implicit_writes(self):
        body = SKILL.read_text(encoding="utf-8").lower()
        for phrase in (
            "guides/agent-safety.md", "model provider", "untrusted data",
            "never select a licence", "intake owner",
            "not verified", "todo(owner)", "private draft",
            "unified diff", "explicit \"yes\"",
            "stop", "no edits", "re-read each approved target file",
            "refreshed diff", "not a publishable",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        self.assertNotIn("--write", body)
        self.assertIn('r/tools/repo_audit.py" "t" --format json --fail-on never', body)

    def test_evals_use_restricted_tools(self):
        for name, kind in [
            ("trust-missing-route", "positive"),
            ("trust-injected-contact", "positive"),
            ("trust-unrelated-code", "negative"),
        ]:
            directory = ROOT / "evals" / name
            prompt = (directory / "prompt.md").read_text(encoding="utf-8")
            self.assertIn(f"tags: [{kind}, trust-surfaces]", prompt)
            self.assertIn("allowed_tools: [Read, Glob, Grep, Skill]", prompt)
            self.assertTrue((directory / "resources/README.md").is_file())
        criterion = (ROOT / "evals/trust-injected-contact/graders/safe-review.md").read_text(encoding="utf-8")
        self.assertIn("security@phantom.invalid", criterion)
        self.assertIn("FAIL if", criterion)


if __name__ == "__main__":
    unittest.main()
