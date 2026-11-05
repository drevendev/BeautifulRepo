"""Offline regressions for the optional synthetic browser recording helper."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

RECORDER = Path(__file__).resolve().parents[1] / "examples" / "combined-audit" / "record.py"
_spec = importlib.util.spec_from_file_location("br_showcase_record", RECORDER)
recorder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(recorder)


def valid_report() -> str:
    return (
        '<!doctype html><html><head><title>test</title></head><body>'
        '<h1>One broken link, two independent checkers</h1>'
        + "".join("<p>" + marker + "</p>" for marker in recorder.MARKERS)
        + "</body></html>"
    )


class RecordingPreparationTests(unittest.TestCase):
    def test_expected_synthetic_html_is_accepted(self):
        recorder.validate_report(valid_report())

    def test_missing_actual_result_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing synthetic checker evidence"):
            recorder.validate_report(
                valid_report().replace("2/2 local-link checks pass.",
                                       "1/2 local-link checks pass.")
            )

    def test_active_content_and_non_reports_are_rejected(self):
        for source in (
            "<html></html>",
            valid_report() + "<script>alert(1)</script>",
            valid_report() + '<iframe src="file:///etc/passwd"></iframe>',
        ):
            with self.subTest(source=source[-40:]):
                with self.assertRaises(ValueError):
                    recorder.validate_report(source)

    def test_scroll_is_bounded_and_returns_to_summary(self):
        values = [recorder.scroll_fraction(t / 4) for t in range(0, 89)]
        self.assertTrue(all(0 <= value <= 1 for value in values))
        self.assertEqual(values[0], 0)
        self.assertEqual(recorder.scroll_fraction(11), 1)
        self.assertEqual(recorder.scroll_fraction(19), 0)
        self.assertLess(recorder.scroll_fraction(6), recorder.scroll_fraction(9))

    def test_no_overwrite_even_without_optional_browser_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "video.webm"
            output.write_bytes(b"keep")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                recorder.record(valid_report(), "/missing/browser", output)
            self.assertEqual(output.read_bytes(), b"keep")

    def test_bad_output_type_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "end in .webm"):
                recorder.record(valid_report(), "/missing/browser",
                                Path(directory) / "video.mp4")


if __name__ == "__main__":
    unittest.main()
