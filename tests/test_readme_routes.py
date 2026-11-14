"""Regression checks for evidence-first README routes and truthful commands."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
PROOF = (ROOT / "guides/working-proof.md").read_text(encoding="utf-8")


def first_screen() -> str:
    """The quickstart alone, not the entire homepage after its heading."""
    return README.split("## Working proof\n", 1)[1].split(
        "\n## The visitor journey", 1
    )[0]


class ReaderRoutesTests(unittest.TestCase):
    def test_three_clear_first_routes_without_layout_table(self):
        section = README.split("## Start here\n", 1)[1].split(
            "\n## Working proof", 1
        )[0]
        items = [line for line in section.splitlines() if line.startswith("- **")]
        self.assertEqual(3, len(items), "first-step chooser should remain three options")
        self.assertFalse(any(line.startswith("|") for line in section.splitlines()),
                         "first-step chooser is navigation, not comparison data")
        for destination in (
            "guides/repository-audit.md",
            "checklists/repository.md",
            "templates/README.template.md",
            "checklists/first-success.md",
            "examples/README.md",
        ):
            with self.subTest(destination=destination):
                self.assertIn(f"]({destination})", section)
        for outcome in ("not a beauty score", "reproducible command",
                        "documented limitations"):
            self.assertIn(outcome, section)

    def test_proof_names_actual_checkout_command_and_output(self):
        quickstart = first_screen()
        self.assertIn("Python 3.11+", quickstart)
        self.assertIn("guides/working-proof.md", quickstart)
        self.assertIn(
            "python -I tools/audit_bundle.py ../your-repository --fail-on never",
            quickstart,
        )
        self.assertIn(
            "python examples/cli-starter/rowcount.py "
            "examples/cli-starter/sample.csv", PROOF
        )
        self.assertIn("Data rows: 3", PROOF)
        self.assertIn("From the repository root:", PROOF)
        self.assertIn("not a schema validator or a hosted service",
                      " ".join(PROOF.split()))

    def test_first_screen_leads_with_the_real_audit_and_discloses_limits(self):
        quickstart = first_screen()
        flat = " ".join(quickstart.split())
        self.assertIn(
            "python -I tools/audit_bundle.py ../your-repository --fail-on never",
            quickstart,
        )
        self.assertIn("broken local destinations even with `--fail-on never`", flat)
        self.assertIn("invalid input or incomplete evidence", flat)
        self.assertIn("guides/adopting-the-checks.md", quickstart)
        self.assertIn("fictional", quickstart)
        self.assertIn("guides/working-proof.md", quickstart)
        self.assertNotIn("python examples/cli-starter/rowcount.py", quickstart)

        # The companion retains actual commands, caveats and reader destinations.
        self.assertLess(
            PROOF.index("python -I tools/audit_bundle.py ../your-repository --fail-on never"),
            PROOF.index("python examples/cli-starter/rowcount.py"),
        )
        for claim in (
            "To audit BeautifulRepo itself instead",
            "python examples/repository-audit/demo.py",
            "python -I examples/combined-audit/demo.py",
            "broken local links still produce exit **1**",
            "not a beauty score",
            "invalid root or incomplete evidence",
        ):
            with self.subTest(claim=claim):
                self.assertIn(claim, " ".join(PROOF.split()))
        for destination in ("../SHOWCASE.md", "../case-studies/patchpitch.md",
                            "../examples/combined-audit/README.md"):
            self.assertIn(f"]({destination})", PROOF)

    def test_first_screen_before_after_numbers_match_real_demo(self):
        import json
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-I", str(ROOT / "examples/repository-audit/demo.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=30, check=True,
        )
        reports = json.loads(result.stdout)
        self.assertIn("guides/working-proof.md", first_screen())
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
                self.assertIn(expected_line, PROOF)

    def test_demo_text_mode_exposes_observed_rules_without_a_score(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-I", str(ROOT / "examples/repository-audit/demo.py"),
             "--format", "text"],
            cwd=ROOT, capture_output=True, text=True, timeout=30, check=True,
        )
        output = result.stdout
        self.assertIn("Synthetic README before/after", output)
        self.assertIn("BEFORE: 0 error(s), 4 warning(s), 1 info", output)
        self.assertIn("AFTER: 0 error(s), 1 warning(s), 1 info", output)
        self.assertIn("README.md:", output)
        for rule in (
            "readme.placeholder", "heading.skipped_level", "license.missing",
            "contributing.missing",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, output)
        self.assertIn("Not reported after the fictional edit:", output)
        self.assertIn("Still reported: contributing.missing, license.missing", output)
        self.assertIn("do not prove readability", output)
        self.assertNotIn("\x1b", output)  # easily capturable plain text

    def test_real_repository_audit_proof_is_pinned_and_candid(self):
        """The shorter homepage must still lead to exact real-repo evidence."""
        case = (ROOT / "case-studies/patchpitch.md").read_text(encoding="utf-8")
        top = PROOF
        quickstart = first_screen()
        self.assertIn("guides/working-proof.md", quickstart)
        self.assertIn("case-studies/patchpitch.md", quickstart)
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

