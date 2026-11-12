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

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "plugin_install_verify.py"
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
                destination.write_bytes(f"---\nname: {name}\n---\n# Example\n".encode("utf-8"))
        for root in (self.source, self.installed):
            for relative in verifier.DEPENDENCIES:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(f"# synthetic {relative}\n".encode("utf-8"))
        subprocess.run(["git", "init", "-q", str(self.source)], check=True)
        subprocess.run(["git", "-C", str(self.source),
                        "add", "skills", "tools", "scripts", "guides", "checklists", "templates"], check=True)
        subprocess.run(["git", "-C", str(self.source), "-c", "user.email=test@example.invalid",
                        "-c", "user.name=Fixture", "commit", "-qm", "synthetic"], check=True)
        self.sha = subprocess.check_output(["git", "-C", str(self.source), "rev-parse", "HEAD"], text=True).strip()

    def test_matching_content_is_only_a_byte_match_not_a_host_pass(self):
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "match")
        self.assertEqual(result["checked_plugin_dependencies"], list(verifier.DEPENDENCIES))
        self.assertEqual(result["different_plugin_dependencies"], [])
        self.assertIn("proof of", result["limitations"])

    def add_optional_manifests(self):
        # Add metadata after the fixture's first commit so both snapshots are
        # pinned Git blobs rather than mutable working-tree files.
        for root in (self.source, self.installed):
            for relative in verifier.OPTIONAL_MANIFESTS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"name": "beautifulrepo", "version": "0.3.0-dev.0"}\n',
                                encoding="utf-8")
        subprocess.run(["git", "-C", str(self.source), "add",
                        *verifier.OPTIONAL_MANIFESTS], check=True)
        subprocess.run(["git", "-C", str(self.source),
                        "-c", "user.email=test@example.invalid", "-c",
                        "user.name=Fixture", "commit", "-qm", "pin manifests"], check=True)
        self.sha = subprocess.check_output(
            ["git", "-C", str(self.source), "rev-parse", "HEAD"], text=True,
        ).strip()

    def test_present_plugin_manifests_match_committed_bytes(self):
        self.add_optional_manifests()
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual("match", result["state"])
        self.assertEqual(list(verifier.OPTIONAL_MANIFESTS), result["checked_present_manifests"])
        self.assertEqual([], result["missing_optional_manifests"])
        self.assertEqual([], result["different_present_manifests"])

    def test_modified_installed_manifest_is_a_mismatch(self):
        self.add_optional_manifests()
        target = self.installed / "plugin.json"
        target.write_text('{"name": "different"}\n', encoding="utf-8")
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual("mismatch", result["state"])
        self.assertEqual(["plugin.json"], result["different_present_manifests"])
        self.assertEqual([], result["different_skill_definitions"])
        self.assertEqual([], result["different_plugin_dependencies"])

    def test_absent_optional_manifest_is_reported_not_falsely_verified(self):
        self.add_optional_manifests()
        (self.installed / ".claude-plugin" / "plugin.json").unlink()
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual("match", result["state"])
        self.assertEqual(["plugin.json"], result["checked_present_manifests"])
        self.assertEqual([".claude-plugin/plugin.json"], result["missing_optional_manifests"])
        self.assertEqual([], result["different_present_manifests"])
        self.assertIn("unverified", result["limitations"])

    def test_redirected_optional_manifest_fails_closed(self):
        self.add_optional_manifests()
        target = self.installed / "plugin.json"
        target.unlink()
        try:
            target.symlink_to(self.source / "plugin.json")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(verifier.VerificationError, "symbolic link"):
            verifier.verify(self.source, self.installed, self.sha)

    def test_dangling_redirected_manifest_parent_is_not_harmless_absence(self):
        self.add_optional_manifests()
        parent = self.installed / ".claude-plugin"
        (parent / "plugin.json").unlink()
        parent.rmdir()
        try:
            parent.symlink_to(self.installed / "missing-directory", target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        with self.assertRaisesRegex(verifier.VerificationError, "redirected component"):
            verifier.verify(self.source, self.installed, self.sha)

    def test_source_cannot_be_its_own_installed_cache_even_with_an_alias(self):
        for installed in (self.source, self.source.parent / "source" / ".." / "source"):
            with self.subTest(installed=str(installed)):
                with self.assertRaisesRegex(verifier.VerificationError, "distinct physical"):
                    verifier.verify(self.source, installed, self.sha)
        result = subprocess.run(
            [sys.executable, "-I", str(MODULE_PATH), "--source", str(self.source),
             "--installed", str(self.source), "--expected-commit", self.sha],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "incomplete")

    def test_changed_install_reports_mismatch_without_writing(self):
        target = self.installed / "skills" / "audit-repo" / "SKILL.md"
        target.write_text("corrupted", encoding="utf-8")
        before = target.read_bytes()
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "mismatch")
        self.assertEqual(result["different_skill_definitions"], ["audit-repo"])
        self.assertEqual(target.read_bytes(), before)

    def test_modified_executable_dependency_reports_mismatch(self):
        target = self.installed / "tools" / "readme_apply.py"
        target.write_bytes(b"# modified executable\n")
        before = target.read_bytes()
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "mismatch")
        self.assertEqual(result["different_skill_definitions"], [])
        self.assertEqual(result["different_plugin_dependencies"], ["tools/readme_apply.py"])
        self.assertEqual(target.read_bytes(), before)

    def test_modified_policy_dependency_reports_mismatch(self):
        target = self.installed / "guides" / "agent-safety.md"
        target.write_bytes(b"# modified policy\n")
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "mismatch")
        self.assertEqual(result["different_plugin_dependencies"], ["guides/agent-safety.md"])

    def test_skill_required_documents_are_covered(self):
        # A MATCH must not hide absent first-success or policy materials
        # that a SKILL.md explicitly requires or selects.
        expected = {
            "checklists/repository.md", "checklists/first-success.md",
            "checklists/confidentiality.md", "guides/cli-repositories.md",
            "guides/community-safety.md", "guides/private-repositories.md",
            "guides/release-notes.md", "templates/README.template.md",
            "templates/LIBRARY_README.template.md",
            "templates/APPLICATION_README.template.md",
            "templates/RESEARCH_DATA_README.template.md",
            "templates/CURATED_README.template.md",
            "templates/INTERNAL_README.template.md",
            "templates/SECURITY.template.md",
            "templates/RELEASE_NOTES.template.md",
        }
        self.assertTrue(expected.issubset(set(verifier.DEPENDENCIES)))

    def test_missing_required_template_is_incomplete(self):
        (self.installed / "templates" / "RELEASE_NOTES.template.md").unlink()
        with self.assertRaisesRegex(verifier.VerificationError, "missing"):
            verifier.verify(self.source, self.installed, self.sha)

    def test_modified_first_success_checklist_reports_mismatch(self):
        target = self.installed / "checklists" / "first-success.md"
        target.write_text("# modified checklist\\n", encoding="utf-8")
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "mismatch")
        self.assertEqual(result["different_plugin_dependencies"],
                         ["checklists/first-success.md"])

    def test_missing_or_redirected_dependency_is_incomplete(self):
        target = self.installed / "scripts" / "release_inventory.py"
        target.unlink()
        with self.assertRaisesRegex(verifier.VerificationError, "missing"):
            verifier.verify(self.source, self.installed, self.sha)
        try:
            target.symlink_to(self.source / "scripts" / "release_inventory.py")
        except OSError:
            self.skipTest("symlink unavailable")
        with self.assertRaisesRegex(verifier.VerificationError, "symbolic link"):
            verifier.verify(self.source, self.installed, self.sha)

    def test_dirty_source_dependency_cannot_override_pinned_blob(self):
        (self.source / "tools" / "repo_audit.py").write_bytes(b"# dirty source\n")
        result = verifier.verify(self.source, self.installed, self.sha)
        self.assertEqual(result["state"], "match")

    def test_wrong_commit_is_incomplete(self):
        with self.assertRaisesRegex(verifier.VerificationError, "differs"):
            verifier.verify(self.source, self.installed, "0" * 40)

    def test_missing_skill_or_extra_skill_is_incomplete(self):
        shutil.rmtree(self.installed / "skills" / "trust-surfaces")
        with self.assertRaisesRegex(verifier.VerificationError, "exactly"):
            verifier.verify(self.source, self.installed, self.sha)

    def test_redirected_root_parent_cannot_pass_as_installed_or_source(self):
        alias = Path(self.temp.name) / "alias-to-checkouts"
        try:
            alias.symlink_to(Path(self.temp.name), target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        for source, installed in (
            (self.source, alias / "installed"),
            (alias / "source", self.installed),
        ):
            with self.subTest(source=str(source), installed=str(installed)):
                with self.assertRaisesRegex(verifier.VerificationError, "redirected component"):
                    verifier.verify(source, installed, self.sha)

    @unittest.skipUnless(sys.platform == "win32", "native junction test requires Windows")
    def test_native_windows_root_junction_is_not_treated_as_ordinary_cache(self):
        alias = Path(self.temp.name) / "junction-to-checkouts"
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(alias), self.temp.name],
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            self.skipTest("creating a test junction is unavailable")
        with self.assertRaisesRegex(verifier.VerificationError, "redirected component"):
            verifier.verify(self.source, alias / "installed", self.sha)

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
            (root / "skills" / "audit-repo" / "SKILL.md").write_bytes(
                b"---\nname: audit-repo\n---\n# Modified after commit\n")
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
