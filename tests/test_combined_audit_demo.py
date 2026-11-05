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
        changed_lines = [
            line for line in payload["repair_diff"].splitlines()
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        ]
        self.assertEqual([
            "-Read the [setup guide](docs/setup.md) to begin.",
            "+Read the [setup guide](docs/guide.md) to begin.",
        ], changed_lines)
        self.assertTrue(payload["repair_diff"].startswith(
            "--- before/README.md\n+++ after/README.md\n"
        ))

    def test_readable_example_is_explicitly_synthetic_and_shows_both_checks(self):
        completed = self.invoke()
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("Synthetic Pocket Trails", completed.stdout)
        self.assertIn("BEFORE: combined exit 1", completed.stdout)
        self.assertIn("AFTER: combined exit 0", completed.stdout)
        self.assertIn("markdown_links: exit 1", completed.stdout)
        self.assertIn("html_navigation: exit 1", completed.stdout)
        self.assertIn("docs/setup.md", completed.stdout)
        self.assertIn("Exact fictional README repair (unified diff)", completed.stdout)
        self.assertIn("+Read the [setup guide](docs/guide.md)", completed.stdout)
        self.assertIn("not a real repository improvement", completed.stdout)


    def test_html_is_real_synthetic_before_after_evidence(self):
        completed = self.invoke("--format", "html")
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(completed.stdout.startswith("<!doctype html>"))
        for phrase in ("Synthetic Pocket Trails fixture", "Before repair",
                       "After repair", "Combined audit exit 1",
                       "Combined audit exit 0", "docs/setup.md",
                       "Markdown Links", "Html Navigation",
                       "No findings from this checker.",
                       "No real repository was repaired.",
                       "Before: missing local link found.",
                       "After: link corrected.",
                       "0/2 local-link checks pass.",
                       "2/2 local-link checks pass."):
            self.assertIn(phrase, completed.stdout)
        self.assertIn('id="repair-heading"', completed.stdout)
        self.assertIn('id="overview-heading"', completed.stdout)
        self.assertIn('class="overview-grid"', completed.stdout)
        self.assertIn("Before:</strong> 0/2 local-link checks pass", completed.stdout)
        self.assertIn("After:</strong> 2/2 local-link checks pass", completed.stdout)
        self.assertLess(completed.stdout.index('id="overview-heading"'),
                        completed.stdout.index('id="repair-heading"'))
        self.assertIn('<span class="sr-only">Removed line: </span>-Read the [setup guide](docs/setup.md)', completed.stdout)
        self.assertIn('<span class="sr-only">Added line: </span>+Read the [setup guide](docs/guide.md)', completed.stdout)
        self.assertIn('class="diff-line diff-removed"', completed.stdout)
        self.assertIn('class="diff-line diff-added"', completed.stdout)
        self.assertIn("prefers-color-scheme: dark", completed.stdout)
        self.assertIn('class="reports"', completed.stdout)
        self.assertIn('href="#after-title"', completed.stdout)
        self.assertIn('id="after-title"', completed.stdout)
        self.assertNotIn("<script", completed.stdout.lower())
        self.assertNotIn("http://", completed.stdout)
        self.assertNotIn("https://", completed.stdout)

    def test_html_overview_uses_current_report_values(self):
        import importlib.util
        module_spec = importlib.util.spec_from_file_location("combined_demo", DEMO)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        completed = self.invoke("--format", "json")
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        # Modify one in-memory checker outcome to reject hard-coded captions.
        result["reports"]["before"]["checks"]["markdown_links"]["exit_code"] = 0
        html = module.html_report(result)
        overview = html.split(
            '<section aria-labelledby="overview-heading">', 1
        )[1].split("</section>", 1)[0]
        self.assertIn("Before:</strong> 1/2 local-link checks pass", overview)
        self.assertNotIn("Before:</strong> 0/2 local-link checks pass", overview)

    def test_html_escapes_hostile_diagnostic(self):
        import importlib.util
        module_spec = importlib.util.spec_from_file_location("combined_demo", DEMO)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        completed = self.invoke("--format", "json")
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        result["reports"]["before"]["checks"]["markdown_links"]["diagnostics"].append(
            "<script>alert(1)</script>\u202e\nfake checker PASS"
        )
        result["repair_diff"] += "\n<img src=x onerror=alert(1)>\u202e\u2028spoofed row\n"
        page = module.html_report(result)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
        self.assertNotIn("<script>", page)
        self.assertIn('class="diff-line diff-context">&lt;img src=x onerror=alert(1)&gt;', page)
        self.assertIn(r"\u202e", page)
        self.assertIn(r"\u2028", page)
        self.assertNotIn("\u202e", page)
        self.assertNotIn("\u2028", page)


if __name__ == "__main__":
    unittest.main()
