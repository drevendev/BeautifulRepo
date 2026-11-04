#!/usr/bin/env python3
"""Combine BeautifulRepo's three offline checkers without running target code.

This is a local source checker, not a renderer, MCP server, or sandbox against
concurrent filesystem changes. No processes or network clients are launched.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import stat
import sys

RESULT_LIMIT = 128 * 1024
JUNCTION_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)
CHECKERS = ("entry_points", "markdown_links", "html_navigation")
MODULES = {
    "entry_points": "repo_audit",
    "markdown_links": "docs_links",
    "html_navigation": "html_navigation",
}


def checked_root(value: str) -> Path:
    path = Path(value).absolute()
    try:
        info = path.lstat()
        if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_reparse_tag", 0) == JUNCTION_TAG):
            raise ValueError("root must be an ordinary directory, not a redirect")
        return path.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("root must be"):
            raise
        raise ValueError("root must be an existing readable directory") from None


def load_checker(name: str):
    """Load only a checked-in sibling module, never a module from the target."""
    path = Path(__file__).resolve().with_name(MODULES[name] + ".py")
    existing = sys.modules.get(MODULES[name])
    if existing is not None and Path(getattr(existing, "__file__", "")).resolve() == path:
        return existing
    spec = importlib.util.spec_from_file_location(MODULES[name], path)
    if spec is None or spec.loader is None:
        raise RuntimeError("checked-in checker module is unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULES[name]] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(MODULES[name], None)
        raise
    return module


def check_once(name: str, root: Path, *, exclude: tuple[str, ...] = ()) -> dict:
    module = load_checker(name)
    if name == "entry_points":
        report = module.audit_repository(root)
        return {"state": "complete", "exit_code": 0, "report": report}
    errors, destinations, files = module.check_repo(root, exclude)
    return {
        "state": "complete", "exit_code": 1 if errors else 0,
        "diagnostics": errors,
        "checked_destinations": destinations,
        "inspected_markdown_files": files,
    }


def bounded(record: dict) -> dict:
    """Over-limit evidence is incomplete, never a truncated success."""
    if len(json.dumps(record, ensure_ascii=True).encode("utf-8")) > RESULT_LIMIT:
        return {"state": "incomplete", "exit_code": None,
                "reason": "checker result exceeded the 128-KiB limit"}
    return record


def run_bundle(root: Path, *, fail_on: str = "error",
               exclude: tuple[str, ...] = ()) -> tuple[dict, int]:
    results: dict = {}
    incomplete = False
    failed = False
    for name in CHECKERS:
        try:
            record = bounded(check_once(name, root, exclude=exclude))
            if record["state"] == "complete" and name == "entry_points":
                report = record["report"]
                if (not isinstance(report, dict) or report.get("schema_version") != 1
                        or not isinstance(report.get("findings"), list)
                        or not isinstance(report.get("summary"), dict)
                        or any(type(report["summary"].get(level)) is not int
                               for level in ("error", "warning", "info"))):
                    raise ValueError("unexpected audit report")
        except Exception:
            # These are the project's trusted checkers; never leak exception paths
            # or turn unexpected failures into a successful scan.
            record = {"state": "incomplete", "exit_code": None,
                      "reason": "checker failed before producing complete evidence"}
        if record["state"] != "complete":
            incomplete = True
        elif name == "entry_points":
            counts = record["report"]["summary"]
            if fail_on == "warning" and (counts["error"] or counts["warning"]):
                failed = True
            elif fail_on == "error" and counts["error"]:
                failed = True
        elif record["exit_code"] == 1:
            failed = True
        results[name] = record

    status = 2 if incomplete else 1 if failed else 0
    return {
        "schema_version": 1,
        "checks": results,
        "exit_code": status,
        "coverage": "Offline source-level inspection; not rendered, network, security or accessibility verification.",
    }, status


def _one_terminal_line(value: str) -> str:
    """Escape untrusted control/format characters in human-readable output."""
    return "".join(
        char if char.isprintable() else
        (f"\\u{ord(char):04x}" if ord(char) <= 0xFFFF
         else f"\\U{ord(char):08x}")
        for char in value
    )


def render_text(result: dict) -> str:
    lines = ["BeautifulRepo combined offline audit (no score)"]
    for name in CHECKERS:
        item = result["checks"][name]
        lines.extend(("", f"{name}: {item['state']} (checker exit {item['exit_code']})"))
        if item["state"] != "complete":
            lines.append("  Incomplete: " + item["reason"])
        elif name == "entry_points":
            report = item["report"]
            for finding in report["findings"]:
                loc = finding["path"] + (f":{finding['line']}" if finding["line"] else "")
                lines.append(f"  {finding['severity'].upper()} [{finding['rule_id']}] "
                             f"{loc}: {finding['message']}")
                lines.append("    Next: " + finding["remediation"])
            counts = report["summary"]
            lines.append(f"  Summary: {counts['error']} error(s), {counts['warning']} warning(s), "
                         f"{counts['info']} informational finding(s)")
        else:
            lines.append(f"  Checked {item['checked_destinations']} local destinations "
                         f"across {item['inspected_markdown_files']} Markdown files.")
            lines.extend("  " + diagnostic for diagnostic in item["diagnostics"])
    lines.extend(("", f"Exit {result['exit_code']}: 0=threshold clear, 1=findings, 2=incomplete."))
    lines.append(result["coverage"])
    return "\n".join(_one_terminal_line(line) for line in lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="stable local repository directory to inspect")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error",
                        help="entry-point threshold; local link errors always fail")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                        help="skip matching Markdown sources in both link checkers; "
                             "does not affect the entry-point audit")
    args = parser.parse_args(argv)
    try:
        root = checked_root(args.root)
    except ValueError as exc:
        print(f"audit_bundle: {exc}", file=sys.stderr)
        return 2
    result, code = run_bundle(root, fail_on=args.fail_on,
                              exclude=tuple(args.exclude))
    if args.format == "json":
        print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True))
    else:
        print(render_text(result), end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
