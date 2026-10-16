"""Root-suite checks for the documented synthetic-data workflow and reader routes."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "research-data-starter"
GUIDE = ROOT / "guides" / "research-data-repositories.md"
TEMPLATE = ROOT / "templates" / "RESEARCH_DATA_README.template.md"
EXPECTED = {"grand_total": 60, "rows": 6, "totals": {"A": 36, "B": 24}}


class ResearchDataIntegrationTests(unittest.TestCase):
    def test_first_success_from_documented_directory(self):
        result = subprocess.run(
            [sys.executable, "analysis.py"], cwd=EXAMPLE, capture_output=True,
            text=True, check=False, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), EXPECTED)
        self.assertEqual(result.stderr, "")

    def test_nested_regressions_are_runnable(self):
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s",
             str(EXAMPLE / "tests"), "-v"],
            cwd=ROOT, capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("test_documented_result", result.stderr)
        self.assertIn("test_error_cli_does_not_print_csv_contents", result.stderr)
        self.assertIn("OK", result.stderr)
        # Do not hard-code the nested test count: the suite may legitimately grow.

    def test_reader_documentation_and_paths(self):
        example = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        guide = GUIDE.read_text(encoding="utf-8")
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("fully fabricated", example)
        self.assertIn("not scientific observations", example)
        self.assertIn("python analysis.py", example)
        self.assertIn("python -m unittest discover -s tests -v", example)
        self.assertIn("data/observations.csv", example)
        self.assertIn("Data status", guide)
        self.assertIn("code license", guide)
        self.assertIn("data license", guide.lower())
        self.assertIn("Do not add fictional DOI", template)
        self.assertTrue((EXAMPLE / "data" / "observations.csv").is_file())
        self.assertTrue((EXAMPLE / "analysis.py").is_file())

    def test_root_routes_are_discoverable(self):
        readme_file = ROOT / "README.md"
        roadmap_file = ROOT / "ROADMAP.md"
        self.assertTrue(readme_file.is_file(), "root README is required in a repo checkout")
        self.assertTrue(roadmap_file.is_file(), "root ROADMAP is required in a repo checkout")
        readme = readme_file.read_text(encoding="utf-8")
        roadmap = roadmap_file.read_text(encoding="utf-8")
        for route in (
            "(guides/research-data-repositories.md)",
            "(examples/research-data-starter/README.md)",
            "(templates/RESEARCH_DATA_README.template.md)",
        ):
            self.assertIn(route, readme)
        self.assertIn("research/data", roadmap.lower())
        self.assertIn("synthetic", roadmap.lower())
        for existing_reader_route in ("guides/cli-repositories.md",
                                      "guides/library-repositories.md",
                                      "guides/repository-audit.md",
                                      "guides/release-notes.md"):
            self.assertIn(existing_reader_route, readme)

    def test_analysis_is_repeatable_and_preserves_input(self):
        fixture = EXAMPLE / "data" / "observations.csv"
        before = fixture.read_bytes()
        outputs = []
        for _ in range(2):
            result = subprocess.run(
                [sys.executable, str(EXAMPLE / "analysis.py")],
                cwd=ROOT, capture_output=True, text=True, check=False, timeout=15,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertEqual(json.loads(result.stdout), EXPECTED)
            outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(fixture.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
