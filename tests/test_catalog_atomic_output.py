"""Regression tests for atomic catalog generation and UTF-8 input boundaries."""
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("catalog_atomic_write", ROOT / "tools/catalog.py")
assert SPEC is not None and SPEC.loader is not None
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


def example_resource(title="Example guide"):
    return {
        "id": "example-guide", "title": title, "category": "guide",
        "url": "https://example.org/guide", "why": "A reason",
        "apply": "An action", "caveat": "Not a runtime test",
        "coverage": "A section was read",
        "reviewed_on": datetime.now(timezone.utc).date().isoformat(),
        "evidence": "source-reviewed",
    }


def run_cli(source: Path, output: Path):
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = catalog.main(["--data", str(source), "--output", str(output), "--write"])
    return code, stdout.getvalue(), stderr.getvalue()


class CatalogAtomicWriteTests(unittest.TestCase):
    def test_invalid_surrogate_does_not_destroy_existing_output(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            source, output = folder / "resources.json", folder / "catalog.md"
            source.write_text(json.dumps({"schema_version": 1, "resources": [
                example_resource("Broken" + chr(0xD800) + "title")
            ]}), encoding="utf-8")
            output.write_bytes(b"existing generated content\n")
            code, stdout, stderr = run_cli(source, output)
            self.assertEqual(code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("cannot process catalog", stderr)
            self.assertEqual(output.read_bytes(), b"existing generated content\n")
            self.assertEqual(sorted(p.name for p in folder.iterdir()),
                             ["catalog.md", "resources.json"])

    def test_replacement_failure_keeps_original_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            source, output = folder / "resources.json", folder / "catalog.md"
            source.write_text(json.dumps({"schema_version": 1, "resources": [
                example_resource()
            ]}), encoding="utf-8")
            output.write_bytes(b"do not erase me")
            with patch.object(catalog.os, "replace", side_effect=OSError("simulated")):
                code, stdout, stderr = run_cli(source, output)
            self.assertEqual(code, 1)
            self.assertEqual(stdout, "")
            self.assertIn("simulated", stderr)
            self.assertEqual(output.read_bytes(), b"do not erase me")
            self.assertEqual(sorted(p.name for p in folder.iterdir()),
                             ["catalog.md", "resources.json"])

    def test_valid_unicode_output_and_mode_are_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            source, output = folder / "resources.json", folder / "catalog.md"
            source.write_text(json.dumps({"schema_version": 1, "resources": [
                example_resource("Bright 🚀 guide")
            ]}), encoding="utf-8")
            output.write_bytes(b"prior")
            output.chmod(0o640)
            # Windows chmod only toggles the read-only bit, so compare with what stuck.
            expected_mode = stat.S_IMODE(output.stat().st_mode)
            code, stdout, stderr = run_cli(source, output)
            self.assertEqual(code, 0, stderr)
            self.assertIn("Bright 🚀 guide", output.read_text("utf-8"))
            self.assertIn("1 resources", stdout)
            self.assertEqual(stderr, "")
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), expected_mode)

    def test_new_generated_file_is_written(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            source, output = folder / "resources.json", folder / "new.md"
            source.write_text(json.dumps({"schema_version": 1, "resources": [
                example_resource()
            ]}), encoding="utf-8")
            code, stdout, stderr = run_cli(source, output)
            self.assertEqual(code, 0, stderr)
            self.assertIn("# Curated resources", output.read_text("utf-8"))
            self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
