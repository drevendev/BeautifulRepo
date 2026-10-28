"""Keep the workshop's working examples and adaptation routes discoverable."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
TYPES = ("cli", "library", "research-data", "application", "curated")


class WorkshopNavigationTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_index_links_each_working_starter(self):
        index = self.read("examples/README.md")
        for kind in TYPES:
            with self.subTest(kind=kind):
                self.assertIn(f"({kind}-starter/README.md)", index)
        self.assertIn("not a", index)
        self.assertIn("production service", index)

    def test_root_preserves_all_starter_routes(self):
        readme = self.read("README.md")
        for kind in TYPES:
            with self.subTest(kind=kind):
                self.assertIn(f"(examples/{kind}-starter/README.md)", readme)
        for route in ("examples/README.md", "checklists/first-success.md",
                      "guides/maintenance-workflow.md", "guides/repository-audit.md",
                      "guides/release-notes.md"):
            self.assertIn(f"({route})", readme)
        self.assertIn("Text alternative:", readme)

    def test_application_template_covers_complete_journey(self):
        text = self.read("templates/APPLICATION_README.template.md")
        for topic in ("ACTUAL_LAUNCH_COMMAND", "SPECIFIC_INTERACTION",
                      "VERIFIED_VISIBLE_CHANGE", "ACTUAL_STOP_METHOD",
                      "ACTUAL_PERSISTENCE_AND_RESET_BEHAVIOR", "EXPLICIT_LOCAL_ONLY_BOUNDARY"):
            self.assertIn(topic, text)
        self.assertIn("Do not substitute a concept image", text)

    def test_collection_template_separates_review_and_automation(self):
        text = self.read("templates/CURATED_README.template.md")
        for topic in ("**Use when:**", "**Why:**", "**Limit:**", "**Source checked:**",
                      "EXPLICIT_EXCLUSIONS", "RETIREMENT_POLICY"):
            self.assertIn(topic, text)
        self.assertIn("not a live source review", text)
        self.assertIn("separate", text.lower())

    def test_new_templates_have_guide_routes(self):
        pairs = (("guides/application-repositories.md", "APPLICATION_README"),
                 ("guides/curated-collections.md", "CURATED_README"))
        for guide, stem in pairs:
            with self.subTest(guide=guide):
                self.assertIn(f"(../templates/{stem}.template.md)", self.read(guide))

    def test_maintenance_commands_and_limits_are_explicit(self):
        workflow = self.read("guides/maintenance-workflow.md")
        for command in ("python tools/catalog.py", "python tools/docs_links.py",
                        "python -m unittest discover -s tests -v"):
            self.assertIn(command, workflow)
        self.assertIn("loopback", workflow)
        self.assertIn("partial", workflow)
        self.assertIn("not prove navigation over HTTP", workflow)

    def test_roadmap_does_not_leave_completed_starters_as_future_work(self):
        roadmap = self.read("ROADMAP.md")
        sections = re.split(r"^## (?:Next|Current work):", roadmap,
                            maxsplit=1, flags=re.MULTILINE)
        self.assertEqual(len(sections), 2, "Missing future-work roadmap section")
        available, upcoming = sections
        for path in ("application-starter/README.md", "curated-starter/README.md"):
            self.assertIn(path, available)
        self.assertNotIn("Expand project-type starter kits", upcoming)

    def test_first_success_checks_behavior_not_only_process_exit(self):
        checklist = self.read("checklists/first-success.md")
        self.assertGreaterEqual(len(re.findall(r"^- \[ \]", checklist, re.MULTILINE)), 5)
        for detail in ("12", "6", "60", "error", "data"):
            self.assertIn(detail, checklist.lower())


if __name__ == "__main__":
    unittest.main()
