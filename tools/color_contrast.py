#!/usr/bin/env python3
"""Report WCAG 2.2 text-contrast ratios for two opaque sRGB hex colors.

This is a color-pair calculator, not a rendered-page accessibility audit.
"""

from __future__ import annotations

import argparse
import json
import re

HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")
THRESHOLDS = {("normal", "AA"): 4.5, ("large", "AA"): 3.0,
              ("normal", "AAA"): 7.0, ("large", "AAA"): 4.5}


def parse_color(value: str) -> tuple[int, int, int]:
    """Accept only fully specified opaque #RRGGBB colors."""
    if not HEX_COLOR.fullmatch(value):
        raise ValueError("expected an opaque six-digit #RRGGBB color")
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def luminance(color: tuple[int, int, int]) -> float:
    def linear(channel: int) -> float:
        s = channel / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def ratio(foreground: str, background: str) -> float:
    first = luminance(parse_color(foreground))
    second = luminance(parse_color(background))
    light, dark = max(first, second), min(first, second)
    return (light + 0.05) / (dark + 0.05)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("foreground", help="opaque #RRGGBB text color")
    parser.add_argument("background", help="opaque #RRGGBB background color")
    parser.add_argument("--text", choices=("normal", "large"), default="normal")
    parser.add_argument("--level", choices=("AA", "AAA"), default="AA")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        computed = ratio(args.foreground, args.background)
    except ValueError as error:
        parser.error(str(error))
    required = THRESHOLDS[(args.text, args.level)]
    passed = computed >= required  # Never round before deciding a threshold.
    if args.format == "json":
        print(json.dumps({"ratio": computed, "threshold": required,
                          "text": args.text, "level": args.level, "passes": passed},
                         sort_keys=True))
    else:
        status = "PASS" if passed else "FAIL"
        print(f"Contrast {computed:.4f}:1; WCAG 2.2 {args.level} {args.text} text "
              f"(minimum {required:g}:1): {status}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
