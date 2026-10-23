"""Structural contract for the GitHub Action other repositories pin."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def working_bash():
    """Return a bash that really runs scripts, or None (System32's WSL stub may not)."""
    candidates = [shutil.which("bash")]
    if os.name == "nt":
        candidates.insert(0, r"C:\Program Files\Git\bin\bash.exe")
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            probe = subprocess.run([candidate, "-c", 'test -n "$BASH_VERSION" && echo ok'],
                                   capture_output=True, text=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.stdout.strip() == "ok":
            return candidate
    return None


class ActionContractTests(unittest.TestCase):
    def setUp(self):
        self.action = (ROOT / "action.yml").read_text(encoding="utf-8")

    def test_action_runs_bundled_tools_with_the_callers_python(self):
        self.assertIn("using: composite", self.action)
        for tool in ("repo_audit.py", "docs_links.py", "html_navigation.py"):
            with self.subTest(tool=tool):
                self.assertIn(f'"$GITHUB_ACTION_PATH/tools/{tool}"', self.action)
        self.assertNotIn("uses:", self.action)  # no nested actions such as setup-python
        self.assertIn("sys.version_info < (3, 11)", self.action)

    def test_inputs_reach_scripts_through_environment_only(self):
        self.assertEqual(re.findall(r"^ +run: (?!\|$).*", self.action, re.MULTILINE), [])
        for block in re.findall(r"run: \|\n((?:        .*\n|\n)+)", self.action):
            with self.subTest(block=block.splitlines()[0]):
                self.assertNotIn("${{", block)

    def test_documented_inputs_match_the_action(self):
        guide = (ROOT / "guides/adopting-the-checks.md").read_text(encoding="utf-8")
        declared = re.findall(r"^  ([a-z-]+):\n    description:", self.action, re.MULTILINE)
        self.assertEqual(declared, ["path", "checks", "audit-fail-on", "exclude"])
        for name in declared:
            with self.subTest(input=name):
                self.assertIn(f"| `{name}` |", guide)
        self.assertIn("audit|docs-links|html-navigation) ;;", self.action)
        for check in ("audit", "docs-links", "html-navigation"):
            with self.subTest(check=check):
                self.assertIn(f"' {check} ')", self.action)
                self.assertIn(f"| `{check}` |", guide)

    def test_check_steps_read_the_validated_list(self):
        conditions = re.findall(r"^      if: (.*)$", self.action, re.MULTILINE)
        self.assertEqual(3, len(conditions))
        for condition in conditions:
            with self.subTest(condition=condition):
                self.assertIn("steps.setup.outputs.checks", condition)
                self.assertNotIn("inputs.checks", condition)

    def run_setup(self, checks: str, fail_on: str = "error"):
        """Run the action's setup step with bash, the way the runner would."""
        bash = working_bash()
        if bash is None:
            self.skipTest("no working bash on this machine")
        script = re.search(r"id: setup\n(?:.*\n)*?      run: \|\n((?:        .*\n|\n)+)",
                           self.action).group(1)
        script = "\n".join(line[8:] for line in script.splitlines())
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "output"
            output.touch()
            env = dict(os.environ, CHECKS=checks, TARGET=folder, FAIL_ON=fail_on,
                       GITHUB_OUTPUT=str(output))
            result = subprocess.run([bash, "-c", script], env=env, cwd=folder,
                                    capture_output=True, text=True, timeout=60, check=False)
            outputs = dict(line.split("=", 1) for line in
                           output.read_text(encoding="utf-8").splitlines() if "=" in line)
        return result, outputs

    def test_any_whitespace_separates_check_names(self):
        for checks in ("audit docs-links", "audit\ndocs-links\n", "\taudit\tdocs-links",
                       "audit docs-links audit"):
            with self.subTest(checks=checks):
                result, outputs = self.run_setup(checks)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertEqual("audit docs-links", outputs.get("checks"))

    def test_empty_unknown_or_globbing_check_lists_fail(self):
        for checks in ("", " ", "\n\n", "audit doc-links", "*"):
            with self.subTest(checks=checks):
                result, outputs = self.run_setup(checks)
                self.assertEqual(1, result.returncode)
                self.assertNotIn("checks", outputs)

    def test_invalid_fail_on_fails_even_without_the_audit(self):
        result, _ = self.run_setup("docs-links", fail_on="warnings")
        self.assertEqual(1, result.returncode)
        self.assertIn("audit-fail-on must be error, warning or never", result.stdout)

    def test_guide_pins_a_commit_and_is_linked(self):
        guide = (ROOT / "guides/adopting-the-checks.md").read_text(encoding="utf-8")
        self.assertRegex(guide, r"uses: drevendev/BeautifulRepo@[0-9a-f]{40} # v\d+\.\d+\.\d+\n")
        for page in ("README.md", "tools/README.md"):
            with self.subTest(page=page):
                text = (ROOT / page).read_text(encoding="utf-8")
                self.assertIn("guides/adopting-the-checks.md", text)

    def test_ci_self_test_exercises_failure_cases(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("uses: ./", workflow)
        self.assertIn('test "$BROKEN" = failure', workflow)
        self.assertIn('test "$TYPO" = failure', workflow)
        self.assertIn('test "$NEWLINE" = failure', workflow)
        self.assertIn('test "$EMPTY" = failure', workflow)


if __name__ == "__main__":
    unittest.main()
