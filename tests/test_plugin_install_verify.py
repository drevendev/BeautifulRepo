"""Local source-versus-installed Agent Skill integrity checks without a model client."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "plugin_install_verify.py"
SPEC = importlib.util.spec_from_file_location("plugin_install_verify", MODULE_PATH)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class PluginInstallVerificationTests(unittest.TestCase):
    def setUp(self):
        if shutil.which("git") is None:
            self.skipTest("Git is unavailable")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.installed = Path(self.temp.name) / "installed"
        self.source.mkdir()
        self.installed.mkdir()
        for root in (self.source, self.installed):
            for name in verifier.SKILLS:
                destination = root / "skills" / name / "SKILL.md"
                destination.parent.mkdir(parents=True)
                destination.write_text(f"---\nname: {name}\n---\n# Example\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.source)], check=True)
        subprocess.run(["git", "-C", str(self.source), "add", "skills"], check=True)
        subprocess.run(["git", "-C", str(self.source), "-c", "user.email=test@example.invalid",
                        "-c", "user.name=Fixture", "commit", "-qm", "synthetic"], check=True)
        self.sha = subprocess.check_output(["git", "-C", str(self.source), "rev-parse", "HEAD"], text=True).strip()

    def test_matching_content_is_only_a_byte_match_not_a_host_pass(self):
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "match")
        self.assertIn("does not prove", result["limitations"])

    def test_changed_install_reports_mismatch_without_writing(self):
        target = self.installed / "skills" / "audit-repo" / "SKILL.md"
        target.write_text("corrupted", encoding="utf-8")
        before = target.read_bytes()
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "mismatch")
        self.assertEqual(result["different_skill_definitions"], ["audit-repo"])
        self.assertEqual(target.read_bytes(), before)

    def test_wrong_commit_is_incomplete(self):
        with self.assertRaisesRegex(verifier.VerificationError, "differs"):
            verifier.verify(self.source, self.installed, "0" * 40)

    def test_missing_skill_or_extra_skill_is_incomplete(self):
        shutil.rmtree(self.installed / "skills" / "trust-surfaces")
        with self.assertRaisesRegex(verifier.VerificationError, "exactly"):
            verifier.verify(self.source, self.installed, self.sha)

    def test_symbolic_link_is_not_followed(self):
        target = self.installed / "skills" / "audit-repo" / "SKILL.md"
        target.unlink()
        try:
            target.symlink_to(self.source / "skills" / "audit-repo" / "SKILL.md")
        except OSError:
            self.skipTest("symlink unavailable")
        with self.assertRaisesRegex(verifier.VerificationError, "symbolic link"):
            verifier.verify(self.source, self.installed, self.sha)

    def test_dirty_source_matching_dirty_install_cannot_fake_pinned_match(self):
        for root in (self.source, self.installed):
            (root / "skills" / "audit-repo" / "SKILL.md").write_text(
                "---\nname: audit-repo\n---\n# Modified after commit\n", encoding="utf-8")
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "mismatch")
        self.assertEqual(result["different_skill_definitions"], ["audit-repo"])

    def test_expected_commit_must_be_full_sha(self):
        with self.assertRaisesRegex(verifier.VerificationError, "full lowercase"):
            verifier.verify(self.source, self.installed, self.sha[:12])

    def test_script_cli_exit_codes(self):
        base = [sys.executable, "-I", str(MODULE_PATH), "--source", str(self.source),
                "--installed", str(self.installed), "--expected-commit", self.sha]
        ok = subprocess.run(base, capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["state"], "match")
        (self.installed / "skills" / "audit-repo" / "SKILL.md").write_text("changed", encoding="utf-8")
        mismatch = subprocess.run(base, capture_output=True, text=True)
        self.assertEqual(mismatch.returncode, 1, mismatch.stderr)
        incomplete = subprocess.run(base[:-1] + ["0" * 40], capture_output=True, text=True)
        self.assertEqual(incomplete.returncode, 2, incomplete.stderr)


if __name__ == "__main__":
    unittest.main()
