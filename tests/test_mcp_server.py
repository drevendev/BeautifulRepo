"""No-SDK contract tests for the optional local MCP adapter.

The official MCP client/transport and Claude/Codex host tests are separate
acceptance requirements; these tests do not claim successful host installation.
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import os
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


    def test_ordinary_nested_absolute_root_without_canonical_spelling_assumption(self):
        with tempfile.TemporaryDirectory() as path:
            # Exercise lexical parents too, not only a pre-resolved final path.
            root = Path(path) / "normal" / "nested"
            root.mkdir(parents=True)
            self.assertEqual(adapter.allowed_root(str(root)), root.resolve())

    def test_parent_traversal_still_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            base = Path(path).resolve()
            (base / "nested").mkdir()
            with self.assertRaisesRegex(ValueError, "parent traversal"):
                adapter.allowed_root(str(base / "nested" / ".."))

    def test_unknown_windows_reparse_ancestor_is_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            base = Path(path).resolve()
            redirected = base / "reparse-like"
            target = redirected / "repo"
            target.mkdir(parents=True)
            original = adapter.os.lstat

            def tagged(candidate):
                info = original(candidate)
                if Path(candidate) == redirected:
                    return types.SimpleNamespace(st_mode=info.st_mode,
                                                 st_reparse_tag=0xA000001D)
                return info

            with mock.patch.object(adapter.os, "lstat", side_effect=tagged):
                with self.assertRaisesRegex(ValueError, "redirects"):
                    adapter.allowed_root(str(target))

            def attribute_only(candidate):
                info = original(candidate)
                if Path(candidate) == redirected:
                    return types.SimpleNamespace(st_mode=info.st_mode,
                                                 st_file_attributes=0x400)
                return info

            with mock.patch.object(adapter, "REPARSE_ATTRIBUTE", 0x400):
                with mock.patch.object(adapter.os, "lstat", side_effect=attribute_only):
                    with self.assertRaisesRegex(ValueError, "redirects"):
                        adapter.allowed_root(str(target))

    def test_junction_tagged_ancestor_is_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            base = Path(path).resolve()
            ancestor = base / "junction-like"
            root = ancestor / "repo"
            root.mkdir(parents=True)
            real_lstat = adapter.os.lstat

            def with_junction_metadata(candidate):
                info = real_lstat(candidate)
                if Path(candidate) == ancestor:
                    return types.SimpleNamespace(
                        st_mode=info.st_mode,
                        st_reparse_tag=adapter.JUNCTION_TAG,
                    )
                return info

            with mock.patch.object(adapter.os, "lstat", side_effect=with_junction_metadata):
                with self.assertRaisesRegex(ValueError, "redirects"):
                    adapter.allowed_root(str(root))


    @unittest.skipUnless(os.name == "nt", "real Windows junction requires Windows")
    def test_real_windows_junction_ancestor_rejected_before_any_checker(self):
        """Use a real junction, not patched lstat metadata, when supported."""
        with tempfile.TemporaryDirectory() as path:
            base = Path(path).resolve()
            real = base / "real"
            repo = real / "repo"
            repo.mkdir(parents=True)
            document = repo / "README.md"
            document.write_text("# Synthetic fixture\n", encoding="utf-8")
            alias = base / "junction"
            # mklink /J creates a directory junction without requiring a
            # symlink privilege. This is an optional native Windows fixture.
            created = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(alias), str(real)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, check=False,
            )
            if created.returncode != 0:
                self.skipTest("directory junction unavailable on this Windows filesystem")
            try:
                self.assertEqual(
                    getattr(os.lstat(alias), "st_reparse_tag", None),
                    adapter.JUNCTION_TAG,
                    "native test must exercise a real mount-point reparse tag",
                )
                with mock.patch.object(adapter, "_bounded_run") as checker:
                    for candidate in (alias, alias / "repo"):
                        with self.subTest(root=str(candidate)):
                            with self.assertRaises(ValueError):
                                adapter.allowed_root(str(candidate))
                            result = adapter.run_check(candidate, "audit_repository")
                            self.assertEqual(result["state"], "incomplete")
                            self.assertEqual(result["exit_code"], 2)
                    checker.assert_not_called()
                self.assertEqual(document.read_text(encoding="utf-8"), "# Synthetic fixture\n")
            finally:
                # Remove the junction itself, never recurse into its target.
                alias.rmdir()
            self.assertTrue(repo.is_dir())


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
            "checks": {key: entry if key == "entry_points" else link},
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
            "--only", "markdown_links",
        ])
        self.assertEqual(kwargs, {})

    def test_timeout_is_incomplete_not_success(self):
        with mock.patch.object(adapter, "_bounded_run",
                               side_effect=subprocess.TimeoutExpired("audit", 1)):
            report = adapter.run_check(self.root, "audit_repository")
        self.assertEqual(report["state"], "incomplete")
        self.assertEqual(report["exit_code"], 2)

    def test_bundled_incomplete_reason_is_actionable_and_path_free(self):
        for checker_reason in (
                "checker result exceeded the 128-KiB limit",
                "checker failed before producing complete evidence"):
            payload = {
                "schema_version": 1, "exit_code": 2,
                "checks": {"markdown_links": {
                    "state": "incomplete", "exit_code": None,
                    "reason": checker_reason,
                }},
            }
            with self.subTest(checker_reason):
                with mock.patch.object(adapter, "_bounded_run", return_value=(
                        2, json.dumps(payload).encode("utf-8"), None)):
                    result = adapter.run_check(self.root, "check_documentation_links")
                self.assertEqual(result["state"], "incomplete")
                self.assertEqual(result["exit_code"], 2)
                self.assertEqual(result["reason"], checker_reason)
                self.assertNotIn("evidence", result)

    def test_unrecognized_incomplete_reason_is_not_leaked(self):
        payload = {
            "schema_version": 1, "exit_code": 2,
            "checks": {"markdown_links": {
                "state": "incomplete", "exit_code": None,
                "reason": "private/path.md: untrusted message",
            }},
        }
        with mock.patch.object(adapter, "_bounded_run", return_value=(
                2, json.dumps(payload).encode("utf-8"), None)):
            result = adapter.run_check(self.root, "check_documentation_links")
        self.assertEqual(result["state"], "incomplete")
        self.assertNotIn("private/path.md", result["reason"])

    def test_inconsistent_bundle_and_checker_status_is_incomplete(self):
        for bundle_exit, checker_exit, state in (
                (0, 1, "complete"),
                (2, 0, "complete"),
                (2, 1, "complete"),
                (1, None, "incomplete"),
        ):
            payload = {
                "schema_version": 1, "exit_code": bundle_exit,
                "checks": {"markdown_links": {
                    "state": state, "exit_code": checker_exit,
                    "diagnostics": [],
                }},
            }
            with self.subTest((bundle_exit, checker_exit, state)):
                with mock.patch.object(adapter, "_bounded_run", return_value=(
                        bundle_exit, json.dumps(payload).encode("utf-8"), None)):
                    result = adapter.run_check(self.root, "check_documentation_links")
                self.assertEqual(result["state"], "incomplete")
                self.assertEqual(result["exit_code"], 2)
                self.assertNotIn("evidence", result)

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

    def test_oversized_markdown_fails_before_checker_launch(self):
        (self.root / "README.md").write_text("12345678", encoding="utf-8")
        with mock.patch.object(adapter, "MAX_SOURCE_BYTES", 4):
            with mock.patch.object(adapter, "_bounded_run") as run:
                result = adapter.run_check(self.root, "check_documentation_links")
        self.assertEqual(result["state"], "incomplete")
        self.assertEqual(result["exit_code"], 2)
        run.assert_not_called()

    def test_too_many_sources_fails_before_checker_launch(self):
        (self.root / "one.md").write_text("one", encoding="utf-8")
        (self.root / "two.markdown").write_text("two", encoding="utf-8")
        with mock.patch.object(adapter, "MAX_MARKDOWN_SOURCES", 1):
            with mock.patch.object(adapter, "_bounded_run") as run:
                result = adapter.run_check(self.root, "check_html_navigation")
        self.assertEqual(result["state"], "incomplete")
        run.assert_not_called()

    def test_outside_markdown_symlink_fails_before_checker_launch(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "secret.txt"
            target.write_text("synthetic", encoding="utf-8")
            try:
                (self.root / "linked.md").symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("file symlinks not available")
            with mock.patch.object(adapter, "_bounded_run") as run:
                result = adapter.run_check(self.root, "check_documentation_links")
            self.assertEqual(result["state"], "incomplete")
            run.assert_not_called()

    def test_non_markdown_symlink_outside_root_fails_before_every_checker(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "private.txt"
            external.write_text("synthetic outside content", encoding="utf-8")
            for name in ("LICENSE", "README.rst", "assets/logo.svg"):
                with self.subTest(name=name):
                    alias = self.root / name
                    alias.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        alias.symlink_to(external)
                    except (OSError, NotImplementedError):
                        self.skipTest("file symlinks unavailable")
                    try:
                        with mock.patch.object(adapter, "_bounded_run") as run:
                            for tool_name in adapter.CHECKS:
                                report = adapter.run_check(self.root, tool_name)
                                self.assertEqual(report["state"], "incomplete")
                                self.assertEqual(report["exit_code"], 2)
                            run.assert_not_called()
                        self.assertEqual(external.read_text(encoding="utf-8"),
                                         "synthetic outside content")
                    finally:
                        alias.unlink()

    def test_non_markdown_symlink_to_in_root_file_remains_allowed(self):
        original = self.root / "original.svg"
        original.write_text("<svg></svg>", encoding="utf-8")
        alias = self.root / "image.svg"
        try:
            alias.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("file symlinks unavailable")
        self.assertTrue(adapter._bounded_source_tree(self.root))

    def test_non_markdown_directory_symlink_is_refused(self):
        ordinary = self.root / "docs"
        ordinary.mkdir()
        alias = self.root / "linked-docs"
        try:
            alias.symlink_to(ordinary, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        with mock.patch.object(adapter, "_bounded_run") as run:
            for tool_name in adapter.CHECKS:
                report = adapter.run_check(self.root, tool_name)
                self.assertEqual(report["state"], "incomplete")
                self.assertEqual(report["exit_code"], 2)
            run.assert_not_called()

    def test_hardlinked_outside_markdown_is_refused_by_every_tool(self):
        with tempfile.TemporaryDirectory() as outside:
            original = Path(outside) / "external.md"
            original.write_text("# Synthetic outside file\n", encoding="utf-8")
            linked = self.root / "README.md"
            try:
                os.link(original, linked)
            except OSError:
                self.skipTest("hard links unavailable on this filesystem")
            self.assertGreater(linked.stat().st_nlink, 1)
            self.assertFalse(adapter._bounded_source_tree(self.root))
            with mock.patch.object(adapter, "_bounded_run") as run:
                for tool_name in adapter.CHECKS:
                    with self.subTest(tool=tool_name):
                        result = adapter.run_check(self.root, tool_name)
                        self.assertEqual(result["state"], "incomplete")
                        self.assertEqual(result["exit_code"], 2)
                run.assert_not_called()
            # Releasing the outside alias makes the same ordinary file safe.
            original.unlink()
            self.assertEqual(linked.stat().st_nlink, 1)
            self.assertTrue(adapter._bounded_source_tree(self.root))

    def test_non_markdown_hardlinked_entrypoints_are_refused(self):
        with tempfile.TemporaryDirectory() as outside:
            for name in ("LICENSE", "README.rst", "index.html"):
                with self.subTest(name=name):
                    original = Path(outside) / name
                    original.write_text("synthetic outside file", encoding="utf-8")
                    linked = self.root / name
                    try:
                        os.link(original, linked)
                    except OSError:
                        self.skipTest("hard links unavailable on this filesystem")
                    self.assertGreater(linked.stat().st_nlink, 1)
                    with mock.patch.object(adapter, "_bounded_run") as run:
                        for tool_name in adapter.CHECKS:
                            report = adapter.run_check(self.root, tool_name)
                            self.assertEqual(report["state"], "incomplete")
                            self.assertEqual(report["exit_code"], 2)
                        run.assert_not_called()
                    linked.unlink()
                    self.assertEqual(original.stat().st_nlink, 1)
                    self.assertTrue(adapter._bounded_source_tree(self.root))

    def test_ordinary_nested_markdown_passes_preflight(self):
        (self.root / "nested").mkdir()
        (self.root / "nested" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        self.assertTrue(adapter._bounded_source_tree(self.root))

    def test_unknown_windows_reparse_sources_fail_closed(self):
        for kind in ("directory", "ordinary-file"):
            with self.subTest(kind=kind):
                path = self.root / ("redirected" if kind == "directory" else "LICENSE")
                if kind == "directory":
                    path.mkdir()
                    (path / "guide.md").write_text("# synthetic", encoding="utf-8")
                else:
                    path.write_text("synthetic", encoding="utf-8")
                original = adapter.os.lstat

                def tagged(candidate, original=original, path=path):
                    info = original(candidate)
                    if Path(candidate) == path:
                        return types.SimpleNamespace(
                            st_mode=info.st_mode,
                            st_reparse_tag=0xA000001D,
                            st_size=getattr(info, "st_size", 0),
                        )
                    return info

                with mock.patch.object(adapter.os, "lstat", side_effect=tagged):
                    with mock.patch.object(adapter, "_bounded_run") as run:
                        for tool_name in adapter.CHECKS:
                            response = adapter.run_check(self.root, tool_name)
                            self.assertEqual(response["state"], "incomplete")
                            self.assertEqual(response["exit_code"], 2)
                        run.assert_not_called()
                if kind == "directory":
                    (path / "guide.md").unlink()
                    path.rmdir()
                else:
                    path.unlink()

    def test_junction_tagged_directory_fails_closed_before_checker(self):
        redirected = self.root / "junction-like"
        redirected.mkdir()
        (redirected / "oversized.md").write_text("12345678", encoding="utf-8")
        real_lstat = adapter.os.lstat

        def with_junction_metadata(path):
            info = real_lstat(path)
            if Path(path) == redirected:
                return types.SimpleNamespace(
                    st_mode=info.st_mode,
                    st_size=info.st_size,
                    st_reparse_tag=adapter.JUNCTION_TAG,
                )
            return info

        # Simulate NTFS junction metadata without requiring elevated Windows
        # privileges. DirEntry.stat may omit the tag; os.lstat must be used.
        with mock.patch.object(adapter.os, "lstat", side_effect=with_junction_metadata):
            with mock.patch.object(adapter, "_bounded_run") as run:
                for tool_name in adapter.CHECKS:
                    with self.subTest(tool=tool_name):
                        response = adapter.run_check(self.root, tool_name)
                        self.assertEqual(response["state"], "incomplete")
                        self.assertEqual(response["exit_code"], 2)
                run.assert_not_called()

    @unittest.skipUnless(os.name == "nt", "native Windows junction requires Windows")
    def test_real_windows_internal_junction_fails_closed(self):
        with tempfile.TemporaryDirectory() as outside:
            destination = Path(outside).resolve() / "outside"
            destination.mkdir()
            document = destination / "README.md"
            document.write_text("# Outside synthetic fixture\n", encoding="utf-8")
            alias = self.root / "linked-docs"
            created = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(alias), str(destination)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, check=False,
            )
            if created.returncode != 0:
                self.skipTest("native Windows junction unavailable")
            try:
                self.assertEqual(
                    getattr(os.lstat(alias), "st_reparse_tag", None),
                    adapter.JUNCTION_TAG,
                )
                with mock.patch.object(adapter, "_bounded_run") as run:
                    for tool_name in adapter.CHECKS:
                        with self.subTest(tool=tool_name):
                            response = adapter.run_check(self.root, tool_name)
                            self.assertEqual(response["state"], "incomplete")
                            self.assertEqual(response["exit_code"], 2)
                    run.assert_not_called()
                self.assertEqual(
                    document.read_text(encoding="utf-8"),
                    "# Outside synthetic fixture\n",
                )
            finally:
                # Remove only the reparse entry, never its target.
                alias.rmdir()
            self.assertTrue(destination.is_dir())

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
