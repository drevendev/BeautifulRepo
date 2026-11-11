"""Per-skill layout probes on disposable copies; no npx or model execution."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "standalone_skill_preflight.py"
spec = importlib.util.spec_from_file_location("standalone_skill_preflight", SCRIPT)
assert spec and spec.loader
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class StandalonePreflightTests(unittest.TestCase):
    def test_isolated_skill_copy_fails_closed_on_shared_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, required in probe.REQUIRED.items():
                skill = root / "skills" / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
                with self.subTest(skill=name):
                    result = probe.inspect(skill)
                    self.assertEqual(result["state"], "incomplete")
                    self.assertEqual(set(result["missing_or_redirected"]), set(required))
                    self.assertEqual(result["assumed_root"], str(root))

    def test_full_root_files_satisfy_only_presence_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in probe.REQUIRED:
                skill = root / "skills" / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("not executable", encoding="utf-8")
            # A real plugin has these files; a standalone SKILL.md copy does not.
            for relative in {p for names in probe.REQUIRED.values() for p in names}:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("would raise if executed", encoding="utf-8")
            for name in probe.REQUIRED:
                with self.subTest(skill=name):
                    result = probe.inspect(root / "skills" / name / "SKILL.md")
                    self.assertEqual(result["state"], "present")
                    self.assertEqual(result["missing_or_redirected"], [])
                    self.assertIn("Not their bytes", result["limitations"])

    def test_redirected_requirement_does_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "audit-repo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("test", encoding="utf-8")
            outside = root / "outside.py"
            outside.write_text("pass", encoding="utf-8")
            tools = root / "tools"
            tools.mkdir()
            try:
                (tools / "repo_audit.py").symlink_to(outside)
            except (NotImplementedError, OSError):
                self.skipTest("file symlinks unavailable")
            report = probe.inspect(skill)
            self.assertIn("tools/repo_audit.py", report["missing_or_redirected"])

    def test_redirected_ancestor_above_root_fails_even_with_complete_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            actual = parent / "complete"
            skill = actual / "skills" / "audit-repo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("ordinary definition", encoding="utf-8")
            for relative in probe.REQUIRED["audit-repo"]:
                path = actual / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("ordinary dependency", encoding="utf-8")
            self.assertEqual(probe.inspect(skill)["state"], "present")

            alias = parent / "redirected-parent"
            try:
                alias.symlink_to(actual, target_is_directory=True)
            except (NotImplementedError, OSError):
                self.skipTest("directory symlinks unavailable")

            for redirected in (
                alias / "skills" / "audit-repo",
                alias / ".." / "complete" / "skills" / "audit-repo",
            ):
                with self.subTest(redirected=str(redirected)):
                    with self.assertRaisesRegex(probe.ProbeError, "redirected"):
                        probe.inspect(redirected)

            command = [sys.executable, "-I", str(SCRIPT), str(alias / "skills" / "audit-repo")]
            completed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["state"], "invalid")

    def test_ordinary_dotdot_in_skill_path_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "audit-repo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("definition", encoding="utf-8")
            (root / "ordinary").mkdir()
            for relative in probe.REQUIRED["audit-repo"]:
                item = root / relative
                item.parent.mkdir(parents=True, exist_ok=True)
                item.write_text("ordinary file", encoding="utf-8")
            route = root / "ordinary" / ".." / "skills" / "audit-repo"
            self.assertEqual(probe.inspect(route)["state"], "present")

    def test_cli_exit_codes_and_no_skill_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "audit-repo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("test", encoding="utf-8")
            command = [sys.executable, "-I", str(SCRIPT), str(skill)]
            incomplete = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(incomplete.returncode, 1, incomplete.stderr)
            self.assertEqual(json.loads(incomplete.stdout)["state"], "incomplete")
            for relative in probe.REQUIRED["audit-repo"]:
                item = root / relative
                item.parent.mkdir(parents=True, exist_ok=True)
                item.write_text("raise RuntimeError('must not execute')\n", encoding="utf-8")
            complete = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(complete.returncode, 0, complete.stderr)
            self.assertEqual(json.loads(complete.stdout)["state"], "present")
            invalid = subprocess.run(command[:-1] + [str(root)], capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 2, invalid.stderr)

    def test_byte_comparison_detects_mismatch_without_executing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "pinned"
            installed = root / "installed"
            for base in (source, installed):
                skill = base / "skills" / "audit-repo"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("ordinary definition", encoding="utf-8")
                for relative in probe.REQUIRED["audit-repo"]:
                    item = base / relative
                    item.parent.mkdir(parents=True, exist_ok=True)
                    item.write_text("do not execute this fixture", encoding="utf-8")
            selected = installed / "skills" / "audit-repo"
            good = probe.inspect(selected, source_root=source)
            self.assertEqual(good["state"], "present")
            self.assertEqual(good["source_comparison"]["mismatched"], [])
            self.assertEqual(
                good["source_comparison"]["checked_files"],
                len(probe.REQUIRED["audit-repo"]) + 1,
            )
            changed = installed / probe.REQUIRED["audit-repo"][0]
            changed.write_text("different bytes", encoding="utf-8")
            failed = probe.inspect(selected, source_root=source)
            self.assertEqual(failed["state"], "mismatch")
            self.assertEqual(failed["source_comparison"]["mismatched"], [
                probe.REQUIRED["audit-repo"][0],
            ])
            completed = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), str(selected),
                 "--source-root", str(source)],
                capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["state"], "mismatch")
            changed.write_text("do not execute this fixture", encoding="utf-8")
            (selected / "SKILL.md").write_text("modified skill instructions", encoding="utf-8")
            changed_skill = probe.inspect(selected, source_root=source)
            self.assertEqual(changed_skill["state"], "mismatch")
            self.assertEqual(
                changed_skill["source_comparison"]["mismatched"],
                ["skills/audit-repo/SKILL.md"],
            )

    def test_byte_comparison_fails_closed_on_untrusted_source_layout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "pinned"
            installed = root / "installed"
            for base in (source, installed):
                skill = base / "skills" / "audit-repo"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("definition", encoding="utf-8")
                for relative in probe.REQUIRED["audit-repo"]:
                    item = base / relative
                    item.parent.mkdir(parents=True, exist_ok=True)
                    item.write_text("ordinary", encoding="utf-8")
            selected = installed / "skills" / "audit-repo"
            with self.assertRaisesRegex(probe.ProbeError, "must differ"):
                probe.inspect(selected, source_root=installed)
            (source / probe.REQUIRED["audit-repo"][0]).unlink()
            with self.assertRaisesRegex(probe.ProbeError, "source reference missing"):
                probe.inspect(selected, source_root=source)
            alias = root / "alias"
            try:
                alias.symlink_to(source, target_is_directory=True)
            except (NotImplementedError, OSError):
                self.skipTest("directory symlinks unavailable")
            with self.assertRaisesRegex(probe.ProbeError, "source root.*redirected"):
                probe.inspect(selected, source_root=alias)

    def test_byte_comparison_cannot_hide_missing_installed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "pinned"
            installed = root / "installed"
            for base in (source, installed):
                skill = base / "skills" / "audit-repo"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("definition", encoding="utf-8")
            for relative in probe.REQUIRED["audit-repo"]:
                item = source / relative
                item.parent.mkdir(parents=True, exist_ok=True)
                item.write_text("ordinary", encoding="utf-8")
            result = probe.inspect(installed / "skills" / "audit-repo", source_root=source)
            self.assertEqual(result["state"], "incomplete")
            self.assertEqual(
                set(result["missing_or_redirected"]),
                set(probe.REQUIRED["audit-repo"]),
            )
            self.assertEqual(result["source_comparison"]["mismatched"], [])


    def test_self_contained_audit_copy_with_source_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "pinned"
            installed = base / "installed" / ".agents" / "skills" / "audit-repo"
            original = source / "skills" / "audit-repo"
            installed.mkdir(parents=True)
            original.mkdir(parents=True)
            (original / "SKILL.md").write_text("definition", encoding="utf-8")
            (installed / "SKILL.md").write_text("definition", encoding="utf-8")
            for relative in probe.REQUIRED["audit-repo"]:
                for root in (source, installed):
                    file = root / relative
                    file.parent.mkdir(parents=True, exist_ok=True)
                    file.write_text("same dependency", encoding="utf-8")
            result = probe.inspect(installed, source_root=source)
            self.assertEqual(result["state"], "present")
            self.assertEqual(result["layout"], "self-contained")
            self.assertEqual(result["assumed_root"], str(installed))
            self.assertEqual(result["source_comparison"]["mismatched"], [])
            modified = installed / "tools/repo_audit.py"
            modified.write_text("tampered", encoding="utf-8")
            result = probe.inspect(installed, source_root=source)
            self.assertEqual(result["state"], "mismatch")
            self.assertEqual(result["source_comparison"]["mismatched"], ["tools/repo_audit.py"])
            modified.unlink()
            result = probe.inspect(installed)
            self.assertEqual(result["state"], "incomplete")
            self.assertIn("tools/repo_audit.py", result["missing_or_redirected"])

    def test_committed_audit_bundle_has_no_dependency_drift(self):
        files = (
            *probe.REQUIRED["audit-repo"],
            "checklists/confidentiality.md",
            "guides/private-repositories.md",
        )
        for relative in files:
            with self.subTest(relative=relative):
                canonical = ROOT / relative
                packaged = ROOT / "skills" / "audit-repo" / relative
                self.assertFalse(packaged.is_symlink())
                self.assertTrue(packaged.is_file())
                self.assertEqual(packaged.read_bytes(), canonical.read_bytes())

    def test_known_skills_have_nonempty_unique_relative_dependencies(self):
        self.assertEqual(len(probe.REQUIRED), 4)
        for name, names in probe.REQUIRED.items():
            with self.subTest(skill=name):
                self.assertTrue(names)
                self.assertEqual(len(names), len(set(names)))
                skill_text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                for value in names:
                    path = Path(value)
                    self.assertFalse(path.is_absolute())
                    self.assertNotIn("..", path.parts)
                    self.assertIn(path.parts[0], {"tools", "scripts", "guides", "checklists", "templates"})
                    self.assertTrue((ROOT / path).is_file(), value)
                    self.assertIn(value, skill_text, value)


if __name__ == "__main__":
    unittest.main()
