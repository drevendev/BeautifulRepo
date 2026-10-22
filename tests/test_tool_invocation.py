"""Running the checkers from outside BeautifulRepo, the way an installed copy or agent would."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LINK_CHECKERS = ("docs_links.py", "html_navigation.py")


class ForeignInvocationTests(unittest.TestCase):
    def make_repo(self) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        (root / "README.md").write_text("# Foreign\n\n[Missing](missing.md)\n", encoding="utf-8")
        return root

    def run_tool(self, script: str, *args: str, cwd: Path):
        # -I drops the script directory and the working directory from sys.path.
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" / script), *args],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False, timeout=60,
        )

    def test_link_checkers_run_in_isolated_mode(self):
        root = self.make_repo()
        for script in LINK_CHECKERS:
            with self.subTest(script=script):
                result = self.run_tool(script, "--root", str(root), cwd=root)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("missing.md", result.stderr)

    def test_default_root_is_the_working_directory_not_the_tool_checkout(self):
        root = self.make_repo()
        for script in LINK_CHECKERS:
            with self.subTest(script=script):
                result = self.run_tool(script, cwd=root)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("missing.md", result.stderr)
        audit = self.run_tool("repo_audit.py", "--format", "json", "--fail-on", "never", cwd=root)
        self.assertEqual(audit.returncode, 0, audit.stderr)
        # BeautifulRepo has a LICENSE; the foreign fixture does not.
        self.assertIn('"rule_id": "license.missing"', audit.stdout)


if __name__ == "__main__":
    unittest.main()
