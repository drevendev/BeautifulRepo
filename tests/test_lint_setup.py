"""The linter is a hash-pinned, CI-only developer tool, never a runtime dependency."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LintSetupTests(unittest.TestCase):
    def test_ruff_is_pinned_to_an_exact_version_and_hash(self):
        requirements = (ROOT / ".github/lint-requirements.txt").read_text(encoding="utf-8")
        self.assertRegex(requirements, r"(?m)^ruff==\d+\.\d+\.\d+ \\\n    --hash=sha256:[0-9a-f]{64}$")

    def test_ci_installs_with_required_hashes_and_lints_everything(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("pip install --require-hashes --no-deps -r .github/lint-requirements.txt",
                      workflow)
        self.assertIn("run: ruff check --output-format github", workflow)
        config = (ROOT / "ruff.toml").read_text(encoding="utf-8")
        for pattern in ("tools/**/*.py", "tests/**/*.py", "examples/**/*.py"):
            with self.subTest(pattern=pattern):
                self.assertIn(f'"{pattern}"', config)

    def test_tools_and_examples_never_import_the_linter(self):
        for path in [*ROOT.glob("tools/*.py"), *ROOT.glob("examples/**/*.py")]:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIsNone(re.search(r"^\s*(?:import|from)\s+ruff\b",
                                            path.read_text(encoding="utf-8"), re.MULTILINE))


if __name__ == "__main__":
    unittest.main()
