"""Regressions for follow-up accessibility, Markdown and JSON boundaries.

The contrast calculation checks palette tokens, not rendered browser accessibility.
"""
from datetime import date
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "examples" / "curated-starter"
BOARD = ROOT / "examples" / "application-starter"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


curate = load_module("workshop_followup_curated", CURATED / "curate.py")
board = load_module("workshop_followup_board", BOARD / "app.py")


def luminance(value):
    code = value.lstrip("#")
    if len(code) == 3:
        code = "".join(c * 2 for c in code)
    channels = [int(code[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    low, high = sorted((luminance(a), luminance(b)))
    return (high + 0.05) / (low + 0.05)


class WorkshopHardeningTests(unittest.TestCase):
    def curated_sample(self):
        return json.loads((CURATED / "items.json").read_text(encoding="utf-8"))

    def test_scope_stays_prose_even_with_block_markers(self):
        for scope in ("# Accidental heading text", "- Accidental list item text",
                      "1. Numbered list item", "---- thematic separator",
                      "Ordinary informational scope text"):
            with self.subTest(scope=scope):
                raw = self.curated_sample()
                raw["scope"] = scope
                output = curate.markdown(curate.report(raw, date(2026, 10, 17), 180))
                self.assertEqual(output.splitlines()[2],
                                 f"**Scope:** {curate.markdown_text(scope)}")

    def test_strikethrough_is_literal(self):
        raw = self.curated_sample()
        raw["entries"][0]["why"] = "This ~~retired~~ pattern is still plain text."
        result = curate.markdown(curate.report(raw, date(2026, 10, 17), 180))
        self.assertIn(r"This \~\~retired\~\~ pattern", result)

    def test_url_rejects_even_empty_fragment(self):
        for suffix in ("#", "?edition=2#", "#section"):
            with self.subTest(suffix=suffix):
                raw = self.curated_sample()
                raw["entries"][0]["url"] = "https://example.com/example" + suffix
                with self.assertRaises(ValueError):
                    curate.validate(raw, date(2026, 10, 17))

    def test_encoded_hash_is_not_a_fragment(self):
        raw = self.curated_sample()
        raw["entries"][0]["url"] = "https://example.com/example%23section"
        self.assertEqual(len(curate.validate(raw, date(2026, 10, 17))), 3)

    def read_fixture(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            path.write_text(source, encoding="utf-8")
            with patch.object(board, "FIXTURE", path):
                return board.read_sample()

    def test_duplicate_board_fields_are_rejected(self):
        cases = (
            '[{"id":"demo","title":"Sample task","status":"open","status":"done","effort":1}]',
            '[{"id":"demo","title":"Sample task","status":"open","effort":1,"effort":99}]',
            '[{"id":"demo","title":"Sample task","status":"open","effort":1,"t\\u0069tle":"Other"}]',
        )
        for source in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, "Duplicate JSON object key"):
                    self.read_fixture(source)

    def test_valid_board_fixture_still_works(self):
        expected = [{"id": "demo", "title": "Sample task", "status": "open", "effort": 1}]
        self.assertEqual(self.read_fixture(
            '[{"id":"demo","title":"Sample task","status":"open","effort":1}]'), expected)

    def test_control_border_palette_contrast(self):
        css = (BOARD / "style.css").read_text(encoding="utf-8")
        self.assertIn("border:1px solid var(--line)", css)
        themes = re.findall(r":root\s*\{([^{}]*)\}", css)
        self.assertEqual(len(themes), 2)
        for theme, text in zip(("light", "dark"), themes):
            colors = dict(re.findall(r"--([a-z]+):\s*(#[0-9a-fA-F]{3,6})\b", text))
            # Control boundaries and the focus outline are non-text cues (3:1); body and
            # muted text need 4.5:1. The 2026-10-23 rendered check measured the same pairs.
            for token, minimum in (("line", 3.0), ("focus", 3.0), ("ink", 4.5), ("muted", 4.5)):
                for adjacent in ("bg", "panel"):
                    with self.subTest(theme=theme, token=token, adjacent=adjacent):
                        self.assertGreaterEqual(contrast(colors[token], colors[adjacent]), minimum)


if __name__ == "__main__":
    unittest.main()
