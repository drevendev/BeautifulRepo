"""Regression-test nested unittest discovery with real temporary test suites."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_library_starter import assert_nested_suite_passed


class NestedDiscoveryTests(unittest.TestCase):
    def run_suite(self, source: str | None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            if source is not None:
                (Path(directory) / "test_example.py").write_text(source, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", directory, "-v"],
                cwd=directory, capture_output=True, text=True, check=False, timeout=15,
            )

    def test_successful_suite_can_grow(self):
        for count in (1, 3, 4):
            with self.subTest(count=count):
                source = "import unittest\nclass ExampleTests(unittest.TestCase):\n"
                source += "".join(
                    f"    def test_case_{number}(self):\n        self.assertTrue(True)\n"
                    for number in range(count)
                )
                completed = self.run_suite(source)
                assert_nested_suite_passed(self, completed)
                self.assertIn(f"Ran {count} test", completed.stderr)

    def test_empty_discovery_is_rejected(self):
        completed = self.run_suite(None)
        self.assertIn("Ran 0 tests", completed.stderr)
        # Python versions may report empty discovery with zero or nonzero status.
        # Our acceptance rule rejects it in either case.
        with self.assertRaises(AssertionError):
            assert_nested_suite_passed(self, completed)

    def test_failed_test_is_rejected(self):
        source = (
            "import unittest\nclass ExampleTests(unittest.TestCase):\n"
            "    def test_failure(self):\n        self.fail('intentional regression fixture')\n"
        )
        completed = self.run_suite(source)
        self.assertNotEqual(completed.returncode, 0)
        with self.assertRaises(AssertionError):
            assert_nested_suite_passed(self, completed)

    def test_import_failure_is_rejected(self):
        completed = self.run_suite("raise RuntimeError('intentional broken module')\n")
        self.assertNotEqual(completed.returncode, 0)
        with self.assertRaises(AssertionError):
            assert_nested_suite_passed(self, completed)

    def test_incomplete_summary_is_rejected(self):
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="OK\n")
        with self.assertRaisesRegex(AssertionError, "Missing unittest execution summary"):
            assert_nested_suite_passed(self, completed)


if __name__ == "__main__":
    unittest.main()
