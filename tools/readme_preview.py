#!/usr/bin/env python3
"""Preview a proposed README against a local checkout without changing files."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata

MAX_BYTES = 256 * 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
JUNCTION_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)


class PreviewError(ValueError):
    """Invalid, unsafe, or stale input for a local README preview."""


def _redirect(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or getattr(info, "st_reparse_tag", 0) == JUNCTION_TAG


def _unsafe_display_character(ch: str) -> bool:
    """Reject controls that could alter the apparent ordering of a terminal diff."""
    cp = ord(ch)
    return (
        (unicodedata.category(ch) == "Cc" and ch not in "\t\r\n")
        or cp in (0x061C, 0x200E, 0x200F, 0x2028, 0x2029)
        or 0x202A <= cp <= 0x202E
        or 0x2066 <= cp <= 0x2069
    )


def read_file(path: Path, label: str) -> tuple[bytes, str]:
    try:
        if _redirect(path) or not stat.S_ISREG(path.lstat().st_mode):
            raise PreviewError(f"{label}: expected a regular, non-symlinked UTF-8 file.")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise PreviewError(f"{label}: not a regular file.")
            data = handle.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise PreviewError(f"{label}: exceeds the 256 KiB limit.")
        text = data.decode("utf-8-sig")
        # Bare carriage returns can overwrite terminal output; CRLF is allowed.
        if "\r" in text.replace("\r\n", ""):
            raise PreviewError(f"{label}: contains a bare carriage return (only CRLF is supported).")
        # C1/bidi controls can spoof output; Unicode separators misframe splitlines().
        if any(_unsafe_display_character(ch) for ch in text):
            raise PreviewError(f"{label}: contains unsupported display control characters.")
        return data, text
    except PreviewError:
        raise
    except (OSError, UnicodeError) as exc:
        raise PreviewError(f"{label}: cannot read a regular UTF-8 file.") from exc


def _line_endings(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    kinds = [name for name, count in (("CRLF", crlf), ("LF", lf), ("CR", cr)) if count]
    return "+".join(kinds) if kinds else "none"


def _diff(original: str, proposed: str) -> str:
    result = difflib.unified_diff(
        original.splitlines(keepends=True), proposed.splitlines(keepends=True),
        fromfile="a/README.md", tofile="b/README.md", lineterm="\n",
    )
    output = []
    for line in result:
        if line.endswith("\n"):
            output.append(line)
        else:
            output.append(line + "\n\\ No newline at end of file\n")
    return "".join(output)


def preview(root: Path, proposal: Path, expected: str | None = None) -> str:
    try:
        if _redirect(root) or not stat.S_ISDIR(root.lstat().st_mode):
            raise PreviewError("root: expected an ordinary, non-symlinked directory.")
    except OSError as exc:
        raise PreviewError("root: cannot inspect target directory.") from exc
    before, old_text = read_file(root / "README.md", "README.md")
    after, new_text = read_file(proposal, "proposal")
    old_hash = hashlib.sha256(before).hexdigest()
    if expected is not None and expected != old_hash:
        raise PreviewError("README.md changed since the recorded SHA-256; prepare a fresh preview.")
    new_hash = hashlib.sha256(after).hexdigest()
    lines = [
        "BeautifulRepo README preview (read-only; no files changed)",
        f"Current README SHA-256:  {old_hash}",
        f"Proposed README SHA-256: {new_hash}",
        f"Line endings: current={_line_endings(before)} proposed={_line_endings(after)}",
    ]
    if before == after:
        lines.append("No differences.")
    else:
        lines.append("Proposed unified diff (review before approving any edit):")
        diff = _diff(old_text, new_text)
        if diff:
            lines.append(diff.rstrip("\n"))
        else:
            lines.append("No decoded-text differences; verify byte-order marks/encoding.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="existing checkout directory")
    parser.add_argument("--proposal", required=True, type=Path, help="pre-existing proposed README text")
    parser.add_argument("--expected-sha256", help="optional current README byte hash to detect stale previews")
    args = parser.parse_args(argv)
    if args.expected_sha256 is not None and not SHA256.fullmatch(args.expected_sha256):
        parser.error("--expected-sha256 must contain 64 lowercase hex characters")
    try:
        # A piped Windows console may default to cp1252; emit valid UTF-8 diffs.
        sys.stdout.reconfigure(encoding="utf-8")
        print(preview(args.root, args.proposal, args.expected_sha256), end="")
    except PreviewError as exc:
        print(f"readme_preview: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
