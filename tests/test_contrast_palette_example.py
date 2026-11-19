"""Behavioral checks for the illustrative color-palette before/after example."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "contrast-palette" / "demo.py"
PAIRS = DEMO.with_name("pairs.json")


def load_demo():
    spec = importlib.util.spec_from_file_location("contrast_palette_example", DEMO)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContrastPaletteExampleTests(unittest.TestCase):
    def setUp(self):
        self.demo = load_demo()
        self.rows = json.loads(PAIRS.read_text(encoding="utf-8"))

    def test_four_real_transitions(self):
        lines = self.demo.evaluate(self.rows)
        self.assertEqual(len(lines), 4)
        self.assertTrue(all("FAIL ->" in line and "PASS" in line for line in lines))

    def test_near_aa_boundary_stays_failing(self):
        self.assertIn("4.478:1 FAIL", self.demo.evaluate(self.rows)[0])

    def test_different_backgrounds_and_levels(self):
        self.assertEqual({r["theme"] for r in self.rows}, {"light", "dark"})
        self.assertEqual({r["level"] for r in self.rows}, {"AA", "AAA"})
        self.assertIn("threshold 7:1", self.demo.evaluate(self.rows)[-1])

    def test_corrected_color_fails_when_reverted(self):
        self.rows[0]["after"] = self.rows[0]["before"]
        with self.assertRaisesRegex(ValueError, "not a failing-to-passing"):
            self.demo.evaluate(self.rows)

    def test_duplicate_entry_is_refused(self):
        self.rows[1]["name"] = self.rows[0]["name"]
        with self.assertRaisesRegex(ValueError, "unique"):
            self.demo.evaluate(self.rows)

    def test_invalid_color_is_refused(self):
        self.rows[0]["before"] = "#fffff"
        with self.assertRaises(ValueError):
            self.demo.evaluate(self.rows)

    def test_script_works_in_isolated_mode_outside_checkout(self):
        with tempfile.TemporaryDirectory() as outside:
            proc = subprocess.run([sys.executable, "-I", str(DEMO)], cwd=outside,
                                  text=True, capture_output=True, timeout=15, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("OK: 4 illustrative palette corrections", proc.stdout)
        self.assertEqual(proc.stdout.count("FAIL ->"), 4)


if __name__ == "__main__":
    unittest.main()
