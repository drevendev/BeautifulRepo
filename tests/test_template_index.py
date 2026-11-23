"""Keep the public template chooser complete as new scaffolds are added."""

from pathlib import Path
import re
import unittest


TEMPLATES = Path(__file__).resolve().parents[1] / "templates"


class TemplateIndexTests(unittest.TestCase):
    def test_every_shipped_template_is_linked_exactly_once(self):
        index = (TEMPLATES / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)\s]+)\)", index)
        template_links = [
            link for link in links
            if link.endswith(".template.md") or link.endswith(".template")
        ]
        shipped = {
            path.name for path in TEMPLATES.iterdir()
            if path.is_file()
            and (path.name.endswith(".template.md") or path.name.endswith(".template"))
        }
        self.assertTrue(shipped, "Expected reusable template files")
        self.assertEqual(shipped, set(template_links),
                         "List each shipped template in templates/README.md")
        self.assertEqual(len(template_links), len(set(template_links)),
                         "Do not repeat template links in the chooser")
        self.assertTrue(
            all((TEMPLATES / link).is_file() for link in template_links),
            "All template choices should be local files in templates/",
        )


if __name__ == "__main__":
    unittest.main()
