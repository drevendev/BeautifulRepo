"""CI integration for the checkout-only library starter and its documented API."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "library-starter"


def assert_nested_suite_passed(
    test_case: unittest.TestCase, completed: subprocess.CompletedProcess[str],
) -> None:
    """Require successful, nonempty discovery without freezing the suite size."""
    test_case.assertEqual(completed.returncode, 0, completed.stderr)
    summary = re.search(r"^Ran ([0-9]+) tests? in ", completed.stderr, re.MULTILINE)
    test_case.assertIsNotNone(summary, "Missing unittest execution summary")
    if summary is not None:
        test_case.assertGreater(int(summary.group(1)), 0, "No nested tests were discovered")
    test_case.assertIn("OK", completed.stderr)


class LibraryStarterIntegrationTests(unittest.TestCase):
    def test_documented_first_call(self):
        completed = subprocess.run(
            [
                sys.executable,
                "demo.py",
            ],
            cwd=EXAMPLE,
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "hello-library-101\n")
        self.assertEqual(completed.stderr, "")

    def test_readme_import_agrees_with_demo(self):
        readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        self.assertIn("from slugline import slugline", readme)
        self.assertIn("python demo.py", readme)
        self.assertIn("**Verified runtime:**", readme)
        self.assertNotIn("Python 3.11+", readme)

    def test_nested_api_suite_is_part_of_default_ci(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(EXAMPLE / "tests"),
                "-v",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
        assert_nested_suite_passed(self, completed)

    def test_library_routes_and_roadmap_are_discoverable(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        for route in (
            "(guides/library-repositories.md)",
            "(examples/library-starter/README.md)",
            "(templates/LIBRARY_README.template.md)",
        ):
            self.assertIn(route, readme)
        self.assertIn("checkout-only example", roadmap)
        self.assertIn("no package is published", roadmap)
        self.assertNotIn("starter kits for libraries", roadmap)

    def test_guide_does_not_advertise_unreleased_install(self):
        guide = (ROOT / "guides" / "library-repositories.md").read_text(
            encoding="utf-8"
        )
        example = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        self.assertIn("not a published distribution", guide)
        self.assertIn("not published on PyPI", example)
        self.assertIn("hello-library-101", example)


if __name__ == "__main__":
    unittest.main()
