"""Black-box synthetic README approval flow: audit, preview, refusal, apply, re-audit.

This verifies the local helpers and checkers, not user consent or model behavior.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HASH_LINE = re.compile(r"^(.+README SHA-256:)\s+([0-9a-f]{64})$", re.MULTILINE)


class ReadmeWorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.target = self.work / "synthetic target"
        self.target.mkdir()
        self.readme = self.target / "README.md"
        self.readme.write_bytes(
            b"# Local Fixture\n\n{{PROJECT_NAME}} helps readers.\n\n"
            b"[here](missing.md)\n"
        )
        self.proposal = self.work / "candidate.md"  # Outside the target checkout.
        self.proposal.write_bytes(
            b"# Local Fixture\n\n"
            b"A small synthetic example of a README-only documentation fix.\n\n"
            b"Read the [usage notes](notes.md) before adapting this example.\n\n"
            b"First-success command: not run or verified.\n"
        )
        (self.target / "notes.md").write_text("# Usage notes\n\nNo target code is run.\n", encoding="utf-8")
        (self.target / "LICENSE").write_text("Synthetic fixture, not a license grant.\n", encoding="utf-8")
        (self.target / "CONTRIBUTING.md").write_text("# Contributing\n\nSynthetic only.\n", encoding="utf-8")
        self.marker = self.work / "target-was-executed"
        (self.target / "do-not-run.py").write_text(
            "from pathlib import Path\n"
            + f"Path({str(self.marker)!r}).write_text('unexpected', encoding='utf-8')\n",
            encoding="utf-8",
        )
        self.unchanged = {
            file.name: file.read_bytes()
            for file in self.target.iterdir()
            if file.name != "README.md"
        }

    def tool(self, name, *args):
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" / name), *map(str, args)],
            cwd=self.work, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )

    def audit(self):
        result = self.tool("repo_audit.py", self.target, "--format", "json", "--fail-on", "never")
        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        return {item["rule_id"] for item in report["findings"]}

    def preview(self):
        result = self.tool(
            "readme_preview.py", "--root", self.target, "--proposal", self.proposal,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Proposed unified diff", result.stdout)
        self.assertIn("-{{PROJECT_NAME}} helps readers.", result.stdout)
        self.assertIn("+Read the [usage notes](notes.md)", result.stdout)
        current = re.search(
            r"^Current README SHA-256:\s+([0-9a-f]{64})$", result.stdout, re.MULTILINE
        )
        proposed = re.search(
            r"^Proposed README SHA-256:\s+([0-9a-f]{64})$", result.stdout, re.MULTILINE
        )
        self.assertIsNotNone(current)
        self.assertIsNotNone(proposed)
        self.assertEqual(hashlib.sha256(self.readme.read_bytes()).hexdigest(), current.group(1))
        self.assertEqual(hashlib.sha256(self.proposal.read_bytes()).hexdigest(), proposed.group(1))
        return current.group(1), proposed.group(1)

    def apply(self, *args):
        return self.tool(
            "readme_apply.py", "--root", self.target, "--proposal", self.proposal, *args
        )

    @staticmethod
    def approval_args(original, candidate):
        # Test-only simulated approval; a real agent must obtain an explicit yes.
        return ("--approved-current-sha256", original,
                "--approved-proposed-sha256", candidate)

    def assert_no_other_changes(self):
        self.assertEqual(
            self.unchanged,
            {file.name: file.read_bytes() for file in self.target.iterdir()
             if file.name != "README.md"},
        )
        self.assertFalse(self.marker.exists(), "target code must never execute")
        self.assertEqual([], list(self.target.glob(".beautifulrepo-readme-*")))

    def test_synthetic_approved_preview_apply_and_before_after_checks(self):
        before_rules = self.audit()
        self.assertTrue({"readme.placeholder", "link.vague_text"} <= before_rules)
        broken_links = self.tool("docs_links.py", "--root", self.target)
        self.assertNotEqual(0, broken_links.returncode, broken_links.stdout)
        self.assertEqual(0, self.tool("html_navigation.py", "--root", self.target).returncode)

        old_bytes = self.readme.read_bytes()
        proposed_bytes = self.proposal.read_bytes()
        original, candidate = self.preview()
        self.assertEqual(old_bytes, self.readme.read_bytes())
        self.assert_no_other_changes()

        # Displaying a preview, or invoking the helper without approval hashes,
        # must not be construed as the missing explicit user confirmation.
        no_consent = self.apply()
        self.assertNotEqual(0, no_consent.returncode)
        self.assertEqual("", no_consent.stdout)
        self.assertEqual(old_bytes, self.readme.read_bytes())

        applied = self.apply(*self.approval_args(original, candidate))
        self.assertEqual(0, applied.returncode, applied.stderr)
        self.assertEqual(proposed_bytes, self.readme.read_bytes())
        self.assertEqual(proposed_bytes, self.proposal.read_bytes())
        after_rules = self.audit()
        self.assertNotIn("readme.placeholder", after_rules)
        self.assertNotIn("link.vague_text", after_rules)
        self.assertEqual(0, self.tool("docs_links.py", "--root", self.target).returncode)
        self.assertEqual(0, self.tool("html_navigation.py", "--root", self.target).returncode)
        self.assert_no_other_changes()

    def test_stale_target_refuses_without_touching_other_files(self):
        original, candidate = self.preview()
        changed = b"# Local Fixture\n\nConcurrent edit.\n"
        self.readme.write_bytes(changed)
        result = self.apply(*self.approval_args(original, candidate))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertEqual(changed, self.readme.read_bytes())
        self.assert_no_other_changes()

    def test_stale_candidate_refuses_without_touching_target(self):
        original, candidate = self.preview()
        old_bytes = self.readme.read_bytes()
        self.proposal.write_bytes(b"# Different candidate\n")
        result = self.apply(*self.approval_args(original, candidate))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertEqual(old_bytes, self.readme.read_bytes())
        self.assert_no_other_changes()


if __name__ == "__main__":
    unittest.main()
