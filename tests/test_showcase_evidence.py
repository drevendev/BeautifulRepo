"""Test the portable, source-labeled browser evidence companion."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import hashlib
import struct
import tempfile
import unittest
import zlib

MODULE = Path(__file__).resolve().parents[1] / "examples/combined-audit/evidence.py"
spec = importlib.util.spec_from_file_location("showcase_evidence", MODULE)
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


def png(width: int, height: int) -> bytes:
    """Build a tiny valid grayscale PNG without third-party libraries."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data)))
    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    pixels = (b"\x00" + b"\xff" * width) * height
    return (evidence.PNG_SIGNATURE + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))


class ShowcaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        (self.folder / "report.html").write_text(
            "<!doctype html>\n" + "\n".join(evidence.EXPECTED_MARKERS), encoding="utf-8"
        )
        for name, dimensions in (("desktop", (1280, 900)), ("mobile", (390, 844))):
            (self.folder / (name + ".png")).write_bytes(png(*dimensions))

    def test_exact_observations_dimensions_and_hashes(self):
        sha = "a" * 40
        result = evidence.render_evidence(self.folder, sha)
        self.assertIn(sha, result)
        self.assertIn("0/2", result)
        self.assertIn("2/2", result)
        self.assertIn("1280×900", result)
        self.assertIn("390×844", result)
        self.assertIn("not a real repository repair", result)
        self.assertIn("not decode/visually review", result)
        self.assertIn(hashlib.sha256((self.folder / "report.html").read_bytes()).hexdigest(), result)
        self.assertNotIn("PASS — mobile", result)

    def test_cli_preserves_existing_evidence(self):
        dest = self.folder / "evidence.md"
        self.assertEqual(0, evidence.main([str(self.folder), "--revision", "f" * 40]))
        before = dest.read_bytes()
        self.assertEqual(2, evidence.main([str(self.folder)]))
        self.assertEqual(before, dest.read_bytes())

    def test_missing_source_marker_is_not_a_success(self):
        (self.folder / "report.html").write_text("<!doctype html>\nmade up", encoding="utf-8")
        self.assertEqual(2, evidence.main([str(self.folder)]))
        self.assertFalse((self.folder / "evidence.md").exists())

    def test_png_header_and_revision_must_be_valid(self):
        (self.folder / "mobile.png").write_bytes(b"not a PNG")
        self.assertEqual(2, evidence.main([str(self.folder)]))
        self.assertFalse((self.folder / "evidence.md").exists())
        (self.folder / "mobile.png").write_bytes(png(390, 844))
        self.assertEqual(2, evidence.main([str(self.folder), "--revision", "not-sha"]))
        self.assertFalse((self.folder / "evidence.md").exists())


if __name__ == "__main__":
    unittest.main()
