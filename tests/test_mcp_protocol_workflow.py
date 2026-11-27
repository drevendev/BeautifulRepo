"""Keep optional MCP protocol coverage genuinely cross-platform.

This guards workflow wiring, not real SDK or model-host execution.
"""
from __future__ import annotations

from pathlib import Path
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "mcp-protocol.yml"


class MCPProtocolWorkflowTests(unittest.TestCase):
    def test_pinned_sdk_probe_runs_on_ubuntu_and_windows(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("os: [ubuntu-latest, windows-latest]", source)
        self.assertIn("runs-on: ${{ matrix.os }}", source)
        self.assertIn("fail-fast: false", source)
        self.assertIn("python-version: '3.11'", source)
        self.assertIn("shell: python", source)
        self.assertIn('dir=os.environ["RUNNER_TEMP"]', source)
        self.assertIn('[sys.executable, "-m", "venv", str(env)], check=True', source)
        self.assertIn('env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")', source)
        self.assertIn('[str(python), "-m", "pip", "install", "mcp==2.3.0"], check=True', source)
        self.assertIn('[str(python), "-I", "-B", "integrations/mcp_protocol_smoke.py"], check=True', source)
        self.assertLess(source.index('"-m", "venv"'), source.index('"pip", "install"'))
        self.assertLess(source.index('"pip", "install"'), source.index('"integrations/mcp_protocol_smoke.py"'))
        self.assertEqual(2, source.count("integrations/mcp_protocol_smoke.py"))
        self.assertIn("persist-credentials: false", source)
        self.assertIn("permissions:\n  contents: read\n", source)

    def test_independent_public_source_matches_documented_install_pin(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        guide = (WORKFLOW.parents[2] / "guides" / "local-mcp.md").read_text(encoding="utf-8")
        pinned_job = source.split("\n  pinned-source:\n", 1)[1]
        pin = pinned_job.split('pin = "', 1)[1].split('"', 1)[0]
        self.assertRegex(pin, r"^[0-9a-f]{40}$")
        self.assertIn(f"git checkout --detach {pin} || exit 1", guide)
        self.assertIn(f"$pin = '{pin}'", guide)
        self.assertIn("os: [ubuntu-latest, windows-latest]", pinned_job)
        self.assertIn('checkout = Path(tmp) / "source"', pinned_job)
        self.assertIn('"GIT_TERMINAL_PROMPT": "0"', pinned_job)
        self.assertIn('["git", "fetch", "--depth=1", "https://github.com/drevendev/BeautifulRepo.git", pin]', pinned_job)
        self.assertIn('["git", "checkout", "--detach", "FETCH_HEAD"]', pinned_job)
        self.assertIn('["git", "rev-parse", "HEAD"]', pinned_job)
        self.assertIn('if actual != pin:', pinned_job)
        self.assertIn('raise SystemExit("Unexpected pinned source SHA")', pinned_job)
        self.assertLess(pinned_job.index("if actual != pin:"), pinned_job.index('"-m", "venv"'))
        self.assertIn('"install", "--no-cache-dir", "mcp==2.3.0"', pinned_job)
        self.assertIn('[str(python), "-I", "-B", "integrations/mcp_protocol_smoke.py"], cwd=checkout, check=True', pinned_job)
        self.assertEqual(2, source.count("      - 'guides/local-mcp.md'"))

    def test_protocol_workflow_remains_optional_and_scoped(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Additional evidence, not a repository protection or release gate.", source)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("      - 'integrations/**'", source)
        self.assertIn("      - 'tools/**'", source)
        self.assertIn("      - '.github/workflows/mcp-protocol.yml'", source)


if __name__ == "__main__":
    unittest.main()
