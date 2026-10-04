#!/usr/bin/env python3
"""Check repository-owned relative destinations in Markdown files without network access."""
from __future__ import annotations

import argparse
import re
import string
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK_START_RE = re.compile(r"!?\[[^\]\n]*\]\(\s*")
INLINE_CODE_RE = re.compile(r"\x60[^\x60\n]*\x60")
FENCE_RE = re.compile(r"^ {0,3}(?P<fence>\x60{3,}|~{3,})(?P<info>.*)$")
CLOSING_FENCE_RE = re.compile(r"^ {0,3}(?P<fence>\x60{3,}|~{3,})[ \t]*$")


def _consume_title_and_close(line: str, position: int):
    """Return the index after an inline link's closing ')' or None."""
    while position < len(line) and line[position] in " \t":
        position += 1

    if position < len(line) and line[position] == ")":
        return position + 1
    if position >= len(line):
        return None

    opener = line[position]
    if opener in "\"'":
        closer = opener
    elif opener == "(":
        closer = ")"
    else:
        return None

    position += 1
    while position < len(line):
        char = line[position]
        if char == "\\" and position + 1 < len(line):
            position += 2
            continue
        if char == closer:
            position += 1
            while position < len(line) and line[position] in " \t":
                position += 1
            if position < len(line) and line[position] == ")":
                return position + 1
            return None
        position += 1
    return None


def _parse_destination(line: str, position: int):
    """Return (destination, end_index) for one inline link destination."""
    if position >= len(line):
        return None

    if line[position] == "<":
        position += 1
        chars = []
        while position < len(line):
            char = line[position]
            if char == "\\" and position + 1 < len(line):
                next_char = line[position + 1]
                if next_char in string.punctuation:
                    chars.append(next_char)
                    position += 2
                    continue
            if char == ">":
                end = _consume_title_and_close(line, position + 1)
                if end is None:
                    return None
                return "".join(chars), end
            if char == "<":
                return None
            chars.append(char)
            position += 1
        return None

    chars = []
    depth = 0
    while position < len(line):
        char = line[position]
        if char == "\\" and position + 1 < len(line):
            next_char = line[position + 1]
            if next_char in string.punctuation:
                chars.append(next_char)
                position += 2
                continue
        if char == "(":
            depth += 1
            chars.append(char)
            position += 1
            continue
        if char == ")":
            if depth:
                depth -= 1
                chars.append(char)
                position += 1
                continue
            if not chars:
                return "", position + 1
            return "".join(chars), position + 1
        if char == " " or ord(char) < 0x20:
            if depth or not chars:
                return None
            end = _consume_title_and_close(line, position)
            if end is None:
                return None
            return "".join(chars), end
        chars.append(char)
        position += 1
    return None


def iter_markdown_destinations(path: Path):
    """Yield (line_number, destination) for inline Markdown links outside code."""
    fence_char = None
    fence_length = 0
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if fence_char is not None:
            closing = CLOSING_FENCE_RE.match(raw_line)
            if closing:
                marker = closing.group("fence")
                if marker[0] == fence_char and len(marker) >= fence_length:
                    fence_char = None
                    fence_length = 0
            continue

        opening = FENCE_RE.match(raw_line)
        if opening:
            marker = opening.group("fence")
            info = opening.group("info")
            if marker[0] != "`" or "`" not in info:
                fence_char = marker[0]
                fence_length = len(marker)
                continue

        line = INLINE_CODE_RE.sub("", raw_line)
        for match in LINK_START_RE.finditer(line):
            parsed = _parse_destination(line, match.end())
            if parsed is not None:
                destination, _ = parsed
                yield lineno, destination


def resolve_local_destination(root: Path, source: Path, destination: str):
    """Return (resolved_path, error) or (None, None) when destination is out of scope."""
    if not destination or destination.startswith("#"):
        return None, None

    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc:
        return None, None

    raw_path = unquote(parsed.path)
    if not raw_path:
        return None, None

    root = root.resolve()
    if raw_path.startswith("/"):
        candidate = root / raw_path.lstrip("/")
    else:
        candidate = source.parent / raw_path

    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, "escapes repository root"
    return resolved, None


def check_repo(root: Path):
    """Return (errors, checked_destinations, markdown_files)."""
    root = root.resolve()
    errors = []
    checked = 0
    markdown_files = 0

    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        markdown_files += 1
        for lineno, destination in iter_markdown_destinations(path):
            resolved, error = resolve_local_destination(root, path, destination)
            if resolved is None and error is None:
                continue
            checked += 1
            relative_source = path.relative_to(root).as_posix()
            if error:
                errors.append(f"{relative_source}:{lineno}: {error}: {destination!r}")
            elif not resolved.exists():
                errors.append(
                    f"{relative_source}:{lineno}: missing relative destination: {destination!r}"
                )

    return errors, checked, markdown_files


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check repository-owned relative Markdown link and image destinations."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root to scan (default: parent of tools/)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")

    errors, checked, markdown_files = check_repo(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(
            f"ERROR: {len(errors)} broken relative Markdown destination(s) "
            f"across {markdown_files} Markdown file(s)",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: checked {checked} relative Markdown destination(s) "
        f"across {markdown_files} Markdown file(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
