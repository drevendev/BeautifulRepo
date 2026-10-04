#!/usr/bin/env python3
"""Check repository-owned relative destinations in Markdown files without network access."""
from __future__ import annotations

import argparse
from html.entities import html5
import re
import string
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

FENCE_RE = re.compile(r"^ {0,3}(?P<fence>\x60{3,}|~{3,})(?P<info>.*)$")
CLOSING_FENCE_RE = re.compile(r"^ {0,3}(?P<fence>\x60{3,}|~{3,})[ \t]*$")
LIST_MARKER_RE = re.compile(
    r"^(?P<marker>(?:[*+-]|[0-9]{1,9}[.)]))(?P<padding>[ \t]+)(?P<body>.*)$"
)
ATX_HEADING_RE = re.compile(r"^#{1,6}(?:[ \t]+|$)")
SETEXT_UNDERLINE_RE = re.compile(r"^(?:=+|-+)[ \t]*$")
THEMATIC_BREAK_RE = re.compile(
    r"^(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})$"
)
BLOCK_QUOTE_RE = re.compile(r"^>[ \t]?")
MARKDOWN_WHITESPACE = " \t\r\n"
BLANK_LINE_RE = re.compile(r"\r?\n[ \t]*\r?\n")
CHARACTER_REFERENCE_RE = re.compile(
    r"&(?:#(?P<dec>[0-9]{1,7})|#[xX](?P<hex>[0-9A-Fa-f]{1,6})|(?P<named>[A-Za-z][A-Za-z0-9]*));"
)


def _decode_character_references(value: str) -> str:
    """Decode only GFM-valid, semicolon-terminated character references."""
    def replace(match):
        named = match.group("named")
        if named is not None:
            return html5.get(named + ";", match.group(0))

        digits = match.group("hex") or match.group("dec")
        base = 16 if match.group("hex") is not None else 10
        code_point = int(digits, base)
        if code_point == 0 or code_point > 0x10FFFF or 0xD800 <= code_point <= 0xDFFF:
            return "\uFFFD"
        return chr(code_point)

    return CHARACTER_REFERENCE_RE.sub(replace, value)


def _iter_inline_link_starts(line: str):
    """Yield destination start indices for inline links with balanced link text."""
    position = 0
    while position < len(line):
        char = line[position]
        if char == "\\" and position + 1 < len(line):
            if line[position + 1] in string.punctuation:
                position += 2
                continue
        if char != "[":
            position += 1
            continue

        depth = 1
        cursor = position + 1
        while cursor < len(line):
            char = line[cursor]
            if char == "\\" and cursor + 1 < len(line):
                if line[cursor + 1] in string.punctuation:
                    cursor += 2
                    continue
            if char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    if cursor + 1 < len(line) and line[cursor + 1] == "(":
                        destination = cursor + 2
                        while destination < len(line) and line[destination] in MARKDOWN_WHITESPACE:
                            destination += 1
                        yield destination
                    break
            cursor += 1
        position += 1


def _consume_title_and_close(line: str, position: int):
    """Return the index after an inline link's closing ')' or None."""
    while position < len(line) and line[position] in MARKDOWN_WHITESPACE:
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
            while position < len(line) and line[position] in MARKDOWN_WHITESPACE:
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
            if char in "\r\n":
                return None
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


def _is_backslash_escaped(text: str, position: int) -> bool:
    """Return whether the character at position is escaped by an odd backslash run."""
    backslashes = 0
    cursor = position - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def _mask_inline_code_spans(text: str) -> str:
    """Mask GFM code spans while preserving offsets and line endings."""
    masked = list(text)
    position = 0

    while position < len(text):
        if text[position] != "`":
            position += 1
            continue

        run_start = position
        while position < len(text) and text[position] == "`":
            position += 1
        run_length = position - run_start

        if _is_backslash_escaped(text, run_start):
            continue

        cursor = position
        closing_end = None
        while cursor < len(text):
            next_start = text.find("`", cursor)
            if next_start == -1:
                break

            next_end = next_start
            while next_end < len(text) and text[next_end] == "`":
                next_end += 1

            if next_end - next_start == run_length:
                closing_end = next_end
                break
            cursor = next_end

        if closing_end is None:
            continue

        for index in range(run_start, closing_end):
            if masked[index] not in "\r\n":
                masked[index] = " "
        position = closing_end

    return "".join(masked)


def _mask_inline_code_blocks(text: str) -> str:
    """Mask code spans within each non-blank inline block."""
    masked = []
    block_start = 0
    separators = list(BLANK_LINE_RE.finditer(text))

    for separator in separators + [None]:
        block_end = separator.start() if separator is not None else len(text)
        masked.append(_mask_inline_code_spans(text[block_start:block_end]))

        if separator is None:
            break
        masked.append(text[separator.start():separator.end()])
        block_start = separator.end()

    return "".join(masked)


def _leading_indent_columns(line: str):
    """Return (visual_columns, character_index) for leading spaces and tabs."""
    columns = 0
    index = 0
    while index < len(line):
        char = line[index]
        if char == " ":
            columns += 1
        elif char == "\t":
            columns += 4 - (columns % 4)
        else:
            break
        index += 1
    return columns, index


def _list_item_content_indent(line: str):
    """Return the content column for a simple top-level GFM list marker, or None."""
    indent, index = _leading_indent_columns(line)
    if indent > 3:
        return None

    match = LIST_MARKER_RE.match(line[index:])
    if match is None:
        return None

    column = indent + len(match.group("marker"))
    padding_columns = 0
    for char in match.group("padding"):
        if char == " ":
            column += 1
            padding_columns += 1
        else:
            width = 4 - (column % 4)
            column += width
            padding_columns += width

    if not 1 <= padding_columns <= 4:
        return None
    return column


def _starts_nonparagraph_block(line: str) -> bool:
    """Recognize common top-level blocks that an indented code block may follow directly."""
    indent, index = _leading_indent_columns(line)
    if indent > 3:
        return False
    body = line[index:]
    return bool(
        ATX_HEADING_RE.match(body)
        or SETEXT_UNDERLINE_RE.match(body)
        or THEMATIC_BREAK_RE.match(body)
        or BLOCK_QUOTE_RE.match(body)
    )


def _mask_indented_code_blocks(text: str) -> str:
    """Mask GFM indented code while preserving paragraph and simple list precedence."""
    masked = []
    paragraph_open = False
    list_content_indent = None
    in_indented_code = False
    code_threshold = 4

    for raw_line in text.splitlines(keepends=True):
        if raw_line.endswith("\r\n"):
            line, ending = raw_line[:-2], "\r\n"
        elif raw_line.endswith(("\n", "\r")):
            line, ending = raw_line[:-1], raw_line[-1]
        else:
            line, ending = raw_line, ""

        if not line.strip(" \t"):
            masked.append(line + ending)
            paragraph_open = False
            continue

        indent, _ = _leading_indent_columns(line)
        if in_indented_code:
            if indent >= code_threshold:
                masked.append(" " * len(line) + ending)
                continue
            in_indented_code = False

        if list_content_indent is not None and indent < list_content_indent:
            list_content_indent = None

        if list_content_indent is None and _starts_nonparagraph_block(line):
            paragraph_open = False
            masked.append(line + ending)
            continue

        marker_indent = _list_item_content_indent(line)
        if marker_indent is not None:
            list_content_indent = marker_indent
            paragraph_open = True
            masked.append(line + ending)
            continue

        if list_content_indent is not None:
            relative_indent = indent - list_content_indent
            if relative_indent >= 4 and not paragraph_open:
                in_indented_code = True
                code_threshold = list_content_indent + 4
                masked.append(" " * len(line) + ending)
                continue
            paragraph_open = True
            masked.append(line + ending)
            continue

        if indent >= 4 and not paragraph_open:
            in_indented_code = True
            code_threshold = 4
            masked.append(" " * len(line) + ending)
            continue

        paragraph_open = not _starts_nonparagraph_block(line)
        masked.append(line + ending)

    return "".join(masked)


def _block_quote_content_start(line: str):
    """Return the content index after one explicit GFM block-quote marker."""
    indent, index = _leading_indent_columns(line)
    if indent > 3 or index >= len(line) or line[index] != ">":
        return None

    index += 1
    if index < len(line) and line[index] in " \t":
        index += 1
    return index


def _mask_block_quote_code_blocks(text: str) -> str:
    """Mask code inside explicit block-quote containers without shifting offsets."""
    lines = text.splitlines(keepends=True)
    masked = []
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        if raw_line.endswith("\r\n"):
            line, ending = raw_line[:-2], "\r\n"
        elif raw_line.endswith(("\n", "\r")):
            line, ending = raw_line[:-1], raw_line[-1]
        else:
            line, ending = raw_line, ""

        content_start = _block_quote_content_start(line)
        if content_start is None:
            masked.append(raw_line)
            index += 1
            continue

        prefixes = []
        content_lengths = []
        inner_parts = []
        while index < len(lines):
            raw_line = lines[index]
            if raw_line.endswith("\r\n"):
                line, ending = raw_line[:-2], "\r\n"
            elif raw_line.endswith(("\n", "\r")):
                line, ending = raw_line[:-1], raw_line[-1]
            else:
                line, ending = raw_line, ""

            content_start = _block_quote_content_start(line)
            if content_start is None:
                break

            prefix = line[:content_start]
            content = line[content_start:] + ending
            prefixes.append(prefix)
            content_lengths.append(len(content))
            inner_parts.append(content)
            index += 1

        inner_masked = _mask_markdown_code("".join(inner_parts))
        offset = 0
        for prefix, content_length in zip(prefixes, content_lengths):
            masked.append(prefix + inner_masked[offset:offset + content_length])
            offset += content_length

    return "".join(masked)


def _mask_markdown_code(text: str) -> str:
    """Mask fenced code and GFM code spans while preserving offsets and line endings."""
    masked = []
    fence_char = None
    fence_length = 0

    for raw_line in text.splitlines(keepends=True):
        if raw_line.endswith("\r\n"):
            line, ending = raw_line[:-2], "\r\n"
        elif raw_line.endswith(("\n", "\r")):
            line, ending = raw_line[:-1], raw_line[-1]
        else:
            line, ending = raw_line, ""

        if fence_char is not None:
            closing = CLOSING_FENCE_RE.match(line)
            if closing:
                marker = closing.group("fence")
                if marker[0] == fence_char and len(marker) >= fence_length:
                    fence_char = None
                    fence_length = 0
            masked.append(" " * len(line) + ending)
            continue

        opening = FENCE_RE.match(line)
        if opening:
            marker = opening.group("fence")
            info = opening.group("info")
            if marker[0] != "`" or "`" not in info:
                fence_char = marker[0]
                fence_length = len(marker)
                masked.append(" " * len(line) + ending)
                continue

        masked.append(line + ending)

    block_masked = _mask_indented_code_blocks("".join(masked))
    quote_masked = _mask_block_quote_code_blocks(block_masked)
    return _mask_inline_code_blocks(quote_masked)


def iter_markdown_destinations(path: Path):
    """Yield (line_number, destination) for inline Markdown links outside code."""
    text = path.read_text(encoding="utf-8")
    masked = _mask_markdown_code(text)

    block_start = 0
    separators = list(BLANK_LINE_RE.finditer(masked))
    for separator in separators + [None]:
        block_end = separator.start() if separator is not None else len(masked)
        block = masked[block_start:block_end]

        for position in _iter_inline_link_starts(block):
            parsed = _parse_destination(block, position)
            if parsed is not None:
                destination, _ = parsed
                absolute_position = block_start + position
                lineno = masked.count("\n", 0, absolute_position) + 1
                yield lineno, destination

        if separator is None:
            break
        block_start = separator.end()


def resolve_local_destination(root: Path, source: Path, destination: str):
    """Return (resolved_path, error) or (None, None) when destination is out of scope."""
    if not destination:
        return None, None

    destination = _decode_character_references(destination)
    if destination.startswith("#"):
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
