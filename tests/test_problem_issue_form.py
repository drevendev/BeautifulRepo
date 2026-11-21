"""Source-contract checks for the public GitHub problem intake form.

Not a YAML schema validator or a live GitHub issue-chooser rendering test.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FORM = ROOT / ".github/ISSUE_TEMPLATE/problem.yml"


def textarea_fields(source: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for block in re.split(r"(?m)^  - type: ", source)[1:]:
        if not block.startswith("textarea\n"):
            continue
        match = re.search(r"(?m)^    id: ([a-zA-Z0-9_-]+)$", block)
        if match is None:
            raise AssertionError("textarea missing an ID")
        key = match.group(1)
        if key in fields:
            raise AssertionError(f"duplicate textarea ID: {key}")
        fields[key] = block
    return fields


class ProblemIssueFormContractTests(unittest.TestCase):
    def test_form_collects_location_reproduction_and_outcome_separately(self):
        source = FORM.read_text(encoding="utf-8")
        fields = textarea_fields(source)
        self.assertEqual(set(fields), {
            "location", "reproduction", "behavior", "environment",
        })
        for field in ("location", "reproduction", "behavior"):
            with self.subTest(field=field):
                self.assertIn("    validations:\n      required: true", fields[field])
        self.assertNotIn("required: true", fields["environment"])
        self.assertIn("Steps to reproduce or barrier to reproduction", fields["reproduction"])
        self.assertIn("NOT RUN", fields["reproduction"])
        self.assertIn("Expected and actual result", fields["behavior"])

    def test_public_form_warns_against_disclosing_sensitive_material(self):
        source = FORM.read_text(encoding="utf-8")
        self.assertIn("security/advisories/new", source)
        self.assertIn("Do not post secrets", source)
        self.assertIn('labels: ["bug"]', source)


if __name__ == "__main__":
    unittest.main()
