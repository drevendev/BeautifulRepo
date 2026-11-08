#!/usr/bin/env python3
"""Opt-in read-only local MCP adapter for BeautifulRepo's existing offline audit.

Development candidate. The optional official MCP SDK is imported only when
starting the server; the existing offline checkers retain zero dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import time
from typing import Any

BUNDLE = Path(__file__).resolve().parents[1] / "tools" / "audit_bundle.py"
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



MAX_MARKDOWN_SOURCES = 5000
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_MARKDOWN_BYTES = 32 * 1024 * 1024
MAX_WALK_ENTRIES = 50000
MAX_PREFLIGHT_SECONDS = 5


def _bounded_source_tree(root: Path) -> bool:
    """Fail closed on oversized/special Markdown sources before checker launch.

    Metadata preflight for a stable, trusted checkout; not a sandbox against
    concurrent filesystem changes. Never read target file contents here.
    """
    deadline = time.monotonic() + MAX_PREFLIGHT_SECONDS
    pending = [root]
    visited = markdown_files = total_bytes = 0
    try:
        while pending:
            if time.monotonic() > deadline:
                return False
            with os.scandir(pending.pop()) as entries:
                for entry in entries:
                    if time.monotonic() > deadline:
                        return False
                    # Match the offline link checkers' unscanned dependency trees.
                    if entry.name in (".git", "node_modules"):
                        continue
                    visited += 1
                    if visited > MAX_WALK_ENTRIES:
                        return False
                    # os.lstat consistently exposes Windows junction tags;
                    # DirEntry.stat can omit reparse metadata on some versions.
                    info = os.lstat(entry.path)
                    if (stat.S_ISDIR(info.st_mode)
                            and getattr(info, "st_reparse_tag", 0) != JUNCTION_TAG):
                        pending.append(Path(entry.path))
                        continue
                    if not entry.name.lower().endswith((".md", ".markdown")):
                        continue
                    if stat.S_ISREG(info.st_mode):
                        size = info.st_size
                    elif stat.S_ISLNK(info.st_mode):
                        target = Path(entry.path).resolve(strict=True)
                        if not target.is_relative_to(root) or not target.is_file():
                            return False
                        target_info = target.stat()
                        if not stat.S_ISREG(target_info.st_mode):
                            return False
                        size = target_info.st_size
                    else:
                        # Never hand a Markdown-named FIFO/device to read_text().
                        return False
                    markdown_files += 1
                    total_bytes += size
                    if (markdown_files > MAX_MARKDOWN_SOURCES
                            or size > MAX_SOURCE_BYTES
                            or total_bytes > MAX_TOTAL_MARKDOWN_BYTES):
                        return False
    except (OSError, ValueError, RuntimeError):
        return False
    return True


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


def _bounded_run(cmd: list[str]) -> tuple[int, bytes, str | None]:
    """Drain both child pipes concurrently, stopping output before RAM/disk growth."""
    captured = [bytearray(), bytearray()]
    overflow = threading.Event()
    read_failed = threading.Event()
    with subprocess.Popen(
        cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as child:
        def terminate() -> None:
            if child.poll() is None:
                try:
                    child.kill()
                except OSError:
                    pass  # Child may have just exited.

        def drain(pipe: Any, index: int) -> None:
            try:
                while True:
                    chunk = pipe.read(64 * 1024)
                    if not chunk:
                        return
                    if len(captured[index]) + len(chunk) > MAX_OUTPUT_BYTES:
                        overflow.set()
                        terminate()
                        return
                    captured[index].extend(chunk)
            except (OSError, ValueError):
                read_failed.set()
                terminate()

        readers = [
            threading.Thread(target=drain, args=(pipe, index), daemon=True)
            for index, pipe in enumerate((child.stdout, child.stderr))
        ]
        for reader in readers:
            reader.start()
        try:
            child.wait(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            terminate()
            child.wait()
            raise
        finally:
            # A stale descendant holding a pipe cannot stall the MCP server forever.
            for reader in readers:
                reader.join(timeout=1)
        if read_failed.is_set() or any(reader.is_alive() for reader in readers):
            return child.returncode, b"", "checker output could not be read safely"
        if overflow.is_set():
            return child.returncode, b"", "checker output exceeded the bounded response limit"
        return child.returncode, bytes(captured[0]), None


def run_check(root: Path, tool_name: str) -> dict[str, Any]:
    """Run only our fixed checker with a fixed argument vector; never target code."""
    check = CHECKS[tool_name]
    try:
        # Recheck the configured target on every invocation, not just at startup.
        fixed_root = allowed_root(str(root))
    except ValueError:
        return incomplete(check, "configured repository root is no longer safe or available")
    if check in ("markdown_links", "html_navigation") and not _bounded_source_tree(fixed_root):
        return incomplete(check, "repository document sources exceeded safe scan limits or could not be inspected")
    if not BUNDLE.is_file():
        return incomplete(check, "checked-in bundle is unavailable")
    # Invoke only the requested checker: unrelated noisy/failed checks must not
    # exhaust this tool's output budget or turn its evidence incomplete.
    cmd = [sys.executable, "-I", "-B", str(BUNDLE), str(fixed_root),
           "--format", "json", "--fail-on", "never", "--only", check]
    try:
        return_code, output, capture_error = _bounded_run(cmd)
        if capture_error:
            return incomplete(check, capture_error)
    except subprocess.TimeoutExpired:
        return incomplete(check, "offline checker timed out")
    except OSError:
        return incomplete(check, "offline checker could not be started")

    if return_code not in (0, 1, 2):
        return incomplete(check, "checker exited unexpectedly")
    try:
        result = json.loads(output.decode("utf-8"))
        record = result["checks"][check]
        if (result["schema_version"] != 1
                or result["exit_code"] != return_code
                or record["state"] not in ("complete", "incomplete")
                or type(record.get("exit_code")) not in (int, type(None))):
            raise ValueError("unexpected checker schema")
        if record["state"] == "incomplete":
            # Only the bundled checker's two fixed, path-free reasons may be
            # surfaced to a model host. Never forward arbitrary source text.
            if return_code != 2 or record["exit_code"] is not None:
                raise ValueError("inconsistent incomplete checker status")
            reason = record.get("reason")
            if reason not in (
                    "checker result exceeded the 128-KiB limit",
                    "checker failed before producing complete evidence"):
                reason = "checker reported incomplete evidence"
            return incomplete(check, reason)
        # One --only checker was requested with --fail-on never. Mismatches
        # must not yield a misleading complete/clean MCP tool response.
        if (type(record["exit_code"]) is not int
                or record["exit_code"] not in (0, 1)
                or return_code != record["exit_code"]
                or (check == "entry_points" and record["exit_code"] != 0)):
            raise ValueError("inconsistent checker status")
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
        "bundle_exit_code": return_code, "coverage": COVERAGE,
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
