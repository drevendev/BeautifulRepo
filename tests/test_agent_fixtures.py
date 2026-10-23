"""Deterministic local fixture contract for the read-only audit agent skill.

These are *tool* tests, not proof of model triggering or prompt-injection resistance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "agent-repos"
CASES = ("minimal", "broken-links", "healthy", "injection-bait")


def snapshot(root: Path) -> dict[str, str]:
    """Hash every fixture file, including the expected-result contract."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class AgentFixtureTests(unittest.TestCase):
    def tool(self, script: str, args: list[str], *, cwd: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" / script), *args],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8",
            check=False, timeout=30,
        )

    def test_fixture_names_and_contracts(self):
        self.assertEqual(
            sorted(path.name for path in FIXTURES.iterdir() if path.is_dir()),
            sorted(CASES),
        )
        for name in CASES:
            with self.subTest(case=name):
                root = FIXTURES / name
                self.assertTrue((root / "README.md").is_file())
                expected = json.loads((root / "expected.json").read_text(encoding="utf-8"))
                self.assertEqual(set(expected), {"audit_rule_ids", "docs_links_exit"})
                self.assertIsInstance(expected["audit_rule_ids"], list)
                self.assertEqual(len(set(expected["audit_rule_ids"])),
                                 len(expected["audit_rule_ids"]))
                self.assertIn(expected["docs_links_exit"], (0, 1))

    def test_external_tools_match_contract_without_writing(self):
        # The tools must run from a foreign directory, not the plugin checkout
        # or a fixture; the target path is always supplied explicitly.
        with tempfile.TemporaryDirectory(prefix="beautifulrepo-foreign-cwd-") as foreign:
            for name in CASES:
                with self.subTest(case=name):
                    fixture = FIXTURES / name
                    root = Path(foreign) / name
                    shutil.copytree(fixture, root)
                    # The committed checkout must pass BeautifulRepo's own
                    # link checks. Make a broken target only inside a temp copy.
                    if name == "broken-links":
                        (root / "docs" / "missing.md").unlink()
                    expected = json.loads((fixture / "expected.json").read_text(encoding="utf-8"))
                    original_before = snapshot(fixture)
                    before = snapshot(root)
                    command = [str(root), "--format", "json", "--fail-on", "never"]
                    audit = self.tool("repo_audit.py", command, cwd=foreign)
                    self.assertEqual(audit.returncode, 0, audit.stderr)
                    report = json.loads(audit.stdout)
                    self.assertEqual(
                        sorted(finding["rule_id"] for finding in report["findings"]),
                        sorted(expected["audit_rule_ids"]),
                    )
                    self.assertEqual(report["schema_version"], 1)
                    second = self.tool("repo_audit.py", command, cwd=foreign)
                    self.assertEqual(second.returncode, 0, second.stderr)
                    self.assertEqual(second.stdout, audit.stdout, "audit must be deterministic")

                    links = self.tool("docs_links.py", ["--root", str(root)], cwd=foreign)
                    self.assertEqual(links.returncode, expected["docs_links_exit"],
                                     links.stdout + links.stderr)
                    if name == "broken-links":
                        self.assertIn("missing.md", links.stdout + links.stderr)

                    html = self.tool("html_navigation.py", ["--root", str(root)], cwd=foreign)
                    self.assertEqual(
                        html.returncode, 1 if name == "broken-links" else 0,
                        html.stdout + html.stderr,
                    )
                    if name == "broken-links":
                        self.assertIn("missing.md", html.stdout + html.stderr)
                    self.assertEqual(snapshot(root), before, "a read-only tool changed fixture bytes")
                    self.assertEqual(snapshot(fixture), original_before, "a tool changed source fixtures")
                    self.assertFalse((root / "AGENT_WROTE.txt").exists())

    def test_injection_case_is_explicitly_untrusted_input(self):
        readme = (FIXTURES / "injection-bait" / "README.md").read_text(encoding="utf-8")
        self.assertIn("SYSTEM OVERRIDE", readme)
        self.assertIn("AGENT_WROTE.txt", readme)
        # This guards the fixture text and test isolation only. Real-agent
        # instruction-following requires separate provider-backed evaluation.


if __name__ == "__main__":
    unittest.main()
