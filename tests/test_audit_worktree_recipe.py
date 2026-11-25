"""Exercise the published POSIX worktree recipe with real Git and audit tools."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "guides" / "audit-before-after.md"


@unittest.skipUnless(os.name == "posix" and shutil.which("git") and shutil.which("sh"),
                     "requires POSIX shell and Git")
class AuditWorktreeRecipeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="audit worktree ")
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name).resolve()
        self.target = self.home / "target checkout"
        self.auditor = self.home / "auditor checkout"
        self.evidence = self.home / "audit evidence"
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        AUDIT_TEST_PYTHON=sys.executable)
        for directory in (self.target, self.auditor):
            directory.mkdir()
            self.git(directory, "init", "-q", "--template=")
            self.git(directory, "config", "user.name", "Fixture")
            self.git(directory, "config", "user.email", "fixture@example.invalid")
        (self.auditor / "tools").mkdir()
        for name in ("repo_audit.py", "audit_delta.py"):
            shutil.copyfile(ROOT / "tools" / name, self.auditor / "tools" / name)
        self.auditor_sha = self.commit(self.auditor)
        readme = self.target / "README.md"
        readme.write_text("# Parcel\n\nTBD\n\n### Try it\n\n| | |\n| --- | --- |\n| Promise | Evidence |\n", encoding="utf-8")
        self.before = self.commit(self.target)
        readme.write_text("# Parcel\n\nA fictional project that indexes notes.\n\n## Try it\n\n- Promise: explain the outcome.\n- Evidence: show a result.\n", encoding="utf-8")
        self.after = self.commit(self.target)
        self.branch = self.git(self.target, "symbolic-ref", "HEAD")
        readme.write_text("Uncommitted work\n", encoding="utf-8")
        self.guide = GUIDE.read_text(encoding="utf-8")

    def git(self, directory, *args):
        result = subprocess.run(["git", "-C", str(directory), *args], env=self.env,
                                capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout.strip()

    def commit(self, directory):
        self.git(directory, "add", ".")
        self.git(directory, "commit", "-qm", "Fixture revision")
        return self.git(directory, "rev-parse", "HEAD")

    def shell(self, script):
        return subprocess.run(["sh", "-c", script], cwd=self.auditor, env=self.env,
                              capture_output=True, text=True, timeout=40, check=False)

    def recipe(self, before):
        blocks = re.findall(r"^~~~sh\n(.*?)^~~~$", self.guide, re.M | re.S)
        (block,) = [item for item in blocks if item.startswith("target=")]
        values = {"target": str(self.target), "before": before,
                  "after": self.after, "evidence": str(self.evidence)}
        for name, value in values.items():
            block, count = re.subn(rf"^{name}=.*$", lambda _: f"{name}={shlex.quote(value)}",
                                   block, flags=re.M)
            self.assertEqual(1, count, name)
        # Select the test runner's interpreter without changing the documented block.
        return 'python() { "$AUDIT_TEST_PYTHON" "$@"; }\n' + block

    def test_published_recipe_creates_comparable_reports_and_preserves_dirty_checkout(self):
        result = self.shell(self.recipe(self.before))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(f"before={self.before}\nafter={self.after}\n",
                         (self.evidence / "revisions.txt").read_text(encoding="utf-8"))
        self.assertEqual(self.auditor_sha, (self.evidence / "auditor-revision.txt").read_text().strip())
        for label, sha, warnings in (("before", self.before, 4), ("after", self.after, 1)):
            self.assertEqual(sha, self.git(self.evidence / label, "rev-parse", "HEAD"))
            report = json.loads((self.evidence / f"{label}.json").read_text(encoding="utf-8"))
            self.assertEqual({"error": 0, "warning": warnings, "info": 1}, report["summary"])
        delta = (self.evidence / "delta.md").read_text(encoding="utf-8")
        self.assertIn("| warning | 4 | 1 | -3 |", delta)
        self.assertIn("**Coverage changed:** no", delta)
        self.assertIn("does not prove a repaired experience", delta)
        self.assertEqual(self.branch, self.git(self.target, "symbolic-ref", "HEAD"))
        self.assertEqual(self.after, self.git(self.target, "rev-parse", "HEAD"))
        self.assertEqual("Uncommitted work\n", (self.target / "README.md").read_text(encoding="utf-8"))
        (cleanup,) = re.findall(r"^~~~sh\n(git -C .*?worktree remove .*?)^~~~$", self.guide, re.M | re.S)
        assignments = f"target={shlex.quote(str(self.target))}\nevidence={shlex.quote(str(self.evidence))}\n"
        result = self.shell("set -e\n" + assignments + cleanup)
        self.assertEqual(0, result.returncode, result.stderr)
        for label in ("before", "after"):
            self.assertFalse((self.evidence / label).exists())
            self.assertTrue((self.evidence / f"{label}.json").is_file())
        self.assertTrue((self.evidence / "delta.md").is_file())

    def test_invalid_revision_stops_before_creating_evidence(self):
        result = self.shell(self.recipe("not-a-fixture-revision"))
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.evidence.exists())
        self.assertEqual(self.after, self.git(self.target, "rev-parse", "HEAD"))
