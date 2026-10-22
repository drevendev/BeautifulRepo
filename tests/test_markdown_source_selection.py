"""Which Markdown sources the link checkers scan in someone else's repository."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_links  # noqa: E402
import html_navigation  # noqa: E402

BROKEN = "[Missing](does-not-exist.md)\n"


class MarkdownSourceSelectionTests(unittest.TestCase):
    def make_repo(self, files: dict[str, str]) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        for relative, body in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        return root

    def scanned(self, root: Path, *exclude: str) -> list[str]:
        return [path.relative_to(root).as_posix()
                for path in docs_links.iter_markdown_files(root, exclude)]

    def test_installed_dependencies_are_never_scanned(self):
        root = self.make_repo({
            "README.md": "# Project\n",
            "node_modules/pkg/README.md": BROKEN,
            "web/node_modules/pkg/CHANGELOG.md": BROKEN,
        })
        self.assertEqual(self.scanned(root), ["README.md"])
        for check in (docs_links.check_repo, html_navigation.check_repo):
            with self.subTest(check=check.__module__):
                errors, _, files = check(root)
                self.assertEqual(errors, [])
                self.assertEqual(files, 1)

    def test_exclude_globs_match_root_relative_paths_and_directories(self):
        root = self.make_repo({
            "README.md": "# Project\n",
            "vendor/lib/README.md": BROKEN,
            "docs/guide.md": "# Guide\n",
            "docs/notes.draft.md": BROKEN,
            "docs/vendor/kept.md": "# Kept\n",
        })
        self.assertCountEqual(self.scanned(root, "vendor", "docs/*.draft.md"),
                              ["README.md", "docs/guide.md", "docs/vendor/kept.md"])

    def test_exclude_patterns_are_normalized(self):
        root = self.make_repo({"README.md": "# Project\n", "third_party/x/README.md": BROKEN})
        for pattern in ("./third_party/", " third_party ", "third_party\\x"):
            with self.subTest(pattern=pattern):
                self.assertEqual(self.scanned(root, pattern), ["README.md"])
        self.assertCountEqual(self.scanned(root, "", "   "),
                              ["README.md", "third_party/x/README.md"])

    def test_excluded_files_remain_link_destinations(self):
        root = self.make_repo({
            "README.md": "[Kept](vendor/README.md#usage) and [gone](vendor/missing.md)\n",
            "vendor/README.md": "## Usage\n" + BROKEN,
        })
        errors, _, files = docs_links.check_repo(root, ["vendor"])
        self.assertEqual(files, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("vendor/missing.md", errors[0])
        errors, _, _ = html_navigation.check_repo(root, ["vendor"])
        self.assertEqual(len(errors), 1)
        self.assertIn("vendor/missing.md", errors[0])

    def test_command_line_accepts_repeated_exclude(self):
        root = self.make_repo({
            "README.md": "# Project\n",
            "vendor/README.md": BROKEN,
            "archive/old.md": BROKEN,
        })
        for script in ("docs_links.py", "html_navigation.py"):
            command = [sys.executable, str(ROOT / "tools" / script), "--root", str(root)]
            with self.subTest(script=script):
                failing = subprocess.run(command + ["--exclude", "vendor"],
                                         capture_output=True, text=True, check=False, timeout=30)
                self.assertEqual(failing.returncode, 1)
                self.assertIn("archive/old.md", failing.stderr)
                passing = subprocess.run(command + ["--exclude", "vendor", "--exclude", "archive"],
                                         capture_output=True, text=True, check=False, timeout=30)
                self.assertEqual(passing.returncode, 0, passing.stderr)
                self.assertIn("1 Markdown file", passing.stdout)


if __name__ == "__main__":
    unittest.main()
