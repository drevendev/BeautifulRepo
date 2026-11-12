"""Keep the immutable MCP host-trial commands consistent with their source link.

This is documentation consistency only, not SDK, filesystem, or model-host acceptance.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest


GUIDE = Path(__file__).resolve().parents[1] / "guides" / "local-mcp.md"


class MCPGuidePinTests(unittest.TestCase):
    def test_posix_and_windows_trials_use_the_same_immutable_commit(self):
        source = GUIDE.read_text(encoding="utf-8")
        match = re.search(
            r"\[BeautifulRepo `([0-9a-f]{40})`\]"
            r"\(https://github\.com/drevendev/BeautifulRepo/commit/([0-9a-f]{40})\)",
            source,
        )
        self.assertIsNotNone(match)
        pin, linked_sha = match.groups()
        self.assertEqual(pin, linked_sha)

        trial = source.split("### Reproduce an immutable development checkout (POSIX)", 1)[1]
        trial = trial.split("### Claude Code: local-scope stdio entry", 1)[0]
        # Both OS recipes and the clickable source must use one exact revision.
        observed = re.findall(r"\b[0-9a-f]{40}\b", trial)
        self.assertEqual([pin] * 5, observed)
        self.assertIn(f"git checkout --detach {pin}", trial)
        self.assertIn(f'test "$(git rev-parse HEAD)" = "{pin}" || exit 1', trial)
        self.assertIn(f"$pin = '{pin}'", trial)
        self.assertIn("git checkout --detach $pin", trial)

    def test_host_and_windows_reparse_coverage_is_not_overclaimed(self):
        source = GUIDE.read_text(encoding="utf-8")
        self.assertIn("The Windows reparse tests use **mocked filesystem metadata**", source)
        self.assertIn("no real NTFS", source)
        self.assertIn("no real NTFS\nreparse-point host test or Claude Code/Codex installation PASS", source)


if __name__ == "__main__":
    unittest.main()
