#!/usr/bin/env python3
"""Record a real Chromium scroll of a generated *fictional* audit report.

This optional media-production helper requires Playwright for Python, its video
encoder and an installed Chrome/Chromium executable. None is needed by the
BeautifulRepo audit or normal CI. No tool is installed automatically.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import sys
import tempfile

MARKERS = (
    "Synthetic Pocket Trails fixture.",
    "0/2 local-link checks pass.",
    "2/2 local-link checks pass.",
    "-Read the [setup guide](docs/setup.md)",
    "+Read the [setup guide](docs/guide.md)",
)
VIEWPORT = (1280, 720)
FRAME_RATE = 15


def validate_report(source: str) -> None:
    """Reject inputs other than the expected standalone synthetic checker report."""
    if len(source.encode("utf-8")) > 2_000_000 or not source.startswith("<!doctype html>"):
        raise ValueError("expected a generated HTML report of at most 2 MB")
    for marker in MARKERS:
        if marker not in source:
            raise ValueError("missing synthetic checker evidence: " + marker)
    # This is not a general-purpose web-page recorder.
    if re.search(r"<\s*(?:script|iframe|object|embed)\b", source, re.I):
        raise ValueError("active content is not supported in the recording input")


def scroll_fraction(t: float) -> float:
    """Twenty-two-second story: overview, details, repair, back to overview."""
    if t < 3:
        return 0.0
    if t < 11:
        x = (t - 3) / 8
        return x * x * (3 - 2 * x)
    if t < 14:
        return 1.0
    if t < 19:
        x = (t - 14) / 5
        return 1 - x * x * (3 - 2 * x)
    return 0.0


def record(html: str, browser_path: str, output: Path) -> None:
    if output.suffix.lower() != ".webm":
        raise ValueError("output file must end in .webm")
    if output.exists():
        raise ValueError("refusing to overwrite existing recording")
    if not output.parent.is_dir():
        raise ValueError("output parent directory must already exist")
    try:
        from playwright.sync_api import sync_playwright, Error as PlaywrightError
    except ImportError as exc:
        raise RuntimeError("optional Playwright package is not installed") from exc

    try:
        with tempfile.TemporaryDirectory(prefix="br-showcase-video-") as temp:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    executable_path=browser_path, headless=True,
                    args=["--disable-background-networking", "--no-first-run",
                          "--no-default-browser-check"],
                )
                try:
                    context = browser.new_context(
                        viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]},
                        record_video_dir=temp,
                        record_video_size={"width": VIEWPORT[0], "height": VIEWPORT[1]},
                        offline=True, service_workers="block", reduced_motion="reduce",
                    )
                    page = context.new_page()
                    # No navigation to arbitrary files, remote assets or target code.
                    page.route("**/*", lambda route: route.abort())
                    page.set_content(html, wait_until="load")
                    if page.locator("h1").inner_text() != "One broken link, two independent checkers":
                        raise RuntimeError("rendered page does not match the synthetic report")
                    height = page.evaluate("document.documentElement.scrollHeight")
                    max_scroll = max(0, height - VIEWPORT[1])
                    video = page.video
                    for frame in range(22 * FRAME_RATE):
                        y = round(max_scroll * scroll_fraction(frame / FRAME_RATE))
                        page.evaluate("(y) => window.scrollTo(0, y)", y)
                        page.wait_for_timeout(round(1000 / FRAME_RATE))
                    context.close()
                    staged = Path(video.path())
                    if not staged.is_file() or staged.stat().st_size < 1024:
                        raise RuntimeError("Chromium did not generate a recording")
                    # Exclusive publication: never replace an existing recording.
                    with output.open("xb") as target, staged.open("rb") as source:
                        shutil.copyfileobj(source, target)
                finally:
                    browser.close()
    except PlaywrightError as exc:
        raise RuntimeError("Chrome/Playwright recording failed; check the optional "
                           "browser and Playwright video-encoder installation") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path,
                        help="generated synthetic report.html")
    parser.add_argument("--output", required=True, type=Path,
                        help="new WebM recording filename")
    parser.add_argument("--browser",
                        help="path/name of an installed Chrome/Chromium executable")
    args = parser.parse_args(argv)
    try:
        html = args.input.read_text(encoding="utf-8")
        validate_report(html)
        browser = shutil.which(args.browser) if args.browser else (
            shutil.which("chromium") or shutil.which("google-chrome")
            or shutil.which("chromium-browser")
        )
        if browser is None:
            raise RuntimeError("installed Chrome/Chromium not found; use --browser PATH")
        record(html, browser, args.output)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Recording incomplete: {exc}", file=sys.stderr)
        return 2
    print(args.output)
    print("Real Chromium recording of a FIXED SYNTHETIC HTML report. "
          "Not a live audit, user session, or accessibility test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
