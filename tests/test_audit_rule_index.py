"""Keep the documented entry-audit rule IDs in sync with finding() sources.

This checks source-level ID inventory, not rule behavior or runtime coverage.
"""
from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "repo_audit.py"
INDEX = ROOT / "guides" / "audit-rule-reference.md"
ROW = re.compile(r"^\|\s*`([a-z][a-z0-9_.]+)`\s*\|\s*([^|]+)\|", re.M)


class AuditRuleReferenceTests(unittest.TestCase):
    def test_index_covers_each_emitted_id_once(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        kinds = None
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == "selected" for t in node.targets):
                continue
            self.assertIsInstance(node.value, ast.Dict)
            kinds = [key.value for key in node.value.keys if isinstance(key, ast.Constant)]
            break
        self.assertEqual(kinds, ["readme", "license", "contributing"])

        emitted = set()
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "finding"):
                continue
            self.assertTrue(node.args, "finding() requires a rule ID")
            rule = node.args[0]
            if isinstance(rule, ast.Constant) and isinstance(rule.value, str):
                emitted.add(rule.value)
            elif isinstance(rule, ast.JoinedStr):
                self.assertEqual(len(rule.values), 2, "unknown computed rule family")
                prefix, suffix = rule.values
                self.assertIsInstance(prefix, ast.FormattedValue)
                self.assertIsInstance(prefix.value, ast.Name)
                self.assertEqual(prefix.value.id, "kind")
                self.assertIsInstance(suffix, ast.Constant)
                self.assertIn(suffix.value, (".missing", ".empty"))
                emitted.update(kind + suffix.value for kind in kinds)
            else:
                self.fail("new dynamic finding() rule ID needs explicit index handling")

        rows = ROW.findall(INDEX.read_text(encoding="utf-8"))
        documented = [id_ for id_, _ in rows]
        self.assertEqual(len(documented), len(set(documented)), "duplicate index ID")
        self.assertEqual(set(documented), emitted)
        self.assertEqual(len(emitted), 23)
        for id_, severity in rows:
            self.assertTrue(any(level in severity for level in ("error", "warning", "info")),
                            f"{id_}: missing severity")


if __name__ == "__main__":
    unittest.main()
