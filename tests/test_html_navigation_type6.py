"""HTML navigation must still inspect real tags inside type-6 GFM blocks."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "html_navigation.py"


class Type6HtmlNavigationTests(unittest.TestCase):
    def check(self, markdown: str, assets: dict[str, str] | None = None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(markdown, encoding="utf-8")
            for name, data in (assets or {}).items():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(data, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-I", str(TOOL), "--root", str(root)],
                cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=15,
            )

    def test_images_and_links_within_div_are_still_checked(self):
        result = self.check(
            "<div>\n"
            '<img src="missing-image.svg">\n'
            '<a href="missing-page.md">Link</a>\n'
            "</div>\n"
            "\n"
            "## Visible\n"
            '<a href="#visible">Works</a>\n'
        )
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("README.md:2: HTML img missing alt attribute", result.stderr)
        self.assertIn("missing HTML img destination: 'missing-image.svg'", result.stderr)
        self.assertIn("missing HTML a destination: 'missing-page.md'", result.stderr)
        self.assertNotIn("missing section anchor: '#visible'", result.stderr)

    def test_markdown_headings_in_type6_block_do_not_create_false_anchors(self):
        result = self.check(
            "<div>\n"
            "## Not a Markdown heading\n"
            "</div>\n"
            "\n"
            '<a href="#not-a-markdown-heading">Bad fragment</a>\n'
        )
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("missing section anchor: '#not-a-markdown-heading'", result.stderr)

    def test_valid_html_id_inside_type6_block_is_still_recognized(self):
        result = self.check(
            '<div id="real-target">\n'
            '<img src="real.svg" alt="Real image">\n'
            "</div>\n"
            "\n"
            '<a href="#real-target">Real target</a>\n',
            {"real.svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>"},
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("OK:", result.stdout)


if __name__ == "__main__":
    unittest.main()
