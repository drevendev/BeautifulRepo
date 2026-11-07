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

    def test_one_checker_cli_is_independent_of_unrelated_failures(self):
        self.write("README.md", "# Fixture\\n\\n[Broken](missing.md)\\n")
        for name, expected in (("entry_points", 0),
                               ("markdown_links", 1), ("html_navigation", 1)):
            with self.subTest(checker=name):
                result = self.invoke("--format", "json", "--only", name,
                                     "--fail-on", "never")
                self.assertEqual(expected, result.returncode, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual({name}, set(payload["checks"]))
                self.assertEqual(expected, payload["exit_code"])
                self.assertEqual("complete", payload["checks"][name]["state"])

        for format_name in ("text", "html"):
            with self.subTest(format=format_name):
                result = self.invoke("--format", format_name,
                                     "--only", "entry_points")
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertNotIn("markdown_links:", result.stdout)
                self.assertNotIn("html_navigation:", result.stdout)

    def test_one_checker_does_not_invoke_other_checker_modules(self):
        with patch.object(bundle, "check_once", wraps=bundle.check_once) as call:
            report, code = bundle.run_bundle(self.repo, only="entry_points")
        self.assertEqual(0, code)
        self.assertEqual({"entry_points"}, set(report["checks"]))
        self.assertEqual(1, call.call_count)
        self.assertEqual("entry_points", call.call_args.args[0])
        with self.assertRaisesRegex(ValueError, "unknown checker"):
            bundle.run_bundle(self.repo, only="not_a_checker")

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

    def test_repeated_excludes_skip_only_matching_link_sources(self):
        # Imported documentation can contain intentionally unresolved local links.
        self.write("vendor/broken.md", "# Vendored\n\n[No target](missing.md)\n")
        unfiltered = self.invoke("--format", "json")
        self.assertEqual(1, unfiltered.returncode, unfiltered.stderr)
        plain = json.loads(unfiltered.stdout)
        for name in ("markdown_links", "html_navigation"):
            self.assertEqual(1, plain["checks"][name]["exit_code"])
            self.assertEqual(4, plain["checks"][name]["inspected_markdown_files"])

        filtered = self.invoke("--format", "json", "--exclude", "*.unused",
                               "--exclude", "vendor")
        self.assertEqual(0, filtered.returncode, filtered.stderr)
        payload = json.loads(filtered.stdout)
        for name in ("markdown_links", "html_navigation"):
            self.assertEqual(0, payload["checks"][name]["exit_code"])
            self.assertEqual("complete", payload["checks"][name]["state"])
            self.assertEqual(3, payload["checks"][name]["inspected_markdown_files"])
        # Excluding Markdown from link scans does not suppress the entry-point audit.
        self.assertEqual("complete", payload["checks"]["entry_points"]["state"])

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

    def test_output_overflow_and_checker_failure_are_incomplete(self):
        oversized = {"state": "complete", "exit_code": 0,
                     "diagnostics": ["x" * (bundle.RESULT_LIMIT + 1)]}
        self.assertEqual("incomplete", bundle.bounded(oversized)["state"])
        with patch.object(bundle, "check_once", side_effect=RuntimeError("private diagnostic")):
            result, code = bundle.run_bundle(self.repo)
        self.assertEqual(2, code)
        self.assertEqual(2, result["exit_code"])
        self.assertTrue(all(item["state"] == "incomplete"
                            for item in result["checks"].values()))
        self.assertNotIn("private diagnostic", json.dumps(result))

    def test_invalid_audit_payload_is_not_silently_passed(self):
        with patch.object(bundle, "check_once", return_value={
            "state": "complete", "exit_code": 0, "report": {"schema_version": 1}
        }):
            result, code = bundle.run_bundle(self.repo)
        self.assertEqual(2, code)
        self.assertEqual("incomplete", result["checks"]["entry_points"]["state"])

    def test_text_mode_escapes_terminal_controls_in_filenames_and_diagnostics(self):
        # Reproducible on Windows too: no platform-specific filenames needed.
        report = {
            "schema_version": 1,
            "checks": {
                "entry_points": {
                    "state": "complete", "exit_code": 0,
                    "report": {
                        "findings": [{
                            "path": "README\n\x1b[31m.md", "line": 4,
                            "severity": "warning", "rule_id": "readme.placeholder",
                            "message": "Untrusted\rname", "remediation": "Review\u202e text",
                        }],
                        "summary": {"error": 0, "warning": 1, "info": 0},
                    },
                },
                "markdown_links": {
                    "state": "complete", "exit_code": 1, "checked_destinations": 1,
                    "inspected_markdown_files": 1,
                    "diagnostics": ["docs/a\x1b[2J.md\nFORGED: broken"],
                },
                "html_navigation": {
                    "state": "complete", "exit_code": 0, "checked_destinations": 0,
                    "inspected_markdown_files": 1, "diagnostics": [],
                },
            },
            "exit_code": 1,
            "coverage": "Offline source-level inspection.",
        }
        output = bundle.render_text(report)
        self.assertNotIn("\x1b", output)
        self.assertNotIn("\r", output)
        self.assertNotIn("\u202e", output)
        self.assertIn(r"README\u000a\u001b[31m.md:4", output)
        self.assertIn(r"Untrusted\u000dname", output)
        self.assertIn(r"Review\u202e text", output)
        self.assertIn(r"docs/a\u001b[2J.md\u000aFORGED: broken", output)
        self.assertIn("\n\nmarkdown_links: complete", output)
        self.assertIn("\n\nExit 1: 0=threshold clear", output)
        self.assertEqual("Safe café 😀", bundle._one_terminal_line("Safe café 😀"))

    def test_text_output_preserves_specific_rules_and_limitations(self):
        self.write("README.md", "# Fixture\n\nTODO: check this.\n")
        result = self.invoke("--fail-on", "warning")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("readme.placeholder", result.stdout)
        self.assertIn("source-level", result.stdout)
        self.assertNotIn(str(self.repo), result.stdout)


if __name__ == "__main__":
    unittest.main()
