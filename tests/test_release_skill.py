"""Source-level contracts for the unpublished, evidence-led release draft skill.

No model is invoked; these tests cannot prove runtime triggering or accuracy.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "draft-release-notes" / "SKILL.md"
EVALS = ROOT / "evals"


class ReleaseSkillTests(unittest.TestCase):
    def test_safe_draft_protocol_is_explicit(self):
        text = SKILL.read_text(encoding="utf-8")
        for required in (
            "guides/agent-safety.md",
            'R/scripts/release_inventory.py" "T"',
            "Unreleased draft",
            "base_commit",
            "head_commit",
            "exact commit SHA",
            "not verified",
            "model provider",
            "shallow history",
        ):
            with self.subTest(required=required):
                self.assertIn(required.lower(), text.lower())
        self.assertNotIn("--write", text)
        self.assertIn("await explicit", text)

    def test_synthetic_no_tag_eval_is_not_a_fake_release(self):
        root = EVALS / "release-no-tag"
        record = json.loads((root / "resources" / "inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "unreleased_draft_only")
        self.assertEqual(record["base_kind"], "root")
        self.assertIsNone(record["base_tag"])
        self.assertEqual(record["commit_count"], len(record["commits"]))
        self.assertEqual(len(record["base_commit"]), 40)
        prompt = (root / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("Unreleased draft", prompt)
        self.assertIn("not a Git checkout", prompt)
        self.assertIn("diffs were not checked", prompt)

    def test_tagged_eval_does_not_assert_publication(self):
        root = EVALS / "release-tagged-history"
        record = json.loads((root / "resources" / "inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "unreleased_draft_only")
        self.assertEqual(record["base_kind"], "tag")
        self.assertEqual(record["base_tag"], "v0.1.0")
        self.assertEqual(record["commits"][0]["sha"], record["head_commit"])
        self.assertIn("not proof the release exists",
                      (root / "prompt.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
