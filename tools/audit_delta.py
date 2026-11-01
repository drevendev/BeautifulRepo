#!/usr/bin/env python3
"""Compare two BeautifulRepo entry-point JSON audits without executing either target."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import stat
import sys

LIMIT = 1024 * 1024
MAX_FINDINGS = 4096
SEVERITIES = ("error", "warning", "info")
RULE = re.compile(r"[a-z][a-z0-9_.-]{0,79}\Z")
JUNCTION_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)


class ReportError(ValueError):
    """Malformed or unsupported local audit evidence."""


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReportError("Duplicate JSON object key.")
        result[key] = value
    return result


def load_report(filename: str, label: str) -> dict:
    path = Path(filename)
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or getattr(info, "st_reparse_tag", 0) == JUNCTION_TAG:
            raise ReportError(f"{label}: expected an ordinary, non-symlinked report file.")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ReportError(f"{label}: report must be an ordinary file.")
            raw = stream.read(LIMIT + 1)
        if len(raw) > LIMIT or b"\x00" in raw:
            raise ReportError(f"{label}: report exceeds 1 MiB or contains NUL bytes.")
        data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_pairs)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ReportError(f"{label}: cannot read a valid UTF-8 JSON report.") from exc
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ReportError(f"{label}: expected repo_audit schema_version 1.")
    if not isinstance(data.get("findings"), list) or len(data["findings"]) > MAX_FINDINGS:
        raise ReportError(f"{label}: findings must be a bounded list.")
    counts = Counter()
    for item in data["findings"]:
        if not isinstance(item, dict):
            raise ReportError(f"{label}: invalid finding.")
        rule, severity = item.get("rule_id"), item.get("severity")
        if not isinstance(rule, str) or not RULE.fullmatch(rule) or severity not in SEVERITIES:
            raise ReportError(f"{label}: invalid rule or severity.")
        counts[severity] += 1
    summary = data.get("summary")
    if not isinstance(summary, dict) or set(summary) != set(SEVERITIES) or any(
        type(summary[level]) is not int or summary[level] != counts[level] for level in SEVERITIES
    ):
        raise ReportError(f"{label}: summary does not match findings.")
    documents, read_files = data.get("documents"), data.get("read_files")
    if (not isinstance(documents, dict) or set(documents) != {"readme", "license", "contributing"}
            or any(value is not None and not isinstance(value, str) for value in documents.values())
            or not isinstance(read_files, list) or len(read_files) > 16
            or any(not isinstance(value, str) or not value for value in read_files)):
        raise ReportError(f"{label}: missing or invalid audited-document coverage.")
    profile = data.get("profile", "public")
    if profile not in ("public", "internal", "private"):
        raise ReportError(f"{label}: unsupported audit profile.")
    return data


def compare(before: dict, after: dict) -> dict:
    first, second = before.get("profile", "public"), after.get("profile", "public")
    if first != second:
        raise ReportError("Audit profiles differ; compare reports with the same --profile.")
    def counts(report):
        return Counter((item["severity"], item["rule_id"]) for item in report["findings"])
    old, new = counts(before), counts(after)
    changes = [
        {"severity": severity, "rule_id": rule, "before": old[severity, rule],
         "after": new[severity, rule], "delta": new[severity, rule] - old[severity, rule]}
        for severity, rule in sorted(set(old) | set(new), key=lambda x: (SEVERITIES.index(x[0]), x[1]))
        if old[severity, rule] != new[severity, rule]
    ]
    return {"schema_version": 1, "audit_schema_version": 1, "profile": first,
            "coverage_changed": (before["documents"] != after["documents"]
                                 or sorted(before["read_files"]) != sorted(after["read_files"])),
            "before": {level: before["summary"][level] for level in SEVERITIES},
            "after": {level: after["summary"][level] for level in SEVERITIES},
            "changes": changes}


def render_text(delta: dict) -> str:
    lines = ["BeautifulRepo audit delta (offline; count changes, not verified fixes)",
             "Coverage changed: " + ("YES — review the entry-point documents inspected."
                                   if delta["coverage_changed"] else "no")]
    for level in SEVERITIES:
        lines.append(f"{level.capitalize()}: {delta['before'][level]} -> {delta['after'][level]}")
    if not delta["changes"]:
        lines.append("No changes to rule counts.")
    else:
        lines.append("Changed rule counts:")
        for item in delta["changes"]:
            lines.append(f"  {item['severity'].upper()} [{item['rule_id']}]: "
                         f"{item['before']} -> {item['after']} ({item['delta']:+d})")
    lines.append("A decreased count is not proof of a repaired experience; verify changes and coverage manually.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", help="saved JSON from repo_audit.py --format json")
    parser.add_argument("after", help="saved JSON from repo_audit.py --format json")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = compare(load_report(args.before, "before"), load_report(args.after, "after"))
    except ReportError as exc:
        print(f"audit_delta: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(render_text(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
