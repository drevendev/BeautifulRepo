"""The link checkers never touch a path outside the repository, even on Windows.

A destination or a link target that names another drive, a UNC network share or a
device is reported from its text alone, never opened.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docs_links  # noqa: E402
import html_navigation  # noqa: E402

UNREACHABLE_HOST = "192.0.2.1"  # TEST-NET-1: never routed


def guarded(real):
    """Wrap an os function so that touching the unreachable host fails the test."""
    def call(path, *args, **kwargs):
        text = os.fspath(path) if isinstance(path, (str, bytes, os.PathLike)) else ""
        if isinstance(text, bytes):
            text = text.decode(errors="replace")
        if UNREACHABLE_HOST in text:
            raise AssertionError(f"filesystem call on {path!r}")
        return real(path, *args, **kwargs)
    return call


class DestinationTextTests(unittest.TestCase):
    NON_PORTABLE = (
        r"\\192.0.2.1\share\x.md",
        "%5C%5C192.0.2.1%5Cshare%5Cx.md",
        "/%5C%5C192.0.2.1%5Cshare%5Cx.md",
        r"\\?\UNC\192.0.2.1\share\x.md",
        r"\\.\pipe\beautifulrepo",
        "%5CWindows%5Cwin.ini",
        "%43:/Windows/win.ini",
        "/C:/Windows/win.ini",
        "docs/c:x.md",
    )

    def test_backslash_and_drive_destinations_are_rejected_before_any_filesystem_call(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            with mock.patch.object(docs_links.os, "lstat", side_effect=AssertionError), \
                    mock.patch.object(docs_links.os, "readlink", side_effect=AssertionError):
                for destination in self.NON_PORTABLE:
                    with self.subTest(destination=destination):
                        resolved, error = docs_links.resolve_local_destination(
                            root, root / "README.md", destination)
                        self.assertIsNone(resolved)
                        self.assertIn("non-portable destination", error)

    def test_drive_and_scheme_relative_urls_stay_out_of_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            with mock.patch.object(docs_links.os, "lstat", side_effect=AssertionError):
                for destination in ("C:/Windows/win.ini", "//192.0.2.1/share/x.md"):
                    with self.subTest(destination=destination):
                        self.assertEqual((None, None), docs_links.resolve_local_destination(
                            root, root / "README.md", destination))

    def test_html_unc_source_attribute_is_reported_without_network_access(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "README.md").write_text(
                f'# T\n\n<img src="\\\\{UNREACHABLE_HOST}\\share\\x.png" alt="x">\n',
                encoding="utf-8")
            with mock.patch("os.lstat", guarded(os.lstat)), \
                    mock.patch("os.stat", guarded(os.stat)):
                errors, _, _ = html_navigation.check_repo(root)
        self.assertEqual(1, len(errors))
        self.assertIn("non-portable destination", errors[0])


class LinkTargetTextTests(unittest.TestCase):
    def test_windows_targets(self):
        root = r"C:\repo"
        cases = {
            r"\\192.0.2.1\share\x.md": None,
            r"\\?\UNC\192.0.2.1\share\x.md": None,
            r"\\.\pipe\beautifulrepo": None,
            r"D:\other\x.md": None,
            "C:x.md": None,
            r"\Windows\win.ini": None,
            r"C:\repository\x.md": None,
            r"C:\repo\docs\x.md": (True, ["docs", "x.md"]),
            r"\\?\c:\REPO\docs": (True, ["docs"]),
            r"C:\repo\..\outside": (True, ["..", "outside"]),
            r"..\docs/x.md": (False, ["..", "docs", "x.md"]),
        }
        for target, expected in cases.items():
            with self.subTest(target=target):
                self.assertEqual(expected, docs_links.link_target_parts(root, target, windows=True))

    def test_posix_targets(self):
        root = "/srv/repo"
        cases = {
            "/etc/passwd": None,
            "/srv/repository/x.md": None,
            "/srv/repo/docs/x.md": (True, ["docs", "x.md"]),
            "../x.md": (False, ["..", "x.md"]),
            r"\\192.0.2.1\share\x.md": (False, [r"\\192.0.2.1\share\x.md"]),
        }
        for target, expected in cases.items():
            with self.subTest(target=target):
                self.assertEqual(expected, docs_links.link_target_parts(root, target, windows=False))

    def test_absolute_target_that_climbs_out_is_still_an_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            # Only the walk runs under the patch: Path.resolve also calls os.lstat on POSIX.
            # No directory listing either, so the walk relies on the mocked lstat alone.
            with mock.patch.object(docs_links, "_entry_names", return_value=None), \
                    mock.patch.object(docs_links.os, "lstat",
                                   return_value=os.stat_result((0o120777,) + (0,) * 9)), \
                    mock.patch.object(docs_links.os, "readlink",
                                      return_value=str(root / ".." / "outside")):
                result = docs_links._follow_within_root(root, ["link", "x.md"])
            self.assertEqual((None, docs_links.ESCAPES_ROOT), result)


class SymlinkCycleTests(unittest.TestCase):
    def test_symlink_cycle_is_a_diagnostic_not_a_hang(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            try:
                (root / "a").symlink_to("a")
            except OSError as error:
                self.skipTest(f"cannot create symlinks here: {error}")
            (root / "README.md").write_text("[A](a)\n", encoding="utf-8")
            errors, _, _ = docs_links.check_repo(root)
        self.assertEqual(["README.md:1: too many levels of symbolic links: 'a'"], errors)


@unittest.skipUnless(os.name == "nt", "junctions and UNC symlink targets are Windows-only")
class WindowsRedirectTests(unittest.TestCase):
    def junction(self, link: Path, target: Path):
        import _winapi
        _winapi.CreateJunction(str(target), str(link))

    def run_tool(self, script: str, root: Path):
        return subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" / script), "--root", str(root)],
            text=True, capture_output=True, check=False, timeout=60,
        )

    def test_junction_loop_does_not_hang_the_walk(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / "docs").mkdir()
            (root / "README.md").write_text("[Docs](docs/guide.md)\n", encoding="utf-8")
            (root / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
            self.junction(root / "docs/loop", root)
            for script in ("docs_links.py", "html_navigation.py"):
                with self.subTest(script=script):
                    result = self.run_tool(script, root)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("across 2 Markdown file", result.stdout)

    def test_junction_inside_the_repository_is_followed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / "docs").mkdir()
            (root / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
            self.junction(root / "alias", root / "docs")
            (root / "README.md").write_text("[Guide](alias/guide.md)\n", encoding="utf-8")
            errors, checked, _ = docs_links.check_repo(root)
            self.assertEqual([], errors)
            self.assertEqual(1, checked)

    def test_junction_out_of_the_repository_is_reported_not_read(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder).resolve()
            root = parent / "repo"
            outside = parent / "outside"
            root.mkdir()
            outside.mkdir()
            (outside / "secret.md").write_text("[Leak](do-not-leak-this-name.md)\n",
                                               encoding="utf-8")
            self.junction(root / "docs", outside)
            (root / "README.md").write_text("[Secret](docs/secret.md)\n", encoding="utf-8")
            result = self.run_tool("docs_links.py", root)
            self.assertEqual(1, result.returncode)
            self.assertIn("escapes repository root: 'docs/secret.md'", result.stderr)
            self.assertNotIn("do-not-leak-this-name.md", result.stderr)

    def test_symlink_to_a_unc_share_is_reported_without_network_access(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            try:
                # target_is_directory=True: otherwise CPython itself probes the share
                # to pick the link type, and the test would wait for a network timeout.
                (root / "shared.md").symlink_to(f"\\\\{UNREACHABLE_HOST}\\share\\x.md",
                                                target_is_directory=True)
            except OSError as error:
                self.skipTest(f"cannot create symlinks here: {error}")
            (root / "README.md").write_text("[Shared](shared.md)\n", encoding="utf-8")
            with mock.patch("os.lstat", guarded(os.lstat)), \
                    mock.patch("os.stat", guarded(os.stat)):
                errors, _, _ = docs_links.check_repo(root)
        self.assertIn("shared.md: Markdown source escapes repository root", errors)
        self.assertIn("README.md:1: escapes repository root: 'shared.md'", errors)


if __name__ == "__main__":
    unittest.main()
