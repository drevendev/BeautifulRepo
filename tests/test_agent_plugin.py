"""Contract for the Claude Code / Codex plugin: manifests agree and skills stay safe and portable."""
import json
import os
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAME = "beautifulrepo"
PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}  # allowed-tools is experimental, never a security boundary
SKILL_NAME = re.compile(r"[a-z0-9](?:[a-z0-9]|-(?!-)){0,63}\Z")


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Validate the scalar frontmatter subset used by our portable skills."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise AssertionError("SKILL.md needs a closed YAML frontmatter block")
    end = lines.index("---", 1)
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(": ")
        if not separator or not key or key in fields:
            raise AssertionError(f"malformed or duplicate frontmatter field: {line!r}")
        fields[key] = value
    return fields, "\n".join(lines[end + 1:])


class PluginManifestTests(unittest.TestCase):
    def test_names_and_versions_agree_across_both_agents(self):
        claude, portable = load(".claude-plugin/plugin.json"), load("plugin.json")
        claude_market, codex_market = load(".claude-plugin/marketplace.json"), load(".agents/plugins/marketplace.json")
        self.assertEqual(claude["name"], NAME)
        self.assertEqual(portable["name"], NAME)
        self.assertEqual(claude["version"], portable["version"])
        for market in (claude_market, codex_market):
            with self.subTest(market=market["name"]):
                self.assertEqual(market["name"], NAME)
                self.assertEqual([plugin["name"] for plugin in market["plugins"]], [NAME])
                self.assertNotIn("version", market["plugins"][0])
        self.assertEqual(claude_market["plugins"][0]["source"], "./")
        self.assertEqual(codex_market["plugins"][0]["source"], {"source": "local", "path": "./"})

    def test_manifest_versions_are_valid(self):
        for path in (".claude-plugin/plugin.json", "plugin.json"):
            version = load(path)["version"]
            with self.subTest(manifest=path):
                self.assertRegex(version, r"\A\d+\.\d+\.\d+(?:-dev\.\d+)?\Z")

    def test_tagged_release_matches_manifests_and_dated_changelog(self):
        ref = os.environ.get("GITHUB_REF", "")
        if not ref.startswith("refs/tags/v"):
            self.skipTest("not running on a v* tag")
        version = ref.removeprefix("refs/tags/v")
        self.assertRegex(version, r"\A\d+\.\d+\.\d+\Z")
        for path in (".claude-plugin/plugin.json", "plugin.json"):
            self.assertEqual(load(path)["version"], version, path)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        heading = rf"(?m)^## \[v{re.escape(version)}\]\s+[—–-]\s+\d{{4}}-\d{{2}}-\d{{2}}\s*$"
        self.assertRegex(changelog, heading)

    def test_codex_reads_only_the_portable_manifest(self):
        # A .codex-plugin/plugin.json overrides the portable one and has broken `codex plugin add`.
        self.assertFalse((ROOT / ".codex-plugin/plugin.json").exists())

    def test_install_guide_is_reachable(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("(guides/agent-plugin.md)", readme)
        guide = (ROOT / "guides/agent-plugin.md").read_text(encoding="utf-8")
        for command in ("claude plugin install beautifulrepo@beautifulrepo",
                        "codex plugin add beautifulrepo@beautifulrepo"):
            self.assertIn(command, guide)


class FrontmatterParserTests(unittest.TestCase):
    def test_duplicate_and_unclosed_frontmatter_fail(self):
        for sample in (
            "---\nname: audit-repo\nname: other\n---\n",
            "---\nname: audit-repo\n",
            "---\ninvalid line\n---\n",
        ):
            with self.subTest(sample=sample):
                with self.assertRaises(AssertionError):
                    frontmatter(sample)


class SkillTests(unittest.TestCase):
    def skills(self):
        found = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(found, "no skills found")
        return found

    def test_frontmatter_is_portable_and_triggers_are_explicit(self):
        for path in self.skills():
            fields, body = frontmatter(path.read_text(encoding="utf-8"))
            with self.subTest(skill=path.parent.name):
                self.assertLessEqual(set(fields), PORTABLE_KEYS)
                self.assertEqual(fields["name"], path.parent.name)
                self.assertRegex(fields["name"], SKILL_NAME)
                self.assertTrue(fields["description"].strip())
                self.assertLessEqual(len(fields["description"]), 1024)
                if "compatibility" in fields:
                    self.assertLessEqual(len(fields["compatibility"]), 500)
                self.assertIn("Use when", fields["description"])
                self.assertIn("Do not use", fields["description"])
                self.assertLess(len(body.splitlines()), 500)

    def test_skills_reference_files_that_exist(self):
        for path in self.skills():
            text = path.read_text(encoding="utf-8")
            with self.subTest(skill=path.parent.name):
                self.assertIn("guides/agent-safety.md", text)
                for relative in set(re.findall(r"\b((?:tools|checklists|guides|templates)/[\w./-]+\.(?:py|md))", text)):
                    target = (ROOT / relative).resolve()
                    self.assertTrue(target.is_relative_to(ROOT.resolve()), relative)
                    self.assertTrue(target.is_file(), relative)

    def test_tool_commands_are_isolated_explicit_and_read_only(self):
        for path in self.skills():
            commands = [line for line in path.read_text(encoding="utf-8").splitlines()
                        if re.search(r'-I "R/tools/\w+\.py"', line)]
            with self.subTest(skill=path.parent.name):
                self.assertTrue(commands, "skill runs no BeautifulRepo tool")
                for line in commands:
                    self.assertNotIn("--write", line)
                    self.assertNotIn("catalog.py", line)
                    if "docs_links.py" in line or "html_navigation.py" in line:
                        self.assertIn('--root "T"', line)
                    if "repo_audit.py" in line:
                        self.assertIn('"T"', line)


if __name__ == "__main__":
    unittest.main()
