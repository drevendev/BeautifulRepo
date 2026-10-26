"""Reproducible, source-backed README first screens for the working Rowcount CLI."""
from pathlib import Path
import subprocess
import sys
import tempfile
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

    def test_all_three_variants_preserve_command_output_and_limit(self):
        for name in ("editorial.md", "terminal-led.md", "contract-first.md"):
            with self.subTest(name=name):
                source = (CASE / name).read_text(encoding="utf-8")
                self.assertIn(COMMAND, source)
                self.assertIn(RESULT, source)
                self.assertIn("Python 3.11+", source)
                self.assertIn("not", source.lower())
                self.assertIn("cli-starter/sample.csv", source)

    def test_contract_first_is_an_actual_boundary_card(self):
        source = (CASE / "contract-first.md").read_text(encoding="utf-8")
        for fact in (
            "## Contract at a glance", "header", "blank", "column",
            "schema", "nonzero exit", "## Reproduce the result",
        ):
            self.assertIn(fact, source)
        self.assertIn("[Compare all three entrances](README.md)", source)
        index = (CASE / "README.md").read_text(encoding="utf-8")
        self.assertIn("[Contract-first](contract-first.md)", index)

    def test_invalid_row_width_fails_instead_of_silently_counting(self):
        with tempfile.TemporaryDirectory() as tempdir:
            malformed = Path(tempdir) / "bad.csv"
            malformed.write_text("name,amount\nA,1\nB\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI / "rowcount.py"), str(malformed)],
                cwd=ROOT, capture_output=True, text=True, check=False, timeout=15,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("expected 2 columns, got 1", result.stderr)

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

    def test_mobile_art_facts_and_contrast(self):
        def brightness(color):
            rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                      for v in rgb]
            return sum(v * w for v, w in
                       zip(linear, (0.2126, 0.7152, 0.0722), strict=True))

        namespace = "{http://www.w3.org/2000/svg}"
        pair = []
        for name in ("rowcount-mobile-light.svg", "rowcount-mobile-dark.svg"):
            root = ET.parse(CASE / name).getroot()
            self.assertEqual(root.get("viewBox"), "0 0 320 216")
            self.assertIn("Rowcount", root.find(namespace + "title").text)
            self.assertIn("not a screenshot", root.find(namespace + "desc").text)
            bg = brightness(root.findall(namespace + "rect")[1].get("fill"))
            texts = root.findall(namespace + "text")
            labels = [node.text for node in texts]
            self.assertIn("$ python rowcount.py sample.csv", labels)
            self.assertIn(RESULT, labels)
            for node in texts:
                fg = brightness(node.get("fill"))
                high, low = sorted((fg, bg), reverse=True)
                with self.subTest(name=name, label=node.text):
                    self.assertGreaterEqual((high + 0.05) / (low + 0.05), 4.5)
                if node.text.startswith("$ python"):
                    self.assertGreaterEqual(float(node.get("font-size")), 13)
            pair.append(labels)
        self.assertEqual(pair[0], pair[1])

    def test_visual_fallback_is_textual_and_descriptive(self):
        source = (CASE / "terminal-led.md").read_text(encoding="utf-8")
        self.assertIn("<picture>", source)
        self.assertIn('media="(prefers-color-scheme: dark)"', source)
        self.assertIn('media="(max-width: 480px)"', source)
        self.assertIn('media="(max-width: 480px) and (prefers-color-scheme: dark)"', source)
        self.assertIn('srcset="rowcount-mobile-light.svg"', source)
        self.assertIn('srcset="rowcount-mobile-dark.svg"', source)
        self.assertLess(source.index('srcset="rowcount-mobile-dark.svg"'),
                        source.index('srcset="rowcount-dark.svg"'))
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
        self.assertIn("\n## Three presentations backed by a real command\n", guide)
        self.assertIn("\n## Review checklist\n", guide)
        self.assertLess(
            guide.index("## Three presentations backed by a real command"),
            guide.index("## Review checklist"),
        )


if __name__ == "__main__":
    unittest.main()
