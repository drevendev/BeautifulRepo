"""Review dates in the guides and catalog warn when due, and fail only scheduled runs."""
from __future__ import annotations

import copy
from datetime import date
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/review_dates.py"
SPEC = importlib.util.spec_from_file_location("review_dates_under_test", TOOL)
review_dates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review_dates)
sys.path.insert(0, str(ROOT / "tools"))
import catalog  # noqa: E402


class ReviewDateTests(unittest.TestCase):
    def repo(self, files: dict[str, str]) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        for name, body in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(body, encoding="utf-8")
        return root

    def run_tool(self, root: Path, *args: str):
        return subprocess.run([sys.executable, "-I", str(TOOL), "--root", str(root), *args],
                              capture_output=True, text=True, check=False)

    def test_finds_every_spelling_used_in_the_handbook(self):
        root = self.repo({"guides/a.md": "Reviewed **2026-10-22**:\n\nAs reviewed 2026-10-20, x.\n"
                                         "Both reviewed\n2026-10-23; recheck later.\n",
                          "guides/programs.md": "**Checked: 2026-10-03.** Rules change.\n",
                          "guides/b.md": "Sources rechecked 2026-10-05.\n# v7.0.1 inspected 2026-10-05\n"})
        found = [(path, line, raw) for path, line, _, raw in review_dates.find_review_dates(root)]
        self.assertEqual([("guides/a.md", 1, "2026-10-22"), ("guides/a.md", 3, "2026-10-20"),
                          ("guides/a.md", 5, "2026-10-23"), ("guides/b.md", 1, "2026-10-05"),
                          ("guides/programs.md", 1, "2026-10-03")], found)

    def test_examples_in_code_are_not_reviews(self):
        root = self.repo({"guides/a.md": "Write `Reviewed **2026-01-01**` like this.\n\n"
                                         "```text\nChecked: 2026-01-02\n```\n\nReviewed 2026-10-20\n"})
        found = [(line, raw) for _, line, _, raw in review_dates.find_review_dates(root)]
        self.assertEqual([(7, "2026-10-20")], found)

    def test_gfm_fences_with_longer_closers_and_unclosed_blocks(self):
        source = "\n".join((
            "```text",
            "Reviewed 1999-01-01",
            "````",
            "Reviewed 2026-10-26",
            "~~~~ markdown",
            "Checked: 1999-01-02",
            "~~~~~",
            "Checked: 2026-10-25",
            "`````",
            "Reviewed 1999-01-03",
            "```",  # too short to close the five-backtick fence
            "Reviewed 1999-01-04",
            "``````",
            "Reviewed 2026-10-24",
        )) + "\n"
        root = self.repo({"guides/a.md": source})
        found = [(line, raw) for _, line, _, raw in review_dates.find_review_dates(root)]
        self.assertEqual([(4, "2026-10-26"), (8, "2026-10-25"),
                          (14, "2026-10-24")], found)
        unfinished = self.repo({"guides/a.md": "Reviewed 2026-10-22\n~~~\n"
                                                "Checked: 1999-01-05\n"})
        self.assertEqual(["2026-10-22"],
                         [raw for _, _, _, raw in review_dates.find_review_dates(unfinished)])

    def test_html_comments_do_not_count_as_source_reviews(self):
        source = ("<!-- Reviewed 1999-01-01 --> Reviewed 2026-10-27\n"
                  "<!--\n"
                  "Checked: 1999-01-02 and ` unmatched\n"
                  "--> Checked: 2026-10-26\n"
                  "`<!--` Reviewed 2026-10-25\n"
                  "``<!-- Reviewed 1999-01-03 -->`` Reviewed 2026-10-24\n"
                  "<!-- Reviewed 1999-01-04\n"
                  "Checked: 1999-01-05\n")
        root = self.repo({"guides/a.md": source})
        found = [(line, raw) for _, line, _, raw in review_dates.find_review_dates(root)]
        self.assertEqual([(1, "2026-10-27"), (4, "2026-10-26"),
                          (5, "2026-10-25"), (6, "2026-10-24")], found)

    def test_unmatched_backtick_width_does_not_hide_real_review_date(self):
        source = ("` Reviewed 2026-10-21 ``\n"
                  "`` Reviewed 1999-01-01 ` still code `` Reviewed 2026-10-20\n")
        root = self.repo({"guides/a.md": source})
        found = [(line, raw) for _, line, _, raw in review_dates.find_review_dates(root)]
        self.assertEqual([(1, "2026-10-21"), (2, "2026-10-20")], found)

    def test_thresholds_programs_30_days_everything_else_180(self):
        root = self.repo({"guides/programs.md": "Checked: 2026-10-03\n",
                          "guides/a.md": "Reviewed **2026-10-03**\n"})
        found = review_dates.find_review_dates(root)
        self.assertEqual(([], []), review_dates.check(found, date(2026, 11, 2)))
        _, warnings = review_dates.check(found, date(2026, 11, 3))
        self.assertEqual(1, len(warnings))
        self.assertIn("guides/programs.md:1", warnings[0])
        _, warnings = review_dates.check(found, date(2027, 4, 2))
        self.assertEqual(2, len(warnings))

    def test_future_and_impossible_dates_are_errors(self):
        root = self.repo({"guides/a.md": "Reviewed 2026-02-30\n\nReviewed 2099-01-01\n"})
        errors, _ = review_dates.check(review_dates.find_review_dates(root), date(2026, 10, 23))
        self.assertEqual(2, len(errors))

    def test_warnings_fail_only_with_the_scheduled_flag(self):
        root = self.repo({"guides/a.md": "Reviewed **2026-01-01**\n"})
        plain = self.run_tool(root, "--today", "2026-10-23")
        self.assertEqual(0, plain.returncode, plain.stderr)
        self.assertIn("WARN: guides/a.md:1", plain.stderr)
        strict = self.run_tool(root, "--today", "2026-10-23", "--fail-on-warning")
        self.assertEqual(1, strict.returncode)

    def test_beautifulrepo_dates_are_parseable_and_not_in_the_future(self):
        found = review_dates.find_review_dates(ROOT)
        self.assertGreaterEqual(len(found), 15)
        errors, _ = review_dates.check(found, date.today())
        self.assertEqual([], errors)

    def test_scheduled_workflow_fails_on_due_dates_but_pull_requests_do_not(self):
        scheduled = (ROOT / ".github/workflows/pins.yml").read_text(encoding="utf-8")
        pull_requests = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tools/catalog.py --fail-on-warning", scheduled)
        self.assertIn("run: python tools/review_dates.py --fail-on-warning", scheduled)
        self.assertNotIn("--fail-on-warning", pull_requests)


class CatalogFailOnWarningTests(unittest.TestCase):
    def test_stale_catalog_fails_only_with_the_flag(self):
        source = json.loads((ROOT / "catalog/resources.json").read_text(encoding="utf-8"))
        data = copy.deepcopy(source)
        for item in data["resources"]:
            item["reviewed_on"] = "2020-01-01"
        with tempfile.TemporaryDirectory() as folder:
            path, view = Path(folder) / "resources.json", Path(folder) / "README.md"
            path.write_text(json.dumps(data), encoding="utf-8")
            args = ["--data", str(path), "--output", str(view)]
            self.assertEqual(0, catalog.main(args + ["--write"]))
            self.assertEqual(0, catalog.main(args))
            self.assertEqual(1, catalog.main(args + ["--fail-on-warning"]))


if __name__ == "__main__":
    unittest.main()
