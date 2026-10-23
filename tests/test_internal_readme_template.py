"""Internal README template and verified fictional example contracts (#77)."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "internal-repository"
TEMPLATE = ROOT / "templates" / "INTERNAL_README.template.md"
AUDIT = ROOT / "tools" / "repo_audit.py"


class InternalReadmeTests(unittest.TestCase):
    def test_template_covers_internal_entry_points(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for heading in (
            "Purpose and status", "Owner and contact", "Get access",
            "Set up with internal dependencies", "Verify a first success",
            "Runbooks", "Data classification and handling", "Usage terms",
        ):
            with self.subTest(heading=heading):
                self.assertIn(f"## {heading}", text)
        self.assertIn("secret manager", text)
        self.assertIn("Do not add a public open-source license", text)

    def test_filled_example_passes_internal_audit_without_warnings(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            shutil.copyfile(EXAMPLE / "README.md", target / "README.md")
            result = subprocess.run(
                [sys.executable, "-I", str(AUDIT), str(target),
                 "--profile", "internal", "--format", "json",
                 "--fail-on", "warning"],
                capture_output=True, text=True, check=False, timeout=15,
            )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report["profile"], "internal")
        self.assertEqual(report["summary"]["error"], 0)
        self.assertEqual(report["summary"]["warning"], 0)
        self.assertNotIn("LICENSE", report["read_files"])
        self.assertIn("readme", report["documents"])
        self.assertTrue(all(item["severity"] == "info" for item in report["findings"]))

    def test_filled_example_is_clearly_fictional_and_locally_linked(self):
        text = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        self.assertIn("Fictional, not deployed", text)
        self.assertIn("runbooks/local-verification.md", text)
        self.assertTrue((EXAMPLE / "runbooks" / "local-verification.md").is_file())
        self.assertIn("packages.internal.example", text)
        self.assertNotIn("{{", text)
        self.assertNotIn("TODO", text)

    def test_example_verifier_has_a_real_result(self):
        result = subprocess.run(
            [sys.executable, "-I", str(EXAMPLE / "verify_example.py")],
            cwd=ROOT, capture_output=True, text=True, check=False, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Sample records: 2\n")


if __name__ == "__main__":
    unittest.main()
