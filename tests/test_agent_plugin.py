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
        checkout = re.findall(
            r"(?m)^git -C BeautifulRepo-candidate checkout --detach ([a-f0-9]{40})$",
            guide,
        )
        self.assertIn("git -C BeautifulRepo-candidate rev-parse HEAD", guide)
        self.assertIn("claude plugin marketplace add ./BeautifulRepo-candidate", guide)
        self.assertIn("codex plugin marketplace add ./BeautifulRepo-candidate", guide)
        # Optional source validation runs before marketplace registration.
        # It does not exercise installed files or model selection.
        preflight = "claude plugin validate ./BeautifulRepo-candidate"
        self.assertIn(preflight, guide)
        self.assertLess(
            guide.index(preflight),
            guide.index("claude plugin marketplace add ./BeautifulRepo-candidate"),
        )
        self.assertIn("v2.1.289+", guide)
        self.assertIn("not an installed-host", guide)
        self.assertNotRegex(
            guide,
            r"(?m)^claude plugin marketplace add drevendev/BeautifulRepo@[a-f0-9]{40}$",
        )
        linked = re.findall(
            r"https://github\.com/drevendev/BeautifulRepo/tree/([a-f0-9]{40})",
            guide,
        )
        self.assertEqual(len(checkout), 1, "need one full-SHA local candidate checkout")
        self.assertEqual(len(linked), 1, "need one matching immutable source link")
        self.assertEqual(checkout, linked)
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        roadmap_pins = re.findall(r"is pinned to `([a-f0-9]{40})`", roadmap)
        self.assertEqual(roadmap_pins, checkout, "roadmap candidate must match the checkout")
        self.assertIn(
            f"https://github.com/drevendev/BeautifulRepo/blob/{checkout[0]}/evals/manual-smoke.md",
            guide,
        )

        comparison = (ROOT / "evals/three-arm-comparison.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            f"https://github.com/drevendev/BeautifulRepo/tree/{checkout[0]}",
            comparison,
            "the three-arm protocol must use the same immutable candidate",
        )
        self.assertIn(
            f"--expected-commit {checkout[0]}",
            guide,
            "offline cache verification must pin the tested candidate",
        )

        # The immutable matrix's step 3 links to a historical installation
        # guide. Without an explicit warning, following that link silently
        # changes the tested source even though all current-checkout pins agree.
        self.assertIn(
            "**Do not follow the matrix's relative installation-guide link.**",
            guide,
        )
        self.assertIn(
            "still installs `cf8ac81ddabb5e2006913e65a2f980ef201baf5c` instead.",
            guide,
        )
        self.assertIn(
            f"`--expected-commit {checkout[0]}` cache",
            guide,
        )

    def test_cache_verifier_is_separately_pinned_from_immutable_candidate(self):
        """The corrected tool must not be attributed to an older source pin."""
        guide = (ROOT / "guides/agent-plugin.md").read_text(encoding="utf-8")
        section = guide.split("## Verify cached skill definitions", 1)[1]
        candidate = "8947574399df2cc11e8ded41cecbef70be4808c6"
        verifier = "56d1c0236000354647cd1ea1987354a3c0025e70"
        self.assertNotEqual(candidate, verifier)
        self.assertIn(
            f"git -C BeautifulRepo-verifier checkout --detach {verifier}",
            section,
        )
        self.assertIn("git -C BeautifulRepo-verifier rev-parse HEAD", section)
        self.assertIn(
            'python -I "/absolute/path/to/BeautifulRepo-verifier/scripts/plugin_install_verify.py"',
            section,
        )
        self.assertIn('--source "/absolute/path/to/BeautifulRepo-candidate"', section)
        self.assertIn(f"--expected-commit {candidate}", section)
        self.assertIn("three distinct physical directories", section)
        self.assertIn("`checked_present_manifests`", section)
        self.assertIn("`missing_optional_manifests`", section)
        self.assertIn("`checked_skill_assets`", section)
        self.assertIn("`different_skill_assets`", section)
        self.assertIn("all Git-tracked, non-`SKILL.md` files", section)
        self.assertIn("The older `ac28c4f6` verifier", section)
        self.assertIn("The intermediate `207ea2c` verifier", section)
        self.assertIn("Unexpected", section)
        self.assertIn("skill-local files", section)
        self.assertIn("up to 1,024 visited entries", section)
        self.assertIn("Extra files **outside**", section)
        pinned_checkouts = re.findall(
            r"(?m)^git -C BeautifulRepo-verifier checkout --detach ([0-9a-f]{40})$",
            section,
        )
        self.assertEqual(pinned_checkouts, [verifier])
        tools_guide = (ROOT / "tools/README.md").read_text(encoding="utf-8")
        self.assertIn("inside the four installed skill folders", tools_guide)
        self.assertIn("Extra files elsewhere in the plugin", tools_guide)
        self.assertNotIn(
            "Extra untracked cache files and missing optional",
            tools_guide,
        )
        self.assertNotIn(
            'python -I "/absolute/path/to/pinned-source/scripts/plugin_install_verify.py"',
            section,
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

    def test_local_tool_skills_require_a_desktop_executor(self):
        """Public skills run local Python/Git; web-only execution cannot audit a checkout."""
        manifest = load("plugin.json")
        self.assertIs(manifest["extensions"]["com.openai"].get("requires_local_executor"), True)

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
        self.assertIn("Plugins Directory", guide)
        self.assertIn("**INCONCLUSIVE/FAIL**", guide)

    def test_codex_guide_distinguishes_marketplace_from_plugin_install(self):
        guide = (ROOT / "guides/agent-plugin.md").read_text(encoding="utf-8")
        released = guide.split(
            "## Install the released audit skill (v0.2.0)", 1
        )[1].split("## Try all four skills", 1)[0]
        candidate = guide.split(
            "## Try all four skills from a pinned development candidate", 1
        )[1].split("## Verify cached skill definitions", 1)[0]

        # A marketplace registration is not proof of plugin installation.
        # Keep both official installation routes discoverable in both paths.
        self.assertRegex(
            released,
            r"(?s)`codex plugin marketplace add`.{0,90}registers a source;"
            r" it does\s+not install the plugin",
        )
        self.assertIn("only **register and list** the source", candidate)
        self.assertIn("**not** installation evidence", candidate)
        for name, section in (("release", released), ("candidate", candidate)):
            with self.subTest(path=name):
                self.assertIn(
                    "https://developers.openai.com/learn/developers-codex-plugin",
                    section,
                )
                self.assertIn("`/plugins`", section)
                self.assertIn("**Install plugin**", section)
                self.assertIn("Plugins Directory", section)
                self.assertIn("installed/cached", section)

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

    def test_skill_root_discovery_is_relative_to_the_skill_directory(self):
        """Portable fallback must walk from skills/<name>/, not the SKILL.md file."""
        for path in self.skills():
            with self.subTest(skill=path.parent.name):
                self.assertEqual((path.parent / ".." / "..").resolve(), ROOT.resolve())
                body = path.read_text(encoding="utf-8")
                self.assertIn("directory containing", body)
                self.assertIn("`../..`", body)

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
