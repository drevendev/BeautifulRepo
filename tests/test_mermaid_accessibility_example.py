"""Source-level contracts for BeautifulRepo's original Mermaid flowcharts.

These tests do not render Mermaid or simulate assistive technology.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FENCE = chr(96) * 3


def section_between(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def first_mermaid_diagram(section: str) -> str:
    match = re.search(
        re.escape(FENCE) + r"mermaid\n(.*?)\n" + re.escape(FENCE),
        section,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError("registered Mermaid source block is missing")
    return match.group(1)


def accessible_fields(diagram: str) -> dict[str, str]:
    fields = {}
    for field in ("accTitle", "accDescr"):
        matches = re.findall(
            rf"(?m)^[ \t]*{field}:[ \t]*(.*)$", diagram
        )
        if len(matches) != 1 or not matches[0].strip():
            raise ValueError(f"missing, empty or duplicated {field}")
        fields[field] = matches[0].strip()
    return fields


class MermaidAccessibilityExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = (ROOT / "guides/readme-visuals.md").read_text(
            encoding="utf-8"
        )
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_guide_registers_original_flowchart_with_accessible_metadata(self):
        section = section_between(
            self.guide,
            "## Mermaid flowcharts: accessible source and text fallback\n",
            "\n## Patterns observed in current repositories",
        )
        diagram = first_mermaid_diagram(section)
        self.assertTrue(diagram.startswith("flowchart LR\n"))
        metadata = accessible_fields(diagram)
        self.assertGreaterEqual(len(metadata["accTitle"].split()), 4)
        self.assertGreaterEqual(len(metadata["accDescr"].split()), 12)
        for node in ("Learn the promise", "Run a verified example",
                     "Find contribution guidance"):
            with self.subTest(node=node):
                self.assertIn(node, diagram)
        self.assertIn('A["Learn the promise"] --> B["Run a verified example"]', diagram)
        self.assertIn('B --> C["Find contribution guidance"]', diagram)

    def test_guide_keeps_complete_nonvisual_route_and_honest_verification(self):
        section = section_between(
            self.guide,
            "## Mermaid flowcharts: accessible source and text fallback\n",
            "\n## Patterns observed in current repositories",
        )
        nonvisual = section.split(FENCE, 2)[-1]
        self.assertIn("**Text equivalent:** Learn the promise", nonvisual)
        self.assertIn("→ Run a verified example", nonvisual)
        self.assertIn("→\nFind contribution guidance", nonvisual)
        self.assertIn("**NOT RUN**", section)
        self.assertIn("mermaid.js.org/config/accessibility", section)
        self.assertIn("../checklists/visual-accessibility-acceptance.md", section)

    def test_readme_journey_has_accessible_source_and_existing_text_route(self):
        section = section_between(
            self.readme, "## The visitor journey\n", "\n## What you get"
        )
        diagram = first_mermaid_diagram(section)
        metadata = accessible_fields(diagram)
        for step in ("Promise", "Evidence", "First success", "Trust", "Contribute"):
            with self.subTest(step=step):
                self.assertIn(step, metadata["accDescr"])
        nonvisual = section.split(FENCE, 2)[-1]
        self.assertIn("**Text alternative:**", nonvisual)
        self.assertIn(
            "Promise (what is this?) → Evidence (what do I get?) →",
            " ".join(nonvisual.split()),
        )

    def test_missing_blank_or_duplicate_accessibility_directive_is_rejected(self):
        good = (
            "flowchart LR\n"
            "accTitle: First success route\n"
            "accDescr: The reader sees a promise and a reproducible result.\n"
            "A --> B"
        )
        self.assertEqual(accessible_fields(good)["accTitle"], "First success route")
        for bad in (
            good.replace("accTitle: First success route\n", ""),
            good.replace("accDescr: The reader sees a promise and a reproducible result.",
                         "accDescr:   "),
            good + "\naccTitle: Duplicated name",
            good + "\naccDescr: Duplicated description",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    accessible_fields(bad)

    def test_missing_registered_fence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            first_mermaid_diagram("A -> B; no Mermaid fence")


if __name__ == "__main__":
    unittest.main()
