"""Black-box and targeted tests for HTML5 static index-page asset checking."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/itch_html5_assets.py'
spec = importlib.util.spec_from_file_location('itch_html5_assets', SCRIPT)
checker = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(checker)


class ItchHTML5AssetsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'game.zip'

    def make(self, html, assets=('js/game.js', 'img/icon.png')):
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('index.html', html)
            for asset in assets:
                archive.writestr(asset, 'demo')

    def run_cli(self):
        return subprocess.run([sys.executable, '-I', str(SCRIPT), str(self.path), '--format', 'json'],
                              text=True, capture_output=True, encoding='utf-8', timeout=8)

    def test_valid_refs_and_unchanged_archive(self):
        self.make('<script src="js/game.js?v=1"></script><img src="img/icon.png#hero">')
        before = self.path.read_bytes()
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(proc.stderr, '')
        self.assertEqual(json.loads(proc.stdout)['checked'], 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_and_case_mismatch(self):
        self.make('<script src="js/GAME.js"></script><img src="bad.png">')
        p = self.run_cli()
        self.assertEqual(p.returncode, 1)
        self.assertEqual({x['rule'] for x in json.loads(p.stdout)['findings']},
                         {'case_mismatch', 'missing_asset'})

    def test_root_relative_and_parent_escape(self):
        self.make('<img src="/img/icon.png"><script src="../js/game.js"></script>')
        self.assertEqual({x['rule'] for x in checker.inspect(self.path)['findings']},
                         {'root_absolute', 'outside_game'})

    def test_percent_encoded_path_and_html_entities(self):
        self.make('<link rel="stylesheet" href="css/My%20Style.css?x=1&amp;y=2">',
                  assets=('css/My Style.css',))
        self.assertEqual(self.run_cli().returncode, 0)

    def test_http_warns_https_and_data_are_unverified(self):
        self.make('<img src="http://example.invalid/x.png"><img src="https://example.invalid/a.png">'
                  '<img src="data:image/png;base64,AAAA">')
        self.assertEqual({x['rule'] for x in checker.inspect(self.path)['findings']},
                         {'insecure_external'})

    def test_base_tag_is_incomplete_not_false_report(self):
        self.make('<base href="assets/"><img src="logo.png">')
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)['status'], 'incomplete')

    def test_large_index_is_incomplete(self):
        self.make('x' * (checker.MAX_INDEX_BYTES + 1), assets=())
        self.assertEqual(self.run_cli().returncode, 2)

    def test_invalid_utf8_is_incomplete(self):
        with zipfile.ZipFile(self.path, 'w') as archive:
            archive.writestr('index.html', b'\xff')
        self.assertEqual(self.run_cli().returncode, 2)

    def test_nonexistent_and_bad_zip_are_incomplete(self):
        self.assertEqual(self.run_cli().returncode, 2)
        self.path.write_bytes(b'not zip')
        self.assertEqual(self.run_cli().returncode, 2)

    def test_srcset_and_dynamic_imports_are_outside_scope(self):
        self.make('<img srcset="missing.webp 1x"><script>import("missing.js")</script>')
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(checker.inspect(self.path)['checked'], 0)

    def test_disallows_duplicate_member_names(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            self.make('<img src="x.png">', assets=('x.png', 'x.png'))
        self.assertEqual(self.run_cli().returncode, 2)

    def test_no_target_file_read_or_extraction(self):
        self.make('<script src="js/game.js"></script>', assets=('js/game.js',))
        with zipfile.ZipFile(self.path, 'r') as archive:
            old = archive.read('js/game.js')
        self.assertEqual(self.run_cli().returncode, 0)
        with zipfile.ZipFile(self.path, 'r') as archive:
            self.assertEqual(archive.read('js/game.js'), old)


if __name__ == '__main__':
    unittest.main()
