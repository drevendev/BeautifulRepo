"""Source-level reflow guards for Pocket Board's validated content boundaries.

These tests protect the CSS/layout contract and untruncated generated HTML.
They are not a substitute for viewport/zoom checks in a real browser.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "application-starter"
CSS = (APP / "style.css").read_text(encoding="utf-8")

spec = importlib.util.spec_from_file_location("pocket_board_reflow", APP / "app.py")
assert spec is not None and spec.loader is not None
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)


def declarations(selector: str) -> dict[str, str]:
    """Read one simple CSS rule without depending on a third-party CSS parser."""
    match = re.search(re.escape(selector) + r"\s*\{([^{}]*)\}", CSS)
    if match is None:
        raise AssertionError(f"Missing CSS selector: {selector}")
    return {
        key.strip(): value.strip()
        for declaration in match.group(1).split(";")
        if ":" in declaration
        for key, value in [declaration.split(":", 1)]
    }


class PocketBoardReflowContractTests(unittest.TestCase):
    def test_flex_and_grid_children_can_shrink(self):
        for selector in (".task,.empty", ".task__heading", ".task__heading h3"):
            with self.subTest(selector=selector):
                self.assertEqual(declarations(selector).get("min-width"), "0")

    def test_unbroken_valid_content_can_wrap(self):
        for selector in (".task__heading h3", ".task p"):
            with self.subTest(selector=selector):
                self.assertEqual(declarations(selector).get("overflow-wrap"), "anywhere")
        badge = declarations(".badge")
        self.assertEqual(badge.get("white-space"), "nowrap")
        self.assertEqual(badge.get("flex-shrink"), "0")

    def test_maximum_accepted_input_is_not_truncated_to_hide_overflow(self):
        cases = (
            ("W" * 80, "a" * 32),
            ("🚀" * 80, "a" * 32),
            ("م" * 80, "a" * 32),
        )
        for title, ident in cases:
            with self.subTest(title=title[:8]):
                validated = board.validate_tasks([{
                    "id": ident, "title": title, "status": "open", "effort": 1,
                }])
                html = board.render_page(validated).decode("utf-8")
                self.assertIn("<h3>" + title + "</h3>", html)
                self.assertIn("ID " + ident + "</p>", html)


if __name__ == "__main__":
    unittest.main()
