"""Editor settings must not silently change how Markdown renders."""
import configparser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EditorConfigTests(unittest.TestCase):
    def test_markdown_hard_breaks_survive_whitespace_trimming(self):
        config = configparser.ConfigParser()
        config.read_string("[root]\n" + (ROOT / ".editorconfig").read_text(encoding="utf-8"))
        self.assertEqual(config["*"]["trim_trailing_whitespace"], "true")
        self.assertEqual(config["*.md"]["trim_trailing_whitespace"], "false")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("**Clarity before decoration.** Explain the result before the implementation.  \n", readme)


if __name__ == "__main__":
    unittest.main()
