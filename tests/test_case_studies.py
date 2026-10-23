"""Case studies share one procedure and one index."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "case-studies"


class CaseStudyIndexTests(unittest.TestCase):
    def setUp(self):
        self.index = (CASES / "README.md").read_text(encoding="utf-8")

    def test_index_lists_every_case(self):
        for path in sorted(CASES.glob("*.md")):
            if path.name == "README.md":
                continue
            with self.subTest(case=path.name):
                self.assertIn(f"]({path.name})", self.index)

    def test_procedure_has_the_five_steps_and_the_rules(self):
        for heading in ("### 1. Snapshot \"before\"", "### 2. Audit with pinned tools",
                        "### 3. Change the target through its own pull request",
                        "### 4. Snapshot \"after\"", "### 5. Write up",
                        "## Rights and quoting", "## Known tool caveats", "## Skeleton"):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.index)
        self.assertIn("Unlicensed targets", self.index)
        self.assertIn("python -I tools/docs_links.py --root ../target", self.index)

    def test_index_is_linked_from_the_readme(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(case-studies/README.md)", readme)


if __name__ == "__main__":
    unittest.main()
