#!/usr/bin/env python3
"""Make a local, captioned playback page for a real synthetic-audit recording.

Requires only the standard library. This does NOT record a browser, verify that
subtitles render, or publish media; it packages already-produced local evidence.
"""
from __future__ import annotations

import argparse
import base64
from html import escape
from pathlib import Path
import re
import sys

STAMP = re.compile(r"^([0-9]{2}):([0-9]{2}):([0-9]{2})\.([0-9]{3})$")
CUE = re.compile(r"^(\S+) --> (\S+)$")


def seconds(stamp: str) -> float:
    match = STAMP.fullmatch(stamp)
    if match is None:
        raise ValueError("unsupported WebVTT timestamp")
    hours, minutes, secs, millis = map(int, match.groups())
    if minutes >= 60 or secs >= 60:
        raise ValueError("invalid WebVTT timestamp")
    return 3600 * hours + 60 * minutes + secs + millis / 1000


def cues(vtt: str) -> list[tuple[str, str]]:
    """Validate the plain, authored WebVTT shape used by this walkthrough."""
    if not vtt.startswith("WEBVTT\n") or len(vtt.encode("utf-8")) > 64_000:
        raise ValueError("expected a small UTF-8 WebVTT file")
    pairs: list[tuple[str, str]] = []
    last_end = 0.0
    for block in re.split(r"\n\s*\n", vtt.strip())[1:]:
        if block.startswith("NOTE"):
            continue
        lines = block.splitlines()
        match = CUE.fullmatch(lines[0]) if lines else None
        if match is None or len(lines) < 2 or not all(line.strip() for line in lines[1:]):
            raise ValueError("expected simple timed WebVTT cues")
        begin, end = seconds(match[1]), seconds(match[2])
        if begin < last_end or end <= begin:
            raise ValueError("WebVTT cues must be ordered and non-overlapping")
        last_end = end
        pairs.append((lines[0], " ".join(lines[1:])))
    if not pairs:
        raise ValueError("no descriptive WebVTT cues found")
    return pairs


def build_player(video: Path, vtt: str) -> str:
    descriptions = cues(vtt)
    # Embed the caption file, not its instructions, into an inert data URL. This
    # avoids browser file:// cross-origin handling of a separate .vtt resource.
    track_url = "data:text/vtt;base64," + base64.b64encode(vtt.encode("utf-8")).decode("ascii")
    filename = escape(video.name, quote=True)
    transcript = "\n".join(
        f"      <li><time>{escape(timing)}</time> {escape(description)}</li>"
        for timing, description in descriptions
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pocket Trails — synthetic audit recording</title>
  <style>
    body {{ font: 1rem/1.6 system-ui, sans-serif; max-width: 60rem;
           margin: 2rem auto; padding: 0 1rem; color: CanvasText; background: Canvas; }}
    video {{ display: block; width: 100%; max-width: 100%; background: #111; }}
    :focus-visible {{ outline: 3px solid #087cc2; outline-offset: 3px; }}
    time {{ font-variant-numeric: tabular-nums; }}
    li {{ padding-bottom: .55rem; }}
  </style>
</head>
<body>
  <main>
    <h1>One broken README link, two checks</h1>
    <p><strong>Synthetic Pocket Trails demonstration.</strong> This is a recording
       of a fictional, locally generated audit report, not a real repository
       repair or a user session. There is no spoken audio.</p>
    <video controls playsinline preload="metadata" aria-describedby="video-help">
      <source src="{filename}" type="video/webm">
      <track kind="captions" src="{track_url}" srclang="en"
             label="English visual descriptions (not speech)" default>
      Your browser does not support HTML video. Read the scene descriptions below.
    </video>
    <p id="video-help">Enable captions in the video controls to see the authored
       visual descriptions. If local playback is blocked, serve this directory
       with a local-only HTTP server. No external service is required.
       Captions and playback accessibility have not been independently certified.</p>
    <h2>Text alternative: scene descriptions</h2>
    <ol>
{transcript}
    </ol>
    <p>Source evidence and reproduction instructions:
       <a href="https://github.com/drevendev/BeautifulRepo/blob/master/SHOWCASE.md">BeautifulRepo showcase</a>.
       This link is optional; local playback does not fetch it.</p>
  </main>
</body>
</html>
"""


def make_player(video: Path, captions: Path, output: Path) -> None:
    if video.suffix.lower() != ".webm" or not video.is_file() or video.stat().st_size < 1024:
        raise ValueError("expected a nonempty existing .webm recording")
    with video.open("rb") as source:
        if source.read(4) != b"\x1a\x45\xdf\xa3":
            raise ValueError("expected WebM EBML header (not a full media validation)")
    if captions.suffix.lower() != ".vtt" or not captions.is_file():
        raise ValueError("expected an existing .vtt caption file")
    if output.suffix.lower() != ".html" or output.parent.resolve() != video.parent.resolve():
        raise ValueError("HTML output must be a .html sibling of the video")
    if output.exists() or output.is_symlink():
        raise ValueError("refusing to overwrite existing playback page")
    player = build_player(video, captions.read_text(encoding="utf-8"))
    with output.open("x", encoding="utf-8", newline="\n") as target:
        target.write(player)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--captions", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        help="new .html page beside the .webm; defaults to walkthrough-player.html")
    args = parser.parse_args(argv)
    output = args.output or args.video.with_name(args.video.stem + "-player.html")
    try:
        make_player(args.video, args.captions, output)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot package local synthetic video: {exc}", file=sys.stderr)
        return 2
    print(output)
    print("Local video and authored descriptions only; watch and verify before sharing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
