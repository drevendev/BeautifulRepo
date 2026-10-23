"""Decision records keep one shape and one index."""
from datetime import date
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "docs" / "decisions"


class DecisionRecordTests(unittest.TestCase):
    def records(self):
        return sorted(DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md"))

    def test_records_are_numbered_without_gaps(self):
        numbers = [int(path.name[:4]) for path in self.records()]
        self.assertGreaterEqual(len(numbers), 4)
        self.assertEqual(list(range(1, len(numbers) + 1)), numbers)

    def test_every_record_has_the_template_fields(self):
        for path in self.records():
            with self.subTest(record=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith(f"# {path.name[:4]}: "))
                date.fromisoformat(re.search(r"^- \*\*Date:\*\* (\S+)$", text, re.M).group(1))
                self.assertRegex(text, r"(?m)^- \*\*Landed in:\*\* .*\]\(https://github\.com/"
                                       r"drevendev/BeautifulRepo/pull/\d+\)")
                self.assertRegex(text, r"(?m)^- \*\*Status:\*\* (accepted|superseded by \d{4})$")
                for part in ("**Context.**", "**Decision.**", "**Consequences.**"):
                    self.assertIn(part, text)

    def test_index_lists_every_record_and_is_linked(self):
        index = (DECISIONS / "README.md").read_text(encoding="utf-8")
        for path in self.records():
            with self.subTest(record=path.name):
                self.assertIn(f"]({path.name})", index)
        for page in ("CONTRIBUTING.md", "guides/maintainer-handoff.md"):
            with self.subTest(page=page):
                self.assertIn("docs/decisions/README.md", (ROOT / page).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
