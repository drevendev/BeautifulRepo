"""Check game README guidance, placeholder integrity and discoverability."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GameReadmeDocsTests(unittest.TestCase):
    def test_guide_is_source_backed_and_not_a_shipping_claim(self):
        text = (ROOT / "guides/game-repositories.md").read_text(encoding="utf-8")
        for expected in ("Reviewed **2026-11-14**", "two audiences",
                         "not automatically open source", "first-success checklist",
                         "not a bundled or tested game",
                         "https://itch.io/docs/creators/getting-started",
                         "https://itch.io/docs/creators/widget"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_template_requires_playable_evidence_build_and_asset_rights(self):
        text = (ROOT / "templates/GAME_README.template.md").read_text(encoding="utf-8")
        for expected in ("## Play the current build", "## See one gameplay moment",
                         "## First minute: controls and goal", "## Build from source",
                         "## Data, assets and permissions", "{{VERIFIED_FULL_SHA}}",
                         "{{VERIFIED_TEST_COMMAND}}", "{{PATH_SCOPED_RIGHTS_AND_PROVENANCE}}"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)
        self.assertIn("not evidence that the hosted/downloadable game works", text)
        self.assertIn("not** automatically license", text)

    def test_public_navigation_is_explicit_about_no_game_bundle(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        index = (ROOT / "templates/README.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("(guides/game-repositories.md)", readme)
        self.assertIn("(templates/GAME_README.template.md)", readme)
        self.assertIn("no bundled game", readme)
        self.assertIn("(GAME_README.template.md)", index)
        self.assertIn("(guides/game-repositories.md)", roadmap)


if __name__ == "__main__":
    unittest.main()
