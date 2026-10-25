"""Offline contract for HTML navigation and fragments in Markdown documents."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import html_navigation  # noqa: E402


class HtmlNavigationTests(unittest.TestCase):
    def check(self, markdown: str, assets: dict[str, str] | None = None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text(markdown, encoding="utf-8")
            for path, body in (assets or {}).items():
                item = root / path
                item.parent.mkdir(parents=True, exist_ok=True)
                item.write_text(body, encoding="utf-8")
            return html_navigation.check_repo(root)

    def test_html_navigation_and_heading_fragment_resolve(self):
        errors, checked, documents = self.check(
            '<a href="#start-here">Start</a>\n'
            '<img src="assets/diagram.svg" alt="Diagram">\n'
            '<source srcset="assets/a.svg 1x, assets/b.svg 2x">\n'
            '<a href="guide.md#usage">Guide</a>\n'
            '<a href="https://example.org/not-local">External</a>\n'
            '## Start here\n',
            {"assets/diagram.svg": "svg", "assets/a.svg": "svg", "assets/b.svg": "svg",
             "guide.md": "# Usage\n"},
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 5)
        self.assertEqual(documents, 2)

    def test_html_img_requires_explicit_alt_but_empty_can_be_decorative(self):
        errors, checked, documents = self.check(
            '<img src="missing-alt.svg">\n'
            '<img src="decorative.svg" alt="">\n'
            '<img src="informative.svg" alt="Inputs and output">\n'
            '<picture><source srcset="dark.svg"><img src="fallback.svg"></picture>\n',
            {
                "missing-alt.svg": "svg",
                "decorative.svg": "svg",
                "informative.svg": "svg",
                "dark.svg": "svg",
                "fallback.svg": "svg",
            },
        )
        self.assertEqual(checked, 5)
        self.assertEqual(documents, 1)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(any("README.md:1: HTML img missing alt attribute" in e
                            for e in errors))
        self.assertTrue(any("README.md:4: HTML img missing alt attribute" in e
                            for e in errors))


    def test_duplicate_html_attributes_cannot_hide_broken_targets(self):
        errors, checked, documents = self.check(
            '# Intro\\n'
            '<a href="missing.md" href="#intro">Bad link</a>\\n'
            '<img src="missing.svg" src="present.svg" alt="Diagram">\\n'
            '<img src="present.svg" alt="" alt="Description">\\n'
            '<span id="original" id="alias"></span>\\n'
            '<a href="#alias">Bad anchor</a>\\n',
            {"present.svg": "svg"},
        )
        self.assertEqual(checked, 4)
        self.assertEqual(documents, 1)
        for expected in (
            "README.md:2: HTML a duplicate href attribute",
            "README.md:3: HTML img duplicate src attribute",
            "README.md:4: HTML img duplicate alt attribute",
            "README.md:5: HTML span duplicate id attribute",
            "missing HTML a destination: 'missing.md'",
            "missing HTML img destination: 'missing.svg'",
            "missing section anchor: '#alias'",
        ):
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_duplicate_html_attributes_ignore_inactive_code(self):
        errors, checked, documents = self.check(
            '`<a href="missing.md" href="#real">example</a>`\\n'
            '```html\\n<img src="missing.svg" src="present.svg">\\n```\\n'
            '## Real\\n'
            '<a href="#real">Active</a>\\n',
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)
        self.assertEqual(documents, 1)

    def test_inline_code_heading_text_is_part_of_github_anchor(self):
        errors, checked, _ = self.check(
            '## Run `python -m unittest`\n'
            '[Jump](#run-python--m-unittest)\n'
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_inline_code_looking_like_html_keeps_visible_heading_text(self):
        examples = (
            ("## Configure `<token>`\n", "configure-token"),
            ("## Use ``<a href>`` with <em>HTML</em>\n", "use-a-href-with-html"),
        )
        for markdown, expected in examples:
            with self.subTest(markdown=markdown):
                # The source checker masks code spans to prevent spurious HTML
                # links. Recreate only that mask for the heading-slug contract.
                masked = html_navigation.docs_links._mask_markdown_code(markdown)
                found = html_navigation.heading_ids(masked, set(), markdown)
                self.assertIn(expected, found)

    def test_data_url_does_not_hide_later_local_srcset_asset(self):
        errors, checked, _ = self.check(
            '<source srcset="data:image/png;base64,AAAA 1x, missing.svg 2x">\n'
        )
        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing.svg", errors[0])

    def test_srcset_candidates_keep_commas_inside_data_urls(self):
        urls = html_navigation.srcset_urls(
            "data:image/png;base64,AAAA 1x, assets/real.svg 2x, "
            "assets/second.svg, assets/third.svg 3x"
        )
        self.assertEqual(urls, [
            "data:image/png;base64,AAAA", "assets/real.svg",
            "assets/second.svg", "assets/third.svg",
        ])

    def test_missing_asset_and_section_are_reported(self):
        errors, _, _ = self.check('<a href="#missing">Bad</a>\n<img src="no.png" alt="Broken demo">\n## Present\n')
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("missing section anchor" in msg for msg in errors))
        self.assertTrue(any("missing HTML img destination" in msg for msg in errors))

    def test_fenced_and_inline_examples_are_not_live_html(self):
        errors, checked, _ = self.check(
            '```html\n<picture><img src="does-not-exist.svg"></picture>\n```\n'
            '`<a href="missing.md">not active</a>`\n'
            '<!-- <img src="also-missing.png"> -->\n'
            '<a href="#real">Active</a>\n'
            '## Real\n'
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_backslash_escaped_html_openers_are_literal(self):
        errors, checked, _ = self.check(
            '\\<img src="missing.png">\n'
            '\\<a href="#missing">not active</a>\n'
            '<img src="real.svg" alt="Real">\n',
            {"real.svg": "svg"},
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_duplicate_markdown_headings_and_explicit_html_ids(self):
        errors, _, _ = self.check(
            '# Overview\n# Overview\n<a href="#overview-1">Second</a>\n'
            '<span id="handmade"></span><a href="#handmade">Explicit</a>\n'
            '[Markdown fragment](#overview)\n'
        )
        self.assertEqual(errors, [])

    def test_generated_heading_suffix_does_not_collide_with_literal_suffix(self):
        errors, checked, _ = self.check(
            "## Intro\n## Intro-1\n## Intro\n"
            "[Third heading](#intro-2)\n"
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)
        self.assertEqual(
            html_navigation.heading_ids("## Intro\n## Intro-1\n## Intro\n", set()),
            {"intro", "intro-1", "intro-2"},
        )

    def test_named_html_anchor_is_resolved(self):
        errors, checked, _ = self.check(
            '<a name="handmade"></a>\n'
            '<a href="#handmade">Jump</a>\n'
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_escape_from_root_is_not_silently_ignored(self):
        errors, _, _ = self.check('<a href="../outside.txt">Outside</a>\n')
        self.assertTrue(any("escapes repository root" in msg for msg in errors))

    def test_remote_and_data_sources_are_outside_offline_scope(self):
        errors, checked, _ = self.check(
            '<img src="data:image/svg+xml,%3Csvg%3E" alt="">\n'
            '<source srcset="data:image/png;base64,AAAA">\n'
            '<a href="mailto:team@example.org">Email</a>\n'
        )
        self.assertEqual(errors, [])
        self.assertEqual(checked, 0)


if __name__ == "__main__":
    unittest.main()
