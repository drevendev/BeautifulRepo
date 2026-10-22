"""Regression checks for the distinction between local tools and agent sessions."""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AgentPrivacyContract(unittest.TestCase):
    def test_local_tools_and_model_session_are_distinct(self):
        safety = (ROOT / "guides/agent-safety.md").read_text(encoding="utf-8")
        guide = (ROOT / "guides/agent-plugin.md").read_text(encoding="utf-8")
        self.assertIn("model provider", safety)
        self.assertIn("model provider", guide)
        self.assertNotIn("nothing leaves the machine", safety)

    def test_portable_description_discloses_model_processing(self):
        portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        details = portable["extensions"]["com.openai"]["interface"]["longDescription"]
        self.assertIn("model provider", details)
        self.assertNotIn("nothing is written or sent anywhere", details)

    def test_metadata_preserves_name_and_version(self):
        portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["name"], claude["name"])
        self.assertEqual(portable["version"], claude["version"])


if __name__ == "__main__":
    unittest.main()
