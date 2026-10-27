"""GFM one-line reference destination regressions for the offline link checker."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "docs_links.py"


class ReferenceLinksTests(unittest.TestCase):
    def check(self, markdown: str, files=()):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(markdown, encoding="utf-8")
            for filename in files:
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-I", str(CHECKER), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )

    def test_full_collapsed_and_shortcut_references_check_local_files(self):
        result = self.check(
            "[Details][doc]\n[Details][]\n![Cover]\n\n"
            "[DOC]: <guides/manual.md> \"Read this\"\n"
            "[details]: guides/manual.md\n"
            "[cover]: images/cover.svg\n",
            files=("guides/manual.md", "images/cover.svg"),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 3 relative Markdown destination(s)", result.stdout)

    def test_forward_reference_and_missing_destination_has_use_line(self):
        result = self.check(
            "See [the manual][Guide].\n\n"
            "[guide]: missing.md 'A title'\n"
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("README.md:1: missing relative destination: 'missing.md'", result.stderr)

    def test_unused_definition_is_not_a_checked_link(self):
        result = self.check("[unused]: missing.md\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_first_definition_wins_with_unicode_casefold(self):
        result = self.check(
            "[Γειά]\n\n[γειά]: existing.md\n[ΓΕΙΆ]: missing.md\n",
            files=("existing.md",),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 1 relative Markdown destination(s)", result.stdout)

    def test_definition_does_not_interrupt_paragraph(self):
        result = self.check("A paragraph\n[ref]: missing.md\n\n[ref]\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_malformed_and_indented_definitions_are_not_links(self):
        result = self.check(
            "[ref]\n\n"
            "    [ref]: missing.md\n"
            "[ref]: existing.md \"title\" trailing\n"
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_code_fence_and_comment_definitions_are_inactive(self):
        result = self.check(
            "~~~md\n[ref]: missing.md\n[ref]\n~~~\n"
            "<!-- [ref]: missing-other.md -->\n\n"
            "[ref]\n"
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_code_fence_reference_use_is_inactive(self):
        result = self.check(
            "[ref]: missing.md\n\n~~~\n[ref]\n~~~\n"
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_escaped_reference_is_not_a_link(self):
        result = self.check("\\[ref]\n\n[ref]: missing.md\n")
        self.assertEqual(0, result.returncode, result.stderr)

    def test_inline_link_overrides_same_label_reference(self):
        result = self.check(
            "[Docs](existing.md)\n\n[Docs]: missing.md\n",
            files=("existing.md",),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 1 relative Markdown destination(s)", result.stdout)

    def test_brackets_in_inline_destination_are_not_shortcut_references(self):
        result = self.check(
            "[File](<with[ref].md>)\n\n[ref]: missing.md\n",
            files=("with[ref].md",),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 1 relative Markdown destination(s)", result.stdout)

    def test_whitespace_normalization_and_external_destinations(self):
        result = self.check(
            "[Foo    Bar] and [Remote]\n\n"
            "[foo bar]: present.md\n"
            "[remote]: https://example.com/docs\n",
            files=("present.md",),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 1 relative Markdown destination(s)", result.stdout)

    def test_thematic_break_starts_a_reference_definition_block(self):
        result = self.check("---\n[doc]: missing.md\n[doc]\n")
        self.assertEqual(1, result.returncode)
        self.assertIn(
            "README.md:3: missing relative destination: 'missing.md'",
            result.stderr,
        )

    def test_setext_heading_underline_starts_a_reference_definition_block(self):
        result = self.check("Heading\n=======\n[doc]: missing.md\n[doc]\n")
        self.assertEqual(1, result.returncode)
        self.assertIn(
            "README.md:4: missing relative destination: 'missing.md'",
            result.stderr,
        )

    def test_traversal_in_used_reference_is_rejected_by_existing_boundary(self):
        result = self.check(
            "[Outside][ref]\n\n[ref]: ../outside.md\n"
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("escapes repository root", result.stderr)
        self.assertIn("README.md:1:", result.stderr)


if __name__ == "__main__":
    unittest.main()
