"""Offline WSGI-contract checks for the fictional application starter."""
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import threading
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import build_opener, ProxyHandler
from wsgiref.simple_server import make_server, WSGIRequestHandler
from wsgiref.util import setup_testing_defaults

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "application-starter"
SCRIPT = EXAMPLE / "app.py"
SPEC = importlib.util.spec_from_file_location("pocket_board_example", SCRIPT)
assert SPEC and SPEC.loader
board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(board)


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.label_ids = set()
        self.select_ids = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        props = dict(attrs)
        if tag == "label" and props.get("for"):
            self.label_ids.add(props["for"])
        if tag == "select" and props.get("id"):
            self.select_ids.add(props["id"])


def invoke(*, path="/", query="", method="GET"):
    environ = {}
    setup_testing_defaults(environ)
    environ.update({"PATH_INFO": path, "QUERY_STRING": query, "REQUEST_METHOD": method})
    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(board.application(environ, start_response))
    return captured["status"], captured["headers"], body.decode("utf-8")


class ApplicationStarterTests(unittest.TestCase):
    def test_first_run(self):
        status, headers, body = invoke()
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("Showing <strong>5</strong> tasks · <strong>15</strong> effort points", body)
        self.assertIn("read-only", body)
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(int(headers["Content-Length"]), len(body.encode()))

    def test_filters(self):
        for query, n, effort in (("status=open", 3, 12), ("status=done", 2, 3),
                                 ("status=all", 5, 15)):
            with self.subTest(query=query):
                status, _, body = invoke(query=query)
                self.assertEqual(status, "200 OK")
                self.assertIn(f"<strong>{n}</strong> tasks · <strong>{effort}</strong>", body)

    def test_bad_queries_do_not_reflect_input(self):
        for query in ("status=archive", "foo=bar", "status=", "status=open&status=done",
                      "status=open&x=1", "status=%3Cscript%3E", "status"):
            with self.subTest(query=query):
                status, _, body = invoke(query=query)
                self.assertEqual(status, "400 Bad Request")
                self.assertEqual(body, "Invalid filter\n")
                self.assertNotIn(query, body)

    def test_methods_and_routes_are_bounded(self):
        self.assertEqual(invoke(method="POST")[0], "405 Method Not Allowed")
        self.assertEqual(invoke(method="POST")[1]["Allow"], "GET")
        self.assertEqual(invoke(path="/data/tasks.json")[0], "404 Not Found")
        self.assertEqual(invoke(path="/../app.py")[0], "404 Not Found")
        self.assertEqual(invoke(path="/health")[2], "ok\n")
        status, headers, css = invoke(path="/style.css")
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/css; charset=utf-8")
        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-color-scheme:dark", css)

    def test_missing_stylesheet_has_generic_error_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "no-style.css"
            with patch.object(board, "STYLE", missing):
                status, headers, body = invoke(path="/style.css")
        self.assertEqual(status, "500 Internal Server Error")
        self.assertEqual(headers["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(body, "Sample unavailable\n")
        self.assertEqual(int(headers["Content-Length"]), len(body.encode()))
        self.assertNotIn(str(missing), body)
        self.assertIn("nosniff", headers["X-Content-Type-Options"])

    def test_health_is_readiness_not_a_false_success(self):
        # The previous implementation returned 200 even when the actual page
        # could no longer read its data or stylesheet.
        self.assertEqual(invoke(path="/health")[0], "200 OK")
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "absent.json"
            with patch.object(board, "FIXTURE", missing):
                status, headers, body = invoke(path="/health")
                self.assertEqual(status, "503 Service Unavailable")
                self.assertEqual(body, "Sample unavailable\n")
                self.assertEqual(int(headers["Content-Length"]), len(body.encode()))
                self.assertNotIn(str(missing), body)
            broken = Path(directory) / "tasks.json"
            broken.write_text("not-json", encoding="utf-8")
            with patch.object(board, "FIXTURE", broken):
                self.assertEqual(invoke(path="/health")[0], "503 Service Unavailable")
            with patch.object(board, "STYLE", missing):
                self.assertEqual(invoke(path="/health")[0], "503 Service Unavailable")

    def test_readiness_rejects_unicode_surrogate_fixture(self):
        # JSON can contain escaped lone surrogates even though UTF-8 HTML cannot.
        # A 200 readiness response when the main page returns 500 is misleading.
        with tempfile.TemporaryDirectory() as directory:
            sample = Path(directory) / "invalid-tasks.json"
            sample.write_text(
                '[{"id":"bad","title":"\\ud800","status":"open","effort":1}]',
                encoding="utf-8",
            )
            with patch.object(board, "FIXTURE", sample):
                home_status, _, home_body = invoke()
                health_status, _, health_body = invoke(path="/health")
        self.assertEqual(home_status, "500 Internal Server Error")
        self.assertEqual(home_body, "Sample unavailable\n")
        self.assertEqual(health_status, "503 Service Unavailable")
        self.assertEqual(health_body, "Sample unavailable\n")

    def test_labels_semantics_and_no_script(self):
        html = invoke()[2]
        parser = DocumentParser()
        parser.feed(html)
        self.assertIn("main", parser.tags)
        self.assertIn("h1", parser.tags)
        self.assertIn("form", parser.tags)
        self.assertIn("button", parser.tags)
        self.assertNotIn("script", parser.tags)
        self.assertEqual(parser.label_ids, {"status"})
        self.assertEqual(parser.select_ids, {"status"})

    def test_safe_escaping_of_source_title(self):
        sample = board.read_sample()
        sample[0] = dict(sample[0], title="<script>alert('x')</script>")
        html = board.render_page(board.validate_tasks(sample)).decode("utf-8")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_invalid_fixture_rejected(self):
        original = board.read_sample()
        samples = []
        samples.append([])
        samples.append(original + [original[0]])
        samples.append([dict(original[0], effort=True)])
        samples.append([dict(original[0], effort=0)])
        samples.append([dict(original[0], status=[])])
        samples.append([dict(original[0], title=" padded ")])
        samples.append([dict(original[0], title="with\\tcontrol\t")])
        samples.append([dict(original[0], id="BAD-ID")])
        samples.append([dict(original[0], private="unexpected")])
        for sample in samples:
            with self.subTest(sample=repr(sample)[:100]), self.assertRaises(ValueError):
                board.validate_tasks(sample)

    def test_results_deterministic_and_fixture_read_only(self):
        before = board.FIXTURE.read_bytes()
        self.assertEqual(board.render_page(board.read_sample()), board.render_page(board.read_sample()))
        for query in ("status=done", "status=open", "status=all"):
            self.assertEqual(invoke(query=query)[0], "200 OK")
        self.assertEqual(board.FIXTURE.read_bytes(), before)
        self.assertEqual(len(board.read_sample()), 5)

    def test_real_loopback_http_and_stylesheet(self):
        # Exercise the documented browser route through an actual ephemeral
        # loopback socket, not only direct WSGI calls. No external network.
        class QuietHandler(WSGIRequestHandler):
            def log_message(self, format, *args):
                pass  # The test inspects responses rather than incidental access logs.

        opener = build_opener(ProxyHandler({}))  # Never inherit an HTTP proxy.
        with make_server("127.0.0.1", 0, board.application, handler_class=QuietHandler) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                origin = f"http://127.0.0.1:{server.server_port}"
                with opener.open(f"{origin}/?status=done", timeout=5) as reply:
                    content = reply.read()
                    self.assertEqual(reply.status, 200)
                    self.assertEqual(reply.headers.get_content_type(), "text/html")
                    self.assertEqual(int(reply.headers["Content-Length"]), len(content))
                    self.assertIn("Showing <strong>2</strong> tasks · <strong>3</strong> effort points", content.decode("utf-8"))
                    self.assertIn("default-src 'none'", reply.headers["Content-Security-Policy"])
                with opener.open(f"{origin}/style.css", timeout=5) as reply:
                    self.assertEqual(reply.status, 200)
                    self.assertIn(b":focus-visible", reply.read())
                with opener.open(f"{origin}/health", timeout=5) as reply:
                    self.assertEqual(reply.read(), b"ok\n")
            finally:
                server.shutdown()
                worker.join(timeout=5)
                self.assertFalse(worker.is_alive(), "Loopback demo server did not stop")

    def test_docs_are_truthful_and_linked_inside_candidate(self):
        readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "guides" / "application-repositories.md").read_text(encoding="utf-8")
        self.assertIn("Preview only", readme)
        self.assertIn("not recommended for production", readme)
        self.assertIn("Reviewed **2026-10-16**", guide)
        self.assertIn("[MIT license](../../LICENSE)", readme)
        self.assertTrue((EXAMPLE / "data" / "tasks.json").is_file())
        home = (ROOT / "README.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        for route in (
            "(guides/application-repositories.md)",
            "(examples/application-starter/README.md)",
        ):
            self.assertIn(route, home)
            self.assertIn(route, roadmap)
        self.assertIn("Application repository starter", roadmap)



if __name__ == "__main__":
    unittest.main()
