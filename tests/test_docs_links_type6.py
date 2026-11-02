"""GFM type-6 HTML block coverage for the offline Markdown link scanner.

These are source-level tests, not a full Markdown-renderer conformance suite.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "docs_links.py"


class Type6HtmlBlockTests(unittest.TestCase):
    def check(self, source: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(source, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-I", str(TOOL), "--root", str(root)],
                cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=15,
            )

    def test_block_level_tags_hide_markdown_links_until_blank(self):
        for opener in ("<DIV class='preview'>", "<details open>", "<table><tr>", "</SECTION>", "<h2>"):
            with self.subTest(opener=opener):
                result = self.check(
                    opener + "\n"
                    + "[Raw](missing-inside-html.md)\n"
                    + "</div>\n"
                    + "\n"
                    + "[Visible](missing-after-blank.md)\n"
                )
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertNotIn("missing-inside-html.md", result.stderr)
                self.assertIn("README.md:5: missing relative destination: 'missing-after-blank.md'", result.stderr)

    def test_close_tag_alone_does_not_end_type6_block(self):
        result = self.check(
            "<div>\n"
            "</div>\n"
            "[Still raw](missing-before-blank.md)\n"
            "\n"
            "[Parsed](missing-after-blank.md)\n"
        )
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertNotIn("missing-before-blank.md", result.stderr)
        self.assertIn("README.md:5: missing relative destination: 'missing-after-blank.md'", result.stderr)

    def test_whitespace_blank_line_restarts_markdown_and_crlf_is_supported(self):
        result = self.check(
            "<div class=demo\r\n"
            "[Raw](missing-before-tab-blank.md)\r\n"
            "\t\r\n"
            "[Parsed](missing-after-tab-blank.md)\r\n"
        )
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertNotIn("missing-before-tab-blank.md", result.stderr)
        self.assertIn("README.md:4: missing relative destination: 'missing-after-tab-blank.md'", result.stderr)

    def test_type6_at_end_of_file_does_not_report_raw_links(self):
        result = self.check("<div>\n[Raw](missing-at-eof.md)\n</div>")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_tag_name_must_have_gfm_boundary(self):
        for line in ("<diversion>", "<div-other>", "<div/ invalid>", "Prefix <div>"):
            with self.subTest(line=line):
                result = self.check(line + "\n[Parsed](missing-not-a-type6.md)\n")
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertIn("missing-not-a-type6.md", result.stderr)

    def test_type6_opener_in_fence_is_inert(self):
        result = self.check(
            "```html\n"
            "<div>\n"
            "```\n"
            "[Parsed](missing-after-fence.md)\n"
        )
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("README.md:4: missing relative destination: 'missing-after-fence.md'", result.stderr)


if __name__ == "__main__":
    unittest.main()
