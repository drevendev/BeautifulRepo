"""Behavioral tests for the offline Markdown destination checker."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "tools/docs_links.py"


class DocsLinksTests(unittest.TestCase):
    def run_checker(self, root: Path):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_relative_root_and_image_destinations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "assets").mkdir()
            (root / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
            (root / "assets/logo.svg").write_text("<svg></svg>\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Guide](docs/guide.md)\n![Logo](/assets/logo.svg)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 2 relative Markdown destination(s)", result.stdout)

    def test_missing_destination_reports_source_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "# Test\n\n[Missing](docs/nope.md)\n", encoding="utf-8"
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn(
                "README.md:3: missing relative destination: 'docs/nope.md'",
                result.stderr,
            )

    def test_external_and_fragment_links_are_out_of_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "[GitHub](https://github.com/)\n[Section](#section)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_fenced_and_inline_code_examples_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "```md\n[Example](missing.md)\n```\n"
                "Use `[Example](also-missing.md)` when documenting syntax.\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_multibacktick_and_multiline_code_spans_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "Use ``[Double](missing-double.md)`` when documenting syntax.\n"
                "Use ``code\n[Multiline](missing-multiline.md)\n`` here.\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_escaped_or_unmatched_backticks_do_not_hide_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "``[Mismatch](missing-mismatch.md)```\n"
                r"\`not code [Escaped opener](missing-escaped.md)`" + "\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn(
                "missing relative destination: 'missing-mismatch.md'",
                result.stderr,
            )
            self.assertIn(
                "missing relative destination: 'missing-escaped.md'",
                result.stderr,
            )

    def test_indented_code_blocks_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "    [Spaces](missing-spaces.md)\n"
                "\t[Tab](missing-tab.md)\n"
                "\n"
                "    [Later chunk](missing-chunk.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_indentation_respects_paragraph_and_list_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "Paragraph\n"
                "    [Paragraph continuation](missing-paragraph.md)\n"
                "- item\n"
                "\n"
                "    [List continuation](missing-list.md)\n"
                "- code item\n"
                "\n"
                "      [Nested code](missing-nested-code.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn(
                "missing relative destination: 'missing-paragraph.md'", result.stderr
            )
            self.assertIn("missing relative destination: 'missing-list.md'", result.stderr)
            self.assertNotIn("missing-nested-code.md", result.stderr)

    def test_block_quote_code_blocks_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "> ~~~md\n"
                "> [Fenced](absent-quoted-fence.md)\n"
                "> ~~~\n"
                ">\n"
                ">     [Indented](absent-quoted-indented.md)\n"
                "> > ~~~\n"
                "> > [Nested fence](absent-nested-fence.md)\n"
                "> > ~~~\n"
                "> >\n"
                "> >     [Nested indented](absent-nested-indented.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_block_quote_paragraph_links_are_still_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "> Paragraph\n"
                ">     [Indented continuation](absent-quote-paragraph.md)\n"
                "> [Visible](absent-quote-visible.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("absent-quote-paragraph.md", result.stderr)
            self.assertIn("absent-quote-visible.md", result.stderr)

    def test_list_container_fences_do_not_hide_following_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "1.  item\n"
                "\n"
                "    ```md\n"
                "    [Ordered](absent-ordered-list-code.md)\n"
                "    ```\n"
                "\n"
                "- ```md\n"
                "  [First block](absent-first-list-code.md)\n"
                "  ```\n"
                "\n"
                "[Visible](absent-after-list.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertNotIn("absent-ordered-list-code.md", result.stderr)
            self.assertNotIn("absent-first-list-code.md", result.stderr)
            self.assertIn("absent-after-list.md", result.stderr)

    def test_nested_empty_and_quoted_list_code_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "-\n"
                "  ```md\n"
                "  [Empty marker](absent-empty-marker-code.md)\n"
                "  ```\n"
                "- outer\n"
                "  - inner\n"
                "\n"
                "    ```md\n"
                "    [Nested](absent-nested-list-code.md)\n"
                "    ```\n"
                "- > ```md\n"
                "  > [List quote](absent-list-quote-code.md)\n"
                "  > ```\n"
                "> - quoted item\n"
                ">\n"
                ">   ```md\n"
                ">   [Quote list](absent-quote-list-code.md)\n"
                ">   ```\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_longer_fence_is_not_closed_by_shorter_nested_fence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "````md\n"
                "[Hidden](missing.md)\n"
                "```\n"
                "[Still hidden](also-missing.md)\n"
                "````\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_balanced_and_escaped_parentheses_in_destinations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            for name in ("a(b).md", "nested(a(b)).md", "escaped(foo).md"):
                (root / "docs" / name).write_text("# Target\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Balanced](docs/a(b).md)\n"
                "[Nested](docs/nested(a(b)).md \"title\")\n"
                r"[Escaped](docs/escaped\(foo\).md)" + "\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 3 relative Markdown destination(s)", result.stdout)

    def test_balanced_and_escaped_brackets_in_link_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "assets").mkdir()
            for name in ("nested.md", "escaped.md"):
                (root / "docs" / name).write_text("# Target\n", encoding="utf-8")
            (root / "assets/logo.svg").write_text("<svg></svg>\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Nested [label]](docs/nested.md)\n"
                r"[Escaped \[label\]](docs/escaped.md)" + "\n"
                "![Alt [nested]](assets/logo.svg)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 3 relative Markdown destination(s)", result.stdout)

    def test_character_references_are_decoded_before_url_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/a&b.md").write_text("# Target\n", encoding="utf-8")
            (root / "docs/literal&bogus;.md").write_text("# Literal\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Entity](docs/a&amp;b.md)\n"
                "[External](https&#58;//example.com/missing.md)\n"
                "[Fragment](&#35;section)\n"
                "[Invalid named](docs/literal&bogus;.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("checked 2 relative Markdown destination(s)", result.stdout)

    def test_multiline_inline_link_titles_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/good.md").write_text("# Target\n", encoding="utf-8")
            (root / "README.md").write_text(
                '[Good](docs/good.md\n  "Title on next line")\n'
                '[Missing](docs/nope.md\n  "Missing title")\n'
                '[Multiline title](docs/good.md "first line\nsecond line")\n',
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn(
                "README.md:3: missing relative destination: 'docs/nope.md'",
                result.stderr,
            )

    def test_noninterrupting_ordered_marker_does_not_hide_fenced_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "Paragraph\n"
                "2. ```md\n"
                "   [Visible](absent-noninterrupting.md)\n"
                "   ```\n"
                "\n"
                "Paragraph\n"
                "1. ```md\n"
                "   [List code](absent-interrupting-list-code.md)\n"
                "   ```\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("absent-noninterrupting.md", result.stderr)
            self.assertNotIn("absent-interrupting-list-code.md", result.stderr)

    def test_type1_raw_html_blocks_are_ignored_without_hiding_following_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "<pre>\n"
                "[Pre](absent-pre.md)\n"
                "</pre>\n"
                "> <pre>\n"
                "> [Quoted](absent-quoted-pre.md)\n"
                "> </pre>\n"
                "- <pre>\n"
                "  [Listed](absent-listed-pre.md)\n"
                "  </pre>\n"
                "\n"
                "[Visible](absent-after-html.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertNotIn("absent-pre.md", result.stderr)
            self.assertNotIn("absent-quoted-pre.md", result.stderr)
            self.assertNotIn("absent-listed-pre.md", result.stderr)
            self.assertIn("absent-after-html.md", result.stderr)

    def test_textarea_is_not_extended_as_a_type1_html_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            opening = "<" + "textarea>"
            closing = "</" + "textarea>"
            (root / "README.md").write_text(
                opening
                + "\n\n"
                + "[Visible after blank](absent-after-textarea-blank.md)\n"
                + closing
                + "\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("absent-after-textarea-blank.md", result.stderr)


    def test_type1_html_marker_inside_fence_does_not_hide_following_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "```md\n"
                "<pre>\n"
                "[Inside fence](absent-inside-fence.md)\n"
                "```\n"
                "[Visible](absent-after-fence.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertNotIn("absent-inside-fence.md", result.stderr)
            self.assertIn("absent-after-fence.md", result.stderr)

    def test_escape_from_repository_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "repo"
            root.mkdir()
            (parent / "outside.md").write_text("# Outside\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Outside](../outside.md)\n", encoding="utf-8"
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("escapes repository root", result.stderr)


    def test_malformed_remote_authority_does_not_crash_local_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "[Remote](https://[broken)\n"
                "[Scheme-relative](//[broken)\n"
                "[Local](absent-local.md)\n",
                encoding="utf-8",
            )
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("missing relative destination: 'absent-local.md'", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_invalid_percent_decoded_path_reports_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("[bad](%00)\n", encoding="utf-8")
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("invalid relative destination", result.stderr)
            self.assertIn("%00", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_invalid_utf8_markdown_reports_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_bytes(b"# Test\n\xff\n")
            result = self.run_checker(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("invalid UTF-8 Markdown", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
