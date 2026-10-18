"""Regressions for ambiguous JSON keys in the public source-backed catalog."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "catalog.py"
SPEC = importlib.util.spec_from_file_location("catalog_duplicate_keys_regression", SCRIPT)
assert SPEC and SPEC.loader
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


def valid_item():
    return {
        "id": "example-guide", "title": "Example guide", "category": "guide",
        "url": "https://example.org/guide", "why": "Source-backed reason",
        "apply": "A specific useful action", "caveat": "Not tested in production",
        "coverage": "Documentation section inspected", "reviewed_on": "2026-10-17",
        "evidence": "source-reviewed",
    }


class CatalogDuplicateJSONKeysTests(unittest.TestCase):
    def run_catalog(self, contents: str):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "resources.json"
            output = Path(directory) / "catalog.md"
            data.write_text(contents, encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = catalog.main(["--data", str(data), "--output", str(output), "--write"])
            return exit_code, stdout.getvalue(), stderr.getvalue(), output.exists()

    def test_duplicate_keys_rejected_before_overwrite(self):
        item = json.dumps(valid_item(), ensure_ascii=False)
        valid = '{"schema_version": 1, "resources": [' + item + ']}'
        cases = {
            "root": '{"schema_version": 999, ' + valid[1:],
            "nested_metadata": valid.replace(
                '"evidence": "source-reviewed"',
                '"evidence": "not-reviewed", "evidence": "source-reviewed"'),
            "escaped_equivalent": valid.replace(
                '"id": "example-guide"',
                '"id": "discarded", "\\u0069d": "example-guide"'),
        }
        for label, source in cases.items():
            with self.subTest(label=label):
                status, stdout, stderr, output_exists = self.run_catalog(source)
                self.assertEqual(status, 1, label)
                self.assertEqual(stdout, "", label)
                self.assertIn("duplicate JSON object key", stderr, label)
                self.assertFalse(output_exists, label)

    def test_valid_catalog_remains_writable(self):
        source = json.dumps({"schema_version": 1, "resources": [valid_item()]})
        status, stdout, stderr, exists = self.run_catalog(source)
        self.assertEqual(status, 0, stderr)
        self.assertIn("1 resources", stdout)
        self.assertEqual(stderr, "")
        self.assertTrue(exists)


if __name__ == "__main__":
    unittest.main()
