"""Offline metadata, failure-path and CLI regressions for HTML5 ZIP preflight."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/itch_html5_zip.py"
spec = importlib.util.spec_from_file_location("itch_html5_zip", SCRIPT)
checker = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(checker)


class ItchHTML5ZipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.archive = Path(self.tmp.name) / "build.zip"

    def build(self, files: list[tuple[str, str]]) -> None:
        with zipfile.ZipFile(self.archive, "w") as out:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                for name, contents in files:
                    out.writestr(name, contents)


    def patch_raw_member_name(self, old: bytes, new: bytes) -> None:
        """Rewrite both ZIP headers, bypassing Windows ZipInfo path normalization."""
        self.assertEqual(len(old), len(new))
        data = self.archive.read_bytes()
        self.assertEqual(data.count(old), 2, "member path must occur in local and central headers")
        self.archive.write_bytes(data.replace(old, new))

    def rules(self) -> set[str]:
        return {item["rule"] for item in checker.inspect(self.archive)["findings"]}

    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-I", str(SCRIPT), str(self.archive), *args],
                              text=True, encoding="utf-8", capture_output=True, timeout=10, env=env)

    def test_valid_small_html5_zip_and_json_contract(self):
        self.build([("index.html", '<script src="js/game.js"></script>'), ("js/game.js", "console.log(1)")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual("", run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["files"], 2)
        self.assertEqual(result["findings"], [])

    def test_zero_byte_root_index_is_a_finding_without_reading_assets(self):
        self.build([("index.html", ""), ("assets/game.js", "console.log(1)")])
        original = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], "findings")
        self.assertEqual(report["files"], 2)
        self.assertEqual(report["uncompressed_bytes"], len("console.log(1)"))
        self.assertEqual(report["findings"], [{
            "rule": "empty_entrypoint",
            "path": "index.html",
            "detail": "root index.html has zero bytes; it cannot serve as a game entry document",
        }])
        self.assertEqual(self.archive.read_bytes(), original)

    def test_nested_index_is_not_root_entry(self):
        self.build([("dist/index.html", "okay")])
        self.assertIn("missing_entrypoint", self.rules())
        self.assertEqual(self.run_cli().returncode, 1)

    def test_entrypoint_is_case_sensitive(self):
        self.build([("Index.html", "okay")])
        self.assertIn("missing_entrypoint", self.rules())

    def test_unix_directory_named_index_is_not_a_valid_entrypoint(self):
        # Python's ZipInfo.is_dir() checks only a trailing slash.
        index = zipfile.ZipInfo("index.html")
        index.create_system = 3
        index.external_attr = (stat.S_IFDIR | 0o755) << 16
        with zipfile.ZipFile(self.archive, "w") as out:
            out.writestr(index, b"")
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "findings")
        self.assertEqual(result["files"], 0)
        self.assertEqual({"entry_type_mismatch", "missing_entrypoint"},
                         {item["rule"] for item in result["findings"]})

    def test_unix_regular_file_named_as_directory_is_reported(self):
        directory_name = zipfile.ZipInfo("assets/")
        directory_name.create_system = 3
        directory_name.external_attr = (stat.S_IFREG | 0o644) << 16
        with zipfile.ZipFile(self.archive, "w") as out:
            out.writestr("index.html", "ok")
            out.writestr(directory_name, b"")
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["files"], 1)
        self.assertIn("entry_type_mismatch",
                      {item["rule"] for item in result["findings"]})

    def test_duplicates_are_not_mistaken_for_single_asset(self):
        self.build([("index.html", "a"), ("index.html", "b")])
        self.assertIn("duplicate_path", self.rules())

    def test_file_blocks_implicit_parent_directory(self):
        self.build([("index.html", "ok"), ("assets", "file"),
                    ("assets/game.js", "console.log(1)")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        findings = json.loads(run.stdout)["findings"]
        self.assertIn("assets/game.js",
                      {f["path"] for f in findings if f["rule"] == "path_type_conflict"})

    def test_explicit_directory_conflicts_with_file_at_same_path(self):
        self.build([("index.html", "ok"), ("assets/", ""), ("assets", "file")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn({"rule": "path_type_conflict", "path": "assets",
                       "detail": "ZIP contains both a file and a directory at this path"},
                      json.loads(run.stdout)["findings"])

    def test_valid_implicit_and_explicit_directory_paths(self):
        for explicit in (False, True):
            with self.subTest(explicit=explicit):
                files = [("index.html", "ok"), ("assets/game.js", "ok")]
                if explicit:
                    files.insert(1, ("assets/", ""))
                self.build(files)
                run = self.run_cli("--format", "json")
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertEqual(json.loads(run.stdout)["findings"], [])

    def test_unsafe_names_rejected_without_extracting(self):
        self.build([("index.html", "okay"), ("../secret", "a"),
                    ("/absolute/file", "x"), ("js/backslash.js", "x"),
                    ("./dot.txt", "x"), ("C:/drive.txt", "x")])
        self.patch_raw_member_name(b"js/backslash.js", b"js\\backslash.js")
        self.assertEqual(len([x for x in checker.inspect(self.archive)["findings"]
                              if x["rule"] == "unsafe_path"]), 5)


    def test_repeated_directory_terminators_are_unsafe_not_silently_normalized(self):
        # ZipInfo.is_dir accepts any trailing slash, including repeated ones.
        # A single final slash is a valid directory marker; a second is empty.
        self.build([("index.html", "ok"), ("assets/", ""),
                    ("scripts//", ""), ("images///", ""),
                    ("assets/game.js", "ok")])
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], "findings")
        self.assertEqual({f["path"] for f in report["findings"]
                          if f["rule"] == "unsafe_path"},
                         {"scripts//", "images///"})
        self.assertEqual(before, self.archive.read_bytes())

    def test_control_character_members_are_rejected_without_extraction(self):
        names = ("assets/line\nfeed.js", "assets/tab\tname.png",
                 "assets/del\x7f.css", "assets/c1\x85.dat")
        # These ZIP member names are legal to encode but unsafe to use as
        # portable asset paths or as unescaped terminal diagnostics.
        self.build([("index.html", "ok")] + [(name, "asset") for name in names])
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "findings")
        self.assertEqual(result["files"], len(names) + 1)
        unsafe = [item for item in result["findings"] if item["rule"] == "unsafe_path"]
        self.assertEqual({item["path"] for item in unsafe}, set(names))
        self.assertEqual(len(unsafe), len(names))
        self.assertEqual(before, self.archive.read_bytes())

    def test_bidi_format_controls_are_reported_without_extraction(self):
        # Unicode bidi formatting may visually reorder the archive member name.
        # They are not C0/C1 controls and were previously accepted as safe.
        bad = ("assets/icon\u202e.gnp", "assets/\u2066game.js\u2069",
               "assets/\u200elogo.png", "assets/\u061cnotice.txt")
        self.build([("index.html", "ok")] + [(name, "asset") for name in bad])
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], "findings")
        self.assertEqual({f["path"] for f in report["findings"]
                          if f["rule"] == "unsafe_path"}, set(bad))
        self.assertIn("\\u202e", run.stdout)
        self.assertEqual(before, self.archive.read_bytes())

    def test_ordinary_rtl_filenames_remain_valid(self):
        # Arabic and Hebrew letters are not Unicode Bidi_Control formatting.
        self.build([("index.html", "ok"), ("assets/\u0645\u0631\u062d\u0628\u0627.png", "asset"),
                    ("assets/\u05e9\u05dc\u05d5\u05dd.txt", "asset")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout)["findings"], [])

    def test_canonically_equivalent_unicode_members_collide(self):
        # Distinct NFC/NFD ZIP paths may alias when extracted on macOS.
        composed = "assets/caf\\u00e9.png"
        decomposed = "assets/cafe\\u0301.png"
        self.build([("index.html", "ok"), (composed, "one"), (decomposed, "two")])
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        findings = json.loads(run.stdout)["findings"]
        self.assertEqual(
            {f["path"] for f in findings if f["rule"] == "unicode_normalization_collision"},
            {decomposed})
        self.assertNotIn("duplicate_path", {f["rule"] for f in findings})
        self.assertEqual(before, self.archive.read_bytes())

    def test_canonically_equivalent_file_blocks_nested_directory(self):
        composed = "assets/caf\\u00e9"
        child = "assets/cafe\\u0301/game.js"
        self.build([("index.html", "ok"), (composed, "file"), (child, "asset")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        collisions = [f for f in json.loads(run.stdout)["findings"]
                      if f["rule"] == "unicode_normalization_collision"]
        self.assertEqual([f["path"] for f in collisions], [child])
        self.assertIn(composed, collisions[0]["detail"])

    def test_decomposed_unicode_name_without_alias_remains_valid(self):
        self.build([("index.html", "ok"), ("assets/cafe\\u0301.png", "asset"),
                    ("assets/caf\\u00e9.txt", "asset")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout)["findings"], [])

    def test_windows_reserved_names_and_trailing_components_are_reported(self):
        bad = ("NUL.txt", "assets/con.JSON", "audio/Lpt1.wav",
               "data/COM¹.json", "icons/end.", "assets/trail /view.png")
        self.build([("index.html", "ok")] + [(name, "asset") for name in bad])
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        report = json.loads(run.stdout)
        self.assertEqual({f["path"] for f in report["findings"]
                          if f["rule"] == "windows_path"}, set(bad))
        self.assertEqual(before, self.archive.read_bytes())

    def test_windows_punctuation_inside_nested_components_is_reported(self):
        bad = ("assets/question?.png", "images/<splash>/a.png",
               "assets/foo:bar.txt", "assets/tag*star.png")
        self.build([("index.html", "ok")] + [(name, "asset") for name in bad])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual({f["path"] for f in json.loads(run.stdout)["findings"]
                          if f["rule"] == "windows_path"}, set(bad))

    def test_case_distinct_members_are_reported_without_double_counting_duplicates(self):
        self.build([("index.html", "ok"), ("assets/logo.png", "x"),
                    ("Assets/LOGO.PNG", "y"), ("Assets/LOGO.PNG", "z"),
                    ("repeat.txt", "x"), ("repeat.txt", "y")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        findings = json.loads(run.stdout)["findings"]
        self.assertEqual([f["path"] for f in findings
                          if f["rule"] == "windows_case_collision"], ["Assets/LOGO.PNG"])
        self.assertIn("duplicate_path", {f["rule"] for f in findings})

    def test_directory_marker_and_case_distinct_file_collide_on_windows(self):
        self.build([("index.html", "ok"), ("assets/", ""), ("ASSETS", "file")])
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        findings = json.loads(run.stdout)["findings"]
        self.assertIn("ASSETS", {f["path"] for f in findings
                                 if f["rule"] == "windows_case_collision"})
        self.assertEqual(before, self.archive.read_bytes())

    def test_case_distinct_file_blocks_implicit_nested_directory(self):
        self.build([("index.html", "ok"), ("assets", "file"),
                    ("ASSETS/logo.png", "asset")])
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        findings = json.loads(run.stdout)["findings"]
        self.assertIn("ASSETS/logo.png", {f["path"] for f in findings
                                          if f["rule"] == "windows_case_collision"})
        self.assertEqual(before, self.archive.read_bytes())

    def test_windows_portable_names_are_not_flagged(self):
        self.build([("index.html", "ok"), ("assets/compass.png", "x"),
                    ("assets/com10.txt", "x"), ("assets/lpt0.txt", "x"),
                    ("assets/.hidden", "x"), ("assets/nulled.txt", "x")])
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout)["findings"], [])

    def test_utf8_member_name_is_accepted_when_flagged(self):
        self.build([("index.html", "ok"), ("café.png", "asset")])
        self.assertNotIn("legacy_name_encoding", self.rules())
        self.assertEqual(self.run_cli().returncode, 0)

    def test_cp437_non_ascii_member_name_is_reported(self):
        self.build([("index.html", "ok"), ("cafe.png", "asset")])
        self.patch_raw_member_name(b"cafe.png", b"caf\x82.png")
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIsNotNone(run.stdout, f"missing captured JSON output: {run.stderr!r}")
        report = json.loads(run.stdout)
        self.assertIn({"rule": "legacy_name_encoding", "path": "café.png",
                       "detail": "non-ASCII ZIP member name lacks the UTF-8 flag; re-export with UTF-8 names"},
                      report["findings"])

    def test_legacy_member_json_survives_ascii_only_console(self):
        self.build([("index.html", "ok"), ("cafe.png", "asset")])
        self.patch_raw_member_name(b"cafe.png", b"caf\x82.png")
        # A Windows terminal or redirected stream may not support Unicode.
        run = self.run_cli("--format", "json",
                           env={**os.environ, "PYTHONIOENCODING": "ascii"})
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIsNotNone(run.stdout, f"missing captured JSON output: {run.stderr!r}")
        self.assertEqual(run.stderr, "")
        self.assertTrue(run.stdout.isascii(), run.stdout)
        self.assertIn("legacy_name_encoding", {x["rule"] for x in json.loads(run.stdout)["findings"]})
        self.assertIn("caf\\u00e9.png", run.stdout)

    def test_invalid_utf8_member_is_incomplete_not_traceback(self):
        self.build([("index.html", "ok"), ("cafe.png", "asset")])
        self.patch_raw_member_name(b"cafe.png", b"caf\x82.png")
        data = bytearray(self.archive.read_bytes())
        # The last member is the one with the corrupted name. Flag both headers.
        for signature, flag_offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            pos = data.rfind(signature)
            self.assertGreaterEqual(pos, 0)
            flags = int.from_bytes(data[pos + flag_offset:pos + flag_offset + 2], "little")
            data[pos + flag_offset:pos + flag_offset + 2] = (flags | 0x800).to_bytes(2, "little")
        self.archive.write_bytes(data)
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertEqual(run.stderr, "")
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("UnicodeDecodeError", result["error"])

    def test_raw_backslash_member_is_reported_by_cli_on_all_platforms(self):
        self.build([("index.html", "ok"), ("js/game.js", "ok")])
        self.patch_raw_member_name(b"js/game.js", b"js\\game.js")
        with zipfile.ZipFile(self.archive) as archive:
            self.assertEqual(archive.infolist()[1].orig_filename, "js\\game.js")
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        findings = json.loads(run.stdout)["findings"]
        self.assertIn("unsafe_path", {item["rule"] for item in findings})

    def test_raw_backslash_alias_collides_with_forward_slash_path(self):
        self.build([("index.html", "ok"), ("js/game.js", "a"), ("js/gane.js", "b")])
        self.patch_raw_member_name(b"js/gane.js", b"js\\game.js")
        self.assertIn("duplicate_path", self.rules())
        self.assertEqual(self.run_cli().returncode, 1)

    def test_long_member_path(self):
        self.build([("index.html", "okay"), ("folder/" + "a" * 235, "x")])
        self.assertIn("path_length", self.rules())

    def test_more_than_1000_files(self):
        self.build([("index.html", "okay")] + [(f"assets/{i}.txt", "") for i in range(1000)])
        self.assertIn("file_count", self.rules())

    def test_sizes_are_checked_from_central_directory_without_extract(self):
        index = zipfile.ZipInfo("index.html")
        big = zipfile.ZipInfo("big.dat")
        big.file_size = checker.MAX_FILE_BYTES + 1
        _, _, findings = checker.check_entries([index, big])
        self.assertIn("file_size", {item["rule"] for item in findings})
        big.file_size = checker.MAX_TOTAL_BYTES + 1
        _, _, findings = checker.check_entries([index, big])
        self.assertIn("total_size", {item["rule"] for item in findings})

    def test_posix_symlink_member_is_not_followed(self):
        index = zipfile.ZipInfo("index.html")
        link = zipfile.ZipInfo("assets/latest.png")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        _, _, findings = checker.check_entries([index, link])
        self.assertIn("special_entry", {item["rule"] for item in findings})

    def test_store_and_deflate_members_are_accepted(self):
        with zipfile.ZipFile(self.archive, "w") as out:
            out.writestr("index.html", "ok", compress_type=zipfile.ZIP_STORED)
            out.writestr("assets/game.js", "ok", compress_type=zipfile.ZIP_DEFLATED)
        self.assertEqual(self.run_cli("--format", "json").returncode, 0)
        self.assertNotIn("compression_method", self.rules())

    def test_bzip2_and_lzma_members_are_nonportable_metadata_findings(self):
        with zipfile.ZipFile(self.archive, "w") as out:
            out.writestr("index.html", "ok")
            out.writestr("assets/bzip2.dat", "asset", compress_type=zipfile.ZIP_BZIP2)
            out.writestr("assets/lzma.dat", "asset", compress_type=zipfile.ZIP_LZMA)
        before = self.archive.read_bytes()
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        findings = json.loads(run.stdout)["findings"]
        self.assertEqual({f["path"] for f in findings if f["rule"] == "compression_method"},
                         {"assets/bzip2.dat", "assets/lzma.dat"})
        self.assertEqual(self.archive.read_bytes(), before)

    def test_unknown_compression_method_is_not_a_false_ok(self):
        self.build([("index.html", "ok"), ("assets/game.js", "asset")])
        # ZIP compression method: local header +8, central header +10.
        # Patch the last entry's two headers; do not unpack any asset.
        data = bytearray(self.archive.read_bytes())
        for signature, method_offset in ((b"PK\x03\x04", 8),
                                         (b"PK\x01\x02", 10)):
            positions = []
            start = 0
            while True:
                pos = data.find(signature, start)
                if pos < 0:
                    break
                positions.append(pos)
                start = pos + 4
            self.assertEqual(len(positions), 2)
            pos = positions[-1]
            data[pos + method_offset:pos + method_offset + 2] = (99).to_bytes(2, "little")
        self.archive.write_bytes(data)
        before = self.archive.read_bytes()
        with zipfile.ZipFile(self.archive) as source:
            self.assertEqual(source.infolist()[-1].compress_type, 99)
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertEqual(run.stderr, "")
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], "findings")
        self.assertEqual({f["path"] for f in report["findings"]
                          if f["rule"] == "compression_method"}, {"assets/game.js"})
        self.assertEqual(self.archive.read_bytes(), before)

    def test_encrypted_flag_reported(self):
        index = zipfile.ZipInfo("index.html")
        index.flag_bits = 1
        _, _, findings = checker.check_entries([index])
        self.assertIn("encrypted_entry", {item["rule"] for item in findings})

    def test_missing_and_invalid_zip_are_incomplete_not_pass(self):
        run = self.run_cli("--format", "json")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["status"], "incomplete")
        self.archive.write_text("not a zip", encoding="utf-8")
        self.assertEqual(self.run_cli().returncode, 2)

    def test_symlink_archive_refused(self):
        target = Path(self.tmp.name) / "source.zip"
        with zipfile.ZipFile(target, "w") as out:
            out.writestr("index.html", "ok")
        try:
            self.archive.symlink_to(target)
        except (NotImplementedError, OSError):
            self.skipTest("symlink creation unavailable")
        self.assertEqual(self.run_cli().returncode, 2)

    def test_read_only_preflight_does_not_mutate_archive(self):
        self.build([("index.html", "ok")])
        before = self.archive.read_bytes()
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.archive.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
