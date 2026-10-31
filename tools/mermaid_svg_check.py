#!/usr/bin/env python3
"""Check captured Mermaid SVG ARIA ID references without rendering or network access.

This is a structural check of a user-saved SVG, not a browser or screen-reader test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

MAX_BYTES = 1_048_576
SVG_NS = "http://www.w3.org/2000/svg"


def element_name(tag: str) -> tuple[str, str]:
    if tag.startswith("{"):
        namespace, _, local = tag[1:].partition("}")
        return namespace, local
    return "", tag


def inspect_svg(raw: bytes) -> dict[str, object]:
    """Return observed SVG structure or raise ValueError on a failed contract."""
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("SVG input is empty or exceeds 1 MiB")
    if b"\0" in raw:
        raise ValueError("SVG must be UTF-8 without NUL bytes")
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("SVG must be valid UTF-8") from exc
    if "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
        raise ValueError("DTD and entity declarations are not accepted")
    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        raise ValueError("SVG XML is malformed") from exc
    namespace, local = element_name(root.tag)
    if local != "svg" or namespace not in ("", SVG_NS):
        raise ValueError("input must have an SVG root element")

    ids: dict[str, list[ET.Element]] = {}
    for element in root.iter():
        identifier = element.get("id")
        if identifier:
            ids.setdefault(identifier, []).append(element)

    observed: dict[str, object] = {
        "status": "STRUCTURE_PASS",
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    for attribute, expected_tag, output_key in (
        ("aria-labelledby", "title", "title"),
        ("aria-describedby", "desc", "description"),
    ):
        references = root.get(attribute, "").split()
        if not references or len(set(references)) != len(references):
            raise ValueError(f"{attribute} must contain unique, nonempty ID references")
        texts = []
        for identifier in references:
            matched = ids.get(identifier, [])
            if len(matched) != 1:
                raise ValueError(f"{attribute} reference is missing or ambiguous")
            node = matched[0]
            ns, name = element_name(node.tag)
            if (ns, name) != (namespace, expected_tag):
                raise ValueError(f"{attribute} must reference an SVG <{expected_tag}> element")
            content = " ".join("".join(node.itertext()).split())
            if not content:
                raise ValueError(f"{attribute} references an empty <{expected_tag}>")
            texts.append(content)
        observed[attribute] = references
        observed[output_key] = " ".join(texts)
    return observed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("svg", type=Path, help="explicitly saved rendered SVG (not a URL)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        if args.svg.is_symlink() or not args.svg.is_file():
            raise OSError("SVG path must be an ordinary file, not a symlink")
        if args.svg.stat().st_size > MAX_BYTES:
            raise ValueError("SVG input exceeds 1 MiB")
        result = inspect_svg(args.svg.read_bytes())
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read SVG: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    else:
        print("STRUCTURE_PASS: SVG ARIA references resolve to nonempty title/desc")
        print(f"SHA-256: {result['sha256']}")
        print(f"Title: {result['title']}")
        print(f"Description: {result['description']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
