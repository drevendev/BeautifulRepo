"""The optional browser-console probe has a tested, bounded measurement contract."""
from pathlib import Path
import json
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "examples/readme-visuals/github-readme-probe.js"
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "Node is optional; browser-console probe needs no Node install")
class BrowserProbeTests(unittest.TestCase):
    def run_probe(self, present=True, pinned=True, github_mode="dark", system_dark=True):
        harness = r'''
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync(process.argv[1], "utf8");
const img = {
  complete: true, naturalWidth: 42, currentSrc: "https://github.com/a/b/image.svg?token=secret",
  getAttribute(key) { return key === "alt" ? "Measured sample" : null; },
};
const article = {
  clientWidth: 300, scrollWidth: 330,
  querySelectorAll(selector) { return selector === "picture img" || selector === "img" ? [img] : []; },
};
const sandbox = {
  document: {
    querySelector() { return process.argv[2] === "yes" ? article : null; },
    documentElement: {
      clientWidth: 320, scrollWidth: 344,
      getAttribute(key) {
        if (process.argv[4] === "none") return null;
        return ({ "data-color-mode": process.argv[4], "data-light-theme": "light",
                  "data-dark-theme": "dark_dimmed" })[key] ?? null;
      },
    },
  },
  window: { innerWidth: 320 },
  location: { origin: "https://github.com", hostname: process.argv[3] === "yes" ? "github.com" : "localhost", pathname: "/a/b/blob/" + "a".repeat(40) + "/README.md", href: "https://github.com/a/b/README.md" },
  matchMedia(query) { return { matches: query.includes("color-scheme") && process.argv[5] === "yes" }; },
  URL, Date, Math,
};
console.log(JSON.stringify(vm.runInNewContext(source, sandbox, {timeout:1000})));
'''
        output = subprocess.run([NODE, "-e", harness, str(PROBE), "yes" if present else "no",
                                 "yes" if pinned else "no", github_mode,
                                 "yes" if system_dark else "no"],
                                text=True, capture_output=True, check=True)
        return json.loads(output.stdout)

    def test_exact_measurements_without_leaking_query_strings(self):
        data = self.run_probe()
        self.assertEqual(data["cssViewportWidth"], 320)
        self.assertEqual(data["pageOverflowPx"], 24)
        self.assertEqual(data["markdownOverflowPx"], 30)
        self.assertTrue(data["prefersDark"])
        self.assertEqual(data["githubAppearance"]["colorMode"], "dark")
        self.assertEqual(data["githubAppearance"]["darkTheme"], "dark_dimmed")
        self.assertEqual(data["images"], 1)
        self.assertEqual(data["unloadedImages"], 0)
        self.assertEqual(data["pictureSelections"][0]["alt"], "Measured sample")
        self.assertEqual(data["pictureSelections"][0]["selectedImagePath"],
                         "https://github.com/a/b/image.svg")
        self.assertNotIn("secret", json.dumps(data))
        self.assertIn("not an accessibility verdict", data["status"])

    def test_forced_site_theme_can_disagree_with_browser_media_preference(self):
        data = self.run_probe(github_mode="dark", system_dark=False)
        self.assertFalse(data["prefersDark"])
        self.assertEqual(data["githubAppearance"]["colorMode"], "dark")
        self.assertEqual(data["githubAppearance"]["lightTheme"], "light")
        self.assertIn("not necessarily", data["caution"])

    def test_absent_site_theme_metadata_is_unknown_not_assumed_light(self):
        data = self.run_probe(github_mode="none")
        self.assertIsNone(data["githubAppearance"]["colorMode"])
        self.assertIsNone(data["githubAppearance"]["darkTheme"])

    def test_missing_renderer_is_not_a_pass(self):
        data = self.run_probe(False)
        self.assertEqual(data["status"], "NOT RUN")
        self.assertIn("No rendered Markdown body", data["reason"])

    def test_non_github_page_is_not_accepted_as_rendered_evidence(self):
        data = self.run_probe(pinned=False)
        self.assertEqual(data["status"], "NOT RUN")
        self.assertIn("full commit SHA", data["reason"])

    def test_helper_is_linked_from_manual_acceptance_protocol(self):
        doc = (ROOT / "checklists/visual-accessibility-acceptance.md").read_text("utf-8")
        self.assertIn("../examples/readme-visuals/github-readme-probe.js", doc)
        self.assertIn("NOT RUN", doc)
        self.assertIn("400%", doc)
        self.assertIn("screen reader", doc.lower())
        self.assertIn("githubAppearance", doc)


if __name__ == "__main__":
    unittest.main()
