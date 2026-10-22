"""Black-box and schema regressions for the curated collection example."""
from __future__ import annotations

from datetime import date
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "curated-starter"
SPEC = importlib.util.spec_from_file_location("curated_example", EXAMPLE / "curate.py")
assert SPEC and SPEC.loader
curate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(curate)


class CuratedCollectionTests(unittest.TestCase):
    def setUp(self):
        self.original = (EXAMPLE / "items.json").read_bytes()
        self.sample = json.loads(self.original)
        self.today = date(2026, 10, 17)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(EXAMPLE / "curate.py"), *args],
                              cwd=EXAMPLE, capture_output=True, text=True, encoding="utf-8",
                              check=False, timeout=10)

    def fixture(self, data):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "collection.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_example_output_and_no_mutation(self):
        text = self.cli("--as-of", "2026-10-17")
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertEqual(text.stdout.count("**Use when:**"), 3)
        self.assertIn("## Community", text.stdout)
        self.assertNotIn("**Review due**", text.stdout)
        self.assertEqual((EXAMPLE / "items.json").read_bytes(), self.original)

    def test_json_report_is_deterministic(self):
        options = ("--as-of", "2026-10-17", "--format", "json")
        a, b = self.cli(*options), self.cli(*options)
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertEqual(a.stdout, b.stdout)
        data = json.loads(a.stdout)
        self.assertEqual(data["review_due"], 0)
        self.assertEqual(len(data["entries"]), 3)

    def test_old_review_is_due_but_not_claimed_broken(self):
        result = self.cli("--as-of", "2027-05-01", "--fail-on-stale")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout.count("**Review due**"), 3)
        result = self.cli("--as-of", "2027-05-01")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_url_or_id_is_rejected(self):
        item = self.sample["entries"][0].copy()
        self.sample["entries"].append(item)
        with self.assertRaisesRegex(ValueError, "duplicate item id"):
            curate.validate(self.sample, self.today)
        self.sample["entries"][-1]["id"] = "new-id"
        with self.assertRaisesRegex(ValueError, "Duplicate destination"):
            curate.validate(self.sample, self.today)

    def test_unsafe_urls_and_dates_are_rejected(self):
        entry = self.sample["entries"][0]
        for url in ("http://example.com", "https://example.com/hello)evil", "https://user@example.com/x",
                    "https://example.com/x y", "javascript:alert(1)", "https://example.com/#frag"):
            with self.subTest(url=url):
                changed = json.loads(json.dumps(self.sample))
                changed["entries"][0]["url"] = url
                with self.assertRaises(ValueError):
                    curate.validate(changed, self.today)
        for when in ("2026-02-30", "2026-1-1", "2027-01-01"):
            with self.subTest(when=when):
                changed = json.loads(json.dumps(self.sample))
                changed["entries"][0]["verified_on"] = when
                with self.assertRaises(ValueError):
                    curate.validate(changed, self.today)

    def test_missing_notes_and_shape_are_rejected(self):
        changed = json.loads(json.dumps(self.sample))
        del changed["entries"][0]["limitation"]
        with self.assertRaisesRegex(ValueError, "Invalid item fields"):
            curate.validate(changed, self.today)
        changed = json.loads(json.dumps(self.sample))
        changed["entries"][0]["why"] = ""
        with self.assertRaisesRegex(ValueError, "Invalid why"):
            curate.validate(changed, self.today)

    def test_safe_markdown_escapes_source_notes(self):
        changed = json.loads(json.dumps(self.sample))
        changed["entries"][0]["title"] = "Guide ](https://other.test) <script>"
        changed["entries"][0]["why"] = "This is useful because <script> is not markup."
        output = curate.markdown(curate.report(changed, self.today, 180))
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn("<script>", output)
        self.assertIn("Guide \\](https://other.test)", output)

    def test_duplicate_json_object_keys_are_rejected(self):
        # json.loads normally keeps only the last spelling of an object key.
        # A collection audit must not silently discard conflicting metadata.
        original = self.original.decode("utf-8")
        variations = (
            original.replace(
                '"title": "Repository stewardship references",',
                '"title": "Stale unreviewed title",\n  "title": "Repository stewardship references",',
                1,
            ),
            original.replace(
                '"id": "github-community-profile",',
                '"id": "discarded-id",\n      "id": "github-community-profile",',
                1,
            ),
        )
        for source in variations:
            with self.subTest(source=source[:60]):
                self.assertNotEqual(source, original)
                temp = tempfile.TemporaryDirectory()
                self.addCleanup(temp.cleanup)
                path = Path(temp.name) / "duplicate.json"
                path.write_text(source, encoding="utf-8")
                result = self.cli("--data", str(path), "--as-of", "2026-10-17")
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("Invalid collection input", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_bad_inputs_have_generic_cli_errors(self):
        changed = json.loads(json.dumps(self.sample))
        changed["entries"][0]["url"] = "https://example.com/]secret-title"
        path = self.fixture(changed)
        result = self.cli("--data", str(path), "--as-of", "2026-10-17")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Invalid collection input", result.stderr)
        self.assertNotIn("secret-title", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
