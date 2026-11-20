#!/usr/bin/env python3
"""Read-only, bounded static asset-path check for an itch.io HTML5 ZIP entry page.

Only literal HTML src / selected link href values in root index.html are checked.
It does not execute JS, parse CSS, resolve srcset or simulate a browser.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import stat
import sys
from urllib.parse import unquote, urlsplit
import zipfile

MAX_INDEX_BYTES = 1_048_576
MAX_ARCHIVE_MEMBERS = 2_000
MAX_REFERENCES = 2_000
SRC_TAGS = {"script", "img", "audio", "video", "source", "track", "embed", "iframe", "input"}
LINK_RELS = {"stylesheet", "icon", "preload", "modulepreload", "manifest", "apple-touch-icon"}


class HTMLReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[tuple[str, str]] = []
        self.base_urls: list[str] = []
        self.too_many = False

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = dict(attributes)
        if tag == "base" and "href" in attrs:
            self.base_urls.append(attrs.get("href") or "")
        url: str | None = None
        if tag in SRC_TAGS:
            url = attrs.get("src")
        elif tag == "link" and LINK_RELS.intersection((attrs.get("rel") or "").lower().split()):
            url = attrs.get("href")
        if url is not None:
            if len(self.urls) >= MAX_REFERENCES:
                self.too_many = True
            else:
                self.urls.append((tag, url))

    handle_startendtag = handle_starttag


def inspect(path: Path) -> dict[str, object]:
    result: dict[str, object] = {"archive": path.name, "status": "incomplete", "checked": 0, "findings": []}
    findings: list[dict[str, str]] = []

    def report(rule: str, url: str, detail: str) -> None:
        findings.append({"rule": rule, "url": url, "detail": detail})

    try:
        if path.is_symlink() or not path.is_file():
            raise ValueError("archive must be an ordinary, existing ZIP file")
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ARCHIVE_MEMBERS:
                raise ValueError("archive contains too many members for this static check")
            names = [info.filename for info in infos]
            if len(set(names)) != len(names):
                raise ValueError("archive contains duplicate member names; run ZIP metadata preflight")
            entries = {info.filename: info for info in infos}
            entry = entries.get("index.html")
            if entry is None or entry.is_dir() or (
                entry.create_system == 3 and stat.S_IFMT(entry.external_attr >> 16) not in (0, stat.S_IFREG)
            ):
                raise ValueError("archive needs exactly one regular root index.html")
            if entry.flag_bits & 1 or entry.file_size > MAX_INDEX_BYTES:
                raise ValueError("index.html is encrypted or exceeds the 1 MiB static-read limit")
            # Never extract or write. Bounded read also rejects incorrect size metadata.
            with archive.open(entry, "r") as html:
                data = html.read(MAX_INDEX_BYTES + 1)
            if len(data) > MAX_INDEX_BYTES:
                raise ValueError("index.html exceeds the 1 MiB static-read limit")
            source = data.decode("utf-8", errors="strict")
            parser = HTMLReferences()
            parser.feed(source)
            parser.close()
            if parser.too_many:
                raise ValueError("index.html contains too many static asset references")
            # A <base href> changes how all relative references resolve.
            # Fail closed rather than confidently reporting wrong paths.
            if parser.base_urls:
                raise ValueError("HTML base href is not supported by this static check")
            names_set = set(names)
            for tag, url in parser.urls:
                raw = url.strip()
                if not raw:
                    continue
                if raw.startswith("/"):
                    report("root_absolute", raw, "root-absolute URL may escape the itch.io game subdirectory")
                    continue
                try:
                    parts = urlsplit(raw)
                except ValueError:
                    report("invalid_url", raw, "invalid static URL")
                    continue
                if parts.scheme or parts.netloc:
                    if parts.scheme.lower() == "http":
                        report("insecure_external", raw, "HTTP asset URL may be blocked on an HTTPS game page")
                    # External resources, data: and blob: are not checked locally.
                    continue
                if not parts.path:
                    continue
                try:
                    decoded = unquote(parts.path, encoding="utf-8", errors="strict")
                except UnicodeError:
                    report("invalid_url", raw, "path is not valid percent-encoded UTF-8")
                    continue
                if decoded.startswith("/") or "\\" in decoded or "\x00" in decoded or "?" in decoded or "#" in decoded:
                    report("invalid_url", raw, "path uses unsupported or unsafe separators")
                    continue
                normalized = posixpath.normpath(decoded)
                if normalized in (".", "..") or normalized.startswith("../"):
                    report("outside_game", raw, "relative path escapes the ZIP's root directory")
                    continue
                if normalized.endswith("/") or decoded.endswith("/"):
                    report("not_a_file", raw, "reference points to a directory rather than a file")
                    continue
                result["checked"] = int(result["checked"]) + 1
                if normalized not in names_set:
                    if any(other.casefold() == normalized.casefold() for other in names_set):
                        report("case_mismatch", raw, "asset path differs in letter case from ZIP member")
                    else:
                        report("missing_asset", raw, "literal HTML reference has no matching ZIP member")
                elif entries[normalized].is_dir():
                    report("not_a_file", raw, "reference resolves to a directory, not an asset file")
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, EOFError) as exc:
        result["error"] = f"cannot complete static HTML check: {type(exc).__name__}: {exc}"
        return result
    result["findings"] = sorted(findings, key=lambda f: (f["rule"], f["url"], f["detail"]))
    result["status"] = "findings" if findings else "ok"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="HTML5 ZIP with root index.html")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    report = inspect(args.archive)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    else:
        print(f"HTML5 static assets: {report['status'].upper()} ({report['checked']} local reference(s) checked)")
        if "error" in report:
            print(report["error"])
        for finding in report["findings"]:
            print(f"- {finding['rule']} {ascii(finding['url'])}: {finding['detail']}")
    return {"ok": 0, "findings": 1, "incomplete": 2}[str(report["status"])]


if __name__ == "__main__":
    sys.exit(main())
