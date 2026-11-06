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

    def test_descriptions_cover_the_four_candidate_skills(self):
        claude = load(".claude-plugin/plugin.json")
        portable = load("plugin.json")
        marketplace = load(".claude-plugin/marketplace.json")["plugins"][0]
        self.assertEqual(claude["description"], portable["description"])
        descriptions = {
            "shared manifest": portable["description"],
            "Codex short": portable["extensions"]["com.openai"]["interface"]["shortDescription"],
            "Codex long": portable["extensions"]["com.openai"]["interface"]["longDescription"],
            "Claude marketplace": marketplace["description"],
        }
        for label, description in descriptions.items():
            with self.subTest(description=label):
                for capability in ("audit", "readme", "trust", "release"):
                    self.assertIn(capability, description.lower())

    def test_development_install_examples_share_one_immutable_candidate(self):
        """Keep Claude/Codex and the manual matrix pinned to one actual commit."""
        guide = (ROOT / "guides/agent-plugin.md").read_text(encoding="utf-8")
        claude = re.findall(
            r"(?m)^claude plugin marketplace add drevendev/BeautifulRepo@([a-f0-9]{40})$",
            guide,
        )
        codex = re.findall(
            r"(?m)^codex plugin marketplace add drevendev/BeautifulRepo --ref ([a-f0-9]{40})$",
            guide,
        )
        linked = re.findall(
            r"https://github\.com/drevendev/BeautifulRepo/tree/([a-f0-9]{40})",
            guide,
        )
        self.assertEqual(len(claude), 1, "need one full-SHA Claude dev installer")
        self.assertEqual(len(codex), 1, "need one full-SHA Codex dev installer")
        self.assertEqual(len(linked), 1, "need one matching immutable source link")
        self.assertEqual(claude, codex)
        self.assertEqual(claude, linked)
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        roadmap_pins = re.findall(r"is pinned to `([a-f0-9]{40})`", roadmap)
        self.assertEqual(roadmap_pins, claude, "roadmap candidate must match installed candidate")
        self.assertIn(
            f"https://github.com/drevendev/BeautifulRepo/blob/{claude[0]}/evals/manual-smoke.md",
            guide,
        )

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
        self.assertIn("claude plugin install beautifulrepo@beautifulrepo", guide)
        self.assertIn(
            "codex plugin marketplace add drevendev/BeautifulRepo --ref v0.2.0",
            guide,
        )
        self.assertIn("codex plugin marketplace list", guide)
        self.assertIn("`/plugins`", guide)
        self.assertIn("Install plugin", guide)

    def test_codex_guide_distinguishes_marketplace_from_plugin_install(self):
        guide = (ROOT / "guides/agent-plugin.md").read_text(encoding="utf-8")
        self.assertIn("registers a **source**, not an installed plugin", guide)
        self.assertIn("**test procedure**", guide)
        for unsupported_command in ("add", "remove", "update"):
            with self.subTest(command=unsupported_command):
                self.assertNotRegex(
                    guide,
                    rf"(?m)^\s*codex plugin {unsupported_command}\s",
                    "Do not advertise an unverified Codex plugin-management command",
                )


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
                        if re.search(r'-I "R/(?:tools|scripts)/\w+\.py"', line)]
            with self.subTest(skill=path.parent.name):
                self.assertTrue(commands, "skill runs no BeautifulRepo tool")
                for line in commands:
                    self.assertNotIn("--write", line)
                    self.assertNotIn("catalog.py", line)
                    if "docs_links.py" in line or "html_navigation.py" in line:
                        self.assertIn('--root "T"', line)
                    if "repo_audit.py" in line or "release_inventory.py" in line:
                        self.assertIn('"T"', line)


if __name__ == "__main__":
    unittest.main()
