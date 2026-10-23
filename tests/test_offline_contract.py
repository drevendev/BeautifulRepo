"""Static regression guard for the offline Python tools and composite Action."""
from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
BLOCKED = ("socket", "http", "ssl", "subprocess", "urllib.request")
SHELL_COMMAND = re.compile(r"(?<![\w-])(?:curl|wget|gh)(?![\w-])")


def blocked_imports(source: str) -> list[str]:
    """Detect direct imports, including aliases and from-urllib imports."""
    findings: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = (item.name for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names = (f"{node.module}.{item.name}" if node.module else item.name
                     for item in node.names)
        else:
            continue
        for name in names:
            if any(name == module or name.startswith(module + ".") for module in BLOCKED):
                findings.append(f"line {node.lineno}: {name}")
    return findings


def action_shell_commands(text: str) -> list[str]:
    """Check literal YAML run blocks for shell command names.

    Conservative: a quoted mention inside a shell block also trips. This is a
    static guard, not shell evaluation or proof of runtime isolation.
    """
    findings: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        start = re.match(r"^(\s*)run:\s*\|[-+]?\s*$", line)
        if not start:
            continue
        indent = len(start.group(1))
        for number in range(index + 1, len(lines)):
            command = lines[number]
            if command.strip() and len(command) - len(command.lstrip()) <= indent:
                break
            stripped = command.strip()
            if stripped.startswith("#"):
                continue
            if SHELL_COMMAND.search(stripped):
                findings.append(f"line {number + 1}: {stripped}")
    return findings


class OfflineContractTests(unittest.TestCase):
    def test_tools_do_not_import_network_or_process_modules(self) -> None:
        scripts = sorted((ROOT / "tools").glob("*.py"))
        self.assertTrue(scripts, "no tools/*.py files discovered")
        failures = []
        for path in scripts:
            for finding in blocked_imports(path.read_text(encoding="utf-8")):
                failures.append(f"{path.relative_to(ROOT)}: {finding}")
        self.assertEqual([], failures, "offline tools gained a forbidden import")

    def test_composite_action_has_no_network_command(self) -> None:
        action = (ROOT / "action.yml").read_text(encoding="utf-8")
        self.assertIn("runs:\n  using: composite", action)
        self.assertEqual([], action_shell_commands(action))

    def test_import_guard_catches_aliases_and_from_imports(self) -> None:
        for source in (
            "import socket as net", "from http.client import HTTPSConnection",
            "from urllib import request", "import urllib.request as req",
            "from ssl import SSLContext", "import subprocess",
            "def later():\n    from socket import create_connection",
        ):
            with self.subTest(source=source):
                self.assertTrue(blocked_imports(source))
        self.assertFalse(blocked_imports("from urllib.parse import urlsplit"))
        self.assertFalse(blocked_imports("import httpx_unused"))

    def test_action_guard_catches_commands_in_run_blocks(self) -> None:
        for command in ("curl https://example.com", "wget https://example.com", "gh api repos"):
            with self.subTest(command=command):
                self.assertEqual(1, len(action_shell_commands("  run: |\n    " + command + "\n")))
        self.assertEqual([], action_shell_commands("# curl is banned\n  run: |\n    echo OK\n"))


if __name__ == "__main__":
    unittest.main()
