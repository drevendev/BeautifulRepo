"""Regression coverage for real copied audit checker behavior in disposable fixtures."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_copied_audit.py"
spec = importlib.util.spec_from_file_location("verify_copied_audit", SCRIPT)
assert spec and spec.loader
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


class CopiedAuditBehaviorTests(unittest.TestCase):
    def test_bundled_checkers_report_expected_positive_and_negative_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            reports = Path(directory) / "results"
            result = trial.run_trial(ROOT / "skills" / "audit-repo", reports)
            self.assertEqual(
                result["cases"]["broken"]["exits"],
                {"repo_audit.py": 0, "docs_links.py": 1, "html_navigation.py": 1},
            )
            self.assertEqual(
                result["cases"]["fixed"]["exits"],
                {"repo_audit.py": 0, "docs_links.py": 0, "html_navigation.py": 0},
            )
            self.assertTrue((reports / "trial-summary.json").is_file())
            self.assertIn("missing", (reports / "broken-docs_links.stderr").read_text().lower())
            self.assertIn("OK:", (reports / "fixed-html_navigation.stdout").read_text())

    def test_missing_copied_checker_cannot_pass_behavioral_trial(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "copied"
            (root / "tools").mkdir(parents=True)
            shutil.copyfile(
                ROOT / "skills/audit-repo/tools/repo_audit.py",
                root / "tools/repo_audit.py",
            )
            shutil.copyfile(
                ROOT / "skills/audit-repo/tools/docs_links.py",
                root / "tools/docs_links.py",
            )
            with self.assertRaisesRegex(ValueError, "missing or redirected: html_navigation.py"):
                trial.run_trial(root, Path(directory) / "results")


if __name__ == "__main__":
    unittest.main()
