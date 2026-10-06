"""Negative and deterministic-output tests for the offline catalog tool."""
import copy
from datetime import date
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("catalog", Path(__file__).parents[1] / "tools/catalog.py")
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)
TODAY = date(2026, 10, 3)


def document():
    return {"schema_version": 1, "resources": [{
        "id": "example-guide", "title": "A guide", "category": "guide",
        "url": "https://example.org/guide", "why": "A useful reason", "apply": "A concrete action",
        "caveat": "Not runtime tested", "coverage": "Introduction inspected",
        "reviewed_on": "2026-10-03", "evidence": "source-reviewed"}]}


class CatalogTests(unittest.TestCase):
    def errors_for(self, field, value):
        data = document()
        data["resources"][0][field] = value
        return catalog.validate(data, TODAY)[0]

    def test_valid(self):
        self.assertEqual(catalog.validate(document(), TODAY), ([], []))

    def test_invalid_root_and_empty_resources(self):
        for data in (None, [], {}, {"schema_version": 1, "resources": []}):
            self.assertTrue(catalog.validate(data, TODAY)[0])

    def test_boolean_is_not_schema_version(self):
        data = document(); data["schema_version"] = True
        self.assertTrue(catalog.validate(data, TODAY)[0])

    def test_missing_and_unknown_field(self):
        data = document(); del data["resources"][0]["why"]
        self.assertTrue(catalog.validate(data, TODAY)[0])
        data = document(); data["resources"][0]["unknown"] = "value"
        self.assertTrue(catalog.validate(data, TODAY)[0])

    def test_empty_or_non_string_fields(self):
        for value in ("", "  ", None, 5, [], {}):
            self.assertTrue(self.errors_for("why", value))

    def test_identifier_category_and_evidence(self):
        self.assertTrue(self.errors_for("id", "Mixed ID"))
        self.assertTrue(self.errors_for("category", "unapproved"))
        self.assertTrue(self.errors_for("evidence", "tested-and-secure"))

    def test_duplicate_id(self):
        data = document(); item = copy.deepcopy(data["resources"][0]); item["url"] += "/other"
        data["resources"].append(item)
        self.assertTrue(any("duplicate id" in x for x in catalog.validate(data, TODAY)[0]))

    def test_equivalent_url_variants_are_duplicates(self):
        for url in ("https://EXAMPLE.org/guide/", "https://example.org:443/guide#part"):
            data = document(); item = copy.deepcopy(data["resources"][0])
            item.update(id="second-guide", url=url); data["resources"].append(item)
            self.assertTrue(any("duplicate source" in x for x in catalog.validate(data, TODAY)[0]))

    def test_invalid_urls(self):
        for url in ("http://example.org", "https:///missing", "https://user:pass@example.org",
                    "https://example.org:bad", "https://example.org/a b", "https://[broken", "https://example.org/<x>"):
            self.assertTrue(self.errors_for("url", url), url)

    def test_dates(self):
        for value in ("2026-10-04", "2026-02-30", "20261003", "2026-1-1"):
            self.assertTrue(self.errors_for("reviewed_on", value), value)

    def test_stale_warning_is_not_structural_failure(self):
        data = document(); data["resources"][0].update(category="program", reviewed_on="2026-08-01")
        errors, warnings = catalog.validate(data, TODAY)
        self.assertFalse(errors); self.assertEqual(len(warnings), 1)

    def test_render_deterministic_and_does_not_mutate(self):
        data = document(); before = copy.deepcopy(data)
        self.assertEqual(catalog.render(data), catalog.render(data))
        self.assertEqual(data, before)

    def test_render_escapes_active_markup(self):
        data = document(); data["resources"][0]["title"] = "<script> [link] *bold*"
        result = catalog.render(data)
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertIn(r"\[link\]", result)

    def test_cli_write_check_drift_and_bad_json(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / "source.json"; out = Path(directory) / "view.md"
            # Old-but-valid dates cause at most warnings on future executions.
            data.write_text(json.dumps(document()), encoding="utf-8")
            args = ["--data", str(data), "--output", str(out)]
            self.assertEqual(catalog.main(args + ["--write"]), 0)
            self.assertEqual(catalog.main(args), 0)
            out.write_text("drift", encoding="utf-8")
            self.assertEqual(catalog.main(args), 1)
            data.write_text("not json", encoding="utf-8")
            self.assertEqual(catalog.main(args), 1)


if __name__ == "__main__":
    unittest.main()
