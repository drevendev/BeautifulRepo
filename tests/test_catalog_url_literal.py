"""Regressions for bounded source URLs and literal Markdown catalog text."""
from datetime import date
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("catalog_url_literal", ROOT / "tools/catalog.py")
assert SPEC and SPEC.loader
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


def item(url: str = "https://example.org/guide", title: str = "Example guide") -> dict:
    return {
        "id": "sample", "title": title, "category": "guide", "url": url,
        "why": "A useful, limited source", "apply": "Check a linked section",
        "caveat": "No network access", "coverage": "Source chapter reviewed",
        "reviewed_on": date.today().isoformat(), "evidence": "source-reviewed",
    }


class CatalogURLLiteralTests(unittest.TestCase):
    def check(self, url: str):
        return catalog.validate({"schema_version": 1, "resources": [item(url)]}, date.today())[0]

    def test_rejects_controls_and_broken_escapes(self):
        for url in (
            "https://example.org/a\x00b",
            "https://example.org/a\x1fb",
            "https://example.org/a\x7fb",
            "https://example.org/%ZZ",
            "https://example.org/%2",
            "https://example.org/path%",
        ):
            with self.subTest(url=repr(url)):
                self.assertTrue(self.check(url), url)

    def test_preserves_intentional_url_features(self):
        for url in (
            "https://example.org/a%20b",
            "https://example.org/a%23b?q=one%2Ftwo",
            "https://[2001:db8::1]/path",
            "https://example.org/path#section",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.check(url), [], url)

    def test_fragments_still_count_as_same_catalog_source(self):
        data = {"schema_version": 1, "resources": [
            item("https://example.org/path#first"),
            {**item("https://example.org/path#second"), "id": "other"},
        ]}
        errors, _ = catalog.validate(data, date.today())
        self.assertTrue(any("duplicate source URL" in error for error in errors), errors)

    def test_catalog_literal_strikethrough(self):
        value = "~~plain title~~"
        encoded = catalog.escape(value)
        self.assertIn(r"\~\~plain title\~\~", encoded)
        data = {"schema_version": 1, "resources": [item(title=value)]}
        output = catalog.render(data)
        self.assertIn("## " + encoded + "\n", output)
        self.assertNotIn("## ~~plain title~~\n", output)


if __name__ == "__main__":
    unittest.main()
