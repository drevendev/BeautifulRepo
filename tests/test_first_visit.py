"""Exercise the documented first-audit command against an untouched target.

Unlike an in-process unit test, this is the public CLI called from a separate
checkout on Linux/Windows CI runners, with a target path containing spaces.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools" / "audit_bundle.py"
LINK_CHECKS = ("markdown_links", "html_navigation")


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*") if path.is_file()
    }


class FirstVisitTests(unittest.TestCase):
    def check_checkout(self, target: Path, expected_exit: int, missing: bool) -> None:
        before = file_snapshot(target)
        completed = subprocess.run(
            [sys.executable, "-I", str(AUDIT), str(target),
             "--fail-on", "never", "--format", "json"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            timeout=90, check=False,
        )
        self.assertEqual(expected_exit, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(1, report["schema_version"])
        self.assertEqual(expected_exit, report["exit_code"])
        self.assertEqual("complete", report["checks"]["entry_points"]["state"])
        for checker in LINK_CHECKS:
            result = report["checks"][checker]
            self.assertEqual("complete", result["state"])
            self.assertEqual(int(missing), result["exit_code"])
            diagnostics = "\n".join(result["diagnostics"])
            if missing:
                self.assertIn("docs/setup.md", diagnostics)
            else:
                self.assertEqual("", diagnostics)
        self.assertEqual(before, file_snapshot(target), "audit changed target files")

    def test_copy_pastable_external_checkout_path_and_repair(self):
        with tempfile.TemporaryDirectory(prefix="beautifulrepo-first-visit-") as tmp:
            target = Path(tmp) / "a repository with spaces"
            (target / "docs").mkdir(parents=True)
            (target / "README.md").write_text(
                "# Test project\n\nRead the [setup guide](docs/setup.md).\n",
                encoding="utf-8",
            )
            (target / "docs" / "guide.md").write_text(
                "# Setup guide\n", encoding="utf-8",
            )
            (target / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (target / "CONTRIBUTING.md").write_text(
                "# Contributing\n", encoding="utf-8",
            )
            self.check_checkout(target, expected_exit=1, missing=True)
            (target / "README.md").write_text(
                "# Test project\n\nRead the [setup guide](docs/guide.md).\n",
                encoding="utf-8",
            )
            self.check_checkout(target, expected_exit=0, missing=False)


    def test_readme_first_audit_from_fresh_sibling_git_clone(self):
        # A path-only subprocess smoke cannot catch errors in the documented
        # "clone beside your repo, cd BeautifulRepo, run ../your-repository"
        # route. Clone from the current checkout without requiring network.
        if not (ROOT / ".git").exists():
            self.skipTest("source is not a Git checkout (e.g. a source archive)")
        with tempfile.TemporaryDirectory(prefix="beautifulrepo-clone-smoke-") as tmp:
            parent = Path(tmp)
            cloned_tools = parent / "BeautifulRepo"
            target = parent / "your-repository"
            (target / "docs").mkdir(parents=True)
            (target / "README.md").write_text(
                "# Sample project\n\nSee [setup](docs/missing.md).\n",
                encoding="utf-8",
            )
            (target / "docs" / "guide.md").write_text("# Setup\n", encoding="utf-8")
            (target / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (target / "CONTRIBUTING.md").write_text(
                "# Contributing\n", encoding="utf-8",
            )

            source_head = subprocess.run(
                ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                capture_output=True, text=True, encoding="utf-8", timeout=20,
                check=False,
            )
            self.assertEqual(0, source_head.returncode, source_head.stderr)
            clone = subprocess.run(
                ["git", "clone", "--quiet", "--no-hardlinks",
                 str(ROOT), str(cloned_tools)],
                capture_output=True, text=True, encoding="utf-8", timeout=120,
                check=False,
            )
            self.assertEqual(0, clone.returncode, clone.stderr)
            cloned_head = subprocess.run(
                ["git", "-C", str(cloned_tools), "rev-parse", "HEAD"],
                capture_output=True, text=True, encoding="utf-8", timeout=20,
                check=False,
            )
            self.assertEqual(0, cloned_head.returncode, cloned_head.stderr)
            self.assertEqual(source_head.stdout.strip(), cloned_head.stdout.strip(),
                             "First-run smoke must use this exact tested commit")
            self.assertTrue((cloned_tools / "tools" / "audit_bundle.py").is_file())

            def documented_command(expected_exit: int, link: str) -> None:
                before = file_snapshot(target)
                run = subprocess.run(
                    [sys.executable, "-I", "tools/audit_bundle.py",
                     "../your-repository", "--fail-on", "never"],
                    cwd=cloned_tools, capture_output=True, text=True,
                    encoding="utf-8", timeout=90, check=False,
                )
                self.assertEqual(expected_exit, run.returncode,
                                 run.stdout + run.stderr)
                self.assertIn(link, run.stdout)
                self.assertIn(f"Exit {expected_exit}:", run.stdout)
                self.assertEqual(before, file_snapshot(target),
                                 "First audit must not change its target")

            documented_command(1, "docs/missing.md")
            (target / "README.md").write_text(
                "# Sample project\n\nSee [setup](docs/guide.md).\n",
                encoding="utf-8",
            )
            documented_command(0, "markdown_links: complete")

            checkout_status = subprocess.run(
                ["git", "-C", str(cloned_tools), "status", "--porcelain",
                 "--untracked-files=all"],
                capture_output=True, text=True, encoding="utf-8", timeout=20,
                check=False,
            )
            self.assertEqual(0, checkout_status.returncode, checkout_status.stderr)
            self.assertEqual("", checkout_status.stdout,
                             "First audit must not change its tool checkout")
            self.assertFalse((cloned_tools / "tools" / "__pycache__").exists(),
                             "Ignored Python bytecode writes are not visible to git status")



    @unittest.skipUnless(sys.platform == "win32", "PowerShell smoke runs on Windows")
    def test_powershell_first_audit_from_sibling_clone(self):
        # Verify the documented native-command exit status, not just that
        # PowerShell can display an audit report. No network is required.
        if not (ROOT / ".git").exists():
            self.skipTest("source is not a Git checkout")
        import shutil
        self.assertIsNotNone(shutil.which("pwsh"), "Windows CI needs PowerShell 7")
        with tempfile.TemporaryDirectory(prefix="beautifulrepo-ps-first-visit-") as tmp:
            parent = Path(tmp)
            clone_root = parent / "BeautifulRepo"
            target = parent / "your-repository"
            (target / "docs").mkdir(parents=True)
            (target / "README.md").write_text(
                "# Sample\\n\\nSee [setup](docs/missing.md).\\n", encoding="utf-8"
            )
            (target / "docs" / "guide.md").write_text("# Setup\\n", encoding="utf-8")
            (target / "LICENSE").write_text("MIT License\\n", encoding="utf-8")
            (target / "CONTRIBUTING.md").write_text("# Contributing\\n", encoding="utf-8")

            clone = subprocess.run(
                ["git", "clone", "--quiet", "--no-hardlinks",
                 str(ROOT), str(clone_root)],
                capture_output=True, text=True, encoding="utf-8",
                timeout=120, check=False,
            )
            self.assertEqual(0, clone.returncode, clone.stderr)
            safe_path = str(clone_root).replace("'", "''")
            script = (
                f"Set-Location -LiteralPath '{safe_path}'; "
                "& python -I .\\tools\\audit_bundle.py "
                "..\\your-repository --fail-on never; "
                "exit $LASTEXITCODE"
            )

            for expected, marker in [(1, "docs/missing.md"),
                                     (0, "markdown_links: complete")]:
                before = file_snapshot(target)
                completed = subprocess.run(
                    ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
                    cwd=parent, capture_output=True, text=True, encoding="utf-8",
                    timeout=90, check=False,
                )
                self.assertEqual(expected, completed.returncode,
                                 completed.stdout + completed.stderr)
                self.assertIn(marker, completed.stdout)
                self.assertIn(f"Exit {expected}:", completed.stdout)
                self.assertEqual(before, file_snapshot(target),
                                 "PowerShell audit must not write the target")
                if expected == 1:
                    (target / "README.md").write_text(
                        "# Sample\\n\\nSee [setup](docs/guide.md).\\n",
                        encoding="utf-8",
                    )

            status = subprocess.run(
                ["git", "-C", str(clone_root), "status", "--porcelain",
                 "--untracked-files=all"],
                capture_output=True, text=True, encoding="utf-8",
                timeout=20, check=False,
            )
            self.assertEqual(0, status.returncode, status.stderr)
            self.assertEqual("", status.stdout, "PowerShell audit changed tools")
            self.assertFalse((clone_root / "tools" / "__pycache__").exists())

if __name__ == "__main__":
    unittest.main()
