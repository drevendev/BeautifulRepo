"""Regression tests for the offline checker's Markdown source-file boundaries."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "tools/docs_links.py"


class DocsLinksSourceSafetyTests(unittest.TestCase):
    def check(self, root: Path):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            text=True, capture_output=True, check=False,
        )

    def symlink(self, link: Path, target: Path):
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"filesystem does not permit symlinks: {error}")

    def test_dangling_markdown_source_is_diagnostic_not_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.symlink(root / "missing-source.md", Path("not-present.md"))
            (root / "README.md").write_text("[Missing](also-not-present.md)\n", encoding="utf-8")
            result = self.check(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("missing-source.md: cannot resolve Markdown source", result.stderr)
            self.assertIn("missing relative destination: 'also-not-present.md'", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_external_source_symlink_does_not_read_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "repo"
            root.mkdir()
            outside = parent / "private.md"
            outside.write_text("[Private](do-not-leak-this-name.md)\n", encoding="utf-8")
            self.symlink(root / "external.md", outside)
            (root / "README.md").write_text("[Missing](local-missing.md)\n", encoding="utf-8")
            result = self.check(root)
            self.assertEqual(1, result.returncode)
            self.assertIn("external.md: Markdown source escapes repository root", result.stderr)
            self.assertIn("missing relative destination: 'local-missing.md'", result.stderr)
            self.assertNotIn("do-not-leak-this-name.md", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
