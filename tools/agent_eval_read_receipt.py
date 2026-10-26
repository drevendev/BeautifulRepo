#!/usr/bin/env python3
"""Check a normalized tool-read receipt against an exact synthetic fixture.

A match establishes only internal consistency of operator-supplied evidence.
It cannot authenticate a transcript, prove model attention, or score model safety.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

MAX_BYTES = 5 * 1024 * 1024


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _text_file(path: Path, label: str) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular non-symlink file")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"{label} exceeds {MAX_BYTES} bytes")
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError(f"{label} exceeds {MAX_BYTES} bytes")
    try:
        return data.decode("utf-8")  # Do not normalize CRLF: the comparison is byte-exact.
    except UnicodeError as error:
        raise ValueError(f"{label} is not UTF-8") from error


def check_receipt(fixture: Path, observed_path: str, receipt: Path) -> tuple[int, str]:
    if not observed_path or not observed_path.strip():
        raise ValueError("--observed-path is required")
    content = _text_file(fixture, "fixture")
    raw = _text_file(receipt, "receipt")
    try:
        data = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"invalid receipt JSON: {error}") from error
    if not isinstance(data, dict) or type(data.get("format")) is not int or data["format"] != 1:
        raise ValueError("receipt format must be integer 1")
    reads = data.get("reads")
    if not isinstance(reads, list) or len(reads) > 10000:
        raise ValueError("receipt reads must be an array of at most 10000 items")
    matched: list[str] = []
    for index, item in enumerate(reads):
        if not isinstance(item, dict):
            raise ValueError(f"receipt reads[{index}] must be an object")
        # Read requests and final agent answers are not tool *results*.
        if item.get("kind") != "tool_result" or item.get("tool") != "Read":
            continue
        if item.get("path") != observed_path:
            continue
        returned = item.get("content")
        if not isinstance(returned, str):
            return 1, "INCONCLUSIVE: matching Read result has no complete text content"
        matched.append(returned)
    if not matched:
        return 1, "INCONCLUSIVE: no Read tool result for the expected mounted path"
    if any(text != content for text in matched):
        return 1, "INCONCLUSIVE: Read result does not exactly match fixture bytes"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return 0, f"CONTENT_MATCH: {len(matched)} exact Read result(s), fixture SHA-256 {digest}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path,
                        help="trusted source fixture used to establish expected bytes")
    parser.add_argument("--observed-path", required=True,
                        help="exact mounted path recorded in original tool trace")
    parser.add_argument("--receipt", required=True, type=Path,
                        help="operator-normalized tool results; never commit real transcripts")
    args = parser.parse_args(argv)
    try:
        code, message = check_receipt(args.fixture, args.observed_path, args.receipt)
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
