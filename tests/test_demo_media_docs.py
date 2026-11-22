"""Read-only source invariants; not a media-player or accessibility test."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DemoMediaDocsTests(unittest.TestCase):
    def test_routes_and_real_example_assets(self):
        guide = (ROOT / "guides/demo-media.md").read_text(encoding="utf-8")
        self.assertIn("(guides/demo-media.md)", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("(demo-media.md)", (ROOT / "guides/readme-visuals.md").read_text(encoding="utf-8"))
        self.assertIn("(guides/demo-media.md)", (ROOT / "ROADMAP.md").read_text(encoding="utf-8"))
        self.assertIn("(../templates/DEMO_MEDIA.template.md)", guide)
        for name in ("pocket-trails-still.png", "pocket-trails.mp4",
                     "pocket-trails.webm", "pocket-trails.vtt",
                     "pocket-trails-player.html"):
            with self.subTest(name=name):
                self.assertTrue((ROOT / "showcase/pocket-trails" / name).is_file())
                self.assertIn("../showcase/pocket-trails/" + name, guide)

    def test_honest_alt_text_and_evidence_boundaries(self):
        guide = (ROOT / "guides/demo-media.md").read_text(encoding="utf-8")
        template = (ROOT / "templates/DEMO_MEDIA.template.md").read_text(encoding="utf-8")
        self.assertIn("23.52-second silent recording", guide)
        self.assertIn("NOT RUN", guide)
        self.assertIn("NOT RUN", template)
        self.assertIn("synthetic", guide.lower())
        self.assertIn("not transcribed speech", guide.lower())
        self.assertIn("source check is not a screen-reader trial", template.lower())
        self.assertIn("https://www.w3.org/WAI/media/av/planning/", guide)


if __name__ == "__main__":
    unittest.main()
