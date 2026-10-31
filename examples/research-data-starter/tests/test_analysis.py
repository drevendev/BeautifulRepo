"""Independent reproduction and invalid-input checks for the synthetic dataset."""
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXAMPLE = Path(__file__).resolve().parents[1]
SCRIPT = EXAMPLE / "analysis.py"
EXPECTED = json.loads((EXAMPLE / "expected-result.json").read_text(encoding="utf-8"))
SPEC = importlib.util.spec_from_file_location("research_data_example", SCRIPT)
assert SPEC and SPEC.loader
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


class ReproduceTests(unittest.TestCase):
    def test_fixture_integrity_matches_documented_sha256(self):
        expected = "126286146ce550b525a0a7d995507a8c8c9db8155471fed79a1f4243483089e8"
        raw = analysis.DEFAULT_INPUT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), expected)
        readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        self.assertIn(expected, readme)

    def test_documented_result(self):
        self.assertEqual(analysis.summarize(analysis.DEFAULT_INPUT), EXPECTED)

    def test_documented_cli_and_valid_json(self):
        proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True,
                              text=True, check=False, timeout=10)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), EXPECTED)
        self.assertEqual(proc.stderr, "")

    def _temporary(self, content):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "observations.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_row_order_does_not_affect_report(self):
        lines = analysis.DEFAULT_INPUT.read_text(encoding="utf-8").splitlines()
        reversed_path = self._temporary("\n".join([lines[0], *reversed(lines[1:])]) + "\n")
        self.assertEqual(analysis.summarize(reversed_path), analysis.summarize(analysis.DEFAULT_INPUT))

    def test_duplicate_key_rejected(self):
        csv = "date,site,count\n2026-01-01,A,1\n2026-01-01,A,2\n"
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            analysis.summarize(self._temporary(csv))

    def test_invalid_dates_rejected(self):
        for d in ("2026-02-30", "2026-2-03", "yesterday"):
            with self.subTest(d=d), self.assertRaises(ValueError):
                analysis.summarize(self._temporary(f"date,site,count\n{d},A,1\n"))

    def test_bad_count_rejected(self):
        for count in ("-1", "NaN", "1.5", ""):
            with self.subTest(count=count), self.assertRaises(ValueError):
                analysis.summarize(self._temporary(f"date,site,count\n2026-01-01,A,{count}\n"))

    def test_non_ascii_numeric_tokens_rejected(self):
        # Python's \d and int() accept some Unicode digits, but the documented
        # CSV contract intentionally uses plain ASCII decimal digits.
        for date_text, count_text in (
            ("2026-01-01", "٣"),
            ("2026-01-01", "３"),
            ("２０２６-０１-０１", "3"),
        ):
            with self.subTest(date=date_text, count=count_text):
                record = f"date,site,count\n{date_text},A,{count_text}\n"
                with self.assertRaises(ValueError):
                    analysis.summarize(self._temporary(record))

    def test_bad_schema_and_extra_columns_rejected(self):
        for data in ("count,site,date\n1,A,2026-01-01\n",
                     "date,site,count\n2026-01-01,A,1,EXTRA\n",
                     "date,site,count\n2026-01-01,A\n"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                analysis.summarize(self._temporary(data))

    def test_empty_data_rejected(self):
        with self.assertRaisesRegex(ValueError, "No data"):
            analysis.summarize(self._temporary("date,site,count\n"))

    def test_error_cli_does_not_print_csv_contents(self):
        path = self._temporary("date,site,count\n2026-01-01,SENSITIVE_PLACEHOLDER,wrong\n")
        proc = subprocess.run([sys.executable, str(SCRIPT), "--input", str(path)],
                              capture_output=True, text=True, check=False, timeout=10)
        self.assertEqual(proc.returncode, 1)
        self.assertNotIn("SENSITIVE_PLACEHOLDER", proc.stderr)
        self.assertNotIn("SENSITIVE_PLACEHOLDER", proc.stdout)


if __name__ == "__main__":
    unittest.main()
