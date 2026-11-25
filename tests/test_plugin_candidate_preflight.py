"""Exercise the published candidate preparation blocks without real Git or hosts."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIN = "600a02c1aff45580ba517c2af2fa8fe4ea8b4f7c"
GIT_STUB = """#!/bin/sh
if [ "$1" = clone ]; then step=clone; else step=$3; fi
printf '%s\\n' "$step" >> "$BR_LOG"
[ "$BR_FAIL" != "$step" ] || exit 7
case "$step" in
rev-parse) printf '%s\\n' "$BR_PIN";;
status) printf '%s' "$BR_DIRTY";;
clean) printf '%s' "$BR_IGNORED";;
esac
"""


@unittest.skipUnless(os.name == "posix" and shutil.which("sh"), "requires POSIX sh")
class PluginCandidatePreflightTests(unittest.TestCase):
    def test_published_preflight(self):
        scenarios = (
            ("success", "", PIN, "", "", "clean"),
            ("clone error", "clone", PIN, "", "", "clone"),
            ("checkout error", "checkout", PIN, "", "", "checkout"),
            ("SHA lookup error", "rev-parse", PIN, "", "", "rev-parse"),
            ("wrong SHA", "", "wrong", "", "", "rev-parse"),
            ("status error", "status", PIN, "", "", "status"),
            ("dirty", "", PIN, "?? file", "", "status"),
            ("clean error", "clean", PIN, "", "", "clean"),
            ("ignored content", "", PIN, "", "Would remove cache/", "clean"),
        )
        for relative in ("guides/agent-plugin.md", "evals/manual-smoke.md"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            blocks = [
                textwrap.dedent(block)
                for block in re.findall(r"(?m)^ *```sh\n([\s\S]*?)^ *```", source)
                if "git clone https://github.com/drevendev/BeautifulRepo.git BeautifulRepo-candidate" in block
            ]
            self.assertEqual(len(blocks), 1, relative)
            for name, fail, pin, dirty, ignored, last in scenarios:
                with self.subTest(document=relative, case=name), tempfile.TemporaryDirectory() as folder:
                    path = Path(folder)
                    git = path / "git"
                    git.write_text(GIT_STUB, encoding="utf-8")
                    git.chmod(0o755)
                    log = path / "log"
                    env = dict(
                        os.environ,
                        PATH=str(path) + os.pathsep + os.environ["PATH"],
                        BR_LOG=str(log),
                        BR_FAIL=fail,
                        BR_PIN=pin,
                        BR_DIRTY=dirty,
                        BR_IGNORED=ignored,
                    )
                    result = subprocess.run(
                        ["sh", "-c", blocks[0]], cwd=path, env=env,
                        capture_output=True, text=True, timeout=15, check=False,
                    )
                    expected = 0 if name == "success" else 1
                    self.assertEqual(result.returncode, expected, result.stderr)
                    steps = ["clone", "checkout", "rev-parse", "status", "clean"]
                    self.assertEqual(log.read_text(encoding="utf-8").splitlines(), steps[:steps.index(last) + 1])
                    self.assertEqual("Verified clean candidate:" in result.stdout, expected == 0)
                    self.assertEqual("STOP:" in result.stderr, expected != 0)


if __name__ == "__main__":
    unittest.main()
