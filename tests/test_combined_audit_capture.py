"""Regression coverage for optional browser captures of real synthetic audit output."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "combined-audit" / "capture.py"
spec = importlib.util.spec_from_file_location("combined_audit_capture", SCRIPT)
capture = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(capture)


class CombinedAuditCaptureTests(unittest.TestCase):
    def test_html_is_produced_by_actual_checked_in_demo(self):
        html = capture.render_demo()
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("Synthetic Pocket Trails fixture.", html)
        self.assertIn("0/2 local-link checks pass.", html)
        self.assertIn("2/2 local-link checks pass.", html)
        self.assertIn("-Read the [setup guide](docs/setup.md)", html)
        self.assertIn("+Read the [setup guide](docs/guide.md)", html)

    def test_stages_report_and_two_pngs_without_overwriting(self):
        # Use a relative destination: the documented ../output must yield
        # absolute file:// URLs even on Windows.
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            output = Path(tmp) / "shots"
            relative_output = output.relative_to(Path.cwd())
            calls = []

            def fake_chromium(args, **kwargs):
                calls.append(args)
                target = next(a.split("=", 1)[1] for a in args
                              if a.startswith("--screenshot="))
                Path(target).write_bytes(capture.PNG_SIGNATURE + b"\0" * 48)
                return subprocess.CompletedProcess(args, 0, "", "")

            html = "<!doctype html><html><body>fixture</body></html>\n"
            with patch.object(capture.subprocess, "run", side_effect=fake_chromium):
                paths = capture.capture("chromium", html, relative_output,
                                        ("desktop", "mobile"))
            self.assertEqual(
                {output / "report.html", output / "desktop.png",
                 output / "mobile.png"}, set(paths)
            )
            self.assertEqual(html, (output / "report.html").read_text("utf-8"))
            self.assertTrue((output / "desktop.png").read_bytes().startswith(
                capture.PNG_SIGNATURE
            ))
            self.assertEqual(2, len(calls))
            self.assertTrue(any("--window-size=1280,900" in c for c in calls))
            self.assertTrue(any("--window-size=390,844" in c for c in calls))
            for args in calls:
                self.assertIn("--disable-background-networking", args)
                screenshot = next(a.split("=", 1)[1] for a in args
                                  if a.startswith("--screenshot="))
                self.assertEqual(output.parent, Path(screenshot).parent.parent)
                self.assertTrue(args[-1].startswith("file://"))
            with self.assertRaisesRegex(RuntimeError, "refusing to overwrite"):
                capture.capture("chromium", html, relative_output, ("desktop",))
            self.assertEqual(html, (output / "report.html").read_text("utf-8"))

    def test_failed_browser_leaves_no_partial_public_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "shots"
            calls = []

            def fake_chromium(args, **kwargs):
                calls.append(args)
                if len(calls) == 1:
                    target = next(a.split("=", 1)[1] for a in args
                                  if a.startswith("--screenshot="))
                    Path(target).write_bytes(capture.PNG_SIGNATURE + b"\0" * 48)
                    return subprocess.CompletedProcess(args, 0, "", "")
                return subprocess.CompletedProcess(args, 1, "", "render failed")

            with patch.object(capture.subprocess, "run", side_effect=fake_chromium):
                with self.assertRaisesRegex(RuntimeError, "mobile browser capture"):
                    capture.capture("chromium", "<!doctype html>", output,
                                    ("desktop", "mobile"))
            self.assertFalse((output / "report.html").exists())
            self.assertFalse((output / "desktop.png").exists())
            self.assertFalse((output / "mobile.png").exists())

    def test_fake_zero_exit_without_png_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(capture.subprocess, "run", return_value=(
                    subprocess.CompletedProcess([], 0, "", ""))):
                with self.assertRaisesRegex(RuntimeError, "browser capture failed"):
                    capture.capture("chromium", "<!doctype html>", Path(tmp) / "shots",
                                    ("desktop",))

    def test_browser_must_be_available(self):
        with patch.object(capture.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "executable not found"):
                capture.find_browser("nonexistent-browser")


if __name__ == "__main__":
    unittest.main()
