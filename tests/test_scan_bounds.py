"""Adversarial Markdown near the 500 KiB cap is scanned in roughly linear time.

The time budgets are generous on purpose: the quadratic scans these tests guard
against took minutes or hours at these sizes, the linear ones take well under a
second, and a slow CI runner should never turn the gap into a flaky failure.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_links  # noqa: E402

SPEC = importlib.util.spec_from_file_location("repo_audit_scan_bounds", ROOT / "tools/repo_audit.py")
repo_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repo_audit)

BUDGET_SECONDS = 15
SIZE = 200_000


class ScanBoundTests(unittest.TestCase):
    def timed(self, function, body: str):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text("# Title\n\n" + body + "\n", encoding="utf-8")
            start = time.perf_counter()
            result = function(root)
            return time.perf_counter() - start, result

    def test_link_scan_is_bounded(self):
        for name, body in {
            "unmatched brackets": "[" * SIZE,
            "link openers without destinations": "[a](" * (SIZE // 4),
        }.items():
            with self.subTest(name):
                elapsed, _ = self.timed(docs_links.check_repo, body)
                self.assertLess(elapsed, BUDGET_SECONDS)

    def test_heading_with_trailing_spaces_is_bounded(self):
        elapsed, report = self.timed(repo_audit.audit_repository, "## x" + " " * SIZE + "y")
        self.assertLess(elapsed, BUDGET_SECONDS)
        self.assertEqual("README.md", report["documents"]["readme"])


class LinkParsingStillMatchesGitHubTests(unittest.TestCase):
    def destinations(self, markdown: str) -> list[str]:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "README.md"
            path.write_text(markdown, encoding="utf-8")
            return [destination for _, destination in docs_links.iter_markdown_destinations(path)]

    def test_nested_and_escaped_link_text(self):
        self.assertEqual(["a.md", "b.md"], self.destinations(
            "[outer [inner] text](a.md) and \\[not a link](x.md) [c \\] d](b.md)\n"))

    def test_unmatched_brackets_do_not_hide_later_links(self):
        self.assertEqual(["a.md"], self.destinations("[[[ [ok](a.md) ]\n"))

    def test_parenthesis_nesting_stops_after_32_levels_like_cmark_gfm(self):
        inner = "x" + "(" * 32 + ")" * 32
        self.assertEqual([inner], self.destinations(f"[deep]({inner})\n"))
        too_deep = "x" + "(" * 33 + ")" * 33
        self.assertEqual([], self.destinations(f"[deeper]({too_deep})\n"))


if __name__ == "__main__":
    unittest.main()
