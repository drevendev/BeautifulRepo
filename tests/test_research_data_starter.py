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
EXPECTED_FILE = EXAMPLE / "expected-result.json"
EXPECTED = json.loads(EXPECTED_FILE.read_text(encoding="utf-8"))
RESULT_START = "<!-- beautifulrepo:research-result:start -->"
RESULT_END = "<!-- beautifulrepo:research-result:end -->"
GUIDE_LOCATION = "guides/research-data-repositories.md"


def _unique_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"{GUIDE_LOCATION}: duplicate JSON key {key!r}")
        result[key] = value
    return result


def _registered_guide_result(markdown: str) -> dict:
    """Read only the explicitly registered JSON result; never execute Markdown."""
    if markdown.count(RESULT_START) != 1 or markdown.count(RESULT_END) != 1:
        raise ValueError(f"{GUIDE_LOCATION}: expected one registered JSON result")
    start = markdown.index(RESULT_START) + len(RESULT_START)
    end = markdown.index(RESULT_END)
    if end <= start:
        raise ValueError(f"{GUIDE_LOCATION}: result markers are reversed")
    block = markdown[start:end].strip()
    if not (block.startswith("```json\n") and block.endswith("\n```")):
        raise ValueError(f"{GUIDE_LOCATION}: expected a single fenced JSON result")
    payload = block[len("```json\n"):-len("\n```")]
    try:
        parsed = json.loads(payload, object_pairs_hook=_unique_json_keys)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{GUIDE_LOCATION}: invalid registered JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{GUIDE_LOCATION}: JSON result must be an object")
    return parsed


def _assert_registered_result_matches_fixture(markdown: str) -> None:
    if _registered_guide_result(markdown) != EXPECTED:
        raise AssertionError(
            f"{GUIDE_LOCATION}: documented result differs from {EXPECTED_FILE.relative_to(ROOT)}"
        )




class ResearchDataIntegrationTests(unittest.TestCase):
    def test_first_success_from_documented_directory(self):
        result = subprocess.run(
            [sys.executable, "analysis.py"], cwd=EXAMPLE, capture_output=True,
            text=True, check=False, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), EXPECTED)
        self.assertEqual(result.stderr, "")

    def test_registered_guide_result_matches_shared_fixture(self):
        _assert_registered_result_matches_fixture(GUIDE.read_text(encoding="utf-8"))

    def test_reordered_json_keys_remain_valid(self):
        guide = GUIDE.read_text(encoding="utf-8")
        reordered = {"totals": {"B": 24, "A": 36}, "rows": 6, "grand_total": 60}
        original = "```json\n" + json.dumps(EXPECTED, indent=2) + "\n```"
        alternate = "```json\n" + json.dumps(reordered, indent=2) + "\n```"
        self.assertIn(original, guide)
        _assert_registered_result_matches_fixture(guide.replace(original, alternate, 1))

    def test_edited_documented_total_reports_guide_path(self):
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertIn('"grand_total": 60', guide)
        altered = guide.replace('"grand_total": 60', '"grand_total": 61', 1)
        with self.assertRaisesRegex(AssertionError, GUIDE_LOCATION):
            _assert_registered_result_matches_fixture(altered)

    def test_missing_malformed_and_duplicate_registered_json_fail(self):
        guide = GUIDE.read_text(encoding="utf-8")
        candidates = (
            guide.replace(RESULT_START, "", 1),
            guide.replace(RESULT_END, "", 1),
            guide.replace("```json", "```bash", 1),
            guide.replace('"rows": 6', '"rows":', 1),
            guide.replace('"rows": 6', '"rows": 6, "rows": 6', 1),
        )
        for altered in candidates:
            with self.subTest(case=altered[:48]):
                with self.assertRaisesRegex(ValueError, GUIDE_LOCATION):
                    _registered_guide_result(altered)

    def test_unregistered_markdown_commands_are_never_executed(self):
        guide = GUIDE.read_text(encoding="utf-8")
        extra = "\n```bash\npython does-not-exist.py\n```\n"
        _assert_registered_result_matches_fixture(guide + extra)

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
