#!/usr/bin/env python3
"""Combine BeautifulRepo's three offline checkers without running target code.

This is a local source checker, not a renderer, MCP server, or sandbox against
concurrent filesystem changes. No processes or network clients are launched.
"""
from __future__ import annotations

import argparse
from html import escape
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


def render_html(result: dict) -> str:
    """Render a standalone offline report, escaping all source diagnostics."""
    def safe(value: object) -> str:
        escaped = escape(_one_terminal_line(str(value)), quote=True)
        # ASCII output also works with narrow Windows terminal encodings.
        return escaped.encode("ascii", "xmlcharrefreplace").decode("ascii")

    status = {
        0: "Threshold clear (warnings may remain)",
        1: "Findings require attention",
        2: "Incomplete evidence; do not treat this as a pass",
    }[result["exit_code"]]
    parts = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>BeautifulRepo offline audit</title>",
        "<style>",
        ":root { color-scheme: light dark; font-family: system-ui, sans-serif; }",
        "body { max-width: 72ch; margin: 0 auto; padding: 1.25rem; line-height: 1.6; }",
        "section { border: 1px solid #8888; border-radius: .5rem; "
        "padding: 1rem; margin: 1rem 0; }",
        "code { overflow-wrap: anywhere; white-space: pre-wrap; }",
        "li { margin: .75rem 0; }",
        "</style></head><body><main>",
        "<h1>BeautifulRepo combined offline audit</h1>",
        "<p>Source-level evidence, not a repository quality score.</p>",
        f"<p><strong>Exit {result['exit_code']}: {safe(status)}</strong></p>",
    ]
    for name in CHECKERS:
        item = result["checks"][name]
        parts.extend((
            f'<section aria-labelledby="{name}">',
            f'<h2 id="{name}">{safe(name.replace("_", " ").title())}</h2>',
            f"<p>Checker state: <strong>{safe(item['state'])}</strong></p>",
        ))
        if item["state"] != "complete":
            parts.append(f"<p>Incomplete: {safe(item['reason'])}</p>")
        elif name == "entry_points":
            report = item["report"]
            counts = report["summary"]
            parts.append(
                f"<p>{counts['error']} errors, {counts['warning']} warnings, "
                f"{counts['info']} informational findings.</p>"
            )
            if report["findings"]:
                parts.append("<ul>")
                for finding in report["findings"]:
                    location = str(finding["path"])
                    if finding["line"]:
                        location += f":{finding['line']}"
                    parts.append(
                        "<li><strong>" + safe(finding["severity"]).upper()
                        + " [" + safe(finding["rule_id"]) + "]</strong> "
                        + "<code>" + safe(location) + "</code>"
                        + "<p>" + safe(finding["message"]) + "</p>"
                        + "<p>Next: " + safe(finding["remediation"]) + "</p></li>"
                    )
                parts.append("</ul>")
            else:
                parts.append("<p>No entry-point findings reported.</p>")
        else:
            parts.append(
                f"<p>Checker exit {item['exit_code']}; "
                f"{item['checked_destinations']} local destinations across "
                f"{item['inspected_markdown_files']} Markdown files.</p>"
            )
            if item["diagnostics"]:
                parts.append("<ul>")
                parts.extend(
                    "<li><code>" + safe(line) + "</code></li>"
                    for line in item["diagnostics"]
                )
                parts.append("</ul>")
            else:
                parts.append("<p>No local-link diagnostics reported.</p>")
        parts.append("</section>")
    parts.extend((
        "<p>" + safe(result["coverage"]) + "</p>",
        "<p>Static local report with no scripts or remote assets. "
        "Paths and diagnostics may be sensitive; review before sharing. "
        "A browser view is not an accessibility certification.</p>",
        "</main></body></html>",
    ))
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="stable local repository directory to inspect")
    parser.add_argument("--format", choices=("text", "json", "html"), default="text")
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
    elif args.format == "html":
        print(render_html(result), end="")
    else:
        print(render_text(result), end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
