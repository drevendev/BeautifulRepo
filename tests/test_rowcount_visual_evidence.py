"""Reproducible, source-backed README first screens for the working Rowcount CLI."""
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "readme-visuals" / "rowcount"
CLI = ROOT / "examples" / "cli-starter"
COMMAND = "python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv"
RESULT = "Data rows: 3"


class RowcountVisualEvidenceTests(unittest.TestCase):
    def test_both_documented_invocations_reproduce_the_facts(self):
        from_root = subprocess.run(
            [sys.executable, str(CLI / "rowcount.py"), str(CLI / "sample.csv")],
            cwd=ROOT, capture_output=True, text=True, check=False, timeout=15,
        )
        from_sample_directory = subprocess.run(
            [sys.executable, "rowcount.py", "sample.csv"],
            cwd=CLI, capture_output=True, text=True, check=False, timeout=15,
        )
        for process in (from_root, from_sample_directory):
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(process.stdout, RESULT + "\n")
            self.assertEqual(process.stderr, "")

    def test_both_variants_preserve_exact_command_output_and_limit(self):
        for name in ("editorial.md", "terminal-led.md"):
            with self.subTest(name=name):
                source = (CASE / name).read_text(encoding="utf-8")
                self.assertIn(COMMAND, source)
                self.assertIn(RESULT, source)
                self.assertIn("Python 3.11+", source)
                self.assertIn("not", source.lower())
                self.assertIn("cli-starter/sample.csv", source)

    def test_dark_and_light_art_have_the_same_information(self):
        records = []
        for name in ("rowcount-light.svg", "rowcount-dark.svg"):
            tree = ET.parse(CASE / name)
            root = tree.getroot()
            ns = "{http://www.w3.org/2000/svg}"
            title = root.find(ns + "title")
            description = root.find(ns + "desc")
            self.assertIn("Rowcount", title.text)
            self.assertIn("not a screenshot", description.text)
            content = [node.text for node in root.iter(ns + "text")]
            self.assertIn("Data rows: 3", content)
            self.assertIn("$ python rowcount.py sample.csv", content)
            records.append(content)
        self.assertEqual(records[0], records[1])

    def test_visual_fallback_is_textual_and_descriptive(self):
        source = (CASE / "terminal-led.md").read_text(encoding="utf-8")
        self.assertIn("<picture>", source)
        self.assertIn('media="(prefers-color-scheme: dark)"', source)
        self.assertIn('media="(prefers-color-scheme: light)"', source)
        self.assertIn('alt="In examples/cli-starter, python rowcount.py sample.csv prints Data rows: 3."', source)

    def test_comparison_links_preserve_readable_navigation(self):
        index = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "The [working Rowcount first-screen comparison]"
            "(readme-visuals/rowcount/README.md)", index,
        )
        self.assertIn("Before adapting a starter, use the [first-success checklist]", index)
        guide = (ROOT / "guides" / "readme-visuals.md").read_text(encoding="utf-8")
        self.assertIn("\n## Two presentations backed by a real command\n", guide)
        self.assertIn("\n## Review checklist\n", guide)
        self.assertLess(
            guide.index("## Two presentations backed by a real command"),
            guide.index("## Review checklist"),
        )


if __name__ == "__main__":
    unittest.main()
