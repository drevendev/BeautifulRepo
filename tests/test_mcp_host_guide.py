"""Keep the experimental MCP host-trial checkout examples pinned together.

This checks a documentation contract only. It does not install a model host,
run an MCP client or certify SDK/host compatibility.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest


GUIDE = Path(__file__).resolve().parents[1] / "guides" / "local-mcp.md"


class McpHostGuidePinTests(unittest.TestCase):
    def test_posix_windows_and_commit_link_use_one_immutable_revision(self):
        text = GUIDE.read_text(encoding="utf-8")
        match = re.search(
            r"\[BeautifulRepo `([0-9a-f]{40})`\]"
            r"\(https://github\.com/drevendev/BeautifulRepo/commit/\1\)",
            text,
        )
        self.assertIsNotNone(match, "guide must link the full pinned commit")
        pin = match.group(1)

        self.assertIn(f"git checkout --detach {pin}", text)
        self.assertIn(
            f'test "$(git rev-parse HEAD)" = "{pin}" || exit 1', text
        )
        self.assertIn(f"$pin = '{pin}'", text)
        self.assertIn("git checkout --detach $pin", text)
        self.assertIn("$actual -ne $pin", text)
        self.assertEqual(
            text.count(pin), 5,
            "all explicit POSIX and PowerShell pin references must agree",
        )

    def test_host_outcomes_remain_explicitly_unverified(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("has not passed a fresh\nClaude Code/Codex host installation", text)
        self.assertIn("not a released MCP version", text)
        self.assertIn("SDK smoke", text)


if __name__ == "__main__":
    unittest.main()
