"""GFM nested-inline precedence and source-coordinate regressions."""
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "docs_links.py"


class NestedInlineLinksTests(unittest.TestCase):
    def inspect(self, markdown: str):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "README.md"
            source.write_bytes(markdown.encode("utf-8"))
            module = runpy.run_path(str(SCRIPT))
            links = [tuple(item) for item in module["iter_markdown_locations"](source)]
            legacy = list(module["iter_markdown_destinations"](source))
            cli = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            return links, legacy, cli

    def test_inner_ordinary_link_wins_over_outer(self):
        markdown = "Ω [outer [inner](inner.md)](outer.md)\n"
        links, legacy, cli = self.inspect(markdown)
        self.assertEqual(
            [(1, markdown.index("[inner]") + 1, "inner.md", 1)], links
        )
        self.assertEqual([(1, "inner.md")], legacy)
        self.assertEqual(1, cli.returncode)
        self.assertIn("missing relative destination: 'inner.md'", cli.stderr)
        self.assertNotIn("'outer.md'", cli.stderr)

    def test_discarded_outer_destination_does_not_mask_side_link(self):
        # The invalid outer link's destination-looking suffix is plain text.
        # Its apparent side link therefore remains independently live.
        links, legacy, cli = self.inspect(
            "[Outer [inner](inner.md)](assets/[side](side.md))\n"
        )
        self.assertEqual(
            [(1, 8, "inner.md", 1), (1, 34, "side.md", 1)], links
        )
        self.assertEqual([(1, "inner.md"), (1, "side.md")], legacy)
        self.assertEqual(1, cli.returncode)
        self.assertIn("'inner.md'", cli.stderr)
        self.assertIn("'side.md'", cli.stderr)
        self.assertNotIn("assets/", cli.stderr)

    def test_fake_link_inside_image_destination_cannot_suppress_outer(self):
        # A syntactically valid-looking ordinary link in an image destination
        # is literal destination text. It cannot invalidate the outer link.
        markdown = "[outer ![alt](path/[fake](fake.md))](outer.md)\\n"
        links, legacy, cli = self.inspect(markdown)
        self.assertEqual(
            [(1, 1, "outer.md", 1),
             (1, markdown.index("![alt]") + 1,
              "path/[fake](fake.md)", 1)],
            links,
        )
        self.assertEqual(
            [(1, "outer.md"), (1, "path/[fake](fake.md)")], legacy
        )
        self.assertEqual(1, cli.returncode)
        self.assertIn("missing relative destination: 'outer.md'", cli.stderr)
        self.assertIn(
            "missing relative destination: 'path/[fake](fake.md)'",
            cli.stderr,
        )
        self.assertNotIn(
            "missing relative destination: 'fake.md'", cli.stderr
        )

    def test_multiple_levels_keep_only_innermost_ordinary_link(self):
        links, legacy, cli = self.inspect(
            "[A [B [C](c.md)](b.md)](a.md)\n"
        )
        self.assertEqual([(1, 7, "c.md", 1)], links)
        self.assertEqual([(1, "c.md")], legacy)
        self.assertNotIn("'a.md'", cli.stderr)
        self.assertNotIn("'b.md'", cli.stderr)

    def test_valid_image_inside_ordinary_link_keeps_both(self):
        links, legacy, cli = self.inspect(
            "[Page ![Logo](logo.svg)](page.md)\n"
        )
        self.assertEqual(
            [(1, 1, "page.md", 1), (1, 7, "logo.svg", 1)], links
        )
        self.assertEqual(
            [(1, "page.md"), (1, "logo.svg")], legacy
        )
        self.assertEqual(1, cli.returncode)
        self.assertIn("'logo.svg'", cli.stderr)
        self.assertIn("'page.md'", cli.stderr)

    def test_nested_link_markup_in_image_alt_is_not_another_link(self):
        links, _, cli = self.inspect(
            "[Page ![alt [inner](not-live.md)](logo.svg)](page.md)\n"
        )
        self.assertEqual(
            [(1, 1, "page.md", 1), (1, 7, "logo.svg", 1)], links
        )
        self.assertNotIn("'not-live.md'", cli.stderr)

    def test_failed_inner_parse_does_not_block_outer_link(self):
        links, _, cli = self.inspect(
            "[outer [broken](has whitespace)](outer.md)\n"
        )
        self.assertEqual([(1, 1, "outer.md", 1)], links)
        self.assertIn("'outer.md'", cli.stderr)
        self.assertNotIn("has whitespace", cli.stderr)

    def test_link_like_brackets_inside_destination_are_literal(self):
        markdown = "[outer](assets/a[inner](word).svg)\n"
        links, _, cli = self.inspect(markdown)
        self.assertEqual(
            [(1, 1, "assets/a[inner](word).svg", 1)], links
        )
        self.assertNotIn("missing relative destination: 'word'", cli.stderr)

    def test_escaped_brackets_and_masked_code_remain_unchanged(self):
        code = chr(96)
        links, _, cli = self.inspect(
            r"[outer \[escaped\]](outer.md) " + "\n"
            + code + "[hidden](hidden.md)" + code
            + " [bad [live](live.md)](bad.md)\n"
        )
        self.assertEqual(
            [(1, 1, "outer.md", 1), (2, 28, "live.md", 2)], links
        )
        self.assertNotIn("'hidden.md'", cli.stderr)
        self.assertNotIn("'bad.md'", cli.stderr)

    def test_crlf_multiline_nested_link_preserves_source_anchor(self):
        links, legacy, cli = self.inspect(
            "Ω [outer\r\n [inner](inner.md)\r\n](outer.md)\r\n"
        )
        self.assertEqual([(2, 2, "inner.md", 2)], links)
        self.assertEqual([(2, "inner.md")], legacy)
        self.assertNotIn("'outer.md'", cli.stderr)


if __name__ == "__main__":
    unittest.main()
