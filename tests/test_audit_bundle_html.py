"""HTML presentation of actual combined audit evidence, without target writes."""
from __future__ import annotations

from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "audit_bundle.py"
spec = importlib.util.spec_from_file_location("audit_bundle_html", TOOL)
bundle = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bundle)


class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class AuditBundleHtmlTests(unittest.TestCase):
    def test_actual_broken_link_in_self_contained_html_without_target_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text(
                "# Test project\n\n[Missing guide](missing.md)\n", encoding="utf-8"
            )
            (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (root / "CONTRIBUTING.md").write_text(
                "# Contribute\n", encoding="utf-8"
            )
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            completed = subprocess.run(
                [sys.executable, "-I", str(TOOL), str(root),
                 "--format", "html"],
                cwd=ROOT, capture_output=True, text=True,
                encoding="utf-8", timeout=90, check=False,
            )
            self.assertEqual(1, completed.returncode, completed.stderr)
            self.assertEqual(before, {p.name: p.read_bytes()
                                      for p in root.iterdir()})
            page = completed.stdout
        parser = TagCollector()
        parser.feed(page)
        tags = [name for name, _ in parser.tags]
        self.assertEqual(1, tags.count("main"))
        self.assertEqual(1, tags.count("h1"))
        self.assertEqual(3, tags.count("h2"))
        self.assertEqual("en", parser.tags[0][1].get("lang"))
        for forbidden in ("script", "link", "img"):
            self.assertNotIn(forbidden, tags)
        self.assertIn("missing.md", page)
        self.assertIn("Exit 1", page)
        self.assertIn("Markdown Links", page)
        self.assertIn("Html Navigation", page)

    def test_untrusted_diagnostics_do_not_insert_html_or_control_characters(self):
        report = {
            "exit_code": 2,
            "coverage": "not a <script> & audit \u2603",
            "checks": {
                "entry_points": {
                    "state": "complete",
                    "report": {
                        "summary": {"error": 0, "warning": 1, "info": 0},
                        "findings": [{
                            "path": "README\n.md", "line": 3,
                            "severity": "warning", "rule_id": "readme.test",
                            "message": "<script>alert('x')</script> \u202e",
                            "remediation": '"quote" & <action>',
                        }],
                    },
                },
                "markdown_links": {
                    "state": "complete", "exit_code": 1,
                    "checked_destinations": 1,
                    "inspected_markdown_files": 1,
                    "diagnostics": ["<img src=x onerror=alert(1)>"],
                },
                "html_navigation": {
                    "state": "incomplete", "exit_code": None,
                    "reason": "<script>failure</script>",
                },
            },
        }
        page = bundle.render_html(report)
        self.assertIn("Exit 2", page)
        self.assertIn("Incomplete:", page)
        self.assertIn("&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;", page)
        self.assertIn(r"\u000a", page)
        self.assertIn(r"\u202e", page)
        self.assertIn("&#9731;", page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
        self.assertNotIn("<script", page)
        self.assertNotIn("<img", page)
        self.assertTrue(page.isascii())
        parser = TagCollector()
        parser.feed(page)
        self.assertEqual(3, sum(tag == "section" for tag, _ in parser.tags))


if __name__ == "__main__":
    unittest.main()
