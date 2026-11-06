#!/usr/bin/env python3
"""Opt-in read-only local MCP adapter for BeautifulRepo's existing offline audit.

Development candidate. The optional official MCP SDK is imported only when
starting the server; the existing offline checkers retain zero dependencies.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any

BUNDLE = Path(__file__).resolve().with_name("audit_bundle.py")
CHECKS = {
    "audit_repository": "entry_points",
    "check_documentation_links": "markdown_links",
    "check_html_navigation": "html_navigation",
}
TIMEOUT_SECONDS = 30
MAX_OUTPUT_BYTES = 512 * 1024
JUNCTION_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)
COVERAGE = (
    "Read-only offline source checks, not a rendered accessibility, security, "
    "external-link, or repository-quality certification."
)


def allowed_root(value: str) -> Path:
    """Require an explicit absolute, ordinary directory with no redirects.

    A filesystem that changes concurrently is outside this adapter's
    security model. All supplied targets must be trusted stable checkouts.
    """
    requested = Path(value)
    if not requested.is_absolute():
        raise ValueError("allowed root must be an absolute directory")
    try:
        resolved = requested.resolve(strict=True)
        if resolved != requested or not resolved.is_dir():
            raise ValueError("allowed root must be an ordinary directory without redirects")
        if resolved == Path(resolved.anchor):
            raise ValueError("filesystem root cannot be the allowed repository")
        if resolved == Path.home().resolve():
            raise ValueError("home directory cannot be the allowed repository")
        info = requested.lstat()
        if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_reparse_tag", 0) == JUNCTION_TAG):
            raise ValueError("allowed root must be an ordinary directory without redirects")
    except (OSError, RuntimeError):
        raise ValueError("allowed root must be an existing readable directory") from None
    return resolved


def incomplete(check: str, reason: str) -> dict[str, Any]:
    return {
        "checker": check, "state": "incomplete", "exit_code": 2,
        "reason": reason, "coverage": COVERAGE,
    }


def run_check(root: Path, tool_name: str) -> dict[str, Any]:
    """Run only our fixed checker with a fixed argument vector; never target code."""
    check = CHECKS[tool_name]
    try:
        # Recheck the configured target on every invocation, not just at startup.
        fixed_root = allowed_root(str(root))
    except ValueError:
        return incomplete(check, "configured repository root is no longer safe or available")
    if not BUNDLE.is_file():
        return incomplete(check, "checked-in bundle is unavailable")
    cmd = [sys.executable, "-I", "-B", str(BUNDLE), str(fixed_root),
           "--format", "json", "--fail-on", "never"]
    try:
        completed = subprocess.run(
            cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=TIMEOUT_SECONDS, check=False,
        )
    except subprocess.TimeoutExpired:
        return incomplete(check, "offline checker timed out")
    except OSError:
        return incomplete(check, "offline checker could not be started")

    if (len(completed.stdout) > MAX_OUTPUT_BYTES
            or len(completed.stderr) > MAX_OUTPUT_BYTES):
        return incomplete(check, "checker output exceeded the bounded response limit")
    if completed.returncode not in (0, 1, 2):
        return incomplete(check, "checker exited unexpectedly")
    try:
        result = json.loads(completed.stdout.decode("utf-8"))
        record = result["checks"][check]
        if (result["schema_version"] != 1
                or result["exit_code"] != completed.returncode
                or record["state"] not in ("complete", "incomplete")
                or type(record.get("exit_code")) not in (int, type(None))):
            raise ValueError("unexpected checker schema")
        if record["state"] == "incomplete":
            return incomplete(check, "checker reported incomplete evidence")
        if check == "entry_points":
            if not isinstance(record.get("report"), dict):
                raise ValueError("missing entry-point report")
        elif not isinstance(record.get("diagnostics"), list):
            raise ValueError("missing link diagnostics")
    except (UnicodeError, ValueError, KeyError, TypeError):
        return incomplete(check, "checker returned an invalid report")
    return {
        "checker": check, "state": record["state"],
        "exit_code": record["exit_code"], "evidence": record,
        "bundle_exit_code": completed.returncode, "coverage": COVERAGE,
    }


def make_server(root: Path):
    """Create three argument-free, read-only tools bound to one configured root."""
    from mcp.server import MCPServer  # Optional dependency, v2.
    server = MCPServer("BeautifulRepo local read-only audit")

    @server.tool()
    def audit_repository() -> dict[str, Any]:
        """Inspect local README, license, contribution and trust entry points."""
        return run_check(root, "audit_repository")

    @server.tool()
    def check_documentation_links() -> dict[str, Any]:
        """Check only repository-owned Markdown destinations; no URL fetching."""
        return run_check(root, "check_documentation_links")

    @server.tool()
    def check_html_navigation() -> dict[str, Any]:
        """Check local HTML/media destinations and Markdown section anchors."""
        return run_check(root, "check_html_navigation")

    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="absolute path to one stable repository")
    args = parser.parse_args(argv)
    try:
        root = allowed_root(args.root)
    except ValueError as exc:
        print(f"BeautifulRepo MCP: {exc}", file=sys.stderr)
        return 2
    try:
        server = make_server(root)
    except ImportError:
        print("BeautifulRepo MCP requires optional mcp==2.3.0 (SDK v2).", file=sys.stderr)
        return 2
    server.run()  # Official SDK stdio default. stdout is protocol-only.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
