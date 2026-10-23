"""Destinations that work on Windows or macOS but are dead on GitHub are reported.

Windows and macOS resolve names case-insensitively and quietly accept trailing dots,
stream suffixes and device names. GitHub is case-sensitive and serves none of those,
so the link checkers compare every name with its directory entry and check the rest
as text, with the same result on every operating system.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_links  # noqa: E402
import html_navigation  # noqa: E402


class PortableDestinationTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        (self.root / "docs").mkdir()
        (self.root / "docs/Guide.md").write_text("# Setup\n", encoding="utf-8")

    def errors(self, destination: str) -> list[str]:
        (self.root / "README.md").write_text(f"[x]({destination})\n", encoding="utf-8")
        errors, _, _ = docs_links.check_repo(self.root)
        return errors

    def test_exact_name_passes(self):
        self.assertEqual([], self.errors("docs/Guide.md"))
        self.assertEqual([], self.errors("docs/"))

    def test_wrong_letter_case_is_reported_everywhere(self):
        for destination in ("docs/guide.md", "DOCS/Guide.md", "Docs/guide.MD", "docs/GUIDE.md#setup"):
            with self.subTest(destination=destination):
                self.assertEqual(
                    [f"README.md:1: {docs_links.CASE_MISMATCH}: {destination!r}"],
                    self.errors(destination))

    def test_names_windows_cannot_check_out_are_non_portable(self):
        cases = {
            "docs/Guide.md.": "trailing dot or space",
            "docs/Guide.md%20": "trailing dot or space",
            "docs/Guide.md::$DATA": "drive letter or colon",
            "a%3Ab.md": "drive letter or colon",
            "NUL": "Windows reserved name",
            "con.md": "Windows reserved name",
            "docs/COM1.txt": "Windows reserved name",
            "lpt9": "Windows reserved name",
        }
        for destination, reason in cases.items():
            with self.subTest(destination=destination):
                self.assertEqual(
                    [f"README.md:1: non-portable destination ({reason}): {destination!r}"],
                    self.errors(destination))

    def test_ordinary_names_close_to_reserved_ones_pass(self):
        for name in ("console.md", "nullable.md", "COM10.md", "docs.v2"):
            with self.subTest(name=name):
                (self.root / name).write_text("x\n", encoding="utf-8")
                self.assertEqual([], self.errors(name))

    def test_html_navigation_reports_case_too(self):
        (self.root / "README.md").write_text('<a href="docs/guide.md">Guide</a>\n', encoding="utf-8")
        errors, _, _ = html_navigation.check_repo(self.root)
        self.assertEqual([f"README.md:1: HTML a {docs_links.CASE_MISMATCH}: 'docs/guide.md'"], errors)


if __name__ == "__main__":
    unittest.main()
