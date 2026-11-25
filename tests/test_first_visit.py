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




    @unittest.skipUnless(sys.platform != "win32", "POSIX shell control-flow test")
    def test_documented_posix_setup_stops_before_audit_on_failure(self):
        import os
        import re
        import shutil

        bash = shutil.which("bash")
        if not bash:
            self.skipTest("Bash unavailable")
        harness = r"""
git() {
    printf '%s\n' "$1" >> "$BR_TEST_LOG"
    case "$1" in
        clone)
            if [ "$BR_TEST_FAIL" = clone ]; then return 1; fi
            if [ "$BR_TEST_FAIL" != location ]; then mkdir BeautifulRepo; fi
            ;;
        checkout)
            [ "$BR_TEST_FAIL" != checkout ]
            ;;
        rev-parse)
            if [ "$BR_TEST_FAIL" = wrong-sha ]; then
                printf '%s\n' wrong
            else
                printf '%s\n' "$BR_TEST_PIN"
            fi
            [ "$BR_TEST_FAIL" != sha ]
            ;;
        *) return 99 ;;
    esac
}
python() {
    if [ "$2" = -c ]; then
        printf '%s\n' version >> "$BR_TEST_LOG"
        [ "$BR_TEST_FAIL" != version ]
    else
        printf '%s\n' audit >> "$BR_TEST_LOG"
        return "$BR_TEST_AUDIT_EXIT"
    fi
}
"""
        stages = {
            "clone": ["clone"],
            "location": ["clone"],
            "checkout": ["clone", "checkout"],
            "sha": ["clone", "checkout", "rev-parse"],
            "wrong-sha": ["clone", "checkout", "rev-parse"],
            "version": ["clone", "checkout", "rev-parse", "version"],
            "": ["clone", "checkout", "rev-parse", "version", "audit"],
        }
        for relative in ("README.md", "guides/combined-audit.md", "guides/working-proof.md"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            block = next(
                snippet for snippet in re.findall(r"\x60\x60\x60bash\n(.*?)\n\x60\x60\x60", source, re.S)
                if snippet.startswith("git clone https://github.com/drevendev/BeautifulRepo.git")
            )
            pin = re.search(r"git checkout --detach ([0-9a-f]{40})", block).group(1)
            for failure, expected in stages.items():
                for audit_exit in ((0, 1, 2) if not failure else (0,)):
                    with self.subTest(document=relative, failure=failure, audit_exit=audit_exit):
                        with tempfile.TemporaryDirectory() as tmp:
                            root = Path(tmp)
                            log = root / "steps.log"
                            # A failed clone must not reuse an older checkout.
                            if failure == "clone":
                                (root / "BeautifulRepo").mkdir()
                            result = subprocess.run(
                                [bash, "--noprofile", "--norc", "-c", harness + "\n" + block],
                                cwd=root, capture_output=True, text=True, timeout=15,
                                env={**os.environ, "BR_TEST_LOG": str(log),
                                     "BR_TEST_FAIL": failure, "BR_TEST_PIN": pin,
                                     "BR_TEST_AUDIT_EXIT": str(audit_exit)},
                                check=False,
                            )
                            self.assertEqual(expected, log.read_text().splitlines())
                            self.assertEqual(1 if failure else audit_exit, result.returncode,
                                             result.stdout + result.stderr)


    def test_documented_pin_runs_the_actual_first_audit_from_a_clean_clone(self):
        # The current-HEAD clone smoke does not exercise the detached SHA that
        # first-time readers actually copy from README/combined-audit.md.
        import re

        pattern = r"^[ \t]*git checkout --detach ([0-9a-f]{40})(?: &&)?$"
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "guides" / "combined-audit.md").read_text(encoding="utf-8")
        readme_pins = re.findall(pattern, readme, flags=re.MULTILINE)
        guide_pins = re.findall(pattern, guide, flags=re.MULTILINE)
        proof = (ROOT / "guides" / "working-proof.md").read_text(encoding="utf-8")
        proof_pins = re.findall(pattern, proof, flags=re.MULTILINE)
        self.assertEqual(1, len(readme_pins), "README needs one first-audit pin")
        self.assertEqual(2, len(guide_pins), "POSIX and PowerShell pins must agree")
        self.assertEqual(1, len(proof_pins), "Working proof needs one first-audit pin")
        pin = readme_pins[0]
        self.assertEqual({pin}, set(guide_pins))
        self.assertEqual([pin], proof_pins, "All public first-run guides must use the same pinned source")
        if not (ROOT / ".git").exists():
            self.skipTest("source archive has no local Git history")

        with tempfile.TemporaryDirectory(prefix="beautifulrepo-pinned-audit-") as tmp:
            parent = Path(tmp)
            checkout = parent / "BeautifulRepo"
            target = parent / "your-repository"
            (target / "docs").mkdir(parents=True)
            (target / "README.md").write_text(
                "# Sample\n\n[Installation](docs/missing.md)\n", encoding="utf-8",
            )
            (target / "docs" / "guide.md").write_text(
                "# Installation\n", encoding="utf-8",
            )
            (target / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (target / "CONTRIBUTING.md").write_text(
                "# Contributing\n", encoding="utf-8",
            )

            for command in (
                ["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(checkout)],
                ["git", "-C", str(checkout), "checkout", "--quiet", "--detach", pin],
            ):
                outcome = subprocess.run(
                    command, capture_output=True, text=True, encoding="utf-8",
                    timeout=120, check=False,
                )
                self.assertEqual(0, outcome.returncode,
                                 f"{command}: {outcome.stderr}")

            actual = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                capture_output=True, text=True, encoding="utf-8",
                timeout=20, check=False,
            )
            self.assertEqual(0, actual.returncode, actual.stderr)
            self.assertEqual(pin, actual.stdout.strip())

            for expected, missing in ((1, True), (0, False)):
                if not missing:
                    (target / "README.md").write_text(
                        "# Sample\n\n[Installation](docs/guide.md)\n",
                        encoding="utf-8",
                    )
                before = file_snapshot(target)
                result = subprocess.run(
                    [sys.executable, "-I", "tools/audit_bundle.py",
                     "../your-repository", "--fail-on", "never",
                     "--format", "json"],
                    cwd=checkout, capture_output=True, text=True,
                    encoding="utf-8", timeout=90, check=False,
                )
                self.assertEqual(expected, result.returncode,
                                 result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(expected, report["exit_code"])
                for name in LINK_CHECKS:
                    check = report["checks"][name]
                    self.assertEqual("complete", check["state"])
                    self.assertEqual(expected, check["exit_code"])
                self.assertEqual(before, file_snapshot(target),
                                 "Pinned first audit changed the target")

            # Exercise the actual pinned text CLI with a strict legacy stream.
            # -I ignores PYTHONIOENCODING, so set the encoding explicitly in
            # this fixed test harness rather than relying on runner locale.
            (target / "README.md").write_text(
                "# Sample\n\n[Installation](docs/café-文档.md)\n",
                encoding="utf-8",
            )
            before = file_snapshot(target)
            result = subprocess.run(
                [sys.executable, "-I", "-S", "-c",
                 "import runpy, sys; "
                 "sys.stdout.reconfigure(encoding='ascii', errors='strict'); "
                 "sys.argv = ['tools/audit_bundle.py', '../your-repository', "
                 "'--fail-on', 'never']; "
                 "runpy.run_path(sys.argv[0], run_name='__main__')"],
                cwd=checkout, capture_output=True, text=True, encoding="ascii",
                timeout=90, check=False,
            )
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn(r"caf\xe9-\u6587\u6863.md", result.stdout)
            self.assertIn("Exit 1:", result.stdout)
            self.assertEqual(before, file_snapshot(target),
                             "Legacy-console audit changed the target")

            clean = subprocess.run(
                ["git", "-C", str(checkout), "status", "--porcelain",
                 "--untracked-files=all"],
                capture_output=True, text=True, encoding="utf-8",
                timeout=20, check=False,
            )
            self.assertEqual(0, clean.returncode, clean.stderr)
            self.assertEqual("", clean.stdout,
                             "Pinned first audit changed its tool checkout")
            self.assertFalse((checkout / "tools" / "__pycache__").exists())


    def test_documented_powershell_setup_stops_before_audit_on_failure(self):
        import os
        import re
        import shutil

        pwsh = shutil.which("pwsh")
        if not pwsh:
            if sys.platform == "win32":
                self.fail("Windows CI needs PowerShell 7")
            self.skipTest("PowerShell unavailable")
        source = (ROOT / "guides" / "combined-audit.md").read_text(encoding="utf-8")
        block = re.search(r"\x60\x60\x60powershell\n(.*?)\n\x60\x60\x60", source, re.S).group(1)
        pin = re.search(r"git checkout --detach ([0-9a-f]{40})", block).group(1)
        harness = r"""
function git {
    $stage = $args[0]
    Add-Content -LiteralPath $env:BR_TEST_LOG -Value $stage
    $global:LASTEXITCODE = 0
    switch ($stage) {
        clone {
            if ($env:BR_TEST_FAIL -eq 'clone') { $global:LASTEXITCODE = 1 }
            elseif ($env:BR_TEST_FAIL -ne 'location') {
                New-Item -ItemType Directory -Path BeautifulRepo | Out-Null
            }
        }
        checkout {
            if ($env:BR_TEST_FAIL -eq 'checkout') { $global:LASTEXITCODE = 1 }
        }
        'rev-parse' {
            if ($env:BR_TEST_FAIL -eq 'sha') { $global:LASTEXITCODE = 1 }
            elseif ($env:BR_TEST_FAIL -eq 'wrong-sha') { 'wrong' }
            else { $env:BR_TEST_PIN }
        }
        default { throw 'Unexpected Git command' }
    }
}
function python {
    if ($args[1] -eq '-c') {
        Add-Content -LiteralPath $env:BR_TEST_LOG -Value version
        $global:LASTEXITCODE = 0
        if ($env:BR_TEST_FAIL -eq 'version') { $global:LASTEXITCODE = 1 }
    } else {
        Add-Content -LiteralPath $env:BR_TEST_LOG -Value audit
        if ((Get-Location).Path -ne (Join-Path $env:BR_TEST_ROOT BeautifulRepo)) {
            throw 'Unexpected audit working directory'
        }
        $global:LASTEXITCODE = [int]$env:BR_TEST_AUDIT_EXIT
    }
}
"""
        stages = {
            "clone": ["clone"],
            "location": ["clone"],
            "checkout": ["clone", "checkout"],
            "sha": ["clone", "checkout", "rev-parse"],
            "wrong-sha": ["clone", "checkout", "rev-parse"],
            "version": ["clone", "checkout", "rev-parse", "version"],
            "": ["clone", "checkout", "rev-parse", "version", "audit"],
        }
        for failure, expected in stages.items():
            for audit_exit in ((0, 1, 2) if not failure else (0,)):
                with self.subTest(failure=failure, audit_exit=audit_exit):
                    with tempfile.TemporaryDirectory(prefix="first audit ") as tmp:
                        root = Path(tmp).resolve()
                        log = root / "steps.log"
                        script = root / "trial.ps1"
                        if failure == "clone":
                            (root / "BeautifulRepo").mkdir()
                        script.write_text(
                            harness + "\ntry {\n" + block
                            + "\n} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 17 }"
                            + "\nexit $LASTEXITCODE\n",
                            encoding="utf-8",
                        )
                        result = subprocess.run(
                            [pwsh, "-NoProfile", "-NonInteractive", "-File", str(script)],
                            cwd=root, capture_output=True, text=True, encoding="utf-8",
                            timeout=30, check=False,
                            env={**os.environ, "BR_TEST_LOG": str(log),
                                 "BR_TEST_ROOT": str(root), "BR_TEST_FAIL": failure,
                                 "BR_TEST_PIN": pin, "BR_TEST_AUDIT_EXIT": str(audit_exit)},
                        )
                        self.assertEqual(expected, log.read_text(encoding="utf-8-sig").splitlines())
                        self.assertEqual(17 if failure else audit_exit, result.returncode,
                                         result.stdout + result.stderr)
                        if not failure:
                            self.assertEqual(str(audit_exit), result.stdout.strip().splitlines()[-1])


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
                "# Sample\n\nSee [setup](docs/missing.md).\n", encoding="utf-8"
            )
            (target / "docs" / "guide.md").write_text("# Setup\n", encoding="utf-8")
            (target / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            (target / "CONTRIBUTING.md").write_text("# Contributing\n", encoding="utf-8")

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
                        "# Sample\n\nSee [setup](docs/guide.md).\n",
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
