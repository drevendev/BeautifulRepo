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
