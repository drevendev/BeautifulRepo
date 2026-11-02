"""Top-level GFM type-7 HTML block regressions for the offline link checkers."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from tools import docs_links  # noqa: E402


class GfmType7Tests(unittest.TestCase):
    def run_checker(self, script: str, root: Path):
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" / script),
             "--root", str(root)],
            text=True, capture_output=True, check=False,
        )

    def test_standalone_complete_tag_masks_markdown_until_blank_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_bytes(
                b'<Widget data-x="value > other">\r\n'
                b'[Raw](missing-inside.md)\r\n'
                b'<img src="missing-real.png">\r\n'
                b'\r\n'
                b'[Visible](missing-after.md)\r\n'
            )
            result = self.run_checker("docs_links.py", root)
            self.assertEqual(1, result.returncode, result.stderr)
            self.assertIn("README.md:5: missing relative destination: 'missing-after.md'",
                          result.stderr)
            self.assertNotIn("missing-inside.md", result.stderr)
            self.assertNotIn("missing-real.png", result.stderr)

    def test_paragraph_and_lazy_continuation_are_not_html_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "A paragraph\n"
                "<a href='remote'>\n"
                "[Lazy](missing-lazy.md)\n"
                "\n"
                "> Quoted paragraph\n"
                "<custom>\n"
                "[Still lazy](missing-quote-lazy.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker("docs_links.py", root)
            self.assertEqual(1, result.returncode)
            self.assertIn("missing-lazy.md", result.stderr)
            self.assertIn("missing-quote-lazy.md", result.stderr)

    def test_inline_incomplete_or_indented_tags_do_not_hide_links(self):
        for opener in (
            "<custom> inline",
            "<custom><a>",
            '<custom title="unfinished>',
            "    <custom>",
            "\t<custom>",
            "<custom/ >",
            "<custom attr=>",
        ):
            with self.subTest(opener=opener), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "README.md").write_text(
                    opener + "\n[Visible](missing.md)\n", encoding="utf-8"
                )
                result = self.run_checker("docs_links.py", root)
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertIn("missing.md", result.stderr)

    def test_block_starts_after_heading_and_reference_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "# Intro\n"
                "<custom attr='x' flag>\n"
                "[Hidden](missing-hidden.md)\n"
                "\n"
                "[asset]: missing-real.md\n"
                "<custom />\n"
                "[Hidden too](missing-hidden-again.md)\n"
                "\n"
                "[Used][asset]\n",
                encoding="utf-8",
            )
            result = self.run_checker("docs_links.py", root)
            self.assertEqual(1, result.returncode, result.stderr)
            self.assertNotIn("missing-hidden.md", result.stderr)
            self.assertNotIn("missing-hidden-again.md", result.stderr)
            self.assertIn("missing-real.md", result.stderr)

    def test_closing_tag_can_open_a_type7_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "</Custom>\n"
                "[Hidden](missing-hidden.md)\n"
                "\n"
                "[Visible](missing-visible.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker("docs_links.py", root)
            self.assertEqual(1, result.returncode, result.stderr)
            self.assertNotIn("missing-hidden.md", result.stderr)
            self.assertIn("README.md:4:", result.stderr)

    def test_html_navigation_retains_real_image_checks_in_raw_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "<Widget>\n"
                "<img src='missing-image.svg'>\n"
                "[Literal](not-a-markdown-link.md)\n"
                "\n",
                encoding="utf-8",
            )
            docs = self.run_checker("docs_links.py", root)
            html = self.run_checker("html_navigation.py", root)
            self.assertEqual(0, docs.returncode, docs.stderr)
            self.assertEqual(1, html.returncode, html.stdout)
            self.assertIn("HTML img missing alt attribute", html.stderr)
            self.assertIn("missing-image.svg", html.stderr)
            self.assertNotIn("not-a-markdown-link.md", html.stderr)

    def test_mask_preserves_exact_offsets_and_all_line_endings(self):
        source = (
            "# Heading\r\n"
            "\r\n"
            " <Widget data-x='ok'>\r\n"
            "[Raw](hidden.md)\r\n"
            "<img src='missing.svg'>\r\n"
            "\r\n"
            "[Visible](real.md)\n"
            "</Widget>\n"
            "[Hidden](another.md)\r"
            "\r"
            "[After](after.md)"
        )
        masked = docs_links._mask_markdown_code(source)
        self.assertEqual(len(source), len(masked))
        for offset, char in enumerate(source):
            if char in "\r\n":
                self.assertEqual(char, masked[offset], offset)
        self.assertNotIn("hidden.md", masked)
        self.assertNotIn("another.md", masked)
        self.assertIn("real.md", masked)
        self.assertIn("after.md", masked)


if __name__ == "__main__":
    unittest.main()
