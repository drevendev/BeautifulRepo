"""Regression checks for the offline audit-delta reader and its honest coverage boundary."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "audit_delta.py"
AUDIT = ROOT / "tools" / "repo_audit.py"

spec = importlib.util.spec_from_file_location("audit_delta", TOOL)
delta = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(delta)


def report(*items, profile="public", read_files=None):
    counts = {severity: sum(item["severity"] == severity for item in items)
              for severity in delta.SEVERITIES}
    obj = {"schema_version": 1, "documents": {"readme": "README.md", "license": None,
            "contributing": None}, "read_files": ["README.md"] if read_files is None else read_files,
           "summary": counts, "findings": list(items)}
    if profile != "public":
        obj["profile"] = profile
    return obj


def finding(rule, severity="warning", line=1):
    return {"rule_id": rule, "severity": severity, "path": "README.md", "line": line}


class AuditDeltaTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.before = self.home / "before.json"
        self.after = self.home / "after.json"

    def run_cli(self, before, after, *options):
        self.before.write_text(json.dumps(before), encoding="utf-8")
        self.after.write_text(json.dumps(after), encoding="utf-8")
        return self.invoke(*options)

    def invoke(self, *options):
        return subprocess.run([sys.executable, "-I", str(TOOL), str(self.before),
                               str(self.after), *options], cwd=self.home,
                              capture_output=True, text=True, timeout=20, check=False)

    def test_rule_counts_not_line_numbers_drive_comparison(self):
        old = report(finding("readme.placeholder", line=2),
                     finding("readme.placeholder", line=3), finding("link.vague_text", "info"))
        new = report(finding("readme.placeholder", line=10))
        result = self.run_cli(old, new, "--format", "json")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["before"], {"error": 0, "warning": 2, "info": 1})
        self.assertEqual(payload["after"], {"error": 0, "warning": 1, "info": 0})
        self.assertEqual([(r["rule_id"], r["delta"]) for r in payload["changes"]],
                         [("readme.placeholder", -1), ("link.vague_text", -1)])
        self.assertFalse(payload["coverage_changed"])
        self.assertNotIn("README.md", result.stdout)

    def test_new_findings_and_coverage_change_are_not_called_fixes(self):
        old = report(finding("readme.placeholder"))
        new = report(finding("link.vague_text", "info"), read_files=[])
        text = self.run_cli(old, new)
        self.assertEqual(0, text.returncode, text.stderr)
        self.assertIn("Coverage changed: YES", text.stdout)
        self.assertIn("not proof", text.stdout)
        self.assertNotIn("FIXED", text.stdout)
        self.assertNotIn("README.md", text.stdout)

    def test_coverage_details_name_roles_but_not_file_paths(self):
        old = report()
        new = report(read_files=["README.md", "COPYING.md"])
        new["documents"]["license"] = "COPYING.md"
        result = self.run_cli(old, new, "--format", "json")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["coverage_changed"])
        self.assertEqual(["license"], payload["coverage_details"]["changed_document_roles"])
        self.assertTrue(payload["coverage_details"]["read_files_changed"])
        self.assertEqual(1, payload["coverage_details"]["read_file_count_before"])
        self.assertEqual(2, payload["coverage_details"]["read_file_count_after"])
        self.assertNotIn("COPYING.md", result.stdout)
        self.assertNotIn("README.md", result.stdout)

    def test_equal_count_file_switch_is_reported_without_names(self):
        before = report(read_files=["README.md"])
        after = report(read_files=["INDEX.md"])
        result = self.run_cli(before, after)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Coverage changed: YES", result.stdout)
        self.assertIn("Inspected-file selection changed: 1 -> 1 entries", result.stdout)
        self.assertNotIn("INDEX.md", result.stdout)
        self.assertNotIn("README.md", result.stdout)

    def test_unmatched_profiles_rejected(self):
        text = self.run_cli(report(profile="public"), report(profile="private"))
        self.assertEqual(2, text.returncode)
        self.assertIn("profiles differ", text.stderr)

    def test_unsupported_summary_and_boolean_schema_rejected(self):
        cases = [report(finding("readme.title")), report()]
        cases[0]["summary"]["warning"] = 0
        cases[1]["schema_version"] = True
        for case in cases:
            with self.subTest(case=case):
                result = self.run_cli(case, report())
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)

    def test_duplicate_json_keys_and_oversize_rejected(self):
        self.before.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        self.after.write_text(json.dumps(report()), encoding="utf-8")
        self.assertEqual(2, self.invoke().returncode)
        self.before.write_bytes(b"x" * (delta.LIMIT + 1))
        self.assertEqual(2, self.invoke().returncode)

    def test_oversized_json_integer_reports_clean_error(self):
        # CPython 3.11+ may reject integers exceeding its decimal digit limit.
        # The parser error must not leak a traceback or exit with code 1.
        max_digits = getattr(sys, "get_int_max_str_digits", lambda: 4300)()
        if max_digits == 0:
            self.skipTest("integer string conversion limit is disabled")
        digits = "9" * max(5000, max_digits + 1)
        oversized_integer = json.dumps(report())[:-1] + ',"unused_number":' + digits + '}'
        self.assertLess(len(oversized_integer), delta.LIMIT)
        self.before.write_text(oversized_integer, encoding="utf-8")
        self.after.write_text(json.dumps(report()), encoding="utf-8")
        result = self.invoke("--format", "json")
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertIn("audit_delta:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_symlink_report_rejected(self):
        self.after.write_text(json.dumps(report()), encoding="utf-8")
        original = self.home / "original.json"
        original.write_text(json.dumps(report()), encoding="utf-8")
        try:
            self.before.symlink_to(original)
        except (NotImplementedError, OSError):
            self.skipTest("symlinks unavailable")
        self.assertEqual(2, self.invoke().returncode)

    def test_real_repo_audit_json_round_trip(self):
        if not AUDIT.is_file():
            self.skipTest("whole repository unavailable outside checkout")
        first, second = self.home / "first", self.home / "second"
        first.mkdir()
        second.mkdir()
        (first / "README.md").write_text("# Project\n\nTBD\n", encoding="utf-8")
        (second / "README.md").write_text("# Project\n\nUsable guide.\n", encoding="utf-8")
        for directory, target in [(first, self.before), (second, self.after)]:
            result = subprocess.run([sys.executable, "-I", str(AUDIT), str(directory),
                                     "--format", "json", "--fail-on", "never"],
                                    cwd=self.home, capture_output=True, text=True, timeout=20)
            self.assertEqual(0, result.returncode, result.stderr)
            target.write_text(result.stdout, encoding="utf-8")
        result = self.invoke("--format", "json")
        self.assertEqual(0, result.returncode, result.stderr)
        changes = json.loads(result.stdout)["changes"]
        self.assertTrue(any(c["rule_id"] == "readme.placeholder" and c["delta"] == -1 for c in changes))


if __name__ == "__main__":
    unittest.main()
