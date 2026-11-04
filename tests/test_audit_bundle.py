"""Black-box regression tests for the three-checker offline audit bundle."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "audit_bundle.py"
spec = importlib.util.spec_from_file_location("audit_bundle", TOOL)
bundle = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bundle)


class AuditBundleTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.repo = Path(folder.name) / "fixture"
        self.repo.mkdir()
        self.write("README.md", "# Fixture\n\nRead [the guide](docs/guide.md).\n")
        self.write("docs/guide.md", "# Guide\n")
        self.write("LICENSE", "MIT License\n")
        self.write("CONTRIBUTING.md", "# Contributing\n\nMake a focused pull request.\n")

    def write(self, name, content):
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def invoke(self, *options, root=None):
        return subprocess.run(
            [sys.executable, "-I", str(TOOL), str(root or self.repo), *options],
            cwd=self.repo, capture_output=True, text=True, encoding="utf-8",
            check=False, timeout=75,
        )

    def test_healthy_fixture_runs_all_native_checkers_and_has_no_target_writes(self):
        before = {p.relative_to(self.repo).as_posix():
                  hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.repo.rglob("*") if p.is_file()}
        result = self.invoke("--format", "json")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(1, payload["schema_version"])
        self.assertEqual(0, payload["exit_code"])
        self.assertEqual(set(bundle.CHECKERS), set(payload["checks"]))
        self.assertTrue(all(value["state"] == "complete"
                            for value in payload["checks"].values()))
        self.assertEqual(0, payload["checks"]["markdown_links"]["exit_code"])
        self.assertEqual(0, payload["checks"]["html_navigation"]["exit_code"])
        after = {p.relative_to(self.repo).as_posix():
                 hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.repo.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_link_reported_by_both_native_link_checkers(self):
        self.write("README.md", "# Fixture\n\n[Broken](missing.md)\n")
        result = self.invoke("--format", "json")
        self.assertEqual(1, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        for name in ("markdown_links", "html_navigation"):
            self.assertEqual("complete", payload["checks"][name]["state"])
            self.assertEqual(1, payload["checks"][name]["exit_code"])
            self.assertIn("missing.md", "\n".join(payload["checks"][name]["diagnostics"]))
        self.assertEqual(0, payload["checks"]["entry_points"]["exit_code"])

    def test_audit_only_warning_obeys_selected_failure_threshold(self):
        self.write("README.md", "# Fixture\n\nTODO: add a usage example.\n")
        default = self.invoke("--format", "json")
        strict = self.invoke("--format", "json", "--fail-on", "warning")
        never = self.invoke("--format", "json", "--fail-on", "never")
        self.assertEqual(0, default.returncode, default.stderr)
        self.assertEqual(1, strict.returncode, strict.stderr)
        self.assertEqual(0, never.returncode, never.stderr)
        report = json.loads(strict.stdout)["checks"]["entry_points"]["report"]
        self.assertTrue(any(item["rule_id"] == "readme.placeholder" for item in report["findings"]))

    def test_invalid_root_and_symlink_root_fail_without_json_claim(self):
        missing = self.invoke("--format", "json", root=self.repo / "not-found")
        self.assertEqual(2, missing.returncode)
        self.assertEqual("", missing.stdout)
        outside = self.repo.parent / "alias"
        try:
            outside.symlink_to(self.repo, target_is_directory=True)
        except (OSError, NotImplementedError):
            return
        redirected = self.invoke("--format", "json", root=outside)
        self.assertEqual(2, redirected.returncode)
        self.assertEqual("", redirected.stdout)

    def test_timeout_output_overflow_and_checker_failure_are_incomplete(self):
        for outcome in (
            (None, "", "", "checker exceeded the 20-second execution limit"),
            (0, "", "", "checker output exceeded the 128-KiB per-stream limit"),
            (2, "", "bad root", None),
        ):
            with self.subTest(outcome=outcome), patch.object(bundle, "capture_command", return_value=outcome):
                result, code = bundle.run_bundle(self.repo)
                self.assertEqual(2, code)
                self.assertEqual(2, result["exit_code"])
                self.assertTrue(all(item["state"] == "incomplete"
                                    for item in result["checks"].values()))

    def test_invalid_audit_payload_is_not_silently_passed(self):
        with patch.object(bundle, "capture_command", return_value=(0, '{"schema_version":1}', "", None)):
            result, code = bundle.run_bundle(self.repo)
        self.assertEqual(2, code)
        self.assertEqual("incomplete", result["checks"]["entry_points"]["state"])

    def test_text_output_preserves_specific_rules_and_limitations(self):
        self.write("README.md", "# Fixture\n\nTODO: check this.\n")
        result = self.invoke("--fail-on", "warning")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("readme.placeholder", result.stdout)
        self.assertIn("source-level", result.stdout)
        self.assertNotIn(str(self.repo), result.stdout)


if __name__ == "__main__":
    unittest.main()
