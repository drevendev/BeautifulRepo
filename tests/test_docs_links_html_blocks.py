"""Black-box regressions for GFM raw HTML block types 3–5 in docs_links."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "docs_links.py"


class GfmRawHtmlLinksTests(unittest.TestCase):
    def check(self, markdown):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "README.md").write_text(markdown, encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--root", str(root)],
            text=True, capture_output=True, encoding="utf-8", check=False,
            timeout=30,
        )

    def test_matching_terminators_and_preserved_positions(self):
        result = self.check(
            "[Before](missing-before.md)\n"
            " <?begin\n"
            "[PI](missing-pi.md)\n"
            "<!DOCTYPE [Wrong end](missing-wrong-pi.md)\n"
            "[shadow]: missing-shadow.md\n"
            "?>\n"
            "<!DOCTYPE html\n"
            "[Declaration](missing-declaration.md)\n"
            "?? [Wrong end](missing-wrong-declaration.md)\n"
            "]] [Still declaration](missing-still-declaration.md)\n"
            ">\n"
            "<![CDATA[\n"
            "[CDATA](missing-cdata.md)\n"
            "?> [Wrong end](missing-wrong-cdata.md)\n"
            "> [Still CDATA](missing-still-cdata.md)\n"
            "]]>\n"
            "[After](missing-after.md)\n"
            "[shadow]\n"
        )
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("README.md:1: missing relative destination: 'missing-before.md'", result.stderr)
        self.assertIn("README.md:17: missing relative destination: 'missing-after.md'", result.stderr)
        for hidden in ("missing-pi.md", "missing-declaration.md", "missing-cdata.md",
                       "missing-shadow.md", "missing-wrong-", "missing-still-"):
            self.assertNotIn(hidden, result.stderr)
        self.assertIn("ERROR: 2 broken relative Markdown destination(s)", result.stderr)

    def test_same_line_closure_and_nonblock_adjacent_markdown(self):
        result = self.check(
            "  <?php [Hidden](inside-pi.md) ?> [Still hidden](end-pi.md)\n"
            "<!DOCTYPE html> [Hidden](inside-declaration.md)\n"
            "<![CDATA[ [Hidden](inside-cdata.md) ]]> [Hidden](end-cdata.md)\n"
            "Text <?php [Inline](missing-inline.md) ?>\n"
            "<!doctype [Lowercase](missing-lowercase.md)\n"
            "[Visible](missing-visible.md)\n"
        )
        self.assertEqual(1, result.returncode, result.stdout)
        for visible in ("missing-inline.md", "missing-lowercase.md", "missing-visible.md"):
            self.assertIn(visible, result.stderr)
        for hidden in ("inside-pi.md", "end-pi.md", "inside-declaration.md",
                       "inside-cdata.md", "end-cdata.md"):
            self.assertNotIn(hidden, result.stderr)
        self.assertIn("ERROR: 3 broken relative Markdown destination(s)", result.stderr)

    def test_unterminated_types_only_accept_their_own_closer(self):
        for opener, wrong in (
            ("<?unfinished", "]]>"),
            ("<!DECLARATION", "]]"),
            ("<![CDATA[", "?>"),
        ):
            with self.subTest(opener=opener):
                result = self.check(
                    "[Before](missing-before.md)\n" + opener + "\n"
                    + "[Inside](missing-inside.md)\n" + wrong + "\n"
                    + "[Still inside](missing-still.md)\n"
                )
                self.assertEqual(1, result.returncode, result.stdout)
                self.assertIn("missing-before.md", result.stderr)
                self.assertNotIn("missing-inside.md", result.stderr)
                self.assertNotIn("missing-still.md", result.stderr)
                self.assertIn("ERROR: 1 broken relative Markdown destination(s)", result.stderr)

    def test_fences_and_inline_entities_do_not_start_raw_blocks(self):
        result = self.check(
            "&#60;?plain text\n"
            "~~~md\n"
            "<![CDATA[\n"
            "<!DECLARATION\n"
            "<?php\n"
            "~~~\n"
            "[Visible](missing-after-fence.md)\n"
        )
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("README.md:7: missing relative destination: 'missing-after-fence.md'", result.stderr)
        self.assertIn("ERROR: 1 broken relative Markdown destination(s)", result.stderr)

    def test_types_in_containers_preserve_following_links(self):
        result = self.check(
            "> <?php\n"
            "> [Quoted](missing-quoted.md)\n"
            "> ?>\n"
            "> [After quote](missing-after-quote.md)\n"
            "\n"
            "- <![CDATA[\n"
            "  [Listed](missing-listed.md)\n"
            "  ]]>\n"
            "\n"
            "[After list](missing-after-list.md)\n"
        )
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertNotIn("missing-quoted.md", result.stderr)
        self.assertNotIn("missing-listed.md", result.stderr)
        self.assertIn("missing-after-quote.md", result.stderr)
        self.assertIn("missing-after-list.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
