"""Read-only, synthetic task-board example. Not a production web server."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "data" / "tasks.json"
STYLE = HERE / "style.css"
VALID_STATES = {"open", "done"}
ID_PATTERN = re.compile(r"[a-z][a-z0-9-]{0,31}\Z")


def validate_tasks(raw: object) -> list[dict[str, object]]:
    """Check a small invented fixture, not an arbitrary public data ingestion API."""
    if not isinstance(raw, list) or not 1 <= len(raw) <= 100:
        raise ValueError("Expected 1–100 synthetic tasks")
    seen: set[str] = set()
    tasks: list[dict[str, object]] = []
    for entry in raw:
        if not isinstance(entry, dict) or set(entry) != {"id", "title", "status", "effort"}:
            raise ValueError("Invalid task fields")
        ident, title, state, effort = (entry[key] for key in ("id", "title", "status", "effort"))
        if not isinstance(ident, str) or not ID_PATTERN.fullmatch(ident) or ident in seen:
            raise ValueError("Invalid or duplicate task id")
        if not isinstance(title, str) or not 1 <= len(title) <= 80 or title != title.strip():
            raise ValueError("Invalid task title")
        if any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF
               for c in title):
            # JSON permits escaped lone surrogates, but UTF-8 HTML does not.
            # Reject the record during validation so /health never reports a
            # ready application when its main page cannot be encoded.
            raise ValueError("Invalid task title")
        if not isinstance(state, str) or state not in VALID_STATES:
            raise ValueError("Invalid task state")
        if type(effort) is not int or not 1 <= effort <= 100:
            raise ValueError("Invalid task effort")
        seen.add(ident)
        tasks.append({"id": ident, "title": title, "status": state, "effort": effort})
    return tasks


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous fixture fields before JSON decoding overwrites them."""
    fields: dict[str, object] = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError("Duplicate JSON object key")
        fields[key] = value
    return fields


def read_sample() -> list[dict[str, object]]:
    return validate_tasks(json.loads(FIXTURE.read_text(encoding="utf-8"),
                                     object_pairs_hook=reject_duplicate_json_keys))


def render_page(tasks: list[dict[str, object]], status_filter: str = "all") -> bytes:
    """Build an HTML page using native form controls and escaped data."""
    if status_filter not in {"all", *VALID_STATES}:
        raise ValueError("Invalid filter")
    visible = [task for task in tasks if status_filter == "all" or task["status"] == status_filter]
    count = len(visible)
    points = sum(int(task["effort"]) for task in visible)
    options = "".join(
        f'<option value="{value}"{" selected" if value == status_filter else ""}>{name}</option>'
        for value, name in (("all", "All tasks"), ("open", "Open"), ("done", "Done"))
    )
    cards = "".join(
        '<li class="task">'
        f'<div class="task__heading"><h3>{escape(str(task["title"]))}</h3>'
        f'<span class="badge">{escape(str(task["status"]).title())}</span></div>'
        f'<p>{int(task["effort"])} effort points · ID {escape(str(task["id"]))}</p>'
        '</li>'
        for task in visible
    ) or '<li class="empty">No tasks match this filter.</li>'
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A fabricated, read-only task board illustrating a trustworthy application repository.">
<title>Pocket Board — synthetic task app</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<a class="skip" href="#content">Skip to main content</a>
<header class="top"><a href="/">Pocket Board</a><span class="top__note">Demo · synthetic data</span></header>
<main id="content" class="wrap">
<section class="intro" aria-labelledby="title">
<p class="eyebrow">A working example, not a hosted product</p>
<h1 id="title">Keep the little things visible.</h1>
<p>Explore a tiny fictional task board. Filter the entries and see the total effort points. No login, uploads, tracking, scripts or database.</p>
</section>
<section class="panel" aria-labelledby="board-heading">
<div class="section-head"><h2 id="board-heading">Sample work</h2><p>All entries are invented.</p></div>
<form method="get" action="/" class="filters">
<label for="status">Show tasks</label>
<select id="status" name="status">{options}</select>
<button type="submit">Apply filter</button>
</form>
<p class="summary" role="status">Showing <strong>{count}</strong> tasks · <strong>{points}</strong> effort points</p>
<ul class="tasks">{cards}</ul>
</section>
<p class="notice">Data is read-only and resets to the checked-in sample. This app makes no persistence, privacy or production hosting claim.</p>
</main>
<footer class="footer">Demo code: Python standard library · local loopback only</footer>
</body>
</html>'''
    return html.encode("utf-8")


def application(environ: dict, start_response):
    """Minimal WSGI handler: GET /, /style.css, /health, nothing else."""
    method = environ.get("REQUEST_METHOD", "GET")
    if method != "GET":
        status, kind, body = "405 Method Not Allowed", "text/plain", b"Method not allowed\n"
        extra = [("Allow", "GET")]
    else:
        extra = []
        path = environ.get("PATH_INFO", "/")
        if path == "/style.css":
            try:
                css = STYLE.read_bytes()
            except OSError:
                # Broken teaching checkout: use the same generic error shape as
                # a missing data fixture, without exposing an absolute path.
                status, kind, body = (
                    "500 Internal Server Error", "text/plain", b"Sample unavailable\n"
                )
            else:
                status, kind, body = "200 OK", "text/css", css
        elif path == "/health":
            # This is a *local demo readiness* signal, not an uptime or security
            # guarantee. A page that cannot read its fixture or CSS is not ready.
            try:
                read_sample()
                STYLE.read_bytes()
            except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
                status, kind, body = (
                    "503 Service Unavailable", "text/plain", b"Sample unavailable\n"
                )
            else:
                status, kind, body = "200 OK", "text/plain", b"ok\n"
        elif path == "/":
            try:
                args = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True,
                                strict_parsing=True, max_num_fields=1)
                if set(args) - {"status"} or any(len(v) != 1 for v in args.values()):
                    raise ValueError("Invalid query")
                selected = args.get("status", ["all"])[0]
                if selected not in {"all", *VALID_STATES}:
                    raise ValueError("Invalid filter")
            except ValueError:
                status, kind, body = "400 Bad Request", "text/plain", b"Invalid filter\n"
            else:
                try:
                    body = render_page(read_sample(), selected)
                except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
                    status, kind, body = "500 Internal Server Error", "text/plain", b"Sample unavailable\n"
                else:
                    status, kind = "200 OK", "text/html"
        else:
            status, kind, body = "404 Not Found", "text/plain", b"Not found\n"
    headers = [
        ("Content-Type", f"{kind}; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Content-Security-Policy", "default-src 'none'; style-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"),
    ] + extra
    start_response(status, headers)
    return [body]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve a fictional task board locally for demonstration")
    parser.add_argument("--port", type=int, default=8000)
    options = parser.parse_args(argv)
    if not 1 <= options.port <= 65535:
        parser.error("port must be between 1 and 65535")
    read_sample()  # Fail early if the teaching fixture was accidentally corrupted.
    with make_server("127.0.0.1", options.port, application) as server:
        print(f"Local preview: http://127.0.0.1:{options.port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
