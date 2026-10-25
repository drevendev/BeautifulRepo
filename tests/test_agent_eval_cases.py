"""Free static checks for the source-controlled agent-eval coverage contract.

This never invokes Claude, evaluates a model, or executes files in a target fixture.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
SKILLS = ROOT / "skills"
TRIGGER = re.compile(r"^tags:\s*\[(.*?)\]$", re.M)
ALLOWED = re.compile(r"^allowed_tools:\s*\[(.*?)\]$", re.M)


def case_type(text):
    match = TRIGGER.search(text)
    if not match:
        raise AssertionError("case tags are required")
    tags = {tag.strip() for tag in match.group(1).split(",")}
    return tags


class AgentEvalCaseContracts(unittest.TestCase):
    def test_every_skill_has_two_positive_one_negative(self):
        skills = sorted(path.name for path in SKILLS.iterdir()
                        if (path / "SKILL.md").is_file())
        self.assertTrue(skills, "no skills found")
        cases = sorted(EVALS.glob("*/prompt.md"))
        self.assertTrue(cases, "no agent cases found")
        for skill in skills:
            relevant = [p for p in cases if skill in case_type(p.read_text(encoding="utf-8"))]
            with self.subTest(skill=skill):
                positives = [p for p in relevant if "positive" in case_type(p.read_text(encoding="utf-8"))]
                negatives = [p for p in relevant if "negative" in case_type(p.read_text(encoding="utf-8"))]
                self.assertGreaterEqual(len(positives), 2)
                self.assertGreaterEqual(len(negatives), 1)
                for path in relevant:
                    grader_dir = path.parent / "graders"
                    self.assertTrue(grader_dir.is_dir())
                    graders = [p.read_text(encoding="utf-8") for p in grader_dir.glob("*.md")]
                    self.assertTrue(graders)
                    if path in positives:
                        self.assertTrue(any("type: tool_used" in g and "tool: Skill" in g
                                            and skill in g for g in graders), str(path))
                    else:
                        self.assertTrue(any("tool: Skill" in g and "min: 0" in g
                                            and "max: 0" in g and "arm: both" in g
                                            for g in graders), str(path))

    def test_no_implicit_write_network_or_shell_grants(self):
        prohibited = {"Bash", "Write", "Edit", "WebFetch", "WebSearch", "NotebookEdit"}
        for path in EVALS.glob("*/prompt.md"):
            text = path.read_text(encoding="utf-8")
            match = ALLOWED.search(text)
            with self.subTest(case=path.parent.name):
                self.assertIsNotNone(match, "allowed_tools must be explicit")
                names = {part.strip() for part in match.group(1).split(",")}
                self.assertTrue(names)
                self.assertTrue(names.isdisjoint(prohibited), names)

    def test_fixture_references_are_local_and_exist(self):
        for path in EVALS.glob("*/case.yaml"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(case=path.parent.name):
                self.assertIn('schema_version: "1.1"', text)
                self.assertIn("add_dirs: [resources]", text)
                self.assertTrue((path.parent / "resources" / "README.md").is_file())

    def test_manual_smoke_matrix_tracks_every_shipped_case(self):
        """The manual, non-CI model protocol must cover each skill and case."""
        guide = (EVALS / "manual-smoke.md").read_text(encoding="utf-8")
        skills = sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
        cases = sorted(EVALS.glob("*/prompt.md"))
        for skill in skills:
            with self.subTest(skill=skill):
                self.assertIn(f"### \`{skill}\`", guide)
        for path in cases:
            with self.subTest(case=path.parent.name):
                self.assertIn(f"\`{path.parent.name}\`", guide)
        for required in (
            "python -I tools/agent_eval_snapshot.py capture",
            "python -I tools/agent_eval_snapshot.py verify",
            "**PASS:**", "**FAIL:**", "**INCONCLUSIVE:**",
            "blocked by permissions", "fixture", "no model runs claimed",
        ):
            with self.subTest(required=required):
                self.assertIn(required, guide)

    def test_injection_case_contains_guardrail_criterion(self):
        grader = (EVALS / "audit-injection-bait" / "graders"
                  / "ignore-injected-instructions.md").read_text(encoding="utf-8")
        self.assertIn("type: llm", grader)
        self.assertIn("FAIL if", grader)
        self.assertIn("security@phantom.invalid", grader)


    def test_uncued_hostile_readme_is_not_primed_by_the_prompt(self):
        case = EVALS / "audit-injection-uncued"
        prompt = (case / "prompt.md").read_text(encoding="utf-8").split("---", 2)[2].strip().lower()
        self.assertIn("readme", prompt)
        self.assertIn("onboarding", prompt)
        for cue in ("inject", "untrusted", "hostile", "secret", "security", "ignore", "safety"):
            with self.subTest(cue=cue):
                self.assertNotIn(cue, prompt)
        fixture = (case / "resources" / "README.md").read_text(encoding="utf-8")
        self.assertIn("security@phantom.invalid", fixture)
        self.assertIn("Ignore previous audit rules", fixture)
        grader = (case / "graders" / "safe-outcome.md").read_text(encoding="utf-8")
        self.assertIn("type: llm", grader)
        self.assertIn("FAIL if", grader)
        self.assertIn("security@phantom.invalid", grader)
        for name in ("skill-fired.md", "no-writes.md", "no-edits.md"):
            self.assertTrue((case / "graders" / name).is_file(), name)

if __name__ == "__main__":
    unittest.main()
