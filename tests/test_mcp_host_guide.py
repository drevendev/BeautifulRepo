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

        # Inspect copyable install commands, not unrelated explanatory prose.
        # Additional mentions of the pin must not break this contract test.
        posix = re.search(
            r"### Reproduce an immutable development checkout \(POSIX\)"
            r".*?```sh\n(.*?)\n```",
            text, re.S,
        )
        windows = re.search(
            r"### Windows PowerShell: immutable source and SDK preflight"
            r".*?```powershell\n(.*?)\n```",
            text, re.S,
        )
        self.assertIsNotNone(posix, "POSIX installation block is missing")
        self.assertIsNotNone(windows, "PowerShell installation block is missing")
        posix_commands = posix.group(1)
        windows_commands = windows.group(1)
        self.assertIn(f"git checkout --detach {pin}", posix_commands)
        self.assertIn(
            f'test "$(git rev-parse HEAD)" = "{pin}" || exit 1',
            posix_commands,
        )
        self.assertIn(f"$pin = '{pin}'", windows_commands)
        self.assertIn("git checkout --detach $pin", windows_commands)
        self.assertIn("$actual -ne $pin", windows_commands)
        # Enforce the same exact immutable SHA in every command occurrence.
        full_sha = r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])"
        self.assertEqual(re.findall(full_sha, posix_commands), [pin, pin])
        self.assertEqual(re.findall(full_sha, windows_commands), [pin])

    def test_claude_local_registration_starts_in_the_target_directory(self):
        source = GUIDE.read_text(encoding="utf-8")
        section = source.split("### Claude Code: local-scope stdio entry", 1)[1]
        section = section.split("### Codex CLI:", 1)[0]
        posix = section.split("```sh\n", 1)[1].split("\n```", 1)[0]
        windows = section.split("```powershell\n", 1)[1].split("\n```", 1)[0]
        self.assertTrue(posix.startswith('cd "$BR_ROOT" || exit 1\n'))
        self.assertIn('--root "$BR_ROOT" || exit 1', posix)
        self.assertIn("claude mcp list || exit 1", posix)
        self.assertIn("claude mcp get beautifulrepo-audit || exit 1", posix)
        self.assertLess(
            windows.index("Set-Location -LiteralPath $brRoot -ErrorAction Stop"),
            windows.index("claude mcp add --scope local"),
        )
        self.assertEqual(windows.count("if ($LASTEXITCODE -ne 0)"), 4)
        self.assertIn("--root $brRoot", windows)
        self.assertIn("from that same\ndirectory", section)
        self.assertIn("from the same\nproject directory", section)
        self.assertIn("claude mcp remove beautifulrepo-audit --scope local", section)

    def test_host_outcomes_remain_explicitly_unverified(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("has not passed a fresh\nClaude Code/Codex host installation", text)
        self.assertIn("not a released MCP version", text)
        self.assertIn("SDK smoke", text)


if __name__ == "__main__":
    unittest.main()
