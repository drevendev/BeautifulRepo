"""Bounded multiline GFM reference definitions in the offline link checker."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "docs_links.py"


class MultilineReferenceTests(unittest.TestCase):
    def check(self, markdown: str, files=()):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_bytes(markdown.encode("utf-8"))
            for filename in files:
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-I", str(CHECKER), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )

    def test_destination_on_next_line_after_colon(self):
        result = self.check(
            "[Guide][doc]\n\n[doc]:\n  guides/intro.md\n",
            files=("guides/intro.md",),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 1 relative Markdown destination(s)", result.stdout)

    def test_destination_title_on_third_line_with_crlf(self):
        result = self.check(
            "![Cover][pic]\r\n\r\n[pic]:\r\n  images/cover.svg\r\n  \"A cover\"\r\n",
            files=("images/cover.svg",),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 1 relative Markdown destination(s)", result.stdout)

    def test_title_on_second_line(self):
        result = self.check(
            "[Details]\n\n[details]: <guides/manual.md>\n  'Manual'\n",
            files=("guides/manual.md",),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 1 relative Markdown destination(s)", result.stdout)

    def test_first_definition_wins_across_multiline_and_single_line(self):
        result = self.check(
            "[One][a] [Two][b]\n\n"
            "[a]:\n first.md\n[a]: missing-first.md\n"
            "[b]: second.md\n[b]:\n missing-second.md\n",
            files=("first.md", "second.md"),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 2 relative Markdown destination(s)", result.stdout)

    def test_bad_destination_reports_link_use_line(self):
        result = self.check("[Missing][ref]\n\n[ref]:\n  absent.md\n")
        self.assertEqual(1, result.returncode)
        self.assertIn("README.md:1: missing relative destination: 'absent.md'", result.stderr)
        self.assertNotIn("README.md:4: missing", result.stderr)

    def test_definition_does_not_interrupt_paragraph(self):
        result = self.check(
            "Paragraph\n[doc]:\n missing.md\n\n[doc]\n",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_blank_line_cannot_bridge_missing_destination(self):
        result = self.check("[doc]:\n\nmissing.md\n\n[doc]\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_invalid_continuation_does_not_swallow_another_link(self):
        result = self.check(
            "[doc]:\nfile.md extra\n\n[Visible](missing.md)\n",
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("README.md:4: missing relative destination: 'missing.md'", result.stderr)
        self.assertEqual(1, result.stderr.count("missing relative destination:"))

    def test_malformed_title_does_not_swallow_next_link(self):
        result = self.check(
            "[doc]: file.md\n\"bad title\" [Visible](missing.md)\n",
            files=("file.md",),
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("README.md:2: missing relative destination: 'missing.md'", result.stderr)

    def test_fences_quotes_lists_and_indented_code_do_not_define(self):
        result = self.check(
            "~~~\n[fence]:\n missing.md\n~~~\n\n"
            "> [quote]:\n> missing.md\n\n"
            "- [item]:\n  missing.md\n\n"
            "    [code]:\n    missing.md\n\n"
            "[fence] [quote] [item] [code]\n",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)

    def test_continuation_limit_fails_without_consuming_later_link(self):
        long_destination = "x" * 4097
        result = self.check(
            "[ref]:\n" + long_destination + "\n\n"
            "[ref]\n[Visible](missing.md)\n"
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("README.md:5: missing relative destination: 'missing.md'", result.stderr)
        self.assertEqual(1, result.stderr.count("missing relative destination:"))

    def test_many_invalid_continuations_remain_bounded(self):
        text = "".join("[ref]:\n" + "a" * 4100 + "\n\n" for _ in range(50))
        result = self.check(text + "[ref]\n")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("checked 0 relative Markdown destination(s)", result.stdout)


if __name__ == "__main__":
    unittest.main()
