"""Black-box structural contracts; no renderer, network or assistive tech invoked."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/mermaid_svg_check.py"


def svg(*, named="name", described="detail", body="<title id='name'>First success</title><desc id='detail'>Promise then verified example</desc>"):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' aria-labelledby='{named}' "
            f"aria-describedby='{described}'>{body}<g><text>Step</text></g></svg>")


class MermaidSvgCheckTests(unittest.TestCase):
    def run_tool(self, source: str | bytes, *args: str):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "capture.svg"
            file.write_bytes(source if isinstance(source, bytes) else source.encode("utf-8"))
            return subprocess.run([sys.executable, "-I", str(TOOL), str(file), *args],
                                  capture_output=True, text=True, check=False)

    def test_good_rendered_svg_reports_observed_text_and_hash(self):
        result = self.run_tool(svg(), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value["status"], "STRUCTURE_PASS")
        self.assertEqual(value["title"], "First success")
        self.assertEqual(value["description"], "Promise then verified example")
        self.assertEqual(len(value["sha256"]), 64)

    def test_dangling_ambiguous_wrong_type_and_empty_refs_fail(self):
        cases = (
            svg(named="missing"),
            svg(named="name name"),
            svg(described="missing"),
            svg(body="<title id='name'> </title><desc id='detail'>Description</desc>"),
            svg(body="<title id='name'>Good</title><title id='name'>Duplicate</title><desc id='detail'>Desc</desc>"),
            svg(body="<desc id='name'>Wrong</desc><desc id='detail'>Desc</desc>"),
            svg(body="<title id='name'>Good</title><title id='detail'>Wrong</title>"),
            svg(named=""),
        )
        for bad in cases:
            with self.subTest(bad=bad):
                result = self.run_tool(bad)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("FAIL:", result.stderr)

    def test_invalid_xml_doctype_nul_and_large_input_reject(self):
        for bad, status in (
            ("<html/>", 1),
            ("<svg>", 1),
            ("<!DOCTYPE svg [<!ENTITY x 'test'>]>" + svg(), 1),
            (b"<svg\0/>", 1),
            (svg() + " " * 1_048_576, 1),
        ):
            with self.subTest(bad=str(bad)[:40]):
                result = self.run_tool(bad)
                self.assertEqual(result.returncode, status, result.stderr)

    def test_no_external_input_or_filesystem_writes(self):
        source = TOOL.read_text(encoding="utf-8")
        self.assertNotIn("urlopen", source)
        self.assertNotIn("requests", source)
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "original.svg"
            original.write_text(svg(), encoding="utf-8")
            linked = Path(temp) / "linked.svg"
            try:
                linked.symlink_to(original)
            except OSError:
                self.skipTest("symlink creation not allowed")
            result = subprocess.run([sys.executable, "-I", str(TOOL), str(linked)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(original.read_text(encoding="utf-8"), svg())


if __name__ == "__main__":
    unittest.main()
