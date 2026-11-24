"""Run the documented Windows MCP setup against fake commands, without network."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


GUIDE = Path(__file__).resolve().parents[1] / "guides" / "local-mcp.md"
PWSH = shutil.which("pwsh")

# The mocks record control flow, not Git, SDK, or host behavior.
HARNESS = r"""
$global:seen = [System.Collections.Generic.List[string]]::new()
$global:LASTEXITCODE = 0
function Record-Step([string]$step) {
    $global:seen.Add($step)
    if ($env:BR_TEST_FAIL -eq $step) { $global:LASTEXITCODE = 1 }
    else { $global:LASTEXITCODE = 0 }
}
function git {
    switch ($args[0]) {
        'clone' { Record-Step 'clone' }
        'checkout' { Record-Step 'checkout' }
        'rev-parse' {
            Record-Step 'sha'
            if ($env:BR_TEST_FAIL -eq 'wrong-sha') { 'wrong' }
            else { $env:BR_TEST_PIN }
        }
        default { throw 'Unexpected Git command' }
    }
}
function py { Record-Step 'venv' }
function test-python {
    if ($args -contains 'pip') { Record-Step 'install' }
    else { Record-Step 'smoke' }
}
function Set-Location {
    [CmdletBinding()]
    param([string]$Path)
    Record-Step 'location'
    if ($env:BR_TEST_FAIL -eq 'location') { Write-Error 'Missing directory' }
}
function Resolve-Path {
    [CmdletBinding()]
    param([string]$Path)
    switch -Wildcard ($Path) {
        '*python.exe' { $step = 'python-path'; $resolved = 'test-python' }
        '*mcp_server.py' { $step = 'server-path'; $resolved = 'C:\test space\server.py' }
        '*healthy' { $step = 'root-path'; $resolved = 'C:\test space\healthy' }
        default { throw 'Unexpected Resolve-Path' }
    }
    Record-Step $step
    if ($env:BR_TEST_FAIL -eq $step) {
        Write-Error 'Missing path'
        return
    }
    [pscustomobject]@{ Path = $resolved }
}
"""


class McpWindowsSetupDocsTests(unittest.TestCase):
    def setUp(self):
        text = GUIDE.read_text(encoding="utf-8")
        section = text.split("### Windows PowerShell:", 1)[1].split("### Claude Code:", 1)[0]
        self.block = section.split("```powershell\n", 1)[1].split("\n```", 1)[0]
        self.pin = re.search(r"\$pin = '([0-9a-f]{40})'", self.block).group(1)

    def test_path_resolution_and_directory_change_are_terminating(self):
        self.assertIn("Set-Location BeautifulRepo -ErrorAction Stop", self.block)
        paths = [line for line in self.block.splitlines() if "Resolve-Path" in line]
        self.assertEqual(len(paths), 3)
        for line in paths:
            self.assertIn("-ErrorAction Stop", line)
        self.assertIn("Get-Command git, py -ErrorAction Stop", self.block)
        self.assertTrue(self.block.startswith(". {"))

    @unittest.skipUnless(PWSH, "PowerShell 7 is unavailable")
    def test_setup_stops_after_each_failed_stage(self):
        stages = [
            "clone", "location", "checkout", "sha", "venv", "python-path",
            "install", "smoke", "server-path", "root-path",
        ]
        tail = r"""
$paths = @($brPython, $brServer, $brRoot)
ConvertTo-Json -Compress -InputObject @{
    ok = $ok
    seen = @($global:seen.ToArray())
    paths = $paths
}
"""
        script = HARNESS + "\ntry {\n" + self.block + "\n$ok = $true\n} catch { $ok = $false }\n" + tail
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "setup-test.ps1"
            path.write_text(script, encoding="utf-8")
            for failure in ["", *stages, "wrong-sha"]:
                with self.subTest(failure=failure):
                    result = subprocess.run(
                        [PWSH, "-NoProfile", "-NonInteractive", "-File", str(path)],
                        env={**os.environ, "BR_TEST_FAIL": failure, "BR_TEST_PIN": self.pin},
                        capture_output=True, text=True, encoding="utf-8", timeout=20,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    evidence = json.loads(result.stdout)
                    if failure:
                        stop = "sha" if failure == "wrong-sha" else failure
                        self.assertFalse(evidence["ok"])
                        self.assertEqual(evidence["seen"], stages[:stages.index(stop) + 1])
                    else:
                        self.assertTrue(evidence["ok"])
                        self.assertEqual(evidence["seen"], stages)
                        self.assertEqual(evidence["paths"], [
                            "test-python", r"C:\test space\server.py", r"C:\test space\healthy",
                        ])
