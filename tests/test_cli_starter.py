"""Black-box checks for the documented, dependency-free CLI example."""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "cli-starter" / "rowcount.py"
SAMPLE = ROOT / "examples" / "cli-starter" / "sample.csv"
README = ROOT / "examples" / "cli-starter" / "README.md"


class CLIStarterTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    def test_documented_sample_output(self):
        result = self.run_cli(str(SAMPLE))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Data rows: 3\n")
        self.assertEqual(result.stderr, "")

    def test_readme_quickstart_matches_actual_cli_output(self):
        """Verify the actual README fence, not a duplicate expected-output constant."""
        readme = README.read_text(encoding="utf-8")
        heading = "## Try it in a checkout\n"
        self.assertEqual(readme.count(heading), 1)
        section = readme.split(heading, 1)[1].split("\n## ", 1)[0]
        commands = re.findall(r"(?ms)^```bash\n(.*?)\n```$", section)
        outputs = re.findall(r"(?ms)^```text\n(.*?)\n```$", section)

        # Never execute arbitrary Markdown shell snippets. Pin the reviewed argv.
        self.assertEqual(
            commands,
            ["python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv"],
        )
        self.assertEqual(len(outputs), 1)
        self.assertTrue(outputs[0])
        result = self.run_cli(str(SAMPLE))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, outputs[0] + "\n")
        self.assertEqual(result.stderr, "")

    def test_help_exit_code(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("csv_file", result.stdout)

    def test_missing_argument_is_usage_error(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr)

    def test_missing_file_does_not_show_traceback(self):
        result = self.run_cli(str(ROOT / "no-such-file.csv"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("rowcount:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_file_error_does_not_expose_absolute_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private-location" / "missing.csv"
            result = self.run_cli(str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read CSV", result.stderr)
        self.assertNotIn(str(path), result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_utf8_is_a_data_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            path.write_bytes(b"name\n\xff\n")
            result = self.run_cli(str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("rowcount:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_header_is_a_data_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.csv"
            path.write_text("", encoding="utf-8")
            result = self.run_cli(str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing a CSV header", result.stderr)

    def test_ragged_records_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ragged.csv"
            path.write_text("a,b\n1\n", encoding="utf-8")
            result = self.run_cli(str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected 2 columns, got 1", result.stderr)

    def test_quoted_newline_counts_as_one_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multiline.csv"
            path.write_text('a,b\n"one\ntwo",3\n\n4,5\n', encoding="utf-8")
            result = self.run_cli(str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Data rows: 2\n")


if __name__ == "__main__":
    unittest.main()
