"""Black-box, network-free tests for the source-only case permalink preflight."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/source_pins.py"
SOURCE = "drevendev/HungryCrab"
SHA = "d20850c4e71382c796c4b4dac554137ebcb7e937"
TREE = f"https://github.com/{SOURCE}/tree/{SHA}"
README = f"https://github.com/{SOURCE}/blob/{SHA}/README.md#L1-L20"


def check(contents: str | None, *, commit: str = SHA, repository: str = SOURCE):
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "case.md"
        if contents is not None:
            path.write_text(contents, encoding="utf-8")
        return invoke(path, commit=commit, repository=repository)


def invoke(path: Path, *, commit: str = SHA, repository: str = SOURCE):
    return subprocess.run(
        [
            sys.executable, "-I", str(TOOL), "--case", str(path),
            "--repository", repository, "--commit", commit,
        ],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )


class SourcePinTests(unittest.TestCase):
    def test_pinned_tree_and_readme_pass_without_network(self):
        result = check(f"# Case\n[revision]({TREE})\n[README]({README})\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 source permalinks", result.stdout)
        self.assertIn("NOT CHECKED", result.stdout)

    def test_real_hungrycrab_case_is_consistent(self):
        result = invoke(ROOT / "case-studies/hungrycrab-first-command.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("NOT CHECKED", result.stdout)

    def test_moving_branch_is_not_accepted(self):
        result = check(f"[tree]({TREE})\n[README](https://github.com/{SOURCE}/blob/master/README.md)\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("moving revision", result.stderr)

    def test_other_commit_is_not_accepted(self):
        other = "1" * 40
        result = check(f"[tree]({TREE})\n[README](https://github.com/{SOURCE}/blob/{other}/README.md)\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("different or moving revision", result.stderr)

    def test_unrelated_github_links_are_ignored(self):
        result = check(f"[tree]({TREE})\n[README]({README})\n"
                       f"[other](https://github.com/octocat/Hello-World/blob/main/README.md)\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_fake_github_host_does_not_count(self):
        result = check(
            f"[tree](https://github.com.evil.invalid/{SOURCE}/tree/{SHA})\n"
            f"[README](https://github.com.evil.invalid/{SOURCE}/blob/{SHA}/README.md)\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("no pinned tree/blob links", result.stderr)

    def test_fenced_example_is_not_evidence(self):
        result = check(
            f"~~~md\n[tree]({TREE})\n[README]({README})\n~~~\n"
            f"Actual: [README]({README})\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 source permalinks", result.stdout)

    def test_inline_code_links_do_not_count_as_source_evidence(self):
        result = check(f"`[tree]({TREE}) [README]({README})`")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no pinned tree/blob links", result.stderr)
        self.assertIn("no source README.md", result.stderr)

    def test_moving_revision_in_inline_code_does_not_fail_real_links(self):
        result = check(
            f"[tree]({TREE})\n[README]({README})\n"
            f"Example: `https://github.com/{SOURCE}/blob/master/README.md`\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 source permalinks", result.stdout)

    def test_multi_backtick_span_with_inner_tick_is_ignored(self):
        result = check(
            f"[tree]({TREE}) [README]({README})\n"
            f"``[bad](https://github.com/{SOURCE}/blob/main/README.md) "
            f"` literal``\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 source permalinks", result.stdout)

    def test_escaped_or_unclosed_backticks_do_not_hide_real_links(self):
        for prefix in (r"\`", "`"):
            with self.subTest(prefix=prefix):
                result = check(f"{prefix}[tree]({TREE}) [README]({README})")
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_link_outside_inline_code_still_fails_on_wrong_revision(self):
        result = check(
            f"`[ignored]({README})`\n"
            f"[README](https://github.com/{SOURCE}/blob/main/README.md)\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("different or moving revision", result.stderr)

    def test_missing_readme_is_error(self):
        result = check(f"[tree]({TREE})\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md", result.stderr)

    def test_short_sha_and_invalid_repository_are_usage_errors(self):
        for commit, repository in (("abc1234", SOURCE), (SHA, "not-a-repository")):
            with self.subTest(commit=commit, repository=repository):
                result = check(f"[README]({README})", commit=commit, repository=repository)
                self.assertEqual(result.returncode, 2)

    def test_missing_or_oversize_case_is_incomplete(self):
        missing = check(None)
        self.assertEqual(missing.returncode, 2)
        oversized = check(f"[README]({README})\n" + ("x" * (256 * 1024)))
        self.assertEqual(oversized.returncode, 2)
        self.assertIn("256 KiB", oversized.stderr)

    def test_linked_input_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / "original.md"
            original.write_text(f"[README]({README})\n", encoding="utf-8")
            link = root / "linked.md"
            try:
                link.symlink_to(original)
            except (OSError, NotImplementedError):
                self.skipTest("cannot create symlink on this filesystem")
            result = invoke(link)
            self.assertEqual(result.returncode, 2)
            self.assertIn("redirected", result.stderr)

    def test_hardlinked_input_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / "original.md"
            original.write_text(f"[README]({README})\n", encoding="utf-8")
            alias = root / "alias.md"
            try:
                os.link(original, alias)
            except (OSError, NotImplementedError):
                self.skipTest("cannot create hard link on this filesystem")
            result = invoke(alias)
            self.assertEqual(result.returncode, 2)
            self.assertIn("single-linked", result.stderr)


if __name__ == "__main__":
    unittest.main()
