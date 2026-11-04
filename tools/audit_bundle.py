#!/usr/bin/env python3
"""Run BeautifulRepo's three offline checkers as one evidence-preserving report.

This local CLI is not an MCP server, remote scanner, or hostile-filesystem sandbox.
It invokes only the checked-in checker scripts; it never executes target code.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

CAPTURE_LIMIT = 128 * 1024
CHECK_TIMEOUT = 20
JUNCTION_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)
CHECKERS = ("entry_points", "markdown_links", "html_navigation")
SCRIPTS = {
    "entry_points": "repo_audit.py",
    "markdown_links": "docs_links.py",
    "html_navigation": "html_navigation.py",
}


def checked_root(value: str) -> Path:
    path = Path(value).absolute()
    try:
        info = path.lstat()
        if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_reparse_tag", 0) == JUNCTION_TAG):
            raise ValueError("root must be an ordinary directory, not a redirect")
        return path.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ValueError("root must be an existing readable directory") from None


def capture_command(arguments: list[str]) -> tuple[int | None, str, str, str | None]:
    """Capture bounded *returned* output; flag timeouts and overflow as incomplete.

    Temporary spool files avoid keeping large checker output in memory. Their
    on-disk size is not an adversarial quota; use a stable trusted checkout.
    """
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            result = subprocess.run(
                arguments, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                timeout=CHECK_TIMEOUT, check=False,
            )
        except subprocess.TimeoutExpired:
            return None, "", "", "checker exceeded the 20-second execution limit"
        except OSError:
            return None, "", "", "checker could not be started"
        stdout.seek(0)
        stderr.seek(0)
        out = stdout.read(CAPTURE_LIMIT + 1)
        err = stderr.read(CAPTURE_LIMIT + 1)
        if len(out) > CAPTURE_LIMIT or len(err) > CAPTURE_LIMIT:
            return result.returncode, "", "", "checker output exceeded the 128-KiB per-stream limit"
        try:
            return result.returncode, out.decode("utf-8"), err.decode("utf-8"), None
        except UnicodeError:
            return result.returncode, "", "", "checker returned invalid UTF-8 output"


def run_bundle(root: Path, *, fail_on: str = "error") -> tuple[dict, int]:
    """Keep native checker outputs distinct; don't turn them into a beauty score."""
    results: dict = {}
    incomplete = False
    failed = False
    scripts = Path(__file__).resolve().parent

    for name in CHECKERS:
        args = [sys.executable, "-I", "-X", "utf8", str(scripts / SCRIPTS[name])]
        if name == "entry_points":
            args += [str(root), "--format", "json", "--fail-on", "never"]
        else:
            args += ["--root", str(root)]
        code, out, err, problem = capture_command(args)
        record: dict = {"state": "complete", "exit_code": code}
        if problem is not None or code not in (0, 1):
            record = {"state": "incomplete", "exit_code": code,
                      "reason": problem or "checker rejected the input or exited unexpectedly"}
            incomplete = True
        elif name == "entry_points":
            try:
                report = json.loads(out)
                if (code != 0 or not isinstance(report, dict)
                        or report.get("schema_version") != 1
                        or not isinstance(report.get("findings"), list)
                        or not isinstance(report.get("summary"), dict)
                        or any(type(report["summary"].get(level)) is not int
                               for level in ("error", "warning", "info"))):
                    raise ValueError("unsupported audit report")
                record["report"] = report
                counts = report["summary"]
                if fail_on == "warning" and (counts["error"] or counts["warning"]):
                    failed = True
                elif fail_on == "error" and counts["error"]:
                    failed = True
            except (ValueError, TypeError):
                record = {"state": "incomplete", "exit_code": code,
                          "reason": "entry-point checker returned an invalid JSON report"}
                incomplete = True
        else:
            record["stdout"] = out.strip()
            record["diagnostics"] = err.splitlines()
            if code == 1:
                failed = True
        results[name] = record

    status = 2 if incomplete else 1 if failed else 0
    return {
        "schema_version": 1,
        "checks": results,
        "exit_code": status,
        "coverage": "Offline, source-level checks only; not a rendered, network, security or accessibility audit.",
    }, status


def render_text(result: dict) -> str:
    lines = ["BeautifulRepo combined offline audit (no score)"]
    for name in CHECKERS:
        item = result["checks"][name]
        lines.append(f"\n{name}: {item['state']} (checker exit {item['exit_code']})")
        if item["state"] != "complete":
            lines.append("  Incomplete: " + item["reason"])
        elif name == "entry_points":
            report = item["report"]
            for finding in report["findings"]:
                loc = finding["path"] + (f":{finding['line']}" if finding["line"] else "")
                lines.append(f"  {finding['severity'].upper()} [{finding['rule_id']}] {loc}: {finding['message']}")
                lines.append("    Next: " + finding["remediation"])
            counts = report["summary"]
            lines.append(f"  Summary: {counts['error']} error(s), {counts['warning']} warning(s), "
                         f"{counts['info']} informational finding(s)")
        else:
            if item["stdout"]:
                lines.append("  " + item["stdout"])
            lines.extend("  " + diagnostic for diagnostic in item["diagnostics"])
    lines.append(f"\nExit {result['exit_code']}: 0=threshold clear, 1=findings, 2=incomplete.")
    lines.append(result["coverage"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="a stable, local repository directory to inspect")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error",
                        help="entry-point audit threshold; local link errors always fail")
    args = parser.parse_args(argv)
    try:
        root = checked_root(args.root)
    except ValueError as exc:
        print(f"audit_bundle: {exc}", file=sys.stderr)
        return 2
    result, code = run_bundle(root, fail_on=args.fail_on)
    if args.format == "json":
        print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True))
    else:
        print(render_text(result), end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
