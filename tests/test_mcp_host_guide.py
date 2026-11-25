"""Keep the experimental MCP host-trial checkout examples pinned together.

This checks a documentation contract only. It does not install a model host,
run an MCP client or certify SDK/host compatibility.
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
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

    def test_codex_registration_stops_on_each_command_failure(self):
        source = GUIDE.read_text(encoding="utf-8")
        section = source.split("### Codex CLI: stdio entry", 1)[1]
        section = section.split("### Report a real host result", 1)[0]
        posix = section.split("```" + "sh\n", 1)[1].split("\n" + "```", 1)[0]
        windows = section.split("```" + "powershell\n", 1)[1].split("\n" + "```", 1)[0]
        self.assertIn("already exists; do not replace another trial", section)
        self.assertIn("Only after every command in the chosen block succeeds", section)
        self.assertIn("Get-Command codex -ErrorAction Stop", windows)
        native_lines = [line.strip() for line in windows.splitlines()]
        commands = [i for i, line in enumerate(native_lines) if line.startswith("codex ")]
        self.assertEqual(len(commands), 4)
        for i in commands:
            self.assertTrue(native_lines[i + 1].startswith("if ($LASTEXITCODE -ne 0)"))
        self.assertIn("--root $brRoot", windows)
        self.assertEqual(posix.count("|| exit 1"), 4)

    @unittest.skipUnless(shutil.which("sh"), "POSIX shell unavailable")
    def test_codex_posix_registration_executes_no_later_command_after_failure(self):
        source = GUIDE.read_text(encoding="utf-8")
        section = source.split("### Codex CLI: stdio entry", 1)[1]
        block = section.split("```" + "sh\n", 1)[1].split("\n" + "```", 1)[0]
        stub = r"""
BR_PYTHON='/trial path/python'
BR_SERVER='/trial path/server.py'
BR_ROOT='/trial path/target'
count=0
codex() {
    count=$((count + 1))
    printf '%s\n' "$count"
    if [ "$count" -eq 2 ]; then
        [ "$#" -eq 10 ] && [ "$5" = "$BR_PYTHON" ] && [ "$8" = "$BR_SERVER" ] && [ "$9" = "--root" ] && [ "${10}" = "$BR_ROOT" ] || return 99
    fi
    [ "$count" -ne "$FAIL_AT" ]
}
"""
        for fail_at in range(5):
            with self.subTest(fail_at=fail_at):
                result = subprocess.run(
                    ["sh", "-c", f"FAIL_AT={fail_at}\n" + stub + block],
                    capture_output=True, text=True, check=False, timeout=10,
                )
                expected = fail_at or 4
                self.assertEqual(result.stdout.splitlines(), [str(i) for i in range(1, expected + 1)])
                self.assertEqual(result.returncode, int(bool(fail_at)), result.stderr)

    def test_host_outcomes_remain_explicitly_unverified(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("has not passed a fresh\nClaude Code/Codex host installation", text)
        self.assertIn("not a released MCP version", text)
        self.assertIn("SDK smoke", text)


if __name__ == "__main__":
    unittest.main()
