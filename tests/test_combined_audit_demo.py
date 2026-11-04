"""Run the user-facing combined-audit demonstration in real subprocesses."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "combined-audit" / "demo.py"


class CombinedAuditDemoTests(unittest.TestCase):
    def invoke(self, *arguments):
        # Windows redirects use a locale code page unless UTF-8 mode is explicit.
        return subprocess.run(
            [sys.executable, "-I", "-X", "utf8", str(DEMO), *arguments],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            timeout=180, check=False,
        )

    def test_json_is_real_link_checker_before_after_evidence(self):
        completed = self.invoke("--format", "json")
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("synthetic", payload["fixture_kind"])
        self.assertEqual(1, payload["reports"]["before"]["exit_code"])
        self.assertEqual(0, payload["reports"]["after"]["exit_code"])
        for name in ("markdown_links", "html_navigation"):
            before = payload["reports"]["before"]["checks"][name]
            after = payload["reports"]["after"]["checks"][name]
            self.assertEqual("complete", before["state"])
            self.assertEqual("complete", after["state"])
            self.assertEqual(1, before["exit_code"])
            self.assertEqual(0, after["exit_code"])
            self.assertIn("docs/setup.md", "\n".join(before["diagnostics"]))
            self.assertFalse(after["diagnostics"])
        self.assertIn("no fixture writes", payload["verification"])

    def test_readable_example_is_explicitly_synthetic_and_shows_both_checks(self):
        completed = self.invoke()
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("Synthetic Pocket Trails", completed.stdout)
        self.assertIn("BEFORE: combined exit 1", completed.stdout)
        self.assertIn("AFTER: combined exit 0", completed.stdout)
        self.assertIn("markdown_links: exit 1", completed.stdout)
        self.assertIn("html_navigation: exit 1", completed.stdout)
        self.assertIn("docs/setup.md", completed.stdout)
        self.assertIn("not a real repository improvement", completed.stdout)


if __name__ == "__main__":
    unittest.main()
