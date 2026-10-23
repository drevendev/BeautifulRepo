"""repo_audit masks code spans within one block, as GitHub renders them.

A lone backtick is plain text on GitHub. Two of them in different paragraphs, or
one in a heading and one below it, must not form a span that hides the findings
between them.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repo_audit_code_spans", ROOT / "tools/repo_audit.py")
repo_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repo_audit)


class AuditCodeSpanTests(unittest.TestCase):
    def findings(self, readme: str) -> list[tuple[str, int | None]]:
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "README.md").write_text(readme, encoding="utf-8")
            report = repo_audit.audit_repository(folder)
        return sorted((item["rule_id"], item["line"]) for item in report["findings"]
                      if item["path"] == "README.md" and item["severity"] != "info")

    def test_stray_backticks_in_separate_paragraphs_hide_nothing(self):
        readme = ("# Title\n\nPress the ` key to open the console.\n\n## Install\n\n"
                  "TODO: write install steps\n\n<img src=\"screenshot.png\">\n\n"
                  "Close it with ` again.\n")
        self.assertEqual([("image.missing_alt", 9), ("readme.placeholder", 7)],
                         self.findings(readme))

    def test_a_heading_backtick_does_not_pair_with_the_next_line(self):
        readme = "# Press the ` key\nTODO: map the ` key\n"
        self.assertEqual([("readme.placeholder", 2)], self.findings(readme))

    def test_a_code_span_may_still_wrap_inside_one_paragraph(self):
        readme = "# Title\n\nWrite `TODO\nmarkers` in code to keep them literal.\n"
        self.assertEqual([], self.findings(readme))


if __name__ == "__main__":
    unittest.main()
