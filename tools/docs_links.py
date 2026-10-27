#!/usr/bin/env python3
"""Check repository-owned relative destinations in Markdown files without network access."""
from __future__ import annotations

import argparse
import fnmatch
from html.entities import html5
import os
import re
import stat
import string
import sys
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote, urlsplit

# Version control and installed dependency trees are never repository-owned documentation.
SKIPPED_DIRECTORIES = frozenset({".git", "node_modules"})

# NTFS junctions redirect like directory symlinks, but lstat reports them only by tag.
JUNCTION_REPARSE_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)
MAX_LINK_HOPS = 40
# Windows reads a component such as "C:" or "c:file" as a drive; joining one would
# replace the repository root, so such a component is never joined.
DRIVE_PREFIX_RE = re.compile(r"^[A-Za-z]:")
ESCAPES_ROOT = "escapes repository root"
CASE_MISMATCH = "letter case differs from the name on disk (GitHub is case-sensitive)"
# Windows reserves these device names in every folder, with or without an extension.
WINDOWS_RESERVED_NAME_RE = re.compile(
    r"^(?:CON|PRN|AUX|NUL|COM[0-9\u00b9\u00b2\u00b3]|LPT[0-9\u00b9\u00b2\u00b3])(?:\..*)?$",
    re.IGNORECASE,
)

FENCE_RE = re.compile(r"^ {0,3}(?P<fence>\x60{3,}|~{3,})(?P<info>.*)$")
CLOSING_FENCE_RE = re.compile(r"^ {0,3}(?P<fence>\x60{3,}|~{3,})[ \t]*$")
LIST_MARKER_RE = re.compile(
    r"^(?P<marker>(?:[*+-]|[0-9]{1,9}[.)]))(?P<padding>[ \t]+)(?P<body>.*)$"
)
EMPTY_LIST_MARKER_RE = re.compile(
    r"^(?P<marker>(?:[*+-]|[0-9]{1,9}[.)]))[ \t]*$"
)
ATX_HEADING_RE = re.compile(r"^#{1,6}(?:[ \t]+|$)")
SETEXT_UNDERLINE_RE = re.compile(r"^(?:=+|-+)[ \t]*$")
THEMATIC_BREAK_RE = re.compile(
    r"^(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})$"
)
BLOCK_QUOTE_RE = re.compile(r"^>[ \t]?")
TYPE1_HTML_BLOCK_OPEN_RE = re.compile(
    r"^ {0,3}<(?P<tag>script|pre|style)(?=[ \t>]|$)", re.IGNORECASE
)
TYPE1_HTML_BLOCK_CLOSE_RE = re.compile(
    r"</(?:script|pre|style)>", re.IGNORECASE
)
TYPE2_HTML_COMMENT_OPEN_RE = re.compile(r"^ {0,3}<!--")
TYPE2_HTML_COMMENT_CLOSE_RE = re.compile(r"-->")
MARKDOWN_WHITESPACE = " \t\r\n"
# cmark-gfm stops reading a bare link destination at its 33rd unclosed '(' (see
# manual_scan_link_url_2), and CommonMark allows such a limit. It also keeps
# lines full of "[a](" from costing one scan to the end of the line per link.
MAX_DESTINATION_PARENS = 32
BLANK_LINE_RE = re.compile(r"\r?\n[ \t]*\r?\n")
MARKDOWN_LINE_END_RE = re.compile(r"(?<=\n)|(?<=\r)(?!\n)")
INLINE_HTML_COMMENT_RE = re.compile(
    r"<!--(?!>|->)(?:(?!--).)*?-->", re.DOTALL
)
CHARACTER_REFERENCE_RE = re.compile(
    r"&(?:#(?P<dec>[0-9]{1,7})|#[xX](?P<hex>[0-9A-Fa-f]{1,6})|(?P<named>[A-Za-z][A-Za-z0-9]*));"
)


def split_markdown_lines(text: str) -> list[str]:
    """Split after each Markdown line ending (\\n, \\r\\n or \\r), keeping the ending.

    str.splitlines also breaks at \\f, \\v, \\x1c-\\x1e, \\x85, U+2028 and U+2029,
    which Markdown treats as ordinary characters. A masked copy that blanks them
    would then have fewer lines than its source.
    """
    parts = MARKDOWN_LINE_END_RE.split(text)
    if parts and parts[-1] == "":
        parts.pop()
    return parts


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
    """Yield destination start indices for inline links with balanced link text.

    One pass pairs every unescaped '[' with its closing ']' through a stack, so text
    full of unmatched brackets costs linear time instead of a rescan per bracket.
    """
    opened: list[int] = []
    starts: list[int] = []
    closing: dict[int, int] = {}
    position = 0
    while position < len(line):
        char = line[position]
        if char == "\\" and position + 1 < len(line) and line[position + 1] in string.punctuation:
            position += 2
            continue
        if char == "[":
            opened.append(position)
            starts.append(position)
        elif char == "]" and opened:
            closing[opened.pop()] = position
        position += 1

    for start in starts:
        close = closing.get(start)
        if close is not None and close + 1 < len(line) and line[close + 1] == "(":
            destination = close + 2
            while destination < len(line) and line[destination] in MARKDOWN_WHITESPACE:
                destination += 1
            yield destination


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
            if depth > MAX_DESTINATION_PARENS:
                return None
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


def _mask_inline_html_comments(text: str) -> str:
    """Mask valid inline HTML comments only inside their Markdown block.

    Prefer reporting a questionable link over suppressing a real one: never mask
    across paragraph, heading, list, or block-quote boundaries.
    """
    masked = list(text)
    segment_start = 0
    offset = 0
    previous_quote_depth = 0

    def mask_segment(start: int, end: int) -> None:
        for match in INLINE_HTML_COMMENT_RE.finditer(text, start, end):
            if _is_backslash_escaped(text, match.start()):
                continue
            for index in range(match.start(), match.end()):
                if masked[index] not in "\r\n":
                    masked[index] = " "

    for raw_line in split_markdown_lines(text):
        line = raw_line.rstrip("\r\n")
        quote_depth = 0
        body = line
        while True:
            start = _block_quote_content_start(body)
            if start is None:
                break
            quote_depth += 1
            body = body[start:]

        blank = not body.strip(" \t")
        indent, index = _leading_indent_columns(body)
        stripped = body[index:]
        single_line_block = indent <= 3 and bool(
            ATX_HEADING_RE.match(stripped)
            or SETEXT_UNDERLINE_RE.match(stripped)
            or THEMATIC_BREAK_RE.match(stripped)
        )
        starts_new_block = (
            single_line_block or _list_item_interrupts_paragraph(body)
        )

        if blank or quote_depth != previous_quote_depth or starts_new_block:
            mask_segment(segment_start, offset)
            segment_start = offset + (len(raw_line) if blank else 0)

        offset += len(raw_line)
        if single_line_block:
            mask_segment(segment_start, offset)
            segment_start = offset
        previous_quote_depth = 0 if blank else quote_depth

    mask_segment(segment_start, len(text))
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


def _list_item_details(line: str, base_indent: int = 0):
    """Return (content column, body index) for a list marker in one container."""
    indent, index = _leading_indent_columns(line)
    if indent < base_indent or indent - base_indent > 3:
        return None

    remainder = line[index:]
    match = LIST_MARKER_RE.match(remainder)
    if match is not None:
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

        return column, index + match.start("body")

    empty = EMPTY_LIST_MARKER_RE.match(remainder)
    if empty is not None:
        return indent + len(empty.group("marker")) + 1, len(line)

    return None


def _list_item_content_indent(line: str, base_indent: int = 0):
    """Return the absolute content column for a list marker, or None."""
    details = _list_item_details(line, base_indent)
    return details[0] if details is not None else None


def _list_item_interrupts_paragraph(line: str) -> bool:
    """Return whether this list marker may interrupt an open GFM paragraph."""
    indent, index = _leading_indent_columns(line)
    if indent > 3:
        return False

    match = LIST_MARKER_RE.match(line[index:])
    if match is None or not match.group("body").strip():
        return False

    marker = match.group("marker")
    if marker[0].isdigit():
        return int(marker[:-1]) == 1
    return True


def _consume_indent_columns(line: str, columns: int):
    """Return (prefix index, residual columns) after removing visual indentation."""
    visual = 0
    index = 0
    while index < len(line) and visual < columns:
        char = line[index]
        if char == " ":
            visual += 1
        elif char == "\t":
            visual += 4 - (visual % 4)
        else:
            break
        index += 1
    if visual < columns:
        return None
    return index, visual - columns


def _mask_list_item_code_blocks(text: str) -> str:
    """Mask code inside explicit list-item containers before root-level fence parsing."""
    lines = split_markdown_lines(text)
    masked = []
    index = 0
    paragraph_open = False
    while index < len(lines):
        raw_line = lines[index]
        if raw_line.endswith("\r\n"):
            line, ending = raw_line[:-2], "\r\n"
        elif raw_line.endswith(("\n", "\r")):
            line, ending = raw_line[:-1], raw_line[-1]
        else:
            line, ending = raw_line, ""

        if not line.strip(" \t"):
            masked.append(raw_line)
            paragraph_open = False
            index += 1
            continue

        details = _list_item_details(line)
        if details is None:
            indent, _ = _leading_indent_columns(line)
            opening = FENCE_RE.match(line)
            valid_fence = opening is not None and (
                opening.group("fence")[0] != "`" or "`" not in opening.group("info")
            )
            if valid_fence or _starts_nonparagraph_block(line):
                paragraph_open = False
            elif indent < 4 or paragraph_open:
                paragraph_open = True
            masked.append(raw_line)
            index += 1
            continue

        if paragraph_open and not _list_item_interrupts_paragraph(line):
            masked.append(raw_line)
            index += 1
            continue

        content_indent, body_index = details
        prefixes = [line[:body_index]]
        residuals = [0]
        inner_parts = [line[body_index:] + ending]
        inner_lengths = [len(inner_parts[-1])]
        index += 1
        while index < len(lines):
            raw_line = lines[index]
            if raw_line.endswith("\r\n"):
                line, ending = raw_line[:-2], "\r\n"
            elif raw_line.endswith(("\n", "\r")):
                line, ending = raw_line[:-1], raw_line[-1]
            else:
                line, ending = raw_line, ""
            if not line.strip(" \t"):
                prefixes.append(line)
                residuals.append(0)
                inner_parts.append(ending)
                inner_lengths.append(len(ending))
                index += 1
                continue
            indent, _ = _leading_indent_columns(line)
            if indent < content_indent:
                break
            consumed = _consume_indent_columns(line, content_indent)
            if consumed is None:
                break
            prefix_index, residual = consumed
            inner = " " * residual + line[prefix_index:] + ending
            prefixes.append(line[:prefix_index])
            residuals.append(residual)
            inner_parts.append(inner)
            inner_lengths.append(len(inner))
            index += 1
        inner_masked = _mask_markdown_code("".join(inner_parts))
        offset = 0
        for prefix, residual, inner_length in zip(prefixes, residuals, inner_lengths, strict=True):
            piece = inner_masked[offset:offset + inner_length]
            offset += inner_length
            masked.append(prefix + piece[residual:])
        paragraph_open = False
    return "".join(masked)


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

    for raw_line in split_markdown_lines(text):
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
    lines = split_markdown_lines(text)
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
        for prefix, content_length in zip(prefixes, content_lengths, strict=True):
            masked.append(prefix + inner_masked[offset:offset + content_length])
            offset += content_length

    return "".join(masked)



def _mask_fenced_and_type1_html_blocks(text: str) -> str:
    """Mask fenced code and GFM type-1/type-2 raw HTML in source order."""
    masked = []
    fence_char = None
    fence_length = 0
    in_type1_html = False
    in_type2_comment = False

    for raw_line in split_markdown_lines(text):
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

        if in_type1_html:
            masked.append(" " * len(line) + ending)
            if TYPE1_HTML_BLOCK_CLOSE_RE.search(line):
                in_type1_html = False
            continue

        if in_type2_comment:
            masked.append(" " * len(line) + ending)
            if TYPE2_HTML_COMMENT_CLOSE_RE.search(line):
                in_type2_comment = False
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

        if TYPE1_HTML_BLOCK_OPEN_RE.match(line):
            masked.append(" " * len(line) + ending)
            if not TYPE1_HTML_BLOCK_CLOSE_RE.search(line):
                in_type1_html = True
            continue

        if TYPE2_HTML_COMMENT_OPEN_RE.match(line):
            masked.append(" " * len(line) + ending)
            if not TYPE2_HTML_COMMENT_CLOSE_RE.search(line):
                in_type2_comment = True
            continue

        masked.append(line + ending)

    return "".join(masked)


def _mask_markdown_code(text: str) -> str:
    """Mask fenced, indented, raw-HTML and inline GFM literal regions."""
    text = _mask_list_item_code_blocks(text)
    block_masked = _mask_fenced_and_type1_html_blocks(text)
    indented_masked = _mask_indented_code_blocks(block_masked)
    quote_masked = _mask_block_quote_code_blocks(indented_masked)
    return _mask_inline_html_comments(_mask_inline_code_blocks(quote_masked))


# Bounded, one-line GFM reference definitions. Multiline definitions and
# definitions nested in lists/quotes are intentionally not interpreted here.
REFERENCE_DEFINITION_RE = re.compile(
    r"^ {0,3}\[(?P<label>(?:\\.|[^\[\]\\\r\n])+)\]:[ \t]*"
    r"(?P<target><(?:\\.|[^<>\r\n])*>|(?:\\.|[^\s\r\n])+)"
    r"(?:[ \t]+(?:\"(?:\\.|[^\"\\\r\n])*\"|'(?:\\.|[^'\\\r\n])*'|\((?:\\.|[^()\\\r\n])*\)))?[ \t]*$"
)
REFERENCE_USE_RE = re.compile(
    r"!?\[(?P<text>(?:\\.|[^\[\]\\\r\n])+)\]"
    r"(?:\[(?P<label>(?:\\.|[^\[\]\\\r\n])*)\])?"
)


def _normalize_reference_label(label: str) -> str:
    """GFM label matching folds case and collapses whitespace."""
    return " ".join(label.split()).casefold()


def _unescape_reference_destination(value: str) -> str:
    """Decode GFM backslash punctuation escapes (entities resolve later)."""
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1]
    unescaped = []
    position = 0
    while position < len(value):
        if (value[position] == "\\" and position + 1 < len(value)
                and value[position + 1] in string.punctuation):
            unescaped.append(value[position + 1])
            position += 2
        else:
            unescaped.append(value[position])
            position += 1
    return "".join(unescaped)


def _extract_reference_definitions(masked: str):
    """Return definitions and a same-size source with definitions blanked.

    Recognize single-line definitions only at a block start; paragraph text
    must not create a link definition. Earlier definitions take precedence.
    """
    definitions = {}
    remaining = []
    at_block_start = True
    for raw_line in split_markdown_lines(masked):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        match = REFERENCE_DEFINITION_RE.fullmatch(line) if at_block_start else None
        if match is not None and _normalize_reference_label(match.group("label")):
            label = _normalize_reference_label(match.group("label"))
            definitions.setdefault(
                label, _unescape_reference_destination(match.group("target"))
            )
            remaining.append(" " * len(line) + ending)
            at_block_start = True
            continue

        remaining.append(raw_line)
        at_block_start = (not line.strip() or
                          bool(re.match(r"^ {0,3}#{1,6}(?:[ \t]|$)", line)))

    return definitions, "".join(remaining)


def _iter_reference_uses(masked: str, definitions: dict[str, str]):
    """Yield (source line, destination) for used local or remote references."""
    for lineno, raw_line in enumerate(split_markdown_lines(masked), 1):
        line = raw_line.rstrip("\r\n")
        # An inline destination can itself contain brackets. Avoid treating
        # those as shortcut references to a separate definition.
        active = list(line)
        for start in _iter_inline_link_starts(line):
            parsed = _parse_destination(line, start)
            if parsed is not None:
                _, end = parsed
                for index in range(start, min(end, len(active))):
                    active[index] = " "
        visible = "".join(active)
        for match in REFERENCE_USE_RE.finditer(visible):
            if (_is_backslash_escaped(visible, match.start())
                    or (match.start() > 0 and visible[match.start() - 1] == "[")):
                continue
            if (match.group("label") is None and match.end() < len(visible)
                    and visible[match.end()] in "(["):
                # Inline link or nested bracket syntax, not a shortcut.
                continue
            label = match.group("label") or match.group("text")
            destination = definitions.get(_normalize_reference_label(label))
            if destination is not None:
                yield lineno, destination


def iter_markdown_destinations(path: Path):
    """Yield local and remote destinations from inline and bounded reference links."""
    text = path.read_text(encoding="utf-8")
    masked = _mask_markdown_code(text)
    definitions, visible = _extract_reference_definitions(masked)

    block_start = 0
    separators = list(BLANK_LINE_RE.finditer(visible))
    for separator in separators + [None]:
        block_end = separator.start() if separator is not None else len(visible)
        block = visible[block_start:block_end]

        for position in _iter_inline_link_starts(block):
            parsed = _parse_destination(block, position)
            if parsed is not None:
                destination, _ = parsed
                absolute_position = block_start + position
                lineno = visible.count("\n", 0, absolute_position) + 1
                yield lineno, destination

        if separator is None:
            break
        block_start = separator.end()

    yield from _iter_reference_uses(visible, definitions)


def _is_redirect(info: os.stat_result) -> bool:
    """Return True for a symbolic link or an NTFS junction, which lstat does not follow."""
    return (stat.S_ISLNK(info.st_mode)
            or getattr(info, "st_reparse_tag", 0) == JUNCTION_REPARSE_TAG)


def _split_parts(text: str, separators: str) -> list[str]:
    return [part for part in re.split(f"[{re.escape(separators)}]", text)
            if part not in ("", ".")]


def _parts_under(root: str, absolute: str, windows: bool):
    """Return ``(True, parts)`` when ``absolute`` names a path under ``root``, else None."""
    separators = "\\/" if windows else "/"
    base = root.rstrip(separators)
    head, rest = absolute[:len(base)], absolute[len(base):]
    if windows:
        same = head.replace("/", "\\").lower() == base.replace("/", "\\").lower()
    else:
        same = head == base
    if not same or (rest and rest[0] not in separators):
        return None
    return True, _split_parts(rest, separators)


def link_target_parts(root: str, target: str, windows: bool = os.name == "nt"):
    """Classify a symbolic link or junction target by its text alone.

    Return ``(from_root, parts)``: the components to follow next, either from the
    repository root or from the link's own directory. Return None for a target
    outside ``root``, including another drive, a UNC network share or a device.
    Such a target is reported, never opened.
    """
    if not windows:
        if target.startswith("/"):
            return _parts_under(root, target, windows)
        return False, _split_parts(target, "/")
    if target.startswith("\\\\?\\") and not target.upper().startswith("\\\\?\\UNC\\"):
        target = target[4:]  # Win32 long-path prefix in front of a drive path
    anchor = PureWindowsPath(target)
    if not anchor.drive and not anchor.root:
        return False, _split_parts(target, "\\/")
    if anchor.drive.startswith(("\\", "/")) or not (anchor.drive and anchor.root):
        return None  # UNC share, device, drive-relative or current-drive path
    return _parts_under(root, target, windows)


def _entry_names(directory: Path, names: dict | None):
    """Return the exact names in ``directory`` (None if unreadable), cached in ``names``."""
    key = os.fspath(directory)
    if names is not None and key in names:
        return names[key]
    try:
        with os.scandir(directory) as entries:
            found = frozenset(entry.name for entry in entries)
    except OSError:
        found = None
    if names is not None:
        names[key] = found
    return found


def _non_portable_reason(path: str):
    """Return why a decoded destination path would not work everywhere, or None.

    Checked as text before any filesystem call: on Windows a backslash or a drive
    prefix turns a "relative" path into another drive, a UNC network share or a
    device, and the other cases name a file Windows cannot check out or opens as
    something else. None of them works in GitHub's rendering of the file either.
    """
    if "\\" in path:
        return "backslash"
    for part in path.split("/"):
        if part in ("", ".", ".."):
            continue
        if ":" in part:
            return "drive letter or colon"
        if part.endswith((".", " ")):
            return "trailing dot or space"
        if WINDOWS_RESERVED_NAME_RE.match(part):
            return "Windows reserved name"
    return None


def _follow_within_root(root: Path, parts, names: dict | None = None):
    """Follow root-relative ``parts`` like the filesystem would, without leaving ``root``.

    Return (path, None) or (None, error). Every filesystem call is an lstat,
    readlink or directory listing of an entry already known to be inside
    ``root``: link targets are checked as text before they are followed. Each
    name must match its directory entry exactly, as on a case-sensitive file
    system. Once an entry is missing, the remaining parts are joined lexically
    and the returned path does not exist. ``names`` caches directory listings.
    """
    pending = list(parts)
    current = root
    hops = 0
    missing = False
    while pending:
        part = pending.pop(0)
        if part == "..":
            if current == root:
                return None, ESCAPES_ROOT
            current = current.parent
            continue
        if os.name == "nt" and DRIVE_PREFIX_RE.match(part):
            return None, ESCAPES_ROOT
        candidate = current / part
        if missing:
            current = candidate
            continue
        listing = _entry_names(current, names)
        if listing is not None and part not in listing:
            folded = part.casefold()
            if any(name.casefold() == folded for name in listing):
                return None, CASE_MISMATCH
            missing = True
            current = candidate
            continue
        try:
            info = os.lstat(candidate)
        except (OSError, ValueError):
            missing = True
            current = candidate
            continue
        if not _is_redirect(info):
            current = candidate
            continue
        hops += 1
        if hops > MAX_LINK_HOPS:
            return None, "too many levels of symbolic links"
        try:
            target = os.readlink(candidate)
        except (OSError, ValueError):
            return None, "cannot read symbolic link"
        followed = link_target_parts(str(root), target)
        if followed is None:
            return None, ESCAPES_ROOT
        from_root, target_parts = followed
        if from_root:
            current = root
        pending[:0] = target_parts
    return current, None


def resolve_markdown_source(root: Path, path: Path, names: dict | None = None):
    """Return (real_path, None) for a Markdown file found under ``root``, or (None, error).

    ``root`` must already be resolved. The error is ESCAPES_ROOT when the file or a
    link on its way points outside ``root``.
    """
    resolved, error = _follow_within_root(root, path.relative_to(root).parts, names)
    if error:
        return None, error
    if not resolved.is_file():
        return None, "cannot resolve"
    return resolved, None


def resolve_local_destination(root: Path, source: Path, destination: str,
                              names: dict | None = None):
    """Return (resolved_path, error) or (None, None) when destination is out of scope.

    Pass the same ``names`` dict for every call in one scan to reuse directory listings.
    """
    if not destination:
        return None, None

    destination = _decode_character_references(destination)
    if destination.startswith("#"):
        return None, None

    try:
        parsed = urlsplit(destination)
    except ValueError:
        # Malformed remote URL authorities are out of scope for local-link checks.
        # In particular, unmatched IPv6 brackets must not abort the scan.
        return None, None
    if parsed.scheme or parsed.netloc:
        return None, None

    raw_path = unquote(parsed.path)
    if not raw_path:
        return None, None
    if "\x00" in raw_path:
        return None, "invalid relative destination"
    reason = _non_portable_reason(raw_path)
    if reason:
        return None, f"non-portable destination ({reason})"

    root = root.resolve()
    if raw_path.startswith("/"):
        base = ()
    else:
        try:
            base = source.parent.relative_to(root).parts
        except ValueError:
            return None, ESCAPES_ROOT
    return _follow_within_root(root, [*base, *_split_parts(raw_path, "/")], names)


def normalize_exclude(pattern: str) -> str:
    """Return a root-relative POSIX glob without surrounding space, ``./`` or trailing ``/``."""
    pattern = pattern.strip().replace("\\", "/")
    while pattern.startswith("./"):
        pattern = pattern[2:]
    return pattern.rstrip("/")


def iter_markdown_files(root: Path, exclude=()) -> list[Path]:
    """Sorted Markdown sources under root, without skipped or excluded paths.

    Each ``exclude`` glob is matched case-sensitively against root-relative POSIX
    paths of directories and files; a matching directory is not descended into.
    Excluded files can still be link destinations.

    Symbolic links and junctions are never followed here, not even to ask whether
    they point at a directory. A link named ``*.md`` or ``*.markdown`` is listed, and
    ``resolve_markdown_source`` decides where it leads.
    """
    patterns = [pattern for pattern in map(normalize_exclude, exclude) if pattern]

    def excluded(relative: str) -> bool:
        return any(fnmatch.fnmatchcase(relative, pattern) for pattern in patterns)

    found = []
    pending = [root]
    while pending:
        directory = pending.pop()
        relative_dir = directory.relative_to(root).as_posix()
        prefix = "" if relative_dir == "." else f"{relative_dir}/"
        try:
            with os.scandir(directory) as entries:
                names = [entry.name for entry in entries]
        except OSError:
            continue
        for name in names:
            try:
                # os.lstat, unlike DirEntry, reports junction reparse tags on every version.
                info = os.lstat(directory / name)
            except OSError:
                continue
            if stat.S_ISDIR(info.st_mode) and not _is_redirect(info):
                if name not in SKIPPED_DIRECTORIES and not excluded(prefix + name):
                    pending.append(directory / name)
            elif (not excluded(prefix + name)
                  and (fnmatch.fnmatch(name, "*.md")
                       or fnmatch.fnmatch(name, "*.markdown"))):
                found.append(directory / name)
    return sorted(found)


def add_exclude_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="skip Markdown sources whose root-relative path or parent directory matches "
             "(repeatable); .git and node_modules are always skipped",
    )


def check_repo(root: Path, exclude=()):
    """Return (errors, checked_destinations, markdown_files)."""
    root = root.resolve()
    errors = []
    checked = 0
    markdown_files = 0
    names: dict = {}

    for path in iter_markdown_files(root, exclude):
        markdown_files += 1
        relative_source = path.relative_to(root).as_posix()
        source_target, error = resolve_markdown_source(root, path, names)
        if error == ESCAPES_ROOT:
            errors.append(f"{relative_source}: Markdown source escapes repository root")
            continue
        if error:
            errors.append(f"{relative_source}: cannot resolve Markdown source")
            continue

        try:
            for lineno, destination in iter_markdown_destinations(source_target):
                resolved, error = resolve_local_destination(root, path, destination, names)
                if resolved is None and error is None:
                    continue
                checked += 1
                if error:
                    errors.append(f"{relative_source}:{lineno}: {error}: {destination!r}")
                elif not resolved.exists():
                    errors.append(
                        f"{relative_source}:{lineno}: missing relative destination: {destination!r}"
                    )
        except UnicodeDecodeError as exc:
            errors.append(f"{relative_source}: invalid UTF-8 Markdown: {exc}")
        except OSError:
            errors.append(f"{relative_source}: cannot read Markdown source")

    return errors, checked, markdown_files


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check repository-owned relative Markdown link and image destinations."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root to scan (default: current directory)",
    )
    add_exclude_argument(parser)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")

    errors, checked, markdown_files = check_repo(root, args.exclude)
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
