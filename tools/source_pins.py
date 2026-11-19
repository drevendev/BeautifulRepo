#!/usr/bin/env python3
"""Offline consistency check for GitHub source permalinks in a source-only case.

This checks written revisions, NOT anonymous access, file existence, licenses,
rendering, execution, or the accuracy of the case's prose.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys

SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SOURCE_URL_RE = re.compile(
    r"https://github[.]com/(?P<owner>[A-Za-z0-9_.-]+)/"
    r"(?P<repo>[A-Za-z0-9_.-]+)/(?P<kind>blob|tree)/"
    r"(?P<revision>[^/?#<>\s)\]]+)(?P<suffix>[^<>\s)\]]*)",
    re.IGNORECASE,
)
FENCE_RE = re.compile(r"^ {0,3}(?P<run>\x60{3,}|~{3,})")
MAX_CASE_BYTES = 256 * 1024


BACKTICK_RUN_RE = re.compile(r"`+")


def mask_inline_code(line: str) -> str:
    """Mask paired one-line backtick spans without moving link source offsets."""
    # Backslashes are literal inside code spans, including before a closer.
    # Consider all runs as possible closing delimiters; reject escaped
    # opening delimiters only when outside a code span.
    runs = list(BACKTICK_RUN_RE.finditer(line))

    next_run_by_length: dict[int, int] = {}
    next_partner: list[int | None] = [None] * len(runs)
    for index in range(len(runs) - 1, -1, -1):
        length = runs[index].end() - runs[index].start()
        next_partner[index] = next_run_by_length.get(length)
        next_run_by_length[length] = index

    parts = []
    cursor = 0
    index = 0
    while index < len(runs):
        # Escape parity applies to an opener, never to a closer inside code.
        left = runs[index].start() - 1
        while left >= 0 and line[left] == "\\":
            left -= 1
        if (runs[index].start() - 1 - left) % 2:
            index += 1
            continue
        closing = next_partner[index]
        if closing is None:
            index += 1
            continue
        start, end = runs[index].start(), runs[closing].end()
        parts.extend((line[cursor:start], " " * (end - start)))
        cursor = end
        index = closing + 1
    parts.append(line[cursor:])
    return "".join(parts)


def active_lines(document: str):
    """Yield 1-based non-fenced source lines; not a full Markdown renderer."""
    fence = None
    for line_no, line in enumerate(document.splitlines(), 1):
        start = FENCE_RE.match(line)
        if fence is None:
            if start is not None:
                run = start.group("run")
                fence = (run[0], len(run))
                continue
            yield line_no, mask_inline_code(line)
        else:
            char, count = fence
            stripped = line.lstrip(" ")
            if len(line) - len(stripped) <= 3 and re.fullmatch(
                re.escape(char) + "{" + str(count) + ",}[ \t]*", stripped
            ):
                fence = None


def check_case(text: str, repository: str, commit: str) -> tuple[list[str], int]:
    """Check pinned links to one specified source; unrelated links are ignored."""
    owner, repo = repository.casefold().split("/", 1)
    problems: list[str] = []
    checked = 0
    readme = 0
    for line_no, line in active_lines(text):
        for match in SOURCE_URL_RE.finditer(line):
            if (match.group("owner").casefold(), match.group("repo").casefold()) != (owner, repo):
                continue
            checked += 1
            if match.group("revision").casefold() != commit:
                problems.append(f"line {line_no}: source link uses a different or moving revision")
            suffix = match.group("suffix")
            if match.group("kind").casefold() == "blob":
                if not suffix.startswith("/"):
                    problems.append(f"line {line_no}: source blob link has no file path")
                elif suffix.split("?", 1)[0].split("#", 1)[0].casefold() == "/readme.md":
                    readme += 1
    if checked == 0:
        problems.append("no pinned tree/blob links to the specified source repository")
    if readme == 0:
        problems.append("no source README.md blob permalink found")
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True, help="local Markdown case file")
    parser.add_argument("--repository", required=True, help="source OWNER/REPO")
    parser.add_argument("--commit", required=True, help="expected full 40-character commit SHA")
    args = parser.parse_args(argv)
    commit = args.commit.lower()
    if not SHA_RE.fullmatch(commit) or not REPOSITORY_RE.fullmatch(args.repository):
        parser.error("provide a valid OWNER/REPO and full 40-character commit SHA")
    path = Path(os.path.abspath(args.case))
    try:
        # Refuse simple aliases, including linked parent paths, before opening.
        if any(item.is_symlink() for item in (path, *path.parents)):
            raise ValueError("redirected input path")
        stat = path.stat()
        if not path.is_file() or stat.st_nlink != 1 or stat.st_size > MAX_CASE_BYTES:
            raise ValueError("input must be a regular, single-linked Markdown file <= 256 KiB")
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: cannot inspect local case: {exc}", file=sys.stderr)
        return 2
    errors, count = check_case(text, args.repository, commit)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(
        f"OK: {count} source permalinks use {args.repository}@{commit}; "
        "anonymous access and source contents NOT CHECKED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
