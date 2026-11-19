"""Numerical and CLI regression cases for the limited text-color checker."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from color_contrast import luminance, parse_color, ratio  # noqa: E402


class ContrastCalculationTests(unittest.TestCase):
    def test_extreme_opposites_are_21_to_one(self):
        self.assertAlmostEqual(ratio("#000000", "#FFFFFF"), 21.0)

    def test_identical_colors_are_one_to_one(self):
        self.assertEqual(ratio("#000000", "#000000"), 1.0)

    def test_direction_does_not_change_ratio(self):
        self.assertEqual(ratio("#777777", "#ffffff"), ratio("#ffffff", "#777777"))

    def test_luminance_reference_values(self):
        self.assertAlmostEqual(luminance((255, 0, 0)), 0.2126)
        self.assertAlmostEqual(luminance((0, 255, 0)), 0.7152)
        self.assertAlmostEqual(luminance((0, 0, 255)), 0.0722)

    def test_lower_and_upper_case_hex(self):
        self.assertEqual(parse_color("#aBcDeF"), (171, 205, 239))

    def test_invalid_or_transparent_colors_are_rejected(self):
        for value in ("red", "777777", "#fff", "#000000ff", "#fffffg", "#fff\nff", " #000000"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_color(value)

    def test_unrounded_near_threshold_fails(self):
        # #777 on white is roughly 4.478:1: too low for 4.5 despite appearances.
        value = ratio("#777777", "#ffffff")
        self.assertGreater(value, 4.4)
        self.assertLess(value, 4.5)


class ContrastCliTests(unittest.TestCase):
    @staticmethod
    def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools/color_contrast.py"), *args],
            capture_output=True, text=True, check=False,
        )

    def test_black_white_passes_default_aa(self):
        run = self.run_cli("#000000", "#ffffff")
        self.assertEqual(run.returncode, 0)
        self.assertIn("Contrast 21.0000:1", run.stdout)
        self.assertIn("PASS", run.stdout)

    def test_near_threshold_fails_without_rounding(self):
        run = self.run_cli("#777777", "#ffffff")
        self.assertEqual(run.returncode, 1)
        self.assertIn("FAIL", run.stdout)

    def test_large_aa_can_pass_when_normal_aa_fails(self):
        run = self.run_cli("#777777", "#ffffff", "--text", "large")
        self.assertEqual(run.returncode, 0)

    def test_aaa_has_higher_threshold(self):
        run = self.run_cli("#777777", "#ffffff", "--level", "AAA")
        self.assertEqual(run.returncode, 1)

    def test_json_report_is_machine_readable(self):
        run = self.run_cli("#000000", "#ffffff", "--format", "json")
        self.assertEqual(run.returncode, 0)
        payload = json.loads(run.stdout)
        self.assertTrue(payload["passes"])
        self.assertEqual(payload["ratio"], 21.0)
        self.assertEqual(payload["threshold"], 4.5)

    def test_bad_hex_exits_two_without_traceback(self):
        run = self.run_cli("#123", "#ffffff")
        self.assertEqual(run.returncode, 2)
        self.assertIn("#RRGGBB", run.stderr)
        self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
