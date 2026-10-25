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
import unicodedata
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
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
TAG = re.compile(r"<[^>]+>")
# Backslash-escaped ASCII punctuation is set aside in a private-use range while links,
# tags and emphasis are removed, then restored as the literal character.
ESCAPED_PUNCTUATION = re.compile(r"\\([!-/:-@\[-`{-~])")
ESCAPE_BASE = 0xE000
SET_ASIDE = re.compile("[\uE021-\uE07E]")
# An underscore run opens emphasis only when not preceded by a letter or digit,
# and closes it only when not followed by one, so snake_case stays intact.
UNDERSCORE_EMPHASIS = re.compile(r"(?<![^\W_])(_+)(?=\S)(.+?)(?<=\S)\1(?![^\W_])")
CLOSING_HASHES = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")


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
        self.images_without_alt: list[int] = []
        self.duplicate_attributes: list[tuple[int, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # HTML's parser retains the first attribute of a repeated name, whereas
        # dict(attrs) retains the last. Follow the browser and report relevant
        # malformed duplicates so they cannot disguise a broken link or alt.
        attributes: dict[str, str | None] = {}
        for attribute, value in attrs:
            if attribute in attributes:
                if attribute in {"href", "src", "srcset", "alt", "id", "name"}:
                    self.duplicate_attributes.append((self.getpos()[0], tag, attribute))
                continue
            attributes[attribute] = value
        if tag == "img" and "alt" not in attributes:
            self.images_without_alt.append(self.getpos()[0])
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


def _lines(text: str) -> list[str]:
    return [line.rstrip("\r\n") for line in docs_links.split_markdown_lines(text)]


def _heading_segments(label: str) -> list[tuple[bool, str]]:
    """Split heading text into (is_code, text) parts at paired equal-length backtick runs."""
    segments: list[tuple[bool, str]] = []
    cursor = plain_start = 0
    while cursor < len(label):
        if label[cursor] != "`":
            cursor += 1
            continue
        opening_end = cursor
        while opening_end < len(label) and label[opening_end] == "`":
            opening_end += 1
        if docs_links._is_backslash_escaped(label, cursor):
            cursor = opening_end
            continue
        length = opening_end - cursor
        search = opening_end
        while True:
            close = label.find("`", search)
            if close == -1:
                cursor = opening_end
                break
            closing_end = close
            while closing_end < len(label) and label[closing_end] == "`":
                closing_end += 1
            if closing_end - close == length:
                code = label[opening_end:close]
                if len(code) > 2 and code[0] == code[-1] == " " and code.strip():
                    code = code[1:-1]
                segments.append((False, label[plain_start:cursor]))
                segments.append((True, code))
                cursor = plain_start = closing_end
                break
            search = closing_end
    segments.append((False, label[plain_start:]))
    return segments


def _rendered_text(markdown: str) -> str:
    """Approximate the visible text GitHub renders for non-code heading Markdown."""
    text = ESCAPED_PUNCTUATION.sub(lambda m: chr(ESCAPE_BASE + ord(m.group(1))), markdown)
    text = IMAGE.sub("", text)  # an image contributes no text, not even its alt
    text = LINK.sub(r"\1", text)
    text = TAG.sub("", text)  # tags and comments first, then entities
    previous = None
    while previous != text:
        previous, text = text, UNDERSCORE_EMPHASIS.sub(r"\2", text)
    text = SET_ASIDE.sub(lambda m: chr(ord(m.group()) - ESCAPE_BASE), text)
    return unescape(text)


def github_heading_slug(label: str) -> str:
    """Return the anchor GitHub generates for ATX heading text, before duplicate suffixes.

    GitHub lowercases the rendered text, removes every character that is not a
    letter, mark, decimal digit, connector punctuation, hyphen or space, and turns
    each space into a hyphen. Code-span text counts literally; images, tags and
    emphasis markers do not.
    """
    text = "".join(part if is_code else _rendered_text(part)
                   for is_code, part in _heading_segments(label))
    return "".join(char for char in text.lower() if _kept_in_slug(char)).replace(" ", "-")


def _kept_in_slug(char: str) -> bool:
    """Approximate the \\p{Word} class GitHub's Ruby regex keeps, plus hyphen and space.

    \\p{Word} is Alphabetic, marks, decimal digits and connector punctuation. Python
    has no Alphabetic property, so letters, letter numbers and the enclosed Latin
    letters (circled and squared) stand in for it.
    """
    if char in "- ":
        return True
    category = unicodedata.category(char)
    return (category[0] in "LM" or category in ("Nd", "Nl", "Pc")
            or "Ⓐ" <= char <= "ⓩ"  # circled A-Z and a-z
            or any(start <= ord(char) < start + 26  # squared, negative circled, negative squared
                   for start in (0x1F130, 0x1F150, 0x1F170)))


def heading_ids(markdown_without_code: str, explicit_ids: set[str],
                original_markdown: str | None = None) -> set[str]:
    """Approximate GitHub's automatic ATX heading IDs with duplicate suffixes.

    We intentionally only claim ATX headings here, not every Markdown extension.
    Explicit HTML IDs are additionally supported by the HTML parser. The masked
    copy decides which lines are headings (none inside code blocks); the text
    comes from the source line, so code spans and comments keep their effect.
    """
    found = set(explicit_ids)
    used_heading_ids: set[str] = set()
    original_lines = _lines(original_markdown or markdown_without_code)
    for line, original_line in zip(_lines(markdown_without_code), original_lines, strict=True):
        match = HEADING.match(line)
        if match is None:
            continue
        if original_markdown is not None:
            match = HEADING.match(original_line) or match
        label = CLOSING_HASHES.sub("", match.group(1).strip()).strip()
        slug = github_heading_slug(label)
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
    parsed_files: dict[Path, tuple[set[str], list[tuple[int, str, str]],
                                   list[int], list[tuple[int, str, str]]]] = {}
    names: dict = {}  # directory listings shared by every resolution in this scan

    def parse_document(path: Path) -> tuple[set[str], list[tuple[int, str, str]],
                                             list[int], list[tuple[int, str, str]]]:
        if path not in parsed_files:
            content = path.read_text(encoding="utf-8")
            masked = mask_escaped_html_openers(docs_links._mask_markdown_code(content))
            markup = MarkupReferences()
            markup.feed(masked)
            parsed_files[path] = (heading_ids(masked, markup.ids, content), markup.refs,
                                  markup.images_without_alt, markup.duplicate_attributes)
        return parsed_files[path]

    for source in docs_links.iter_markdown_files(root, exclude):
        name = source.relative_to(root).as_posix()
        resolved_source, error = docs_links.resolve_markdown_source(root, source, names)
        if error:
            errors.append(f"{name}: invalid Markdown source location")
            continue
        inspected += 1
        try:
            _, refs, images_without_alt, duplicate_attributes = parse_document(resolved_source)
        except (OSError, UnicodeError):
            errors.append(f"{name}: cannot decode Markdown source")
            continue

        for line, tag, attribute in duplicate_attributes:
            errors.append(f"{name}:{line}: HTML {tag} duplicate {attribute} attribute")

        # Unlike alt="", omitting alt leaves a raw HTML image without a text
        # alternative. An empty alt is valid for purely decorative images;
        # semantic suitability still needs human review.
        for line in images_without_alt:
            errors.append(f'{name}:{line}: HTML img missing alt attribute')

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
            target, error = docs_links.resolve_local_destination(root, source, value, names)
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
            if parsed.fragment and target.suffix.lower() in {".md", ".markdown"}:
                try:
                    anchors, _, _, _ = parse_document(target)
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
