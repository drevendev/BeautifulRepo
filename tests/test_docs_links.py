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


if __name__ == "__main__":
    unittest.main()
