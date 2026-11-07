"""No-SDK contract tests for the optional local MCP adapter.

The official MCP client/transport and Claude/Codex host tests are separate
acceptance requirements; these tests do not claim successful host installation.
"""
from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "integrations" / "mcp_server.py"
SPEC = importlib.util.spec_from_file_location("beautifulrepo_mcp_adapter", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


class RootBoundaryTests(unittest.TestCase):
    def test_explicit_absolute_root(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path).resolve()
            self.assertEqual(adapter.allowed_root(str(root)), root)
            with self.assertRaisesRegex(ValueError, "absolute"):
                adapter.allowed_root(".")

    def test_nonexistent_home_and_filesystem_root_rejected(self):
        with self.assertRaises(ValueError):
            adapter.allowed_root(str(Path.home()))
        with self.assertRaises(ValueError):
            adapter.allowed_root(str(Path(Path.cwd().anchor)))
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(ValueError):
                adapter.allowed_root(str(Path(path) / "missing"))

    def test_symlink_parent_cannot_redirect_target(self):
        with tempfile.TemporaryDirectory() as path:
            base = Path(path).resolve()
            real = base / "real"
            real.mkdir()
            alias = base / "alias"
            try:
                alias.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks not available")
            with self.assertRaises(ValueError):
                adapter.allowed_root(str(alias))
            nested = real / "nested"
            nested.mkdir()
            with self.assertRaises(ValueError):
                adapter.allowed_root(str(alias / "nested"))


class CheckerWrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def response(self, key="markdown_links", code=1):
        link = {
            "state": "complete", "exit_code": 1,
            "diagnostics": ["README.md:1: missing docs/setup.md"],
            "checked_destinations": 1, "inspected_markdown_files": 1,
        }
        entry = {
            "state": "complete", "exit_code": 0,
            "report": {"schema_version": 1, "findings": [],
                       "summary": {"error": 0, "warning": 0, "info": 0}},
        }
        payload = {
            "schema_version": 1, "exit_code": code,
            "checks": {"entry_points": entry, "markdown_links": link,
                       "html_navigation": link},
        }
        return subprocess.CompletedProcess([], code, json.dumps(payload).encode(), b"")

    def test_fixed_command_and_native_diagnostics(self):
        with mock.patch.object(adapter, "_bounded_run",
                               return_value=(1, self.response().stdout, None)) as run:
            report = adapter.run_check(self.root, "check_documentation_links")
        self.assertEqual(report["state"], "complete")
        self.assertEqual(report["exit_code"], 1)
        self.assertIn("docs/setup.md", report["evidence"]["diagnostics"][0])
        args, kwargs = run.call_args
        self.assertEqual(args[0], [
            sys.executable, "-I", "-B", str(adapter.BUNDLE),
            str(self.root), "--format", "json", "--fail-on", "never",
        ])
        self.assertEqual(kwargs, {})

    def test_timeout_is_incomplete_not_success(self):
        with mock.patch.object(adapter, "_bounded_run",
                               side_effect=subprocess.TimeoutExpired("audit", 1)):
            report = adapter.run_check(self.root, "audit_repository")
        self.assertEqual(report["state"], "incomplete")
        self.assertEqual(report["exit_code"], 2)

    def test_bad_output_is_incomplete(self):
        with mock.patch.object(adapter, "_bounded_run",
                               return_value=(0, b"garbage", None)):
            report = adapter.run_check(self.root, "check_html_navigation")
        self.assertEqual(report["state"], "incomplete")
        self.assertNotIn("evidence", report)

    def test_large_output_is_incomplete(self):
        reason = "checker output exceeded the bounded response limit"
        with mock.patch.object(adapter, "_bounded_run",
                               return_value=(-9, b"", reason)):
            report = adapter.run_check(self.root, "check_html_navigation")
        self.assertEqual(report["state"], "incomplete")
        self.assertEqual(report["reason"], reason)

    def test_large_stderr_is_incomplete_without_response_bytes(self):
        with mock.patch.object(adapter, "_bounded_run",
                               return_value=(-9, b"", "checker output exceeded the bounded response limit")):
            report = adapter.run_check(self.root, "audit_repository")
        self.assertEqual(report["state"], "incomplete")
        self.assertEqual(report["exit_code"], 2)
        self.assertNotIn("evidence", report)

    def test_rechecks_root_before_every_call(self):
        with mock.patch.object(adapter, "_bounded_run") as run:
            report = adapter.run_check(self.root / "missing", "audit_repository")
        self.assertEqual(report["state"], "incomplete")
        run.assert_not_called()

    def test_real_bundle_reports_broken_link_without_target_edit(self):
        (self.root / "README.md").write_text("# Example\n\n[Guide](docs/missing.md)\n", encoding="utf-8")
        before = (self.root / "README.md").read_bytes()
        report = adapter.run_check(self.root, "check_documentation_links")
        self.assertEqual(report["state"], "complete", report)
        self.assertEqual(report["exit_code"], 1)
        self.assertTrue(any("missing" in str(item).lower()
                            for item in report["evidence"]["diagnostics"]), report)
        self.assertEqual((self.root / "README.md").read_bytes(), before)


class BoundedCaptureTests(unittest.TestCase):
    def test_short_stdout_and_stderr_are_drained(self):
        code, output, reason = adapter._bounded_run([
            sys.executable, "-I", "-c",
            "import os; os.write(1, b'hello'); os.write(2, b'diagnostic')",
        ])
        self.assertEqual((code, output, reason), (0, b"hello", None))

    def test_noisy_stdout_is_killed_before_end_of_sleep(self):
        code, output, reason = adapter._bounded_run([
            sys.executable, "-I", "-c",
            "import os,time; os.write(1, b'x' * 1048576); time.sleep(5)",
        ])
        self.assertIsNotNone(code)
        self.assertEqual(output, b"")
        self.assertEqual(reason, "checker output exceeded the bounded response limit")

    def test_noisy_stderr_is_killed_before_end_of_sleep(self):
        code, output, reason = adapter._bounded_run([
            sys.executable, "-I", "-c",
            "import os,time; os.write(2, b'x' * 1048576); time.sleep(5)",
        ])
        self.assertIsNotNone(code)
        self.assertEqual(output, b"")
        self.assertEqual(reason, "checker output exceeded the bounded response limit")

    def test_real_process_timeout(self):
        with mock.patch.object(adapter, "TIMEOUT_SECONDS", 0.1):
            with self.assertRaises(subprocess.TimeoutExpired):
                adapter._bounded_run([
                    sys.executable, "-I", "-c", "import time; time.sleep(5)",
                ])


class ToolSurfaceTests(unittest.TestCase):
    def test_three_argument_free_read_only_tools_are_registered(self):
        registrations = {}
        class FakeServer:
            def __init__(self, name):
                self.name = name
            def tool(self):
                def register(func):
                    registrations[func.__name__] = func
                    return func
                return register

        with mock.patch.dict(sys.modules, {
            "mcp": types.ModuleType("mcp"),
            "mcp.server": types.ModuleType("mcp.server"),
        }):
            sys.modules["mcp.server"].MCPServer = FakeServer
            with tempfile.TemporaryDirectory() as tmp:
                server = adapter.make_server(Path(tmp))
        self.assertIsInstance(server, FakeServer)
        self.assertEqual(set(registrations), set(adapter.CHECKS))
        for func in registrations.values():
            self.assertEqual(len(inspect.signature(func).parameters), 0)


if __name__ == "__main__":
    unittest.main()
