"""Case studies share one procedure and one index."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
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

    def test_audit_recipe_captures_each_checker_in_isolated_mode(self):
        for command in (
            'capture audit python -I tools/repo_audit.py "$target" --profile public '
            '--format json --fail-on never',
            'capture markdown python -I tools/docs_links.py --root "$target"',
            'capture html python -I tools/html_navigation.py --root "$target"',
        ):
            with self.subTest(command=command):
                self.assertIn(command, self.index)
        for suffix in ("out", "err", "status"):
            with self.subTest(suffix=suffix):
                self.assertIn(f'"$evidence/$name.{suffix}"', self.index)

    def test_index_is_linked_from_the_readme(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(case-studies/README.md)", readme)



@unittest.skipUnless(os.name == "posix" and shutil.which("sh"), "requires POSIX shell")
class CaseCaptureRecipeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="case capture ")
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name).resolve()
        self.target = self.home / "target snapshot"
        self.target.mkdir()
        self.evidence = self.home / "private evidence"
        self.readme = self.target / "README.md"
        self.readme.write_text(
            "# Parcel\n\nA fictional note index.\n\n## Try it\n\n"
            "[Missing](absent.md)\n\n<a href=\"#absent-heading\">Missing section</a>\n",
            encoding="utf-8",
        )
        self.index = (CASES / "README.md").read_text(encoding="utf-8")

    def run_recipe(self):
        blocks = re.findall(r"^\x60{3}bash\n(.*?)^\x60{3}$", self.index, re.M | re.S)
        (block,) = [item for item in blocks if item.startswith("target=")]
        for name, value in (("target", self.target), ("evidence", self.evidence)):
            assignment = f"{name}={shlex.quote(str(value))}"
            block, count = re.subn(
                rf"^{name}=.*$", lambda _, assignment=assignment: assignment, block, flags=re.M
            )
            self.assertEqual(1, count, name)
        env = dict(os.environ, CASE_TEST_PYTHON=sys.executable)
        return subprocess.run(
            ["sh", "-c", 'python() { "$CASE_TEST_PYTHON" "$@"; }\n' + block],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=40, check=False,
        )

    def read(self, checker, suffix):
        return (self.evidence / f"{checker}.{suffix}").read_text(encoding="utf-8")

    def test_nonzero_checker_does_not_suppress_later_evidence(self):
        original = self.readme.read_bytes()
        result = self.run_recipe()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("0\n", self.read("audit", "status"))
        report = json.loads(self.read("audit", "out"))
        self.assertIn("license.missing", [item["rule_id"] for item in report["findings"]])
        self.assertEqual("1\n", self.read("markdown", "status"))
        self.assertIn("absent.md", self.read("markdown", "err"))
        self.assertEqual("1\n", self.read("html", "status"))
        self.assertIn("absent-heading", self.read("html", "err"))
        self.assertEqual(
            {f"{checker}.{suffix}" for checker in ("audit", "markdown", "html")
             for suffix in ("out", "err", "status")},
            {item.name for item in self.evidence.iterdir()},
        )
        self.assertEqual(0o700, stat.S_IMODE(self.evidence.stat().st_mode))
        self.assertEqual(original, self.readme.read_bytes())
        self.assertEqual(["README.md"], sorted(item.name for item in self.target.iterdir()))

    def test_existing_evidence_is_not_overwritten(self):
        self.evidence.mkdir()
        marker = self.evidence / "audit.out"
        marker.write_bytes(b"previous evidence")
        result = self.run_recipe()
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(b"previous evidence", marker.read_bytes())
        self.assertEqual(["audit.out"], sorted(item.name for item in self.evidence.iterdir()))


if __name__ == "__main__":
    unittest.main()
