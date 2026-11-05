#!/usr/bin/env python3
"""Capture real Chromium screenshots of the reproducible *synthetic* audit demo.

Chromium is an optional external executable, not a Python package dependency.
The capture is local evidence of a rendered fixture, not a user study or an
accessibility, privacy, security, or cross-browser certification.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

DEMO = Path(__file__).with_name("demo.py")
VIEWPORTS = {"desktop": (1280, 900), "mobile": (390, 844)}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def find_browser(requested: str | None) -> str:
    choices = (requested,) if requested else (
        "chromium", "chromium-browser", "google-chrome", "chrome",
    )
    for name in choices:
        browser = shutil.which(name)
        if browser:
            return browser
    raise RuntimeError("Chromium/Chrome executable not found; use --browser PATH")


def render_demo() -> str:
    """Generate HTML by executing the actual combined-audit example."""
    result = subprocess.run(
        [sys.executable, "-I", "-X", "utf8", str(DEMO), "--format", "html"],
        cwd=DEMO.parents[2], capture_output=True, text=True, encoding="utf-8",
        check=False, timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "synthetic checker demo did not complete: " + result.stderr.strip()[:240]
        )
    html = result.stdout
    if (not html.startswith("<!doctype html>")
            or "Synthetic Pocket Trails fixture." not in html
            or "0/2 local-link checks pass." not in html
            or "2/2 local-link checks pass." not in html):
        raise RuntimeError("the generated HTML lacks expected checker evidence")
    return html


def capture(browser: str, html: str, output_dir: Path,
            views: tuple[str, ...]) -> list[Path]:
    """Stage all files, then publish them only after every screenshot succeeds."""
    # tempfile may return a relative path when given a relative dir; file://
    # screenshots require absolute paths, including the documented ../output.
    output_dir = output_dir.expanduser().resolve(strict=False)
    filenames = ["report.html", *(f"{name}.png" for name in views)]
    if output_dir.exists() and not output_dir.is_dir():
        raise RuntimeError("output directory path is a file")
    if any((output_dir / name).exists() for name in filenames):
        raise RuntimeError("refusing to overwrite an existing report or screenshot")

    # Stage beside the destination to keep Windows cross-volume moves safe.
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
            prefix="beautifulrepo-capture-", dir=output_dir.parent) as temporary:
        staging = Path(temporary)
        source = staging / "report.html"
        source.write_text(html, encoding="utf-8")
        for name in views:
            width, height = VIEWPORTS[name]
            target = staging / f"{name}.png"
            cmd = [
                browser, "--headless", "--disable-gpu",
                "--hide-scrollbars", "--disable-background-networking",
                "--no-first-run", "--no-default-browser-check",
                "--force-device-scale-factor=1",
                f"--user-data-dir={staging / ('profile-' + name)}",
                f"--window-size={width},{height}",
                f"--screenshot={target}",
                source.as_uri(),
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace", check=False, timeout=60,
            )
            if (result.returncode != 0 or not target.is_file()
                    or target.stat().st_size < 32
                    or target.read_bytes()[:8] != PNG_SIGNATURE):
                raise RuntimeError(
                    f"{name} browser capture failed (exit {result.returncode}): "
                    + result.stderr.strip()[-240:]
                )
        output_dir.mkdir(parents=True, exist_ok=True)
        # Avoid replacing files created concurrently between preflight and publish.
        if any((output_dir / name).exists() for name in filenames):
            raise RuntimeError("output appeared during capture; refusing to overwrite")
        written = []
        for name in filenames:
            destination = output_dir / name
            (staging / name).replace(destination)
            written.append(destination)
        return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="destination for generated report.html and PNGs")
    parser.add_argument("--view", choices=("desktop", "mobile", "both"),
                        default="both", help="requested window size presets")
    parser.add_argument("--browser",
                        help="installed Chromium/Chrome executable or PATH lookup name")
    args = parser.parse_args(argv)
    views = tuple(VIEWPORTS) if args.view == "both" else (args.view,)
    try:
        browser = find_browser(args.browser)
        html = render_demo()
        results = capture(browser, html, args.output_dir, views)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"Capture incomplete: {exc}", file=sys.stderr)
        return 2
    for file in results:
        print(file)
    print("Synthetic fixture only. Inspect the PNGs and report before publication; "
          "window-size flags alone are not mobile/accessibility acceptance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
