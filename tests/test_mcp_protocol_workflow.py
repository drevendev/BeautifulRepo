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
        self.assertIn('python -m pip install "mcp==2.3.0"', source)
        self.assertIn("python -I -B integrations/mcp_protocol_smoke.py", source)
        self.assertEqual(1, source.count("integrations/mcp_protocol_smoke.py"))
        self.assertIn("persist-credentials: false", source)
        self.assertIn("permissions:\n  contents: read\n", source)

    def test_protocol_workflow_remains_optional_and_scoped(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Additional evidence, not a repository protection or release gate.", source)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("      - 'integrations/**'", source)
        self.assertIn("      - 'tools/**'", source)
        self.assertIn("      - '.github/workflows/mcp-protocol.yml'", source)


if __name__ == "__main__":
    unittest.main()
