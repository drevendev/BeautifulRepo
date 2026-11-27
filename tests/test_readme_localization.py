"""Exercise the displayed bilingual navigation with the real checkers."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "guides/readme-localization.md"


class LocalizedReadmeTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.target = Path(folder.name)
        blocks = re.findall(
            r"^```markdown\n(.*?)^```$", GUIDE.read_text(encoding="utf-8"),
            re.MULTILINE | re.DOTALL,
        )
        self.assertEqual(2, len(blocks))
        (self.target / "docs").mkdir()
        self.primary = self.target / "README.md"
        self.translation = self.target / "docs/README.fr.md"
        for path, content in zip((self.primary, self.translation), blocks, strict=True):
            path.write_text(content, encoding="utf-8")

    def check(self, tool):
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" / tool),
             "--root", str(self.target)],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
            check=False,
        )

    def test_language_switch_and_authoritative_fragment(self):
        for tool in ("docs_links.py", "html_navigation.py"):
            with self.subTest(tool=tool):
                result = self.check(tool)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_removed_translation_breaks_default_language_route(self):
        self.translation.unlink()
        result = self.check("docs_links.py")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("docs/README.fr.md", result.stderr)

    def test_renamed_authoritative_heading_requires_fragment_review(self):
        content = self.primary.read_text(encoding="utf-8")
        self.assertIn("## First run", content)
        self.primary.write_text(
            content.replace("## First run", "## Quickstart"), encoding="utf-8",
        )
        links = self.check("docs_links.py")
        self.assertEqual(0, links.returncode, links.stdout + links.stderr)
        anchors = self.check("html_navigation.py")
        self.assertEqual(1, anchors.returncode, anchors.stdout + anchors.stderr)
        self.assertIn("first-run", anchors.stdout + anchors.stderr)
