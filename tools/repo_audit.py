#!/usr/bin/env python3
"""Read-only, offline checks for a repository's reader-facing entry points.

This is a bounded source inspection, not a renderer, security scanner, license
classifier, or beauty score. It never imports or executes the target project.
"""
from __future__ import annotations

import argparse
import bisect
import json
import os
from pathlib import Path
import re
import stat
import sys
from html.parser import HTMLParser
from typing import Any

MAX_DOCUMENT_BYTES = 500 * 1024
MAX_DIRECTORY_ENTRIES = 4096
LOCATIONS = (".github", "", "docs")
DOCUMENT_SUFFIXES = (".md", ".markdown", ".rst", ".txt", "")
LEVELS = {"error": 0, "warning": 1, "info": 2}
PROFILES = ("public", "internal", "private")
# NTFS junctions redirect like directory symlinks, but only lstat's reparse tag shows them.
JUNCTION_REPARSE_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)
MARKDOWN_LINE_END_RE = re.compile(r"(?<=\n)|(?<=\r)(?!\n)")
# Lines that stand alone as a block: ATX headings, setext underlines, thematic breaks.
BLOCK_BOUNDARY_LINE = re.compile(r" {0,3}(?:#{1,6}(?:[ \t]|$)|=+[ \t]*$|-+[ \t]*$|(?:[*_][ \t]*){3,}$)")


class AuditInputError(ValueError):
    """An invalid target or an incomplete directory inventory."""


def finding(rule: str, severity: str, path: str, line: int | None,
            message: str, remedy: str) -> dict[str, Any]:
    return {"rule_id": rule, "severity": severity, "path": path, "line": line,
            "message": message, "remediation": remedy}


def _is_redirect(path: Path) -> bool:
    """Return True for a symbolic link or an NTFS junction; neither is followed."""
    try:
        info = path.lstat()
    except OSError:
        return False
    return (stat.S_ISLNK(info.st_mode)
            or getattr(info, "st_reparse_tag", 0) == JUNCTION_REPARSE_TAG)


def _inventory(root: Path, findings: list[dict[str, Any]]) -> dict[str, list[Path]]:
    inventory: dict[str, list[Path]] = {}
    for location in LOCATIONS:
        directory = root / location
        if _is_redirect(directory):
            findings.append(finding("path.symlink", "warning", location, None,
                                    "Directory symlink or junction was not followed.",
                                    "Audit a stable checkout with ordinary directories."))
            inventory[location] = []
            continue
        try:
            if not directory.is_dir():
                inventory[location] = []
                continue
            with os.scandir(directory) as entries:
                names = []
                for entry in entries:
                    if len(names) >= MAX_DIRECTORY_ENTRIES:
                        raise AuditInputError("Directory inventory exceeds the bounded scan limit.")
                    names.append(directory / entry.name)
                inventory[location] = sorted(names, key=lambda p: (p.name.casefold(), p.name))
        except OSError:
            raise AuditInputError("Cannot inspect the target's entry-point directories.") from None
    return inventory


def _candidates(inventory: dict[str, list[Path]], stem: str,
                locations: tuple[str, ...] = LOCATIONS) -> list[Path]:
    ranks = {stem.casefold() + suffix: i for i, suffix in enumerate(DOCUMENT_SUFFIXES)}
    result = []
    for location in locations:
        matches = [p for p in inventory[location] if p.name.casefold() in ranks]
        result.extend(sorted(matches, key=lambda p: (ranks[p.name.casefold()], p.name)))
    return result


def _read_document(path: Path, root: Path, findings: list[dict[str, Any]],
                   read_files: list[str]) -> str | None:
    relative = path.relative_to(root).as_posix()
    try:
        # A stable checkout is required: these checks are not a hostile-filesystem sandbox.
        if _is_redirect(path) or not stat.S_ISREG(path.lstat().st_mode):
            findings.append(finding("path.non_regular", "error", relative, None,
                                    "Selected document is not an ordinary file; it was not read.",
                                    "Use a regular file rather than a symlink or special device."))
            return None
        flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise OSError("not regular")
            raw = handle.read(MAX_DOCUMENT_BYTES + 1)
        if len(raw) > MAX_DOCUMENT_BYTES:
            findings.append(finding("document.too_large", "error", relative, None,
                                    "Document exceeds the 500 KiB inspection limit; it was not parsed.",
                                    "Move detailed material to linked documents; rerun the audit."))
            return None
        text = raw.decode("utf-8-sig")
        if "\x00" in text:
            raise UnicodeError("NUL in text")
        read_files.append(relative)
        return text
    except UnicodeError:
        findings.append(finding("document.encoding", "error", relative, None,
                                "Document is not readable UTF-8 text.",
                                "Save a text document as UTF-8 and rerun the audit."))
    except OSError:
        findings.append(finding("document.unreadable", "error", relative, None,
                                "Selected document could not be read.",
                                "Check its permissions and audit a stable local checkout."))
    return None


def _split_lines(text: str) -> list[str]:
    """Split after each Markdown line ending (\\n, \\r\\n or \\r), keeping the ending.

    str.splitlines also breaks at \\f, \\v, \\x1c-\\x1e, \\x85, U+2028 and U+2029,
    which Markdown treats as ordinary characters. A masked copy that blanks them
    would then have fewer lines than its source.
    """
    parts = MARKDOWN_LINE_END_RE.split(text)
    if parts and parts[-1] == "":
        parts.pop()
    return parts


def _masked(text: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in text)


def _mask_code_spans(source: str) -> str:
    runs = list(re.finditer(r"`+", source))
    by_width: dict[int, list[int]] = {}
    for i, run in enumerate(runs):
        by_width.setdefault(len(run.group()), []).append(i)
    chars = list(source)
    i = 0
    while i < len(runs):
        candidates = by_width[len(runs[i].group())]
        j = bisect.bisect_right(candidates, i)
        if j == len(candidates):
            i += 1
            continue
        end = candidates[j]
        for pos in range(runs[i].start(), runs[end].end()):
            if chars[pos] != "\n":
                chars[pos] = " "
        i = end + 1
    return "".join(chars)


def visible_source(text: str, *, mask_inline: bool = True) -> str:
    """Mask common fenced code/comments, preserving source line numbers.

    This intentionally implements a bounded Markdown subset, not a renderer.
    """
    lines = []
    active: tuple[str, int] | None = None
    in_comment = False
    for line in _split_lines(text):
        if active is not None:
            match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
            if match and match[1][0] == active[0] and len(match[1]) >= active[1] and not match[2].strip():
                active = None
            lines.append(_masked(line))
            continue
        # Inline examples of comment delimiters must not open real comments.
        outside_code = _mask_code_spans(line)
        cursor = 0
        pieces = []
        while cursor < len(line):
            if in_comment:
                closing = line.find("-->", cursor)
                if closing < 0:
                    pieces.append(_masked(line[cursor:]))
                    break
                pieces.append(_masked(line[cursor:closing + 3]))
                cursor = closing + 3
                in_comment = False
            else:
                opening = outside_code.find("<!--", cursor)
                if opening < 0:
                    pieces.append(line[cursor:])
                    break
                pieces.append(line[cursor:opening])
                cursor = opening
                in_comment = True
        visible_line = "".join(pieces)
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", visible_line.rstrip("\r\n"))
        if match and not (match[1][0] == "`" and "`" in match[2]):
            active = (match[1][0], len(match[1]))
            lines.append(_masked(visible_line))
        else:
            lines.append(visible_line)
    source = "".join(lines)
    return _mask_code_spans_by_block(source) if mask_inline else source


def _mask_code_spans_by_block(source: str) -> str:
    """Mask code spans block by block: a span never crosses a blank line or a heading.

    GitHub renders a lone backtick as plain text, so two stray backticks in
    different paragraphs must not hide everything between them.
    """
    masked: list[str] = []
    block: list[str] = []

    def flush() -> None:
        if block:
            masked.append(_mask_code_spans("".join(block)))
            block.clear()

    for line in _split_lines(source):
        content = line.rstrip("\r\n")
        if not content.strip():
            flush()
            masked.append(line)
        elif BLOCK_BOUNDARY_LINE.match(content):
            flush()
            masked.append(_mask_code_spans(line))
        else:
            block.append(line)
    flush()
    return "".join(masked)


class _HTMLFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[tuple[int, int]] = []
        self.images: list[tuple[int, dict[str, str | None]]] = []
        self._heading: tuple[int, int] | None = None
        self._heading_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            self.images.append((self.getpos()[0], dict(attrs)))
        if re.fullmatch(r"h[1-6]", tag):
            self._heading = (self.getpos()[0], int(tag[1]))
            self._heading_text = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._heading and tag == f"h{self._heading[1]}":
            if "".join(self._heading_text).strip():
                self.headings.append(self._heading)
            self._heading = None


def _is_repository_raw_asset(url: str) -> bool:
    """Identify GitHub-hosted raw images that depend on a remote/session."""
    return bool(re.match(
        r"^https?://(?:raw\\.githubusercontent\\.com/|"
        r"github\\.com/[^/?#]+/[^/?#]+/raw/)", url, re.IGNORECASE,
    ))


def _has_owner_contact(text: str) -> bool:
    """Recognize an explicit owner/contact/support heading or labelled field."""
    heading = re.search(
        r"(?im)^ {0,3}#{1,6}[ \\t]+(?:owners?|ownership|owning team|"
        r"maintainers?|contacts?|support|help desk|team)(?:\\b|[ \\t:/&-])", text,
    )
    field = re.search(
        r"(?im)^ {0,3}(?:owner|owning team|maintainer|contact|"
        r"support(?: channel)?|team):[ \\t]*\\S+", text,
    )
    return bool(heading or field)


def _absolute_image_findings(visible: str, path: str,
                             html_images: list[tuple[int, dict[str, str | None]]]
                             ) -> list[dict[str, Any]]:
    """Report common inline/reference Markdown images and HTML <img> raw URLs."""
    findings: list[dict[str, Any]] = []
    lines = [line.rstrip("\\r\\n") for line in _split_lines(visible)]
    references: dict[str, str] = {}
    definition = re.compile(r"^ {0,3}\\[([^\\]\\r\\n]{1,128})\\]:[ \\t]*<?(https?://[^\\s)>]+)", re.I)
    inline = re.compile(r"(?<!\\\\)!\\[[^\\]\\r\\n]{0,256}\\]\\(\\s*<?(https?://[^\\s)>]+)", re.I)
    referenced = re.compile(r"(?<!\\\\)!\\[([^\\]\\r\\n]{1,256})\\]\\[([^\\]\\r\\n]{0,128})\\]")
    shortcut = re.compile(r"(?<!\\\\)!\\[([^\\]\\r\\n]{1,256})\\](?![\\[(])")

    for line in lines:
        match = definition.match(line)
        if match:
            references.setdefault(" ".join(match[1].casefold().split()), match[2])

    def record(line_number: int) -> None:
        findings.append(finding(
            "readme.absolute_repo_asset", "warning", path, line_number,
            "Image uses a GitHub raw URL that may fail in clones, mirrors or private views.",
            "Prefer a checked-in repository-relative image path; review any external dependency.",
        ))

    for number, line in enumerate(lines, 1):
        for match in inline.finditer(line):
            if _is_repository_raw_asset(match[1]):
                record(number)
        for match in referenced.finditer(line):
            label = " ".join((match[2] or match[1]).casefold().split())
            if _is_repository_raw_asset(references.get(label, "")):
                record(number)
        for match in shortcut.finditer(line):
            label = " ".join(match[1].casefold().split())
            if _is_repository_raw_asset(references.get(label, "")):
                record(number)
    for number, attrs in html_images:
        if _is_repository_raw_asset(attrs.get("src") or ""):
            record(number)
    return findings


def _inspect_markdown(text: str, path: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    visible = visible_source(text)
    lines = [line.rstrip("\r\n") for line in _split_lines(visible)]
    heading_lines = [line.rstrip("\r\n")
                     for line in _split_lines(visible_source(text, mask_inline=False))]
    html = _HTMLFacts()
    html.feed(visible)
    html.close()
    findings.extend(_absolute_image_findings(visible, path, html.images))
    headings = list(html.headings)
    for index, line in enumerate(lines):
        heading_line = heading_lines[index]
        # rstrip() instead of a lazy `(.+?)\s*$`, which backtracks quadratically on
        # a long run of trailing spaces.
        atx = re.match(r" {0,3}(#{1,6})[ \t]+(.+)", heading_line.rstrip())
        if atx and atx[2].strip("# \t"):
            headings.append((index + 1, len(atx[1])))
        elif index and heading_lines[index - 1].strip() and re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", heading_line):
            if not heading_lines[index - 1].lstrip().startswith(("|", "#", ">", "<")):
                headings.append((index, 1 if line.strip().startswith("=") else 2))
        if re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}|\b(?:TODO|TBD|FIXME)\b", line):
            findings.append(finding("readme.placeholder", "warning", path, index + 1,
                                    "Possible unfilled placeholder in reader-facing text.",
                                    "Replace unfinished prose, or verify that the token is intentional."))
        if re.search(r"(?<!\\)!\[\s*\]\s*(?:\(|\[)", line):
            findings.append(finding("image.empty_alt", "info", path, index + 1,
                                    "Markdown image has empty alternative text; human review is needed.",
                                    "Keep it empty for decoration; describe information-bearing images."))
        if line.lstrip().startswith("|") and index + 1 < len(lines):
            cells = line.strip().strip("|").split("|")
            separator = lines[index + 1].strip().strip("|").split("|")
            if len(cells) > 1 and all(not cell.strip() for cell in cells) and all(
                    re.fullmatch(r"\s*:?-{3,}:?\s*", cell) for cell in separator):
                findings.append(finding("table.empty_headers", "warning", path, index + 1,
                                        "Table header cells are empty; this may be a layout table.",
                                        "Use a list for layout, or give a genuine data table meaningful headers."))
    headings.sort()
    if not any(level == 1 for _, level in headings):
        findings.append(finding("readme.title", "warning", path, 1,
                                "No nonempty level-one title was found in supported heading syntax.",
                                "Add a clear Markdown or HTML title; check the rendered result."))
    previous = 0
    first_title = True
    for line, level in headings:
        if level > previous + 1:
            findings.append(finding("heading.skipped_level", "warning", path, line,
                                    f"Heading level jumps from {previous} to {level}.",
                                    "Use a meaningful heading hierarchy rather than levels chosen for size."))
        if level == 1 and not first_title:
            findings.append(finding("heading.multiple_titles", "info", path, line,
                                    "Another level-one title was found.",
                                    "Check whether it should be a subsection instead."))
        if level == 1:
            first_title = False
        previous = level
    for line, attrs in html.images:
        role = (attrs.get("role") or "").lower()
        named = bool(attrs.get("aria-label") or attrs.get("aria-labelledby"))
        if "alt" not in attrs and role not in {"none", "presentation"} and not named and attrs.get("aria-hidden") != "true":
            findings.append(finding("image.missing_alt", "warning", path, line,
                                    "HTML image has no alt attribute or supported explicit naming/decorative marker.",
                                    "Add meaningful alt text, or explicitly mark a decorative image."))
        elif "alt" in attrs and not (attrs["alt"] or "").strip():
            findings.append(finding("image.empty_alt", "info", path, line,
                                    "HTML image has empty alternative text; this can be correct for decoration.",
                                    "Verify its purpose; empty alt is not automatically an accessibility defect."))
    return findings


def audit_repository(target: str | Path, *, profile: str = "public") -> dict[str, Any]:
    if profile not in PROFILES:
        raise AuditInputError("profile must be public, internal or private.")
    try:
        root = Path(target).resolve(strict=True)
        if not root.is_dir():
            raise AuditInputError("Target must be an existing directory.")
    except (OSError, RuntimeError, ValueError):
        raise AuditInputError("Target must be an existing readable directory.") from None
    findings: list[dict[str, Any]] = []
    read_files: list[str] = []
    inventory = _inventory(root, findings)
    readmes = _candidates(inventory, "README")
    licenses = _candidates(inventory, "LICENSE", ("",)) + _candidates(inventory, "LICENCE", ("",)) + _candidates(inventory, "COPYING", ("",))
    contributing = _candidates(inventory, "CONTRIBUTING")
    selected = {"readme": readmes[:1], "license": licenses[:1], "contributing": contributing[:1]}
    documents: dict[str, str | None] = {}
    for kind, paths in selected.items():
        documents[kind] = paths[0].relative_to(root).as_posix() if paths else None
        if not paths:
            severity = {"readme": "error", "license": "warning", "contributing": "info"}[kind]
            remedy = "Inspect the documented scope; add a real document or provide an intentional alternative."
            if kind == "license" and profile != "public":
                severity = "info"
                remedy = "State internal-use terms in the README or link the company policy."
            findings.append(finding(f"{kind}.missing", severity, ".", None,
                                    f"No dedicated {kind} document found in the supported local locations.",
                                    remedy))
            continue
        text = _read_document(paths[0], root, findings, read_files)
        if text is None:
            continue
        relative = documents[kind]
        assert relative is not None
        if not text.strip():
            findings.append(finding(f"{kind}.empty", "error" if kind == "readme" else "warning",
                                    relative, 1, "Selected document is empty.",
                                    "Replace the empty file with useful project-specific information."))
        elif kind == "readme":
            is_markdown = paths[0].suffix.lower() in {".md", ".markdown"}
            if is_markdown:
                findings.extend(_inspect_markdown(text, relative))
            else:
                findings.append(finding("readme.unsupported_format", "info", relative, None,
                                        "README was found, but its format is outside the Markdown checks.",
                                        "Review the rendered document manually; it is not treated as missing."))
            if profile != "public":
                source = visible_source(text, mask_inline=False) if is_markdown else text
                if not _has_owner_contact(source):
                    findings.append(finding(
                        "readme.owner_contact", "warning", relative, None,
                        "No explicit owner, maintainer, contact or support section was found.",
                        "Name the owning team and an approved internal contact or support route.",
                    ))
    findings.sort(key=lambda f: (LEVELS[f["severity"]], f["path"], f["line"] or 0, f["rule_id"]))
    return {"schema_version": 1, "profile": profile, "documents": documents, "read_files": sorted(read_files),
            "summary": {level: sum(f["severity"] == level for f in findings) for level in LEVELS},
            "findings": findings}


def exit_status(report: dict[str, Any], fail_on: str) -> int:
    if fail_on == "never":
        return 0
    return int(bool(report["summary"]["error"] or (fail_on == "warning" and report["summary"]["warning"])))


def render_text(report: dict[str, Any]) -> str:
    def safe(value: str) -> str:
        return json.dumps(value, ensure_ascii=True)[1:-1]
    lines = ["BeautifulRepo entry-point audit (offline; no score)"]
    for item in report["findings"]:
        location = safe(item["path"]) + (f":{item['line']}" if item['line'] else "")
        lines.extend((f"{item['severity'].upper()} [{item['rule_id']}] {location}: {item['message']}",
                      f"  Next: {item['remediation']}"))
    counts = report["summary"]
    lines.append(f"Summary: {counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} informational finding(s).")
    lines.append("Source inspection only: no network requests, project execution or compliance certification.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="local repository directory (default: current directory)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--profile", choices=PROFILES, default="public",
                        help="locally selected guidance profile; no remote visibility is inspected")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error",
                        help="failure threshold; informational findings never fail a valid audit")
    args = parser.parse_args(argv)
    try:
        report = audit_repository(args.root, profile=args.profile)
    except AuditInputError as exc:
        print(f"repo_audit: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(render_text(report), end="")
    return exit_status(report, args.fail_on)


if __name__ == "__main__":
    raise SystemExit(main())
