"""Black-box tests for the offline GitHub Actions badge target checker."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "workflow_badges.py"
REPO = "drevendev/BeautifulRepo"
BADGE = "https://github.com/drevendev/BeautifulRepo/actions/workflows/quality.yml/badge.svg"


class WorkflowBadgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "README.md").write_text("# Example\n", encoding="utf-8")

    def run_tool(self, repo=REPO, *, require_badge=False):
        command = [sys.executable, "-I", str(SCRIPT), "--root", str(self.root),
                   "--repo", repo]
        if require_badge:
            command.append("--require-badge")
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def workflow(self, name="quality.yml"):
        path = self.root / ".github/workflows" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("name: Quality\n", encoding="utf-8")
        return path

    def test_beautifulrepo_automatically_checks_its_own_workflow_badge(self):
        command = "python -I tools/workflow_badges.py --root . --repo " + REPO + " --require-badge"
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: " + command, workflow)
        for page in ("README.md", "CONTRIBUTING.md"):
            with self.subTest(page=page):
                self.assertIn(command, (ROOT / page).read_text(encoding="utf-8"))
        result = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--root", str(ROOT), "--repo", REPO,
             "--require-badge"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checked 1 same-repository workflow badge(s)", result.stdout)

    def test_present_workflow_markdown_badge_succeeds(self):
        self.workflow()
        (self.root / "README.md").write_text(
            f"# Example\n![Build]({BADGE}?branch=master)\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 1 same-repository workflow badge(s)", out.stdout)

    def test_missing_workflow_html_badge_fails_at_line(self):
        (self.root / "README.md").write_text(
            f'# Example\n<a href="./">\n  <img alt="CI status" src="{BADGE}">\n</a>\n',
            encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)
        self.assertIn("README.md:3: missing or redirected workflow: ", out.stderr)
        self.assertIn(".github/workflows/quality.yml", out.stderr)

    def test_existing_workflow_wrong_case_is_not_accepted(self):
        self.workflow("Quality.yml")
        (self.root / "README.md").write_text(f"![CI]({BADGE})\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)

    def test_external_and_unrelated_badges_are_out_of_scope(self):
        (self.root / "README.md").write_text(
            "![CI](https://github.com/other/project/actions/workflows/quality.yml/badge.svg)\n"
            "![License](https://img.shields.io/badge/license-MIT-green.svg)\n",
            encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 0", out.stdout)

    def test_fences_comments_and_inline_code_are_not_evidence(self):
        (self.root / "README.md").write_text(
            "```md\n" + f"![False]({BADGE})\n" + "```\n"
            + "<!--\n" + f"![Hidden]({BADGE})\n" + "-->\n"
            + f"Use `![Sample]({BADGE})` in your docs.\n",
            encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 0", out.stdout)

    def test_redirected_workflow_is_not_accepted(self):
        other = self.root / "outside.yml"
        other.write_text("name: Not local\n", encoding="utf-8")
        path = self.root / ".github/workflows/quality.yml"
        path.parent.mkdir(parents=True)
        try:
            path.symlink_to(other)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {type(exc).__name__}")
        (self.root / "README.md").write_text(f"![CI]({BADGE})\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)
        self.assertIn("missing or redirected", out.stderr)

    def test_unsupported_escaped_name_fails_closed(self):
        (self.root / "README.md").write_text(
            "![CI](https://github.com/drevendev/BeautifulRepo/actions/workflows/"
            "..%2Fprivate.yml/badge.svg)\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)
        self.assertIn("unsupported", out.stderr)

    def test_malformed_percent_encoded_workflow_name_is_an_error(self):
        (self.root / "README.md").write_text(
            "![CI](https://github.com/drevendev/BeautifulRepo/actions/workflows/"
            "%FF.yml/badge.svg)\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)
        self.assertIn("not valid UTF-8", out.stderr)

    def test_crlf_preserves_badge_line_number(self):
        (self.root / "README.md").write_bytes((
            "# Example\r\n\r\n![CI](" + BADGE + ")\r\n").encode("utf-8"))
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)
        self.assertIn("README.md:3:", out.stderr)

    def test_absent_readme_is_input_error(self):
        (self.root / "README.md").unlink()
        out = self.run_tool()
        self.assertEqual(out.returncode, 2)
        self.assertIn("README.md is missing", out.stderr)

    def test_invalid_utf8_is_input_error(self):
        (self.root / "README.md").write_bytes(b"# Example\n\xff")
        out = self.run_tool()
        self.assertEqual(out.returncode, 2)

    def test_no_project_code_is_run(self):
        self.workflow()
        (self.root / "README.md").write_text(f"![CI]({BADGE})\n", encoding="utf-8")
        (self.root / "site.py").write_text("raise RuntimeError('must not run')\n")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_no_badges_is_valid_not_proof(self):
        self.workflow()
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 0", out.stdout)

    def test_required_badge_rejects_zero_matches_without_changing_default(self):
        self.workflow()
        out = self.run_tool(require_badge=True)
        self.assertEqual(out.returncode, 1)
        self.assertIn("no same-repository GitHub Actions workflow badge", out.stderr)
        self.assertIn("--require-badge", out.stderr)
        self.assertIn("0 same-repository workflow badge(s)", out.stderr)
        (self.root / "README.md").write_text(
            "![Badge](https://img.shields.io/badge/build-green-green.svg)\n",
            encoding="utf-8")
        out = self.run_tool(require_badge=True)
        self.assertEqual(out.returncode, 1)
        self.assertIn("--require-badge", out.stderr)

    def test_required_badge_accepts_reference_style_target(self):
        self.workflow()
        (self.root / "README.md").write_text(
            f"![Build][status]\n[status]: {BADGE}\n", encoding="utf-8")
        out = self.run_tool(require_badge=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 1", out.stdout)

    def test_shortcut_reference_image_uses_definition_and_accepts_real_workflow(self):
        self.workflow()
        (self.root / "README.md").write_text(
            f"![Build]\n[build]: {BADGE}\n", encoding="utf-8")
        out = self.run_tool(require_badge=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 1 same-repository workflow badge(s)", out.stdout)

    def test_shortcut_reference_missing_workflow_reports_image_line(self):
        (self.root / "README.md").write_text(
            "# Title\n\n![Build]\n"
            f"[BUILD]: {BADGE.replace('quality.yml', 'missing.yml')}\n",
            encoding="utf-8")
        out = self.run_tool(require_badge=True)
        self.assertEqual(out.returncode, 1)
        self.assertIn("README.md:3: missing or redirected workflow", out.stderr)
        self.assertIn("missing.yml", out.stderr)

    def test_shortcut_is_not_double_counted_with_inline_or_explicit_references(self):
        self.workflow()
        (self.root / "README.md").write_text(
            f"![Inline]({BADGE})\n"
            "![Explicit][ci]\n"
            f"[ci]: {BADGE}\n"
            "![Undefined]\n",
            encoding="utf-8")
        out = self.run_tool(require_badge=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 2 same-repository workflow badge(s)", out.stdout)

    def test_shortcut_reference_inside_code_is_not_evidence(self):
        (self.root / "README.md").write_text(
            "~~~md\n![CI]\n~~~\n"
            "`![CI]`\n"
            f"[CI]: {BADGE}\n", encoding="utf-8")
        out = self.run_tool(require_badge=True)
        self.assertEqual(out.returncode, 1)
        self.assertIn("no same-repository GitHub Actions workflow badge", out.stderr)

    def test_reference_style_badge_checks_workflow_at_image_line(self):
        (self.root / "README.md").write_text(
            "# Demo\n\n![Build][ci]\n\n"
            f'[ci]: <{BADGE}> "CI status"\n', encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)
        self.assertIn("README.md:3: missing or redirected workflow", out.stderr)

    def test_reference_style_label_is_casefolded_and_whitespace_collapsed(self):
        self.workflow()
        (self.root / "README.md").write_text(
            "![Build][ BUILD  CHECK ]\n"
            f"[build check]: {BADGE}\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 1", out.stdout)

    def test_reference_style_empty_label_uses_image_alt_text(self):
        self.workflow()
        (self.root / "README.md").write_text(
            f"![CI][]\n[ci]: <{BADGE}>\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 1", out.stdout)

    def test_first_reference_definition_wins(self):
        self.workflow()
        missing_badge = BADGE.replace("quality.yml", "gone.yml")
        (self.root / "README.md").write_text(
            "![CI][build]\n"
            f"[build]: {missing_badge}\n"
            f"[build]: {BADGE}\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 1)
        self.assertIn("gone.yml", out.stderr)

    def test_unreferenced_definition_and_quoted_example_are_not_badges(self):
        (self.root / "README.md").write_text(
            f"[unused]: {BADGE}\n"
            "~~~markdown\n"
            "![Build][ci]\n"
            "~~~\n"
            f"[ci]: {BADGE}\n", encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 0", out.stdout)

    def test_badges_in_html_and_markdown_both_checked(self):
        self.workflow()
        (self.root / "README.md").write_text(
            f"![CI]({BADGE})\n<img src=\"{BADGE}\" alt=\"CI\">\n",
            encoding="utf-8")
        out = self.run_tool()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("checked 2", out.stdout)


if __name__ == "__main__":
    unittest.main()
