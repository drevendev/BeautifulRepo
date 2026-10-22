"""Input-boundary regressions for the small curated-collection CLI."""
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'examples' / 'curated-starter' / 'curate.py'
SPEC = importlib.util.spec_from_file_location('curated_input_example', SCRIPT)
assert SPEC and SPEC.loader
curate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(curate)


class CuratedInputTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(SCRIPT.with_name('items.json').read_text(encoding='utf-8'))

    def cli_source(self, source, *args):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            path.write_bytes(source if isinstance(source, bytes) else source.encode('utf-8'))
            return subprocess.run(
                [sys.executable, str(SCRIPT), '--data', str(path), '--as-of', '2026-10-17', *args],
                capture_output=True, text=True, encoding='utf-8', check=False, timeout=10,
            )

    def assert_invalid(self, source):
        result = self.cli_source(source)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr, 'Invalid collection input or unavailable file\n')

    def test_unpaired_surrogates_in_url_have_controlled_error(self):
        self.raw['entries'][0]['url'] = 'https://example.com/\ud800'
        self.assert_invalid(json.dumps(self.raw))

    def test_malformed_hostnames_and_percent_escapes_are_rejected(self):
        for url in ('https://bad..example.com/', 'https://-bad.example.com/',
                    'https://example.com/%GG', 'https://example.com/%',
                    'https://example.com/\x7fhidden', 'https://example.com:/'):
            with self.subTest(url=url):
                self.raw['entries'][0]['url'] = url
                self.assert_invalid(json.dumps(self.raw))

    def test_unicode_paths_and_encoded_characters_are_supported(self):
        for url in ('https://example.com/日本語', 'https://example.com/a%20b?x=1&y=2'):
            with self.subTest(url=url):
                self.raw['entries'][0]['url'] = url
                result = self.cli_source(json.dumps(self.raw), '--format', 'json')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(url, [x['url'] for x in json.loads(result.stdout)['entries']])

    def test_large_json_is_rejected_before_parsing(self):
        self.assert_invalid(' ' * (1024 * 1024) + json.dumps(self.raw))

    def test_deep_json_has_generic_error(self):
        self.assert_invalid('[' * 2000 + '0' + ']' * 2000)

    def test_invalid_utf8_has_generic_error(self):
        self.assert_invalid(b'\xff')

    def test_review_age_boundary_is_strictly_older(self):
        start = date(2026, 10, 17)
        self.assertEqual(curate.report(self.raw, start + timedelta(days=180), 180)['review_due'], 0)
        self.assertEqual(curate.report(self.raw, start + timedelta(days=181), 180)['review_due'], 3)

    def test_query_strings_remain_distinct(self):
        entry = self.raw['entries'][0].copy()
        entry.update(id='query-variant', url=entry['url'] + '?edition=2')
        self.raw['entries'].append(entry)
        self.assertEqual(len(curate.validate(self.raw, date(2026, 10, 17))), 4)

    def test_escaped_duplicate_key_spelling_is_rejected(self):
        source = json.dumps(self.raw).replace('"title":', '"title": "discarded", "t\\u0069tle":', 1)
        self.assert_invalid(source)


if __name__ == '__main__':
    unittest.main()
