"""Regression checks for evidence-first README routes and truthful commands."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")


class ReaderRoutesTests(unittest.TestCase):
    def test_three_clear_first_routes_without_directory_table(self):
        section = README.split("## Start here\n", 1)[1].split(
            "\n## The visitor journey", 1
        )[0]
        rows = [line for line in section.splitlines() if line.startswith("|")]
        self.assertEqual(len(rows), 5)  # header, separator, three destinations
        for row in rows:
            with self.subTest(row=row):
                self.assertEqual(row.count("|"), 4)
        self.assertIn("guides/repository-audit.md", section)
        self.assertIn("templates/README.template.md", section)
        self.assertIn("examples/README.md", section)

    def test_proof_names_actual_checkout_command_and_output(self):
        top = README.split("## Working proof\n", 1)[1].split(
            "\n## Start here", 1
        )[0]
        self.assertIn("Python 3.11+", top)
        self.assertIn(
            "python examples/cli-starter/rowcount.py "
            "examples/cli-starter/sample.csv", top
        )
        self.assertIn("Data rows: 3", top)
        self.assertIn("from the repository root", top)
        self.assertIn("not a schema validator or a hosted service", " ".join(top.split()))

    def test_first_screen_leads_with_the_real_audit_and_discloses_limits(self):
        section = README.split("## Working proof\n", 1)[1].split(
            "\n## Start here", 1
        )[0]
        self.assertLess(section.index("python -I tools/repo_audit.py ."),
                        section.index("python examples/cli-starter/rowcount.py"))
        self.assertIn("python examples/repository-audit/demo.py", section)
        self.assertIn("python -I tools/repo_audit.py ../your-repository --fail-on never",
                      section)
        self.assertIn("guides/adopting-the-checks.md", section)
        self.assertIn("not a beauty score", section)
        self.assertIn("invalid paths or", section)
        self.assertIn("fictional", section)

    def test_first_screen_before_after_numbers_match_real_demo(self):
        import json
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-I", str(ROOT / "examples/repository-audit/demo.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=30, check=True,
        )
        reports = json.loads(result.stdout)
        section = README.split("## Working proof\n", 1)[1].split(
            "\n## Start here", 1
        )[0]
        for label, counts in (
            ("before", (0, 4, 1)),
            ("after", (0, 1, 1)),
        ):
            with self.subTest(label=label):
                summary = reports[label]["summary"]
                self.assertEqual(
                    (summary["error"], summary["warning"], summary["info"]), counts
                )
                expected_line = (
                    "before: 0 errors, 4 warnings, 1 informational finding"
                    if label == "before"
                    else "after:  0 errors, 1 warning,  1 informational finding"
                )
                self.assertIn(expected_line, section)

    def test_real_repository_audit_proof_is_pinned_and_candid(self):
        """Do not silently detach homepage evidence from the original case."""
        case = (ROOT / "case-studies/patchpitch.md").read_text(encoding="utf-8")
        top = README.split("## Working proof\\n", 1)[1].split(
            "\\n## Start here", 1
        )[0]
        self.assertIn("Recorded result on a real repository", top)
        for revision in (
            "1424fc8fbfef82a5cd473272843e0c5cdc097b36",
            "43284a7286ead07d37ff32b8206ac4000856fd04",
            "4f06f26ccef6e8b28d77c71633482b7a1a68518a",
        ):
            with self.subTest(revision=revision):
                self.assertIn(revision, top)
                self.assertIn(revision, case)
        top_flat = " ".join(top.split())
        case_flat = " ".join(case.split())
        for finding in (
            "0 errors, 0 warnings, 1 informational finding",
            "0 errors, 0 warnings, 0 informational findings",
            "contributing.missing",
        ):
            with self.subTest(finding=finding):
                self.assertIn(finding, top_flat)
                self.assertIn(finding, case_flat)
        self.assertIn("not a fresh run", top)
        self.assertIn("did **not** detect", top)
        self.assertIn("unresolved text-contrast concerns", top)

    def test_detailed_handbook_remains_complete_but_not_duplicate_table(self):
        section = README.split("## Explore the handbook\n", 1)[1].split(
            "\n## Principles", 1
        )[0]
        self.assertNotIn("| ---", section)
        for route in (
            "guides/cli-repositories.md",
            "guides/library-repositories.md",
            "guides/application-repositories.md",
            "guides/research-data-repositories.md",
            "guides/curated-collections.md",
            "guides/release-notes.md",
            "templates/RELEASE_NOTES.template.md",
            "guides/editorial-evidence.md",
            "guides/discoverability.md",
        ):
            with self.subTest(route=route):
                self.assertIn(f"({route})", section)

    def test_fictional_visual_example_is_not_presented_as_real_cli(self):
        section = README.split("## See the difference\n", 1)[1].split(
            "\n## This repository checks itself", 1
        )[0]
        self.assertIn("fictional", section)
        self.assertIn("examples/readme-visuals/DESIGN_INTENT.md", section)


if __name__ == "__main__":
    unittest.main()

