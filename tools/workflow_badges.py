#!/usr/bin/env python3
"""Check local workflow targets of same-repository GitHub Actions README badges.

No network access, target code execution, Git invocation or repository writes.
This checks *presence of a referenced workflow file*, never CI success.
"""
from __future__ import annotations

import argparse
import bisect
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import unquote, urlsplit

MAX_README_BYTES = 256 * 1024
REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
WORKFLOW_RE = re.compile(r"[A-Za-z0-9_.-]+\.ya?ml\Z", re.IGNORECASE)
MARKDOWN_IMAGE_RE = re.compile(
    r"(?<!\\)!\[[^\]\n]{0,256}\]\(\s*<?([^\s<>\)]+)", re.IGNORECASE
)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
BACKTICKS = re.compile(r"(?<!\\)`+")
JUNCTION_REPARSE_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)


class InputError(ValueError):
    """Target or arguments do not meet the bounded offline contract."""


def _safe_read(path: Path) -> str:
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            raise InputError("README.md must be an ordinary file, not a link.")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise InputError("README.md is not an ordinary file.")
            raw = handle.read(MAX_README_BYTES + 1)
        if len(raw) > MAX_README_BYTES:
            raise InputError("README.md exceeds the 256 KiB scan limit.")
        content = raw.decode("utf-8-sig")
        if "\x00" in content:
            raise UnicodeError("NUL")
        return content
    except FileNotFoundError:
        raise InputError("README.md is missing.") from None
    except UnicodeError:
        raise InputError("README.md is not valid UTF-8 text.") from None
    except OSError:
        raise InputError("README.md cannot be read.") from None


def _mask_inline_code(line: str) -> str:
    runs = list(BACKTICKS.finditer(line))
    positions: dict[int, list[int]] = {}
    for index, run in enumerate(runs):
        positions.setdefault(len(run.group()), []).append(index)
    chars = list(line)
    i = 0
    while i < len(runs):
        matching = positions[len(runs[i].group())]
        next_index = bisect.bisect_right(matching, i)
        if next_index == len(matching):
            i += 1
            continue
        close = matching[next_index]
        for index in range(runs[i].start(), runs[close].end()):
            chars[index] = " "
        i = close + 1
    return "".join(chars)


def _visible(source: str) -> str:
    """Mask common GFM code and HTML comment regions without shifting lines.

    This intentionally is not a full Markdown renderer or sanitizer.
    """
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    result = []
    fence: tuple[str, int] | None = None
    for line in source.splitlines(keepends=True):
        match = FENCE_RE.match(line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= fence[1] \
                    and not line[match.end():].strip():
                fence = None
            result.append("\n" if line.endswith("\n") else "")
            continue
        if match and not (match[1][0] == "`" and "`" in line[match.end():]):
            fence = (match[1][0], len(match[1]))
            result.append("\n" if line.endswith("\n") else "")
        else:
            result.append(_mask_inline_code(line))
    text = "".join(result)
    # Mask comments, including an unfinished comment through end of file.
    return re.sub(r"<!--(?:.*?-->|.*\Z)",
                  lambda m: re.sub(r"[^\n]", " ", m.group()),
                  text, flags=re.DOTALL)


class _ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            # Browsers honor the first duplicate src attribute.
            src = next((value for name, value in attrs if name == "src"), None)
            if src is not None:
                self.images.append((self.getpos()[0], src))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def _badges(source: str) -> list[tuple[int, str]]:
    visible = _visible(source)
    found = [(visible.count("\n", 0, m.start()) + 1, m[1])
             for m in MARKDOWN_IMAGE_RE.finditer(visible)]
    parser = _ImageParser()
    parser.feed(visible)
    parser.close()
    found.extend(parser.images)
    return sorted(found)


def _same_repo_workflow(src: str, expected: str) -> tuple[str | None, str | None]:
    """Return (workflow filename, error) for same-repo GitHub Actions badges.

    None/None means the source is outside this intentionally narrow check.
    """
    try:
        url = urlsplit(src)
    except ValueError:
        return None, None
    if url.scheme.casefold() != "https" or url.netloc.casefold() != "github.com":
        return None, None
    segments = url.path.split("/")
    if len(segments) != 7 or segments[0] or segments[3:5] != ["actions", "workflows"] \
            or segments[6].casefold() != "badge.svg":
        return None, None
    if f"{segments[1]}/{segments[2]}".casefold() != expected.casefold():
        return None, None
    try:
        filename = unquote(segments[5], errors="strict")
    except UnicodeError:
        return None, "Workflow name in badge URL is not valid UTF-8."
    if not WORKFLOW_RE.fullmatch(filename):
        return None, "Workflow name in badge URL is unsupported; inspect it manually."
    return filename, None


def _normal_dir(path: Path) -> bool:
    try:
        info = path.lstat()
        return (stat.S_ISDIR(info.st_mode)
                and getattr(info, "st_reparse_tag", 0) != JUNCTION_REPARSE_TAG)
    except OSError:
        return False


def check(root: Path, repository: str) -> tuple[int, list[str]]:
    if not REPOSITORY_RE.fullmatch(repository):
        raise InputError("--repo must have owner/name format.")
    try:
        resolved = root.resolve(strict=True)
        if not resolved.is_dir():
            raise InputError("--root must be an existing directory.")
    except (OSError, RuntimeError):
        raise InputError("--root must be an existing directory.") from None
    text = _safe_read(resolved / "README.md")
    checked = 0
    errors: list[str] = []
    for line, src in _badges(text):
        filename, invalid = _same_repo_workflow(src, repository)
        if not filename and not invalid:
            continue
        checked += 1
        if invalid:
            errors.append(f"README.md:{line}: {invalid}")
            continue
        path = resolved / ".github" / "workflows" / filename
        # Do not traverse redirected parent directories or use the target contents.
        try:
            parents = (resolved / ".github", resolved / ".github" / "workflows")
            if not all(_normal_dir(p) for p in parents):
                raise OSError("redirect or missing directory")
            # Windows path lookup is case-insensitive, but GitHub/Linux paths are not.
            # Verify the actual directory entry rather than accepting a case alias.
            with os.scandir(parents[1]) as entries:
                found_exact = False
                for count, entry in enumerate(entries):
                    if count >= 4096:
                        raise OSError("too many workflow directory entries")
                    if entry.name == filename:
                        found_exact = True
                        break
            if not found_exact or not stat.S_ISREG(path.lstat().st_mode):
                raise OSError("missing, case-mismatched or redirected workflow")
        except OSError:
            errors.append(f"README.md:{line}: missing or redirected workflow: "
                          f".github/workflows/{filename}")
    return checked, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="repository checkout to inspect (default: current directory)")
    parser.add_argument("--repo", required=True, help="expected GitHub owner/repository slug")
    args = parser.parse_args(argv)
    try:
        checked, errors = check(args.root, args.repo)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for message in errors:
        print(f"ERROR: {message}", file=sys.stderr)
    if errors:
        print(f"ERROR: {len(errors)} problem(s) in {checked} same-repository "
              "workflow badge(s).", file=sys.stderr)
        return 1
    print(f"OK: checked {checked} same-repository workflow badge(s); "
          "this does not verify CI results or other badges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
