"""Black-box regressions for the offline reviewed-action pin consistency check."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "action_pins.py"
CHECKOUT = "3d3c42e5aac5ba805825da76410c181273ba90b1"
PYTHON = "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0"


class ActionPinTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / ".github/workflows").mkdir(parents=True)
        self.pins = {
            "actions/checkout": {"sha": CHECKOUT, "version": "v7.0.1", "reviewed": "2026-10-05"},
            "actions/setup-python": {"sha": PYTHON, "version": "v7.1.0", "reviewed": "2026-10-29"},
        }
        self.write_manifest()
        self.write_workflow()

    def write_manifest(self):
        (self.root / ".github/action-pins.json").write_text(
            json.dumps(self.pins, indent=2) + "\n", encoding="utf-8")

    def write_workflow(self, contents=None):
        if contents is None:
            contents = (
                "name: Sample\nsteps:\n"
                f"  - uses: actions/checkout@{CHECKOUT} # v7.0.1 ref inspected 2026-10-05\n"
                f"  - uses: actions/setup-python@{PYTHON} # v7.1.0 ref inspected 2026-10-29\n"
                "  - uses: ./\n"
                "  - uses: docker://alpine:3.19\n"
            )
        (self.root / ".github/workflows/ci.yml").write_text(contents, encoding="utf-8")

    def run_tool(self):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(self.root)],
                              cwd=self.root, capture_output=True, text=True, check=False)

    def test_current_fixture_matches_reviewed_manifest(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 reviewed external action references", result.stdout)

    def test_single_and_double_quoted_uses_are_checked_normally(self):
        source = (self.root / ".github/workflows/ci.yml").read_text()
        source = source.replace(
            f"actions/checkout@{CHECKOUT}",
            f"'actions/checkout@{CHECKOUT}'",
        ).replace(
            f"actions/setup-python@{PYTHON}",
            f'"actions/setup-python@{PYTHON}"',
        ).replace("- uses: ./", '- uses: "./"').replace(
            "- uses: docker://alpine:3.19",
            "- uses: 'docker://alpine:3.19'",
        )
        self.write_workflow(source)
        result = self.run_tool()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("2 reviewed external action references", result.stdout)

    def test_quoted_uses_mapping_keys_are_checked(self):
        source = (self.root / ".github/workflows/ci.yml").read_text()
        source = source.replace("- uses: actions/checkout@", '- "uses": actions/checkout@')
        source = source.replace("- uses: actions/setup-python@", "- 'uses': actions/setup-python@")
        self.write_workflow(source)
        clean = self.run_tool()
        self.assertEqual(0, clean.returncode, clean.stderr)
        self.assertIn("2 reviewed external action references", clean.stdout)

        self.write_workflow(source.replace(f"actions/checkout@{CHECKOUT}",
                                           "actions/checkout@main"))
        unpinned = self.run_tool()
        self.assertEqual(1, unpinned.returncode)
        self.assertIn("40-character commit SHA", unpinned.stderr)

        self.write_workflow(source.replace(f"actions/setup-python@{PYTHON}",
                                           f"unreviewed/action@{PYTHON}"))
        unreviewed = self.run_tool()
        self.assertEqual(1, unreviewed.returncode)
        self.assertIn("no reviewed manifest entry", unreviewed.stderr)

    def test_windows_crlf_workflows_remain_visible_to_pin_checker(self):
        # write_bytes preserves exact CRLF on Windows as well as POSIX.
        path = self.root / ".github/workflows/ci.yml"
        source = path.read_text(encoding="utf-8")
        path.write_bytes(source.replace("\n", "\r\n").encode("utf-8"))
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 reviewed external action references", result.stdout)

    def test_mixed_lf_crlf_cannot_hide_unpinned_or_unreviewed_actions(self):
        path = self.root / ".github/workflows/ci.yml"
        source = path.read_text(encoding="utf-8")
        for key, reference, expected in (
            ("uses", "other/unsafe@v1", "40-character commit SHA"),
            ('"uses"', "other/unsafe@v1", "40-character commit SHA"),
            ("'uses'", f"other/unsafe@{CHECKOUT}", "no reviewed manifest entry"),
        ):
            with self.subTest(key=key, reference=reference):
                path.write_bytes((source + f"  - {key}: {reference}\r\n").encode("utf-8"))
                result = self.run_tool()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(expected, result.stderr)

    def test_quoted_unpinned_and_unreviewed_uses_still_fail(self):
        source = (self.root / ".github/workflows/ci.yml").read_text()
        self.write_workflow(source.replace(
            f"actions/checkout@{CHECKOUT}",
            "'actions/checkout@v7'",
        ))
        result = self.run_tool()
        self.assertEqual(1, result.returncode)
        self.assertIn("40-character commit SHA", result.stderr)

        self.write_workflow(source.replace(
            f"actions/checkout@{CHECKOUT}",
            f'"other/unreviewed@{CHECKOUT}"',
        ))
        result = self.run_tool()
        self.assertEqual(1, result.returncode)
        self.assertIn("no reviewed manifest entry", result.stderr)

    def test_dependabot_sha_bump_without_review_fails(self):
        source = (self.root / ".github/workflows/ci.yml").read_text()
        self.write_workflow(source.replace(CHECKOUT, "a" * 40))
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn("SHA differs from reviewed manifest", result.stderr)

    def test_stale_annotation_fails(self):
        source = (self.root / ".github/workflows/ci.yml").read_text()
        self.write_workflow(source.replace("v7.1.0 ref inspected 2026-10-29",
                                           "v7.0.0 ref inspected 2026-10-05"))
        self.assertIn("annotation must be", self.run_tool().stderr)

    def test_unpinned_tag_fails(self):
        source = (self.root / ".github/workflows/ci.yml").read_text()
        self.write_workflow(source.replace(f"checkout@{CHECKOUT}", "checkout@v7"))
        self.assertIn("40-character commit SHA", self.run_tool().stderr)

    def test_unknown_action_requires_review(self):
        source = (self.root / ".github/workflows/ci.yml").read_text()
        self.write_workflow(source + f"  - uses: other/action@{CHECKOUT} # v7.0.1 ref inspected 2026-10-05\n")
        self.assertIn("no reviewed manifest entry", self.run_tool().stderr)

    def test_unused_manifest_entry_fails(self):
        self.pins["owner/extra"] = {"sha": CHECKOUT, "version": "v1.0.0", "reviewed": "2026-10-29"}
        self.write_manifest()
        self.assertIn("entry is not used", self.run_tool().stderr)

    def test_duplicate_json_key_fails_closed(self):
        content = (self.root / ".github/action-pins.json").read_text()
        content = content.replace('"version": "v7.0.1",',
                                  '"version": "v7.0.1", "version": "v7.1.0",')
        (self.root / ".github/action-pins.json").write_text(content)
        self.assertEqual(self.run_tool().returncode, 2)

    def test_manifest_symlink_fails_closed(self):
        original = self.root / ".github/action-pins.json"
        other = self.root / "elsewhere.json"
        original.rename(other)
        try:
            original.symlink_to(other)
        except OSError as exc:
            self.skipTest(f"no symlink support: {exc}")
        self.assertEqual(self.run_tool().returncode, 2)

    def test_github_parent_directory_symlink_outside_root_fails_closed(self):
        # A symlink on .github bypassed the old workflows-only symlink check.
        external = tempfile.TemporaryDirectory()
        self.addCleanup(external.cleanup)
        source = self.root / ".github"
        outside = Path(external.name) / "github-outside-root"
        source.rename(outside)
        try:
            source.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlinks unavailable: {exc}")
        result = self.run_tool()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(".github must be an ordinary directory", result.stderr)
        self.assertTrue((outside / "workflows/ci.yml").is_file())

    def test_missing_manifest_or_workflow_fails_closed(self):
        (self.root / ".github/action-pins.json").unlink()
        self.assertEqual(self.run_tool().returncode, 2)
        self.write_manifest()
        (self.root / ".github/workflows/ci.yml").unlink()
        self.assertEqual(self.run_tool().returncode, 2)

    def test_malformed_review_date_fails_closed(self):
        self.pins["actions/checkout"]["reviewed"] = "2026-02-30"
        self.write_manifest()
        self.assertEqual(self.run_tool().returncode, 2)

    def test_no_target_code_is_executed(self):
        (self.root / "main.py").write_text("raise RuntimeError('never run')\n")
        self.assertEqual(self.run_tool().returncode, 0)


if __name__ == "__main__":
    unittest.main()
