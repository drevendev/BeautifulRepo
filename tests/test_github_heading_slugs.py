"""Heading anchors match the ones GitHub generates for Markdown documents.

Every expected value below was read back from GitHub's Markdown API
(`gh api markdown -f mode=markdown`, `id="user-content-..."`) on 2026-10-23.
Recheck them there if GitHub's anchor rules ever appear to change.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_links  # noqa: E402
import html_navigation  # noqa: E402

GITHUB_ANCHORS = {
    "Terms & Conditions": "terms--conditions",
    "A  B": "a--b",
    "a &lt; b &gt; c": "a--b--c",
    "Using _foo_ safely": "using-foo-safely",
    "The __init__ method": "the-init-method",
    "हिन्दी": "हिन्दी",
    "The `__init__` method": "the-__init__-method",
    "snake_case_name": "snake_case_name",
    r"\_escaped\_": "_escaped_",
    "Link [text](x.md) here": "link-text-here",
    "Logo ![alt](logo.png) here": "logo--here",
    "Ünïcödé Çafé": "ünïcödé-çafé",
    "C# and F#": "c-and-f",
    "Tab\there": "tabhere",
    "Smile :smile: now": "smile-smile-now",
    "1.2.3 Release": "123-release",
    "Über *bold* and **strong**": "über-bold-and-strong",
    "`<token>` value": "token-value",
    "x &amp; y": "x--y",
    "Emoji \U0001F389 party": "emoji--party",
    "Non breaking": "nonbreaking",
    "Trailing #": "trailing",
    "Run `python -m unittest`": "run-python--m-unittest",
    "Use ``<a href>`` with <em>HTML</em>": "use-a-href-with-html",
}


class GitHubHeadingSlugTests(unittest.TestCase):
    def ids(self, markdown: str) -> set[str]:
        masked = docs_links._mask_markdown_code(markdown)
        return html_navigation.heading_ids(masked, set(), markdown)

    def test_each_heading_gets_githubs_anchor(self):
        for heading, anchor in GITHUB_ANCHORS.items():
            with self.subTest(heading=heading):
                self.assertEqual({anchor}, self.ids(f"## {heading}\n"))

    def test_a_comment_leaves_both_spaces_and_duplicates_get_suffixes(self):
        self.assertEqual({"a--b", "a--b-1"}, self.ids("## A  B\n\n## A <!-- note --> B\n"))
        self.assertEqual({"dup", "dup-1"}, self.ids("## Dup\n\n## Dup\n"))

    def test_a_link_to_a_collapsed_anchor_is_reported(self):
        markdown = "## Terms & Conditions\n\n[ok](#terms--conditions) [dead](#terms-conditions)\n"
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "README.md").write_text(markdown, encoding="utf-8")
            errors, checked, _ = html_navigation.check_repo(Path(folder))
        self.assertEqual(2, checked)
        self.assertEqual(["README.md:3: missing section anchor: '#terms-conditions'"], errors)


if __name__ == "__main__":
    unittest.main()
