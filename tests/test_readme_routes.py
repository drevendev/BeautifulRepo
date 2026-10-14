"""Regression: README reader routes preserve a well-formed visitor journey."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReaderRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_start_here_rows_are_three_columns(self):
        section = self.readme.split("## Start here\n", 1)[1].split(
            "\n## The visitor journey", 1
        )[0]
        rows = [line for line in section.splitlines() if line.startswith("|")]
        self.assertGreaterEqual(len(rows), 7)
        for line in rows:
            with self.subTest(row=line):
                self.assertEqual(line.count("|"), 4)

    def test_first_repo_route_is_scaffold_not_release_notes(self):
        self.assertIn(
            "| starting a repository from scratch | "
            "[README scaffold](templates/README.template.md) |",
            self.readme,
        )
        self.assertIn(
            "| writing upgrade announcements | "
            "[Release-note writing guide](guides/release-notes.md)",
            self.readme,
        )

    def test_handbook_indexes_cli_and_release_notes(self):
        handbook = self.readme.split("## Explore the handbook\n", 1)[1].split(
            "\n## Principles", 1
        )[0]
        self.assertIn("[CLI repository starter](guides/cli-repositories.md)", handbook)
        self.assertIn("[Release-note writing guide](guides/release-notes.md)", handbook)
        self.assertIn("[release-note template](templates/RELEASE_NOTES.template.md)", handbook)


if __name__ == "__main__":
    unittest.main()
