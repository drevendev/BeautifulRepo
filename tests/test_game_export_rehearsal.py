"""Exercise the documented subdirectory hazard with synthetic HTTP fixtures."""
from functools import partial
from http.client import HTTPConnection
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class GameExportRehearsalTests(unittest.TestCase):
    def test_documented_asset_references_at_root_and_under_subdirectory(self):
        guide = (ROOT / "guides/game-repositories.md").read_text(encoding="utf-8")
        heading = "## Rehearse a browser build under a subdirectory\n"
        self.assertEqual(guide.count(heading), 1)
        section = guide.split(heading, 1)[1].split("\n## ", 1)[0]
        blocks = re.findall(r"(?ms)^```html\n(.*?)^``` *$", section)
        self.assertEqual(len(blocks), 1)
        references = re.findall(r'<script src="([^"]+)"></script>', blocks[0])
        # Documentation is data: never request an arbitrary extracted URL.
        self.assertEqual(references, ["/assets/game.js", "./assets/game.js"])
        absolute, relative = references
        asset = b"// synthetic asset, never executed\n"
        with TemporaryDirectory() as tmp:
            staging = Path(tmp)
            build = staging / "build"
            (build / "assets").mkdir(parents=True)
            (build / "index.html").write_text(blocks[0], encoding="utf-8")
            (build / "assets/game.js").write_bytes(asset)
            for directory, page, expected in (
                (build, "/index.html", (200, 200)),
                (staging, "/build/index.html", (404, 200)),
            ):
                with self.subTest(page=page), HTTPServer(
                    ("127.0.0.1", 0), partial(QuietHandler, directory=str(directory))
                ) as server:
                    thread = Thread(target=server.serve_forever, daemon=True)
                    thread.start()
                    try:
                        host, port = server.server_address
                        page_url = f"http://{host}:{port}{page}"
                        for ref, status in zip((absolute, relative), expected, strict=True):
                            path = urljoin(page, ref)
                            # All paths are fixed local paths, not external URLs.
                            conn = HTTPConnection(host, port, timeout=5)
                            try:
                                conn.request("GET", path)
                                response = conn.getresponse()
                                content = response.read()
                                self.assertEqual(response.status, status, (page_url, ref))
                                if status == 200:
                                    self.assertEqual(content, asset)
                            finally:
                                conn.close()
                    finally:
                        server.shutdown()
                        thread.join(timeout=5)
                        self.assertFalse(thread.is_alive())


if __name__ == "__main__":
    unittest.main()
