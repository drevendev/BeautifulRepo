#!/usr/bin/env python3
"""Check local HTML links/assets and section fragments in repository Markdown.

Offline companion to docs_links.py. This is a bounded source check, not a
complete GitHub-Flavored Markdown renderer or a network accessibility audit.
"""
from __future__ import annotations

import argparse
from html import unescape
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

try:
    from . import docs_links
except ImportError:
    # Direct invocation. Load the sibling by path: `python -I` drops the script's
    # directory from sys.path, so a plain `import docs_links` would fail there.
    _SIBLING = Path(__file__).resolve().with_name("docs_links.py")
    docs_links = sys.modules.get("docs_links")
    if docs_links is None or Path(getattr(docs_links, "__file__", "")).resolve() != _SIBLING:
        _spec = importlib.util.spec_from_file_location("docs_links", _SIBLING)
        assert _spec is not None and _spec.loader is not None
        docs_links = importlib.util.module_from_spec(_spec)
        sys.modules["docs_links"] = docs_links
        _spec.loader.exec_module(docs_links)

HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+|$)(.*)$")
LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def srcset_urls(value: str) -> list[str]:
    """Collect srcset candidate URLs without splitting commas inside data URLs.

    This scans the HTML candidate boundaries (URL, optional descriptor, comma),
    but intentionally does not validate descriptors or image capabilities.
    """
    urls: list[str] = []
    index = 0
    while index < len(value):
        while index < len(value) and (value[index].isspace() or value[index] == ","):
            index += 1
        start = index
        while index < len(value) and not value[index].isspace():
            index += 1
        url = value[start:index]
        if not url:
            break
        end_of_candidate = url.endswith(",")
        url = url.rstrip(",")
        if url:
            urls.append(url)
        if end_of_candidate:
            continue
        # Skip descriptors through the next candidate delimiter. A comma within
        # CSS-style parentheses is not a descriptor separator.
        nesting = 0
        while index < len(value):
            char = value[index]
            if char == "(":
                nesting += 1
            elif char == ")" and nesting:
                nesting -= 1
            elif char == "," and not nesting:
                index += 1
                break
            index += 1
    return urls


class MarkupReferences(HTMLParser):
    """Collect active HTML destinations and explicit IDs with source lines."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[int, str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        identifier = attributes.get("id")
        if identifier:
            self.ids.add(identifier)
        named_anchor = attributes.get("name") if tag == "a" else None
        if named_anchor:
            self.ids.add(named_anchor)
        for attribute in (("href",) if tag == "a" else
                          ("src", "srcset") if tag in {"img", "source"} else ()):
            value = attributes.get(attribute)
            if not value:
                continue
            if attribute == "srcset":
                # Do not split on every comma: data: URLs contain literal commas.
                # A remote/data candidate must not hide a later local asset.
                for candidate in srcset_urls(value):
                    self.refs.append((self.getpos()[0], tag, candidate))
            else:
                self.refs.append((self.getpos()[0], tag, value))

    handle_startendtag = handle_starttag


def mask_escaped_html_openers(markdown: str) -> str:
    """Prevent Markdown backslash-escaped `<` from becoming live HTML.

    The existing code-region masker preserves line numbers; preserve them here too.
    An even-length run of preceding backslashes does not escape `<`.
    """
    chars = list(markdown)
    for index, char in enumerate(markdown):
        if char == "<" and docs_links._is_backslash_escaped(markdown, index):
            chars[index] = " "
    return "".join(chars)


def restore_heading_code(masked: str, original: str) -> str:
    """Keep inline code *text* in live headings without unmasking code blocks.

    docs_links masks code spans to prevent false active HTML links. GitHub's
    heading anchors nevertheless include the visible text within inline code.
    Restore matched backtick spans only for heading-slug normalization, never
    for scanning active HTML destinations.
    """
    restored = list(masked)
    position = 0
    while position < len(original):
        if original[position] != "`":
            position += 1
            continue
        run_end = position
        while run_end < len(original) and original[run_end] == "`":
            run_end += 1
        run_length = run_end - position
        if docs_links._is_backslash_escaped(original, position):
            position = run_end
            continue
        close = run_end
        matched = False
        while close < len(original):
            next_open = original.find("`", close)
            if next_open == -1:
                break
            next_end = next_open
            while next_end < len(original) and original[next_end] == "`":
                next_end += 1
            if next_end - next_open == run_length:
                for index in range(position, next_end):
                    if restored[index] == " ":
                        restored[index] = original[index]
                position = next_end
                matched = True
                break
            close = next_end
        if not matched:
            position = run_end
    return "".join(restored)


def protect_inline_code_angles(label: str) -> str:
    """Keep code-span text visible when stripping actual HTML heading tags.

    A code span like `<token>` contributes `token` to a GitHub heading slug;
    it is not an HTML tag to discard. Only paired equal-length backtick runs
    are considered, consistent with the code-region masking contract.
    """
    rendered = list(label)
    cursor = 0
    while cursor < len(label):
        if label[cursor] != "`":
            cursor += 1
            continue
        opening_end = cursor
        while opening_end < len(label) and label[opening_end] == "`":
            opening_end += 1
        length = opening_end - cursor
        if docs_links._is_backslash_escaped(label, cursor):
            cursor = opening_end
            continue
        next_at = opening_end
        while True:
            close = label.find("`", next_at)
            if close == -1:
                cursor = opening_end
                break
            closing_end = close
            while closing_end < len(label) and label[closing_end] == "`":
                closing_end += 1
            if closing_end - close == length:
                for position in range(opening_end, close):
                    if rendered[position] in "<>":
                        rendered[position] = ""
                cursor = closing_end
                break
            next_at = closing_end
    return "".join(rendered)


def _lines(text: str) -> list[str]:
    return [line.rstrip("\r\n") for line in docs_links.split_markdown_lines(text)]


def heading_ids(markdown_without_code: str, explicit_ids: set[str],
                original_markdown: str | None = None) -> set[str]:
    """Approximate GitHub's automatic ATX heading IDs with duplicate suffixes.

    We intentionally only claim ATX headings here, not every Markdown extension.
    Explicit HTML IDs are additionally supported by the HTML parser. The source
    heading restores visible inline-code text excluded from HTML destination scans.
    """
    found = set(explicit_ids)
    used_heading_ids: set[str] = set()
    original_lines = _lines(original_markdown or markdown_without_code)
    for line, original_line in zip(_lines(markdown_without_code), original_lines):
        match = HEADING.match(line)
        if match is not None and original_markdown is not None:
            line = restore_heading_code(line, original_line)
            match = HEADING.match(line)
        if match is None:
            continue
        label = match.group(1).strip().rstrip("#").strip()
        label = LINK.sub(r"\1", label)
        label = protect_inline_code_angles(label)
        label = unescape(label).lower()
        label = re.sub(r"<[^>]+>", "", label)
        label = "".join(char for char in label if char.isalnum() or char in " _-")
        slug = re.sub(r"[ \t]+", "-", label)
        if slug:
            candidate = slug
            suffix = 0
            while candidate in used_heading_ids:
                suffix += 1
                candidate = f"{slug}-{suffix}"
            used_heading_ids.add(candidate)
            found.add(candidate)
    return found


def check_repo(root: Path, exclude=()) -> tuple[list[str], int, int]:
    """Return (errors, checked_local_destinations, Markdown files inspected)."""
    root = root.resolve()
    errors: list[str] = []
    checked = 0
    inspected = 0
    parsed_files: dict[Path, tuple[set[str], list[tuple[int, str, str]]]] = {}

    def parse_document(path: Path) -> tuple[set[str], list[tuple[int, str, str]]]:
        if path not in parsed_files:
            content = path.read_text(encoding="utf-8")
            masked = mask_escaped_html_openers(docs_links._mask_markdown_code(content))
            markup = MarkupReferences()
            markup.feed(masked)
            parsed_files[path] = (heading_ids(masked, markup.ids, content), markup.refs)
        return parsed_files[path]

    for source in docs_links.iter_markdown_files(root, exclude):
        name = source.relative_to(root).as_posix()
        resolved_source, error = docs_links.resolve_markdown_source(root, source)
        if error:
            errors.append(f"{name}: invalid Markdown source location")
            continue
        inspected += 1
        try:
            _, refs = parse_document(resolved_source)
        except (OSError, UnicodeError):
            errors.append(f"{name}: cannot decode Markdown source")
            continue

        # HTML attributes and Markdown inline links share fragment validation.
        destinations = [(line, f"HTML {tag}", value) for line, tag, value in refs]
        destinations += [(line, "Markdown", value)
                         for line, value in docs_links.iter_markdown_destinations(resolved_source)]
        for line, kind, value in destinations:
            try:
                parsed = urlsplit(docs_links._decode_character_references(value))
            except ValueError:
                # Malformed remote URLs are outside the offline contract.
                continue
            if parsed.scheme or parsed.netloc:
                continue
            target, error = docs_links.resolve_local_destination(root, source, value)
            if target is None and error is None:
                if parsed.path:
                    continue
                target = resolved_source  # same-file #fragment link
            checked += 1
            if error:
                errors.append(f"{name}:{line}: {kind} {error}: {value!r}")
                continue
            assert target is not None
            if not target.is_file() and not target.is_dir():
                errors.append(f"{name}:{line}: missing {kind} destination: {value!r}")
                continue
            if parsed.fragment and target.suffix.lower() == ".md":
                try:
                    anchors, _ = parse_document(target)
                except (OSError, UnicodeError):
                    errors.append(f"{name}:{line}: cannot read anchor target: {value!r}")
                    continue
                fragment = unquote(parsed.fragment)
                if fragment.startswith("user-content-"):
                    fragment = fragment[len("user-content-"):]
                if fragment not in anchors:
                    errors.append(f"{name}:{line}: missing section anchor: {value!r}")

    return errors, checked, inspected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="repository root to scan (default: current directory)")
    docs_links.add_exclude_argument(parser)
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error("root must be an existing directory")
    errors, checked, inspected = check_repo(args.root, args.exclude)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"ERROR: {len(errors)} local HTML/fragment issue(s)", file=sys.stderr)
        return 1
    print(f"OK: {checked} local HTML/fragment destinations across {inspected} Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
