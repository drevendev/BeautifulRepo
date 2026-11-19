#!/usr/bin/env python3
"""Check four illustrative before/after text colors using BeautifulRepo's calculator.

This verifies declared opaque sRGB pairs, NOT browser-computed styles or WCAG
conformance of a rendered page. The palette is original synthetic fixture data.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PAIRS = Path(__file__).with_name("pairs.json")


def contrast_module():
    """Load the repository's actual sibling tool even under python -I."""
    source = ROOT / "tools" / "color_contrast.py"
    spec = importlib.util.spec_from_file_location("beautifulrepo_color_contrast", source)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load the local contrast calculator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(rows: object, *, calculator=None) -> list[str]:
    """Require every example to describe an actual failing-to-passing change."""
    if calculator is None:
        calculator = contrast_module()
    if not isinstance(rows, list) or len(rows) != 4:
        raise ValueError("expected exactly four example pairs")
    expected_keys = {"name", "theme", "text", "level", "background", "before", "after"}
    results = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != expected_keys:
            raise ValueError("example row has missing or unexpected keys")
        if not all(isinstance(v, str) for v in row.values()):
            raise ValueError("example values must be strings")
        name = row["name"]
        if not name or name in seen:
            raise ValueError("example names must be nonempty and unique")
        seen.add(name)
        if row["theme"] not in {"light", "dark"}:
            raise ValueError("theme must be light or dark")
        threshold = calculator.THRESHOLDS.get((row["text"], row["level"]))
        if threshold is None:
            raise ValueError("unsupported WCAG text size or level")
        before = calculator.ratio(row["before"], row["background"])
        after = calculator.ratio(row["after"], row["background"])
        if before >= threshold or after < threshold:
            raise ValueError(f"{name}: this is not a failing-to-passing correction")
        results.append(
            f"{name} ({row['theme']}, {row['level']} {row['text']}): "
            f"{before:.3f}:1 FAIL -> {after:.3f}:1 PASS "
            f"(threshold {threshold:g}:1)"
        )
    return results


def reject_duplicate_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous object keys even in nested palette fixture rows."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key!r}")
        result[key] = value
    return result


def main() -> int:
    try:
        rows = json.loads(PAIRS.read_text(encoding="utf-8"),
                          object_pairs_hook=reject_duplicate_members)
        results = evaluate(rows)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: palette example cannot be verified: {error}", file=sys.stderr)
        return 2
    for line in results:
        print(line)
    print(f"OK: {len(results)} illustrative palette corrections pass declared numerical thresholds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
