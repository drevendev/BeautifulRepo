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
        self.assertIn("not a hosted service", " ".join(top.split()))

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

