"""Behavioral and CLI regressions for the bounded offline entry-point audit."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1] / "tools" / "repo_audit.py"
SPEC = importlib.util.spec_from_file_location("repo_audit_under_test", TOOL)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.write("README.md", "# Example\n\nA small demonstration.\n\n## Try it\n\nRun the documented example.\n")
        self.write("LICENSE", "Example fixture; no licensing decision is made by this test.\n")
        self.write("CONTRIBUTING.md", "# Contributing\n\nDiscuss a proposed change first.\n")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8")
        return path

    def report(self):
        return audit.audit_repository(self.root)

    def codes(self, report=None):
        return [item["rule_id"] for item in (report or self.report())["findings"]]

    def cli(self, *arguments, cwd=None):
        return subprocess.run(
            [sys.executable, str(TOOL), *arguments],
            cwd=cwd or self.root, capture_output=True, text=True,
            check=False, timeout=15,
        )

    def test_clean_entry_points(self):
        report = self.report()
        self.assertEqual(report["summary"], {"error": 0, "warning": 0, "info": 0})
        self.assertEqual(report["read_files"], ["CONTRIBUTING.md", "LICENSE", "README.md"])
        self.assertEqual(report["schema_version"], 1)

    def test_missing_readme_is_an_error(self):
        (self.root / "README.md").unlink()
        report = self.report()
        self.assertIn("readme.missing", self.codes(report))
        self.assertEqual(audit.exit_status(report, "error"), 1)

    def test_missing_license_is_a_warning_not_a_legal_verdict(self):
        (self.root / "LICENSE").unlink()
        report = self.report()
        item = next(f for f in report["findings"] if f["rule_id"] == "license.missing")
        self.assertEqual(item["severity"], "warning")
        self.assertEqual(audit.exit_status(report, "error"), 0)
        self.assertEqual(audit.exit_status(report, "warning"), 1)

    def test_missing_contributing_is_informational(self):
        (self.root / "CONTRIBUTING.md").unlink()
        report = self.report()
        self.assertEqual(report["summary"], {"error": 0, "warning": 0, "info": 1})
        self.assertEqual(audit.exit_status(report, "warning"), 0)

    def test_readme_location_priority(self):
        self.write("docs/README.md", "# Docs\n")
        self.write(".github/README.md", "# Front page\n")
        self.assertEqual(self.report()["documents"]["readme"], ".github/README.md")
        (self.root / ".github/README.md").unlink()
        self.assertEqual(self.report()["documents"]["readme"], "README.md")
        (self.root / "README.md").unlink()
        self.assertEqual(self.report()["documents"]["readme"], "docs/README.md")

    def test_case_insensitive_contribution_and_license_candidates(self):
        (self.root / "CONTRIBUTING.md").unlink()
        (self.root / "LICENSE").unlink()
        self.write(".github/Contributing.MD", "# Contribution guide\n")
        self.write("Licence.txt", "Fixture text\n")
        report = self.report()
        self.assertEqual(report["documents"]["contributing"], ".github/Contributing.MD")
        self.assertEqual(report["documents"]["license"], "Licence.txt")

    def test_multiple_same_location_candidates_have_stable_order(self):
        self.write("README.txt", "Plain text\n")
        self.write("README.markdown", "# Other markdown\n")
        self.assertEqual(self.report()["documents"]["readme"], "README.md")

    def test_unsupported_readme_is_not_missing(self):
        (self.root / "README.md").unlink()
        self.write("README.rst", "Example\n=======\n")
        codes = self.codes()
        self.assertIn("readme.unsupported_format", codes)
        self.assertNotIn("readme.missing", codes)
        self.assertNotIn("readme.title", codes)

    def test_empty_readme_is_an_error(self):
        self.write("README.md", " \n\t")
        report = self.report()
        self.assertIn("readme.empty", self.codes(report))
        self.assertEqual(report["summary"]["error"], 1)

    def test_empty_supporting_document_is_a_warning(self):
        self.write("LICENSE", "")
        self.write("CONTRIBUTING.md", "")
        report = self.report()
        self.assertEqual(report["summary"]["warning"], 2)
        self.assertEqual(report["summary"]["error"], 0)

    def test_markdown_and_html_titles(self):
        for title in ("# Example\n", "Example\n=======\n", "<div><h1>Example <em>API</em></h1></div>\n"):
            with self.subTest(title=title):
                self.write("README.md", title)
                self.assertNotIn("readme.title", self.codes())

    def test_code_formatted_title_is_not_missing(self):
        self.write("README.md", "# `ExampleAPI`\n")
        self.assertNotIn("readme.title", self.codes())

    def test_comment_delimiter_in_inline_example_does_not_hide_prose(self):
        self.write("README.md", "# Example\nUse `<!--` to open a comment.\nTBD\n")
        self.assertIn("readme.placeholder", self.codes())

    def test_blank_html_heading_is_not_a_title(self):
        self.write("README.md", "<h1>   </h1>\n")
        self.assertIn("readme.title", self.codes())

    def test_skipped_heading_has_source_line(self):
        self.write("README.md", "# Example\n\n### Details\n")
        item = next(f for f in self.report()["findings"] if f["rule_id"] == "heading.skipped_level")
        self.assertEqual(item["line"], 3)

    def test_multiple_titles_are_informational(self):
        self.write("README.md", "# One\n\n# Two\n")
        report = self.report()
        self.assertEqual(report["summary"], {"error": 0, "warning": 0, "info": 1})
        self.assertIn("heading.multiple_titles", self.codes(report))

    def test_placeholder_rule_and_line(self):
        self.write("README.md", "# Example\n\n{{PROJECT_NAME}} is TBD.\n")
        items = [f for f in self.report()["findings"] if f["rule_id"] == "readme.placeholder"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["line"], 3)

    def test_fenced_and_inline_code_do_not_trigger_prose_rules(self):
        self.write("README.md", "# Example\n\n```md\n### TODO\n<img src='x'>\n```\n~~~text\n{{NAME}}\n~~~\n`TODO` and ``{{NAME}} ` text`` are examples.\n")
        self.assertEqual(self.report()["findings"], [])

    def test_long_fence_needs_matching_length(self):
        self.write("README.md", "# Example\n````md\n```\nTODO\n````\n\nTBD\n")
        items = [f for f in self.report()["findings"] if f["rule_id"] == "readme.placeholder"]
        self.assertEqual([f["line"] for f in items], [7])

    def test_comments_ignore_prose_and_keep_later_findings(self):
        self.write("README.md", "# Example\n<!--\nTODO\n<img src='x'>\n-->\nTBD\n")
        items = self.report()["findings"]
        self.assertEqual([(f["rule_id"], f["line"]) for f in items], [("readme.placeholder", 6)])

    def test_fence_inside_comment_does_not_hide_later_text(self):
        self.write("README.md", "# Example\n<!--\n```\n-->\nTBD\n")
        self.assertIn("readme.placeholder", self.codes())

    def test_comment_marker_in_fence_does_not_hide_later_text(self):
        self.write("README.md", "# Example\n```html\n<!--\n```\nTBD\n")
        self.assertIn("readme.placeholder", self.codes())

    def test_markdown_empty_alt_is_information_not_failure(self):
        self.write("README.md", "# Example\n\n![](decoration.svg)\n![ ] [decoration]\n")
        report = self.report()
        self.assertEqual(report["summary"]["info"], 2)
        self.assertEqual(audit.exit_status(report, "warning"), 0)

    def test_html_missing_alt_differs_from_empty_alt(self):
        self.write("README.md", '# Example\n<img src="a.svg">\n<img src="b.svg" alt="">\n')
        report = self.report()
        self.assertEqual(report["summary"], {"error": 0, "warning": 1, "info": 1})
        self.assertIn("image.missing_alt", self.codes(report))
        self.assertIn("image.empty_alt", self.codes(report))

    def test_html_explicit_naming_or_decoration_avoids_missing_alt_finding(self):
        self.write("README.md", '# Example\n<img src="a" alt="Result">\n<img src="b" role="presentation">\n<img src="c" aria-label="Result">\n<img src="d" aria-hidden="true">\n')
        self.assertNotIn("image.missing_alt", self.codes())

    def test_empty_table_headers_are_distinguished_from_data_table(self):
        for header, expected in (("| | |", True), ("| Name | Result |", False)):
            with self.subTest(header=header):
                self.write("README.md", f"# Example\n\n{header}\n| --- | --- |\n| A | B |\n")
                self.assertEqual("table.empty_headers" in self.codes(), expected)

    def test_invalid_utf8_and_nul_report_encoding_without_leaking_content(self):
        for raw in (b"# Example\n\xffPRIVATE", b"# Example\n\x00PRIVATE"):
            with self.subTest(raw=raw):
                self.write("README.md", raw)
                report = self.report()
                self.assertIn("document.encoding", self.codes(report))
                self.assertNotIn("PRIVATE", json.dumps(report))

    def test_utf8_bom_is_accepted(self):
        self.write("README.md", b"\xef\xbb\xbf# Example\n")
        self.assertEqual(self.report()["findings"], [])

    def test_read_limit_is_enforced(self):
        self.write("README.md", "# Example\n" + "x" * audit.MAX_DOCUMENT_BYTES)
        report = self.report()
        self.assertIn("document.too_large", self.codes(report))
        self.assertNotIn("README.md", report["read_files"])

    def test_selected_file_symlink_is_not_followed(self):
        target = self.write("private-source.txt", "PRIVATE\n")
        (self.root / "README.md").unlink()
        try:
            (self.root / "README.md").symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {type(exc).__name__}")
        report = self.report()
        self.assertIn("path.non_regular", self.codes(report))
        self.assertNotIn("PRIVATE", json.dumps(report))
        self.assertNotIn("README.md", report["read_files"])

    def test_directory_symlink_is_not_followed(self):
        target = self.root / "elsewhere"
        target.mkdir()
        (target / "README.md").write_text("PRIVATE", encoding="utf-8")
        try:
            (self.root / ".github").symlink_to(target, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {type(exc).__name__}")
        report = self.report()
        self.assertIn("path.symlink", self.codes(report))
        self.assertEqual(report["documents"]["readme"], "README.md")

    @unittest.skipUnless(os.name == "nt", "NTFS junctions exist only on Windows")
    def test_directory_junction_is_not_followed(self):
        import _winapi
        with tempfile.TemporaryDirectory() as outside:
            (Path(outside) / "README.md").write_text("PRIVATE\n", encoding="utf-8")
            _winapi.CreateJunction(outside, str(self.root / "docs"))
            report = self.report()
            (self.root / "docs").rmdir()  # removes the junction, not its target
        self.assertIn("path.symlink", self.codes(report))
        self.assertNotIn("PRIVATE", json.dumps(report))
        self.assertNotIn("docs/README.md", report["read_files"])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO not supported on this platform")
    def test_fifo_is_rejected_without_blocking(self):
        (self.root / "README.md").unlink()
        os.mkfifo(self.root / "README.md")
        result = self.cli(str(self.root), "--format", "json")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("path.non_regular", self.codes(json.loads(result.stdout)))

    def test_unreadable_file_uses_generic_diagnostic(self):
        original_open = os.open
        def denied(path, *args, **kwargs):
            if Path(path).name == "README.md":
                raise PermissionError(f"private path {self.root}")
            return original_open(path, *args, **kwargs)
        with patch.object(audit.os, "open", side_effect=denied):
            report = self.report()
        self.assertIn("document.unreadable", self.codes(report))
        self.assertNotIn(str(self.root), json.dumps(report))

    def test_directory_inventory_limit_is_not_silent_truncation(self):
        with patch.object(audit, "MAX_DIRECTORY_ENTRIES", 2):
            with self.assertRaises(audit.AuditInputError):
                self.report()

    def test_does_not_execute_or_modify_the_target(self):
        self.write("setup.py", "raise RuntimeError('must not run')\n")
        before = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        self.report()
        after = {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}
        self.assertEqual(before, after)

    def test_invalid_target_exit_two_and_no_absolute_path(self):
        result = self.cli(str(self.root / "private-unavailable"), "--format", "json")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertNotIn(str(self.root), result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_file_target_is_invalid(self):
        with self.assertRaises(audit.AuditInputError):
            audit.audit_repository(self.root / "README.md")

    def test_cli_defaults_to_current_directory(self):
        result = self.cli("--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["documents"]["readme"], "README.md")

    def test_json_is_deterministic_and_contains_relative_paths_only(self):
        self.write("README.md", "# Example\n\nTBD\n### Details\n")
        first = self.cli(str(self.root), "--format", "json")
        second = self.cli(str(self.root), "--format", "json")
        self.assertEqual(first.stdout, second.stdout)
        self.assertNotIn(str(self.root), first.stdout)
        self.assertNotIn("timestamp", first.stdout)
        self.assertNotIn("score", json.loads(first.stdout))
        self.assertEqual(first.stderr, "")

    def test_cli_thresholds(self):
        self.write("README.md", "# Example\nTBD\n")
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(self.cli("--fail-on", "warning").returncode, 1)
        (self.root / "README.md").unlink()
        self.assertEqual(self.cli().returncode, 1)
        self.assertEqual(self.cli("--fail-on", "never").returncode, 0)
        self.assertEqual(self.cli("does-not-exist", "--fail-on", "never").returncode, 2)

    def test_documented_walkthrough_runs_with_expected_findings(self):
        demo = TOOL.parents[1] / "examples" / "repository-audit" / "demo.py"
        result = subprocess.run([sys.executable, str(demo)], capture_output=True,
                                text=True, check=False, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["before"]["summary"], {"error": 0, "warning": 4, "info": 1})
        self.assertEqual(report["after"]["summary"], {"error": 0, "warning": 1, "info": 1})
        self.assertEqual(report["after"]["rules"], ["license.missing", "contributing.missing"])

    def test_terminal_control_characters_in_path_are_escaped(self):
        report = {"findings": [audit.finding("fixture.rule", "info", "evil\x1b[31m\nname", 1, "Example", "Review")],
                  "summary": {"error": 0, "warning": 0, "info": 1}}
        text = audit.render_text(report)
        self.assertNotIn("\x1b", text)
        self.assertIn("\\u001b", text)
        self.assertIn("\\nname", text)


if __name__ == "__main__":
    unittest.main()
