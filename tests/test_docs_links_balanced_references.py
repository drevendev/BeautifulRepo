"""Balanced reference-use regression coverage for the offline Markdown checker."""
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "docs_links.py"


class BalancedReferenceUseTests(unittest.TestCase):
    def inspect(self, markdown: str):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "README.md"
            source.write_bytes(markdown.encode("utf-8"))
            module = runpy.run_path(str(SCRIPT))
            locations = [tuple(loc) for loc in module["iter_markdown_locations"](source)]
            legacy = list(module["iter_markdown_destinations"](source))
            cli = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            return locations, legacy, cli

    def test_balanced_nested_text_is_one_full_reference(self):
        markdown = (
            "[outer [middle [deep]]][ref]\n\n[ref]: missing.md\n"
        )
        locations, legacy, cli = self.inspect(markdown)
        self.assertEqual([(1, 1, "missing.md", 1)], locations)
        self.assertEqual([(1, "missing.md")], legacy)
        self.assertEqual(1, cli.returncode)
        self.assertEqual(1, cli.stderr.count("missing relative destination"))

    def test_full_collapsed_shortcut_and_explicit_label_not_double_counted(self):
        markdown = (
            "[Full][id] [Collapsed][] [Shortcut]\n\n"
            "[id]: full.md\n[collapsed]: collapsed.md\n"
            "[shortcut]: shortcut.md\n"
        )
        locations, legacy, _ = self.inspect(markdown)
        self.assertEqual(
            [(1, 1, "full.md", 1),
             (1, markdown.index("[Collapsed]") + 1, "collapsed.md", 1),
             (1, markdown.index("[Shortcut]") + 1, "shortcut.md", 1)],
            locations,
        )
        self.assertEqual(
            [(1, "full.md"), (1, "collapsed.md"), (1, "shortcut.md")],
            legacy,
        )

    def test_nested_ordinary_reference_wins_and_outer_label_recovers(self):
        markdown = (
            "[outer [inner][child]][outer]\n\n"
            "[child]: inner.md\n[outer]: recovered.md\n"
        )
        locations, _, cli = self.inspect(markdown)
        self.assertEqual(
            [(1, markdown.index("[inner]") + 1, "inner.md", 1),
             (1, markdown.split("\n", 1)[0].rindex("[outer]") + 1, "recovered.md", 1)],
            locations,
        )
        self.assertIn("'inner.md'", cli.stderr)
        self.assertIn("'recovered.md'", cli.stderr)

    def test_unresolved_inner_reference_does_not_hide_outer(self):
        locations, _, cli = self.inspect(
            "[outer [broken][unknown]][ref]\n\n[ref]: outer.md\n"
        )
        self.assertEqual([(1, 1, "outer.md", 1)], locations)
        self.assertEqual(1, cli.stderr.count("missing relative destination"))

    def test_reference_image_inside_outer_reference_remains_live(self):
        markdown = (
            "[Page ![Logo][image]][page]\n\n"
            "[image]: logo.svg\n[page]: page.md\n"
        )
        locations, legacy, _ = self.inspect(markdown)
        self.assertEqual(
            [(1, 1, "page.md", 1),
             (1, markdown.index("![Logo]") + 1, "logo.svg", 1)],
            locations,
        )
        self.assertEqual([(1, "page.md"), (1, "logo.svg")], legacy)

    def test_nested_reference_in_image_alt_is_not_a_live_link(self):
        locations, _, cli = self.inspect(
            "![alt [fake][child]][image]\n\n"
            "[child]: hidden.md\n[image]: logo.svg\n"
        )
        self.assertEqual([(1, 1, "logo.svg", 1)], locations)
        self.assertNotIn("'hidden.md'", cli.stderr)

    def test_inline_image_alt_and_inline_destination_remain_literal(self):
        locations, _, cli = self.inspect(
            "![alt [fake][child]](logo.svg) "
            "[target](assets/[child](hidden.md))\n\n"
            "[child]: hidden.md\n"
        )
        self.assertEqual(
            [(1, 1, "logo.svg", 1),
             (1, 32, "assets/[child](hidden.md)", 1)],
            locations,
        )
        self.assertNotIn("missing relative destination: 'hidden.md'", cli.stderr)

    def test_escaped_brackets_unicode_crlf_and_source_character_columns(self):
        markdown = (
            "Ω [Visible \\[escaped\\] [nested]][  REF  ]\r\n"
            "\r\n[ref]: a.md\r\n"
        )
        locations, legacy, _ = self.inspect(markdown)
        self.assertEqual([(1, 3, "a.md", 1)], locations)
        self.assertEqual([(1, "a.md")], legacy)

    def test_nested_collapsed_label_does_not_invent_definition(self):
        locations, _, _ = self.inspect(
            "[outer [inner]][]\n\n[inner]: inner.md\n"
        )
        self.assertEqual([(1, 8, "inner.md", 1)], locations)

    def test_deep_or_long_text_has_bounded_nonrecursive_work(self):
        deep = "[" * 5000 + "text" + "]" * 5000 + "[ref]"
        long_text = "[" + "x" * 110_000 + "][ref]"
        locations, legacy, _ = self.inspect(
            deep + "\n" + long_text + "\n\n[ref]: missing.md\n"
        )
        self.assertEqual(
            [(1, 1, "missing.md", 1), (2, 1, "missing.md", 2)],
            locations,
        )
        self.assertEqual([(1, "missing.md"), (2, "missing.md")], legacy)


    def test_inline_link_inside_reference_wins_and_trailing_label_recovers(self):
        # GFM links example 541: the outer full reference is not a link.
        line = "[outer [inner](inner.md)][ref]"
        locations, _, cli = self.inspect(line + "\n\n[ref]: outer.md\n")
        self.assertEqual(
            [(1, line.index("[inner]") + 1, "inner.md", 1),
             (1, line.rindex("[ref]") + 1, "outer.md", 1)],
            locations,
        )
        self.assertIn("'inner.md'", cli.stderr)
        self.assertIn("'outer.md'", cli.stderr)

    def test_reference_inside_inline_wins_over_outer_inline(self):
        line = "[outer [inner][child]](outer.md)"
        locations, _, cli = self.inspect(line + "\n\n[child]: inner.md\n")
        self.assertEqual(
            [(1, line.index("[inner]") + 1, "inner.md", 1)],
            locations,
        )
        self.assertIn("'inner.md'", cli.stderr)
        self.assertNotIn("'outer.md'", cli.stderr)

    def test_inline_image_inside_reference_does_not_suppress_link(self):
        line = "[outer ![badge](badge.svg)][ref]"
        locations, _, _ = self.inspect(line + "\n\n[ref]: outer.md\n")
        self.assertEqual(
            [(1, line.index("![badge]") + 1, "badge.svg", 1),
             (1, 1, "outer.md", 1)],
            locations,
        )

    def test_reference_image_inside_inline_does_not_suppress_link(self):
        line = "[outer ![badge][image]](outer.md)"
        locations, _, _ = self.inspect(line + "\n\n[image]: badge.svg\n")
        self.assertEqual(
            [(1, 1, "outer.md", 1),
             (1, line.index("![badge]") + 1, "badge.svg", 1)],
            locations,
        )


    def test_invalid_outer_inline_tail_exposes_live_reference(self):
        # A successful inner link cancels the outer inline link. Its
        # destination-looking tail is literal text containing a live ref.
        line = "[outer [inner](inner.md)](assets/[side][ref])"
        locations, legacy, cli = self.inspect(
            line + "\n\n[ref]: side.md\n"
        )
        self.assertEqual(
            [(1, line.index("[inner]") + 1, "inner.md", 1),
             (1, line.index("[side]") + 1, "side.md", 1)],
            locations,
        )
        self.assertEqual([(1, "inner.md"), (1, "side.md")], legacy)
        self.assertIn("'inner.md'", cli.stderr)
        self.assertIn("'side.md'", cli.stderr)
        self.assertNotIn("assets/[side][ref]", cli.stderr)

    def test_live_inline_and_image_destinations_mask_reference_lookalikes(self):
        # A live inline destination and a live image destination both
        # keep their bracket-looking path text literal, not a reference.
        line = "[valid](assets/[side][ref]) ![badge](assets/[side][ref])"
        locations, _, cli = self.inspect(
            line + "\n\n[ref]: side.md\n"
        )
        self.assertEqual(
            [(1, 1, "assets/[side][ref]", 1),
             (1, line.index("![badge]") + 1, "assets/[side][ref]", 1)],
            locations,
        )
        self.assertNotIn("'side.md'", cli.stderr)


    def test_nested_reference_invalidates_outer_inline_and_exposes_tail(self):
        # GFM: a successful inner reference link cancels the outer inline
        # link, so its destination-looking tail contains a real reference.
        line = "[outer [inner][child]](assets/[side][ref])"
        locations, legacy, cli = self.inspect(
            line + "\n\n[child]: inner.md\n[ref]: side.md\n"
        )
        self.assertEqual(
            [(1, line.index("[inner]") + 1, "inner.md", 1),
             (1, line.index("[side]") + 1, "side.md", 1)],
            locations,
        )
        self.assertEqual([(1, "inner.md"), (1, "side.md")], legacy)
        self.assertIn("'inner.md'", cli.stderr)
        self.assertIn("'side.md'", cli.stderr)
        self.assertNotIn("assets/[side][ref]", cli.stderr)

    def test_balanced_nested_reference_also_invalidates_outer_inline(self):
        line = "[outer [nested [deep]][child]](assets/[side][ref])"
        locations, _, cli = self.inspect(
            line + "\n\n[child]: inner.md\n[ref]: side.md\n"
        )
        self.assertEqual(
            [(1, line.index("[nested") + 1, "inner.md", 1),
             (1, line.index("[side]") + 1, "side.md", 1)],
            locations,
        )
        self.assertIn("'inner.md'", cli.stderr)
        self.assertIn("'side.md'", cli.stderr)

    def test_nested_reference_image_keeps_outer_inline_destination_literal(self):
        line = "[outer ![badge][image]](assets/[side][ref])"
        locations, _, cli = self.inspect(
            line + "\n\n[image]: badge.svg\n[ref]: side.md\n"
        )
        self.assertEqual(
            [(1, 1, "assets/[side][ref]", 1),
             (1, line.index("![badge]") + 1, "badge.svg", 1)],
            locations,
        )
        self.assertIn("'badge.svg'", cli.stderr)
        self.assertNotIn("'side.md'", cli.stderr)



    def test_inline_syntax_inside_reference_image_alt_is_literal(self):
        line = "![alt [fake](fake.md)][image] [real](real.md)"
        locations, legacy, cli = self.inspect(
            line + "\n\n[image]: logo.svg\n"
        )
        expected = [
            (1, 1, "logo.svg", 1),
            (1, line.index("[real]") + 1, "real.md", 1),
        ]
        self.assertEqual(expected, locations)
        self.assertEqual([(1, "logo.svg"), (1, "real.md")], legacy)
        self.assertIn("'logo.svg'", cli.stderr)
        self.assertIn("'real.md'", cli.stderr)
        self.assertNotIn("'fake.md'", cli.stderr)

    def test_reference_image_alt_inside_full_reference_ignores_inline_link(self):
        line = "[Page ![alt [fake](fake.md)][image]][page]"
        locations, _, cli = self.inspect(
            line + "\n\n[image]: logo.svg\n[page]: page.md\n"
        )
        self.assertEqual(
            [(1, 1, "page.md", 1),
             (1, line.index("![alt") + 1, "logo.svg", 1)],
            locations,
        )
        self.assertIn("'page.md'", cli.stderr)
        self.assertIn("'logo.svg'", cli.stderr)
        self.assertNotIn("'fake.md'", cli.stderr)

    def test_unresolved_reference_image_does_not_hide_real_inline_link(self):
        # An unresolved image is literal Markdown; its inner link stays live.
        line = "![alt [fake](fake.md)][unknown] [real](real.md)"
        locations, _, cli = self.inspect(line + "\n")
        self.assertEqual(
            [(1, line.index("[fake]") + 1, "fake.md", 1),
             (1, line.index("[real]") + 1, "real.md", 1)],
            locations,
        )
        self.assertIn("'fake.md'", cli.stderr)
        self.assertIn("'real.md'", cli.stderr)


if __name__ == "__main__":
    unittest.main()
