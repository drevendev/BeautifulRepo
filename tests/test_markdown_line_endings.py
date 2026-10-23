"""Only \\n, \\r\\n and \\r end a Markdown line in the tools, as in CommonMark.

str.splitlines also breaks at form feeds, vertical tabs, NEL and the Unicode line
and paragraph separators. Those characters inside code or prose used to desync the
masked copy from its source: html_navigation crashed or rejected valid anchors,
and repo_audit cited the wrong line.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_links  # noqa: E402
import html_navigation  # noqa: E402

SPEC = importlib.util.spec_from_file_location("repo_audit_line_endings", ROOT / "tools/repo_audit.py")
repo_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repo_audit)

NOT_LINE_ENDINGS = {"form feed": "\f", "vertical tab": "\v", "NEL": "\x85",
                    "line separator": " ", "paragraph separator": " "}


class LineEndingTests(unittest.TestCase):
    def repo(self, markdown: str):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        (root / "README.md").write_text(markdown, encoding="utf-8")
        return root

    def test_splitter_keeps_only_markdown_line_endings(self):
        self.assertEqual(["a\n", "b\r\n", "c\r", "d\f e"],
                         docs_links.split_markdown_lines("a\nb\r\nc\rd\f e"))
        self.assertEqual([], docs_links.split_markdown_lines(""))

    def test_html_navigation_anchors_survive_odd_characters(self):
        for name, char in NOT_LINE_ENDINGS.items():
            documents = {
                "fenced code": f"# Title\n\n```js\na = 1;{char}b = 2;\n```\n\n"
                               "A longer line that mentions `some_code_span` near its end.\n"
                               "## Usage\n\n[usage](#usage)\n",
                "heading after code": f"# Title\n\n```js\nconst s = 'line{char}separator';\n```\n\n"
                                      "## The `run` command\n\n[run](#the-run-command)\n",
                "inline code": f"# Title\n\nUse `a{char}b` here.\n\n## Usage\n\n[usage](#usage)\n",
                "prose": f"# Title\n\nIntro{char}text.\n\n## Usage\n\n[usage](#usage)\n",
            }
            for where, markdown in documents.items():
                with self.subTest(char=name, where=where):
                    errors, _, _ = html_navigation.check_repo(self.repo(markdown))
                    self.assertEqual([], errors)

    def test_docs_links_line_numbers_count_only_markdown_lines(self):
        for name, char in NOT_LINE_ENDINGS.items():
            with self.subTest(char=name):
                root = self.repo(f"# T\n\n```\nx{char}y\n```\n\n[missing](nope.md)\n")
                errors, _, _ = docs_links.check_repo(root)
                self.assertEqual(["README.md:7: missing relative destination: 'nope.md'"], errors)

    def test_repo_audit_cites_the_source_line(self):
        for name, char in NOT_LINE_ENDINGS.items():
            with self.subTest(char=name):
                root = self.repo(f"# Project title\n\nSection one.\n{char}\n## Two\n\nTODO: finish this\n")
                report = repo_audit.audit_repository(root)
                placeholders = [item["line"] for item in report["findings"]
                                if item["rule_id"] == "readme.placeholder"]
                self.assertEqual([7], placeholders)


if __name__ == "__main__":
    unittest.main()
