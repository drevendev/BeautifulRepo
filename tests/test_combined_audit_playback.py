"""Dependency-free regressions for the optional WebM+VTT playback companion."""
import base64
from html import unescape
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import quote, unquote, urlsplit

PLAYER = Path(__file__).resolve().parents[1] / "examples" / "combined-audit" / "playback.py"
_spec = importlib.util.spec_from_file_location("br_showcase_playback", PLAYER)
player = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(player)

VTT = """WEBVTT

NOTE Authored descriptions, not speech.

00:00:00.000 --> 00:00:03.000
Fictional result: 0/2 to 2/2.

00:00:03.000 --> 00:00:08.000
Broken local link to docs/setup.md.
"""


class PlaybackTests(unittest.TestCase):
    def test_caption_timing_is_checked(self):
        self.assertEqual(len(player.cues(VTT)), 2)
        for bad in (
            "WEBVTT\n\n00:00:04.000 --> 00:00:02.000\nBad\n",
            "WEBVTT\n\n00:00:00.000 --> 00:00:03.000\nFirst\n\n"
            "00:00:02.000 --> 00:00:05.000\nOverlap\n",
            "WEBVTT\n\nNOTE No cues\n",
            "WEBVTT\n\n00:00:00.000 --> 00:00:70.000\nBad seconds\n",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    player.cues(bad)

    def test_caption_data_and_text_alternative_are_source_bound(self):
        markup = player.build_player(Path("walkthrough.webm"), VTT)
        match = re.search(r'src="data:text/vtt;base64,([A-Za-z0-9+/=]+)"', markup)
        self.assertIsNotNone(match)
        self.assertEqual(base64.b64decode(match[1]).decode("utf-8"), VTT)
        self.assertIn("Broken local link to docs/setup.md.", markup)
        self.assertIn('kind="captions"', markup)
        self.assertNotIn("<script", markup)
        self.assertNotIn("http://", markup)
        self.assertIn("Synthetic Pocket Trails", markup)

    def test_caption_text_and_filenames_are_escaped(self):
        injected = VTT.replace("Broken local link", "<script>alert('x')</script> link")
        markup = player.build_player(Path('a" onload="evil.webm'), injected)
        self.assertNotIn("<script>alert", markup)
        self.assertIn("&lt;script&gt;", markup)
        self.assertIn("%22", markup)
        self.assertNotIn('src="a" onload=', markup)

    def test_media_urls_encode_reserved_characters_as_one_sibling_segment(self):
        # Parsing the source URL must never turn a valid local filename into
        # a fragment/query or reinterpret literal percent escapes.
        for name in (
            "with space.webm",
            "with#hash.webm",
            "with?query.webm",
            "with%percent.webm",
            'with"quote.webm',
            "with&entity.webm",
            "café.webm",
        ):
            with self.subTest(name=name):
                markup = player.build_player(Path(name), VTT)
                match = re.search(r'<source src="([^"]+)"', markup)
                self.assertIsNotNone(match)
                source_url = unescape(match[1])
                self.assertEqual(source_url, quote(name, safe=""))
                parsed = urlsplit(source_url)
                self.assertEqual(parsed.query, "")
                self.assertEqual(parsed.fragment, "")
                self.assertEqual(unquote(parsed.path), name)
                self.assertNotIn("/", parsed.path)

    def test_exclusive_creation_and_source_bytes_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video = root / "walkthrough.webm"
            captions = root / "walkthrough.vtt"
            page = root / "walkthrough-player.html"
            video.write_bytes(b"\x1a\x45\xdf\xa3" + b"A" * 1050)
            captions.write_text(VTT, encoding="utf-8")
            before = video.read_bytes(), captions.read_bytes()
            player.make_player(video, captions, page)
            markup = page.read_text(encoding="utf-8")
            self.assertIn('src="walkthrough.webm"', markup)
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                player.make_player(video, captions, page)
            self.assertEqual(before, (video.read_bytes(), captions.read_bytes()))

    def test_missing_media_and_output_elsewhere_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video = root / "walkthrough.webm"
            captions = root / "walkthrough.vtt"
            captions.write_text(VTT, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "recording"):
                player.make_player(video, captions, root / "player.html")
            video.write_bytes(b"abc")
            with self.assertRaisesRegex(ValueError, "recording"):
                player.make_player(video, captions, root / "player.html")
            video.write_bytes(b"x" * 1100)
            with self.assertRaisesRegex(ValueError, "EBML"):
                player.make_player(video, captions, root / "player.html")
            video.write_bytes(b"\x1a\x45\xdf\xa3" + b"A" * 1050)
            with self.assertRaisesRegex(ValueError, "sibling"):
                player.make_player(video, captions, root / "different" / "player.html")
            self.assertFalse((root / "player.html").exists())


if __name__ == "__main__":
    unittest.main()
