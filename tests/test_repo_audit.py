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

    def test_vague_inline_link_text_is_informational_with_source_lines(self):
        self.write("README.md",
                   "# Example\n\n"
                   "[Here](guide.md)\n"
                   "[READ   MORE](details.md)\n"
                   "[click here](setup.md)\n"
                   "[This link](report.md)\n"
                   "[Complete setup guide](setup.md)\n")
        report = self.report()
        matches = [item for item in report["findings"]
                   if item["rule_id"] == "link.vague_text"]
        self.assertEqual([(item["line"], item["severity"]) for item in matches],
                         [(3, "info"), (4, "info"), (5, "info"), (6, "info")])
        self.assertEqual(audit.exit_status(report, "warning"), 0)
        self.assertEqual(audit.exit_status(report, "error"), 0)

    def test_vague_link_heuristic_ignores_images_code_comments_and_escapes(self):
        self.write("README.md",
                   "# Example\n"
                   "![here](diagram.svg)\n"
                   "Use `[read more](sample.md)` as a syntax example.\n"
                   "<!-- [click here](commented.md) -->\n"
                   "```md\n[here](fenced.md)\n```\n"
                   "\\[here](escaped.md)\n"
                   "[Descriptive installation instructions](install.md)\n")
        self.assertNotIn("link.vague_text", self.codes())

    def test_vague_link_finding_never_echoes_destination(self):
        self.write("README.md", "# Example\n[here](private-route-token.md)\n")
        report = self.report()
        self.assertIn("link.vague_text", self.codes(report))
        self.assertNotIn("private-route-token", json.dumps(report))
        self.assertIn("link.vague_text", audit.render_text(report))


    def test_vague_link_scan_is_bounded_for_many_unterminated_prefixes(self):
        # A malformed 420 KiB line remains inside the document's 500 KiB limit.
        # The CLI's 15-second timeout catches the formerly quadratic regex.
        self.write("README.md", "# Example\n" + "[here](" * 60000 + "\n")
        result = self.cli("--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("link.vague_text", self.codes(json.loads(result.stdout)))

    def test_vague_link_destination_cap_is_explicit(self):
        self.write("README.md", "# Example\n[here](" + "x" * 2048 + ")\n")
        self.assertIn("link.vague_text", self.codes())
        self.write("README.md", "# Example\n[here](" + "x" * 2049 + ")\n")
        self.assertNotIn("link.vague_text", self.codes())

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

    def test_html_role_token_list_honors_first_role_conservatively(self):
        self.write("README.md",
                   '# Example\n'
                   '<img src="a.svg" role="none presentation">\n'
                   '<img src="b.svg" role="  presentation none  ">\n'
                   '<img src="c.svg" role="img presentation">\n'
                   '<img src="d.svg" role="unsupported presentation">\n'
                   '<img src="e.svg" role="none presentation" role="img">\n'
                   '<img src="f.svg" role="img" role="none presentation">\n')
        findings = self.report()["findings"]
        self.assertEqual([f["line"] for f in findings
                          if f["rule_id"] == "image.missing_alt"], [4, 5, 7])
        self.assertEqual([f["line"] for f in findings
                          if f["rule_id"] == "image.duplicate_attribute"], [6, 7])

    def test_whitespace_only_aria_does_not_hide_missing_image_alt(self):
        self.write("README.md",
                   '# Example\n'
                   '<img src="a.svg" aria-label="   ">\n'
                   '<img src="b.svg" aria-labelledby="  \t ">\n'
                   '<img src="c.svg" aria-label=" " aria-labelledby="  ">\n'
                   '<img src="d.svg" aria-label=" Chart A ">\n'
                   '<img src="e.svg" aria-labelledby="chart-caption">\n')
        missing = [f["line"] for f in self.report()["findings"]
                   if f["rule_id"] == "image.missing_alt"]
        self.assertEqual(missing, [2, 3, 4])

    def test_duplicate_whitespace_aria_keeps_the_first_attribute(self):
        self.write("README.md",
                   '# Example\n'
                   '<img src="a.svg" aria-label="  " aria-label="Ignored">\n'
                   '<img src="b.svg" aria-labelledby=" " aria-labelledby="label">\n')
        findings = self.report()["findings"]
        self.assertEqual([f["line"] for f in findings
                          if f["rule_id"] == "image.missing_alt"], [2, 3])
        self.assertEqual([f["line"] for f in findings
                          if f["rule_id"] == "image.duplicate_attribute"], [2, 3])

    def test_duplicate_html_image_alt_uses_first_value(self):
        self.write("README.md",
                   '# Example\n'
                   '<img src="a.svg" alt="" alt="Ignored">\n'
                   '<img src="b.svg" alt="Actual result" alt="" />\n')
        report = self.report()
        duplicate = [f for f in report["findings"]
                     if f["rule_id"] == "image.duplicate_attribute"]
        empty = [f for f in report["findings"]
                 if f["rule_id"] == "image.empty_alt"]
        self.assertEqual([(f["line"], f["severity"]) for f in duplicate],
                         [(2, "warning"), (3, "warning")])
        self.assertEqual([f["line"] for f in empty], [2])
        self.assertNotIn("image.missing_alt", self.codes(report))

    def test_duplicate_html_image_role_and_aria_do_not_mask_missing_name(self):
        self.write("README.md",
                   '# Example\n'
                   '<img src="a.svg" aria-label="" aria-label="Ignored">\n'
                   '<img src="b.svg" role="img" role="presentation">\n'
                   '<img src="c.svg" role="presentation" role="img">\n'
                   '<img src="d.svg" aria-hidden="true" aria-hidden="false">\n')
        report = self.report()
        missing = [f["line"] for f in report["findings"]
                   if f["rule_id"] == "image.missing_alt"]
        duplicates = [f["line"] for f in report["findings"]
                      if f["rule_id"] == "image.duplicate_attribute"]
        self.assertEqual(missing, [2, 3])
        self.assertEqual(duplicates, [2, 3, 4, 5])

    def test_duplicate_html_image_src_does_not_hide_remote_dependency(self):
        remote = "https://raw.githubusercontent.com/acme/demo/main/sample.svg"
        self.write("README.md",
                   '# Example\n'
                   f'<img src="{remote}" src="local.svg" alt="Before">\n'
                   f'<img src="local.svg" src="{remote}" alt="After">\n')
        report = self.report()
        remote_findings = [f["line"] for f in report["findings"]
                           if f["rule_id"] == "readme.absolute_repo_asset"]
        duplicates = [f["line"] for f in report["findings"]
                      if f["rule_id"] == "image.duplicate_attribute"]
        self.assertEqual(remote_findings, [2])
        self.assertEqual(duplicates, [2, 3])

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


    def test_default_public_profile_preserves_text_format(self):
        implicit = self.report()
        explicit = audit.audit_repository(self.root, profile="public")
        self.assertEqual(implicit, explicit)
        self.assertEqual(audit.render_text(implicit), audit.render_text(explicit))
        self.assertNotIn("profile", implicit)
        result = self.cli("--format", "json")
        self.assertNotIn("profile", json.loads(result.stdout))

    def test_internal_and_private_license_and_owner_contact(self):
        (self.root / "LICENSE").unlink()
        for profile in ("internal", "private"):
            with self.subTest(profile=profile):
                report = audit.audit_repository(self.root, profile=profile)
                by_rule = {item["rule_id"]: item for item in report["findings"]}
                self.assertEqual(by_rule["license.missing"]["severity"], "info")
                self.assertIn("internal-use terms", by_rule["license.missing"]["remediation"])
                self.assertEqual(by_rule["readme.owner_contact"]["severity"], "warning")
                self.assertEqual(audit.exit_status(report, "warning"), 1)
        public = self.report()
        self.assertNotIn("readme.owner_contact", self.codes(public))
        self.assertEqual(next(f for f in public["findings"]
                              if f["rule_id"] == "license.missing")["severity"], "warning")
        self.write("README.md", "# Example\n\n## Owner and contact\n\nInternal Ops Team.\n")
        updated = audit.audit_repository(self.root, profile="internal")
        self.assertNotIn("readme.owner_contact", self.codes(updated))
        self.assertEqual(updated["summary"], {"error": 0, "warning": 0, "info": 1})

    def test_contact_must_be_a_section_not_a_vague_prose_mention(self):
        self.write("README.md", "# Example\n\nThe owner can get support later.\n")
        self.assertIn("readme.owner_contact", self.codes(
            audit.audit_repository(self.root, profile="internal")))
        self.write("README.md", "# Example\n\nSupport: #internal-help\n")
        self.assertNotIn("readme.owner_contact", self.codes(
            audit.audit_repository(self.root, profile="private")))

    def test_absolute_github_image_urls_in_markdown_reference_and_html(self):
        self.write("README.md",
                   "# Example\n\n"
                   "![inline](https://raw.githubusercontent.com/acme/app/main/banner.png)\n"
                   "![ref][banner]\n"
                   "[banner]: https://github.com/acme/app/raw/main/screenshot.png\n"
                   '<img src="https://github.com/acme/app/raw/main/chart.svg" alt="Chart">\n')
        for profile in audit.PROFILES:
            with self.subTest(profile=profile):
                report = audit.audit_repository(self.root, profile=profile)
                items = [f for f in report["findings"]
                         if f["rule_id"] == "readme.absolute_repo_asset"]
                self.assertEqual([f["line"] for f in items], [3, 4, 6])

    def test_absolute_image_rule_ignores_non_images_code_and_lookalike_hosts(self):
        tick = chr(96)
        self.write("README.md",
                   "# Example\n"
                   "[repo](https://raw.githubusercontent.com/u/r/main/README.md)\n"
                   "![safe](https://raw.githubusercontent.com.evil.example/img.png)\n"
                   "![local](assets/logo.svg)\n"
                   "\n"
                   f"{tick}![inline](https://raw.githubusercontent.com/u/r/main/code.png){tick}\n"
                   f"{tick * 3}markdown\n"
                   "![code](https://github.com/u/r/raw/main/code.png)\n"
                   f"{tick * 3}\n"
                   "<!-- ![comment](https://raw.githubusercontent.com/u/r/main/hide.png) -->\n")
        self.assertNotIn("readme.absolute_repo_asset", self.codes())

    def test_profile_validation_and_json_contract(self):
        self.assertEqual(self.cli("--profile", "hidden").returncode, 2)
        for profile in ("internal", "private"):
            with self.subTest(profile=profile):
                result = self.cli("--profile", profile, "--format", "json")
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["schema_version"], 1)
                self.assertEqual(report["profile"], profile)
        with self.assertRaises(audit.AuditInputError):
            audit.audit_repository(self.root, profile="hidden")


    def test_opt_in_source_spans_are_exact_and_legacy_default_is_unchanged(self):
        self.write("README.md", "# Example\nΩ [here](docs.md) TODO\n")
        original = self.report()
        spanned = audit.audit_repository(self.root, source_spans=True)
        self.assertEqual(spanned["schema_version"], 1)
        self.assertEqual(spanned["summary"], original["summary"])
        self.assertEqual(
            [{key: value for key, value in item.items() if key != "location"}
             for item in spanned["findings"]],
            original["findings"],
        )
        self.assertTrue(all("location" not in item for item in original["findings"]))
        entries = {item["rule_id"]: item for item in spanned["findings"]}
        self.assertEqual(entries["link.vague_text"]["path"], "README.md")
        self.assertEqual(entries["link.vague_text"]["line"], 2)
        self.assertEqual(entries["link.vague_text"]["location"], {
            "start": {"line": 2, "column": 3},
            "end": {"line": 2, "column": 18},
        })
        self.assertEqual(entries["readme.placeholder"]["location"], {
            "start": {"line": 2, "column": 19},
            "end": {"line": 2, "column": 23},
        })

    def test_source_spans_use_code_points_for_crlf_and_no_final_newline(self):
        self.write("README.md", "# Example\r\nπ [here](guide.md)\r\n".encode("utf-8"))
        report = audit.audit_repository(self.root, source_spans=True)
        link = next(x for x in report["findings"] if x["rule_id"] == "link.vague_text")
        self.assertEqual(link["location"], {
            "start": {"line": 2, "column": 3},
            "end": {"line": 2, "column": 19},
        })
        self.write("README.md", b"# Example\r\n[here](x.md)")
        report = audit.audit_repository(self.root, source_spans=True)
        link = next(x for x in report["findings"] if x["rule_id"] == "link.vague_text")
        self.assertEqual(link["location"], {
            "start": {"line": 2, "column": 1},
            "end": {"line": 2, "column": 13},
        })
        self.assertEqual(audit._source_span([0, 4, 8], 2, 5), {
            "start": {"line": 1, "column": 3},
            "end": {"line": 2, "column": 2},
        })

    def test_unknown_spans_are_null_and_hidden_code_is_not_reported(self):
        (self.root / "LICENSE").unlink()
        tick = chr(96)
        self.write("README.md",
                   "# Example\n"
                   "<!-- [here](hidden.md) TODO -->\n"
                   "[here](\nother.md)\n"
                   f"{tick * 3}\n[click here](fenced.md) TODO\n{tick * 3}\n"
                   "[Here](active.md)\n")
        report = audit.audit_repository(self.root, source_spans=True)
        self.assertEqual(len([f for f in report["findings"]
                              if f["rule_id"] == "link.vague_text"]), 1)
        self.assertNotIn("readme.placeholder", self.codes(report))
        missing = next(f for f in report["findings"] if f["rule_id"] == "license.missing")
        self.assertEqual(missing["path"], ".")
        self.assertIsNone(missing["line"])
        self.assertIsNone(missing["location"])

    def test_source_spans_cli_is_json_only_and_deterministic(self):
        self.write("README.md", "# Example\n[here](docs.md)\n")
        first = self.cli("--format", "json", "--source-spans")
        second = self.cli("--format", "json", "--source-spans")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout)["schema_version"], 1)
        self.assertIn('"location"', first.stdout)
        self.assertNotIn(str(self.root), first.stdout)
        self.assertEqual(self.cli("--source-spans").returncode, 2)
        default_report = json.loads(self.cli("--format", "json").stdout)
        self.assertTrue(all("location" not in f for f in default_report["findings"]))

    def test_oversized_document_with_spans_is_bounded_and_has_no_position(self):
        self.write("README.md", b"# Example\n" + b"a" * (audit.MAX_DOCUMENT_BYTES + 1))
        report = audit.audit_repository(self.root, source_spans=True)
        item = next(f for f in report["findings"]
                    if f["rule_id"] == "document.too_large")
        self.assertIsNone(item["line"])
        self.assertIsNone(item["location"])


if __name__ == "__main__":
    unittest.main()
