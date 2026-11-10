"""Structural acceptance for the optional asset provenance record checker."""
from __future__ import annotations

from datetime import date
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "asset_records.py"
spec = importlib.util.spec_from_file_location("asset_records", MODULE)
asset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(asset)


def record(decision="APPROVED — reviewer checked the evidence", date_value="2026-11-10 / Test Reviewer"):
    fields = {
        "Used at": "README.md (illustrative)",
        "What it depicts/contains": "Example illustration",
        "Creator/rightsholder": "Fictional author (synthetic fixture)",
        "Original source": "synthetic fixture, not a real license grant",
        "Source revision/acquired on": "2026-11-09",
        "Rights basis": "synthetic owned asset in this test only",
        "Allowed use checked": "synthetic permitted use for fixture",
        "Changes made": "none",
        "Required credit/notice": "synthetic fixture-only credit",
        "Text equivalent": "illustrated steps; text summary is here",
        "Decision": decision,
        "Reviewed on / by": date_value,
        "Recheck when": "any source or distribution changes",
    }
    return "# Fixture record (not real permission)\n\n## assets/example.svg\n" + "\n".join(
        f"- **{field}:** {fields[field]}" for field in asset.FIELDS
    ) + "\n"


class AssetRecordsTest(unittest.TestCase):
    def test_complete_record_is_structurally_valid_but_not_legal_verification(self):
        result = asset.validate(record(), today=date(2026, 11, 10))
        self.assertEqual(result["decisions"], {"approved": 1, "pending": 0, "removed": 0})
        self.assertIn("no asset source", result["notice"])

    def test_pending_is_bounded_publication_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "records.md")
            path.write_text(record("PENDING — verify permissions"), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(MODULE), str(path), "--format", "json"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertIn('"has_pending_decisions": true', proc.stdout)
            self.assertNotIn("Fictional author", proc.stdout)

    def test_template_placeholder_is_rejected(self):
        with self.assertRaisesRegex(asset.RecordError, "template value"):
            asset.validate(record().replace("README.md (illustrative)", "REPOSITORY_PATHS_AND_EMBEDS"), today=date(2026, 11, 10))

    def test_missing_and_duplicate_fields_are_rejected(self):
        value = record()
        with self.assertRaisesRegex(asset.RecordError, "missing field"):
            asset.validate(value.replace("- **Used at:** README.md (illustrative)\n", ""), today=date(2026, 11, 10))
        with self.assertRaisesRegex(asset.RecordError, "repeated field"):
            asset.validate(value + "- **Used at:** elsewhere\n", today=date(2026, 11, 10))

    def test_future_date_and_unknown_approved_rights_are_rejected(self):
        with self.assertRaisesRegex(asset.RecordError, "future"):
            asset.validate(record(date_value="2030-01-01 / Test Reviewer"), today=date(2026, 11, 10))
        with self.assertRaisesRegex(asset.RecordError, "unresolved"):
            asset.validate(record().replace("synthetic owned asset in this test only", "unverified"), today=date(2026, 11, 10))

    def test_duplicate_assets_and_nonordinary_file_are_rejected(self):
        with self.assertRaisesRegex(asset.RecordError, "duplicate asset section"):
            asset.validate(record() + record(), today=date(2026, 11, 10))
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory, "original.md")
            alias = Path(directory, "alias.md")
            original.write_text(record(), encoding="utf-8")
            try:
                alias.symlink_to(original)
            except (NotImplementedError, OSError):
                self.skipTest("test platform cannot create file symlinks")
            with self.assertRaises(asset.RecordError):
                asset.read_text(alias)

    def test_oversized_and_non_utf8_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "large.md")
            path.write_bytes(b"a" * (asset.MAX_BYTES + 1))
            with self.assertRaises(asset.RecordError):
                asset.read_text(path)
            path.write_bytes(b"\xff")
            with self.assertRaises(asset.RecordError):
                asset.read_text(path)


if __name__ == "__main__":
    unittest.main()
