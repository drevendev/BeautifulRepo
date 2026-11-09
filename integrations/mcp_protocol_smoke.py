#!/usr/bin/env python3
"""Optional real-SDK MCP stdio smoke test (no LLM calls or remote services).

Install mcp==2.3.0 in a disposable environment before running this script.
It launches the actual local adapter, exercises both modern discovery and
legacy initialize lifecycles, lists and calls all three tools on healthy/broken
synthetic fixtures, and checks for target writes.
It does NOT test Claude Code, Codex, or external-user installation.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from mcp import Client, StdioServerParameters

SERVER = Path(__file__).resolve().with_name("mcp_server.py")
BUNDLE = SERVER.parents[1] / "tools" / "audit_bundle.py"
# Intentionally do not import the adapter: expected routing must remain
# independent, or a wrong MCP tool-to-checker mapping would pass both sides.
CHECKS = {
    "audit_repository": "entry_points",
    "check_documentation_links": "markdown_links",
    "check_html_navigation": "html_navigation",
}
COVERAGE = (
    "Read-only offline source checks, not a rendered accessibility, security, "
    "external-link, or repository-quality certification."
)


def direct_cli_receipt(root: Path, tool_name: str) -> tuple[dict, int]:
    """Get independent source evidence from the real CLI, not run_check again."""
    check = CHECKS[tool_name]
    completed = subprocess.run(
        [
            sys.executable, "-I", "-B", str(BUNDLE), str(root),
            "--format", "json", "--fail-on", "never", "--only", check,
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    result = json.loads(completed.stdout.decode("utf-8"))
    record = result["checks"][check]
    if (result["schema_version"] != 1
            or result["exit_code"] != completed.returncode
            or completed.returncode not in (0, 1)
            or record["state"] != "complete"
            or record["exit_code"] != completed.returncode):
        raise AssertionError(f"direct CLI returned inconsistent evidence for {check}")
    return record, completed.returncode


def snapshot(root: Path) -> dict[str, str]:
    """Detect additions/deletions as well as changed file contents."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


def check_startup_refusals(root: Path) -> tuple[int, bool]:
    """Verify the actual server process refuses unsafe roots before MCP starts."""
    candidates = [
        ("relative root", "."),
        ("missing root", str(root / "does-not-exist")),
        ("filesystem root", str(Path(root.anchor))),
        ("home directory", str(Path.home().resolve())),
    ]
    alias = root.parent / "mcp-root-symlink"
    symlink_tested = False
    try:
        try:
            alias.symlink_to(root, target_is_directory=True)
            symlink_tested = True
            candidates.append(("symlink root", str(alias)))
        except (OSError, NotImplementedError):
            # Windows CI may not grant symlink creation rights; do not claim a PASS.
            pass
        for label, candidate in candidates:
            completed = subprocess.run(
                [sys.executable, "-I", "-B", str(SERVER), "--root", candidate],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=10, check=False,
            )
            if (completed.returncode != 2 or completed.stdout
                    or b"BeautifulRepo MCP:" not in completed.stderr):
                raise AssertionError(
                    f"{label}: unsafe server startup was not refused "
                    "with exit 2, clean stdout and a bounded stderr error"
                )
    finally:
        if symlink_tested:
            alias.unlink()
    return len(candidates), symlink_tested


async def probe(root: Path, *, broken: bool, mode: str,
                exercise_missing_root: bool = False) -> str:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-I", "-B", str(SERVER), "--root", str(root)],
    )
    before = snapshot(root)
    async with Client(params, mode=mode) as client:
        version = str(client.protocol_version)
        expected_version = {"auto": "2026-07-28", "legacy": "2025-11-25"}[mode]
        if version != expected_version:
            raise AssertionError(
                f"{mode}: expected MCP {expected_version}, got {version}"
            )
        listed = await client.list_tools()
        actual = {tool.name: tool for tool in listed.tools}
        if set(actual) != set(CHECKS):
            raise AssertionError(f"unexpected MCP tools: {sorted(actual)}")
        for name, tool in actual.items():
            if tool.input_schema.get("properties"):
                raise AssertionError(f"{name} must accept no arguments")
            response = await client.call_tool(name, {})
            if response.is_error:
                raise AssertionError(f"MCP tool {name} failed: {response.content!r}")
            # A second call to adapter.run_check would share the very logic
            # under test and could let the same broken wrapper pass twice.
            direct_record, direct_exit = direct_cli_receipt(root, name)
            observed = response.structured_content
            if (not isinstance(observed, dict)
                    or observed.get("checker") != CHECKS[name]
                    or observed.get("state") != "complete"
                    or observed.get("evidence") != direct_record
                    or observed.get("exit_code") != direct_exit
                    or observed.get("bundle_exit_code") != direct_exit):
                raise AssertionError(
                    f"MCP tool evidence disagrees with independent CLI for {name}"
                )
            expected_exit = 0 if name == "audit_repository" or not broken else 1
            if direct_exit != expected_exit:
                raise AssertionError(
                    f"{name}: expected direct CLI exit {expected_exit}, got {direct_exit}"
                )
        if exercise_missing_root:
            # The configured path must be revalidated on EACH tool invocation,
            # even while the real MCP process/client session remains connected.
            parked = root.parent / "temporarily-absent-repository"
            root.rename(parked)
            try:
                for name, check in CHECKS.items():
                    response = await client.call_tool(name, {})
                    expected = {
                        "checker": check, "state": "incomplete", "exit_code": 2,
                        "reason": "configured repository root is no longer safe or available",
                        "coverage": COVERAGE,
                    }
                    if response.is_error or response.structured_content != expected:
                        raise AssertionError(
                            f"{name}: lost root did not return incomplete evidence"
                        )
            finally:
                parked.rename(root)
    if before != snapshot(root):
        raise AssertionError("MCP checker created, removed, or modified fixture files")
    return version


async def probe_refused_alias(root: Path, *, mode: str, label: str) -> str:
    """Check fail-closed tool results over the real SDK connection."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-I", "-B", str(SERVER), "--root", str(root)],
    )
    before = snapshot(root)
    async with Client(params, mode=mode) as client:
        version = str(client.protocol_version)
        expected_version = {"auto": "2026-07-28", "legacy": "2025-11-25"}[mode]
        if version != expected_version:
            raise AssertionError(f"{label}: {mode} negotiated {version}")
        listed = {tool.name for tool in (await client.list_tools()).tools}
        if listed != set(CHECKS):
            raise AssertionError(f"{label}: unexpected tools: {sorted(listed)}")
        for name, check in CHECKS.items():
            response = await client.call_tool(name, {})
            expected = {
                "checker": check, "state": "incomplete", "exit_code": 2,
                "reason": "repository document sources exceeded safe scan limits or could not be inspected",
                "coverage": COVERAGE,
            }
            if response.is_error or response.structured_content != expected:
                raise AssertionError(
                    f"{label}: {mode} {name} did not refuse an external document alias"
                )
    if before != snapshot(root):
        raise AssertionError(f"{label}: MCP tools changed fixture files")
    return version


async def check_external_document_aliases(root: Path) -> tuple[list[str], list[str]]:
    """Probe a non-Markdown hard link and an outside Markdown symlink.

    The outside file is synthetic and on the same temporary filesystem.
    A platform that cannot create a link is reported as untested, not PASS.
    """
    outside = root.parent / "synthetic-outside-source.txt"
    expected_bytes = b"Synthetic outside document; not private data.\\n"
    outside.write_bytes(expected_bytes)
    exercised: list[str] = []
    skipped: list[str] = []
    cases = (
        ("hard-linked LICENSE", "LICENSE", "hard"),
        ("outside Markdown symlink", "outside.md", "symlink"),
    )
    for label, name, kind in cases:
        link = root / name
        try:
            if kind == "hard":
                os.link(outside, link)
            else:
                link.symlink_to(outside)
        except (OSError, NotImplementedError) as exc:
            if os.name != "nt":
                raise AssertionError(f"{label}: cannot create regression fixture") from exc
            skipped.append(label)
            continue
        try:
            for mode in ("auto", "legacy"):
                await probe_refused_alias(root, mode=mode, label=label)
            exercised.append(label)
        finally:
            link.unlink()
    if outside.read_bytes() != expected_bytes:
        raise AssertionError("outside synthetic document was modified")
    return exercised, skipped


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="beautifulrepo-mcp-") as tmp:
        workspace = Path(tmp).resolve()
        root = workspace / "fixture"
        root.mkdir()
        (root / "docs").mkdir()
        (root / "README.md").write_text(
            "# Fixture\n\n[Guide](docs/guide.md)\n", encoding="utf-8"
        )
        (root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        refusal_count, symlink_tested = check_startup_refusals(root)
        modern_healthy = await probe(
            root, broken=False, mode="auto", exercise_missing_root=True
        )
        legacy_healthy = await probe(
            root, broken=False, mode="legacy", exercise_missing_root=True
        )
        (root / "README.md").write_text(
            "# Fixture\n\n[Broken](docs/missing.md)\n", encoding="utf-8"
        )
        modern_broken = await probe(root, broken=True, mode="auto")
        legacy_broken = await probe(root, broken=True, mode="legacy")
        if modern_healthy != modern_broken or legacy_healthy != legacy_broken:
            raise AssertionError("protocol version changed within an MCP lifecycle")
        aliases_exercised, aliases_skipped = await check_external_document_aliases(root)
        print(
            f"MCP stdio SDK smoke PASS; modern discovery {modern_healthy}; "
            f"legacy initialize {legacy_healthy}; "
            "3 tools listed and matched separate direct CLI bundle runs on healthy/broken synthetic roots "
            "in both lifecycles; "
            f"fixture files unchanged; {refusal_count} unsafe startup roots refused "
            f"(symlink exercised: {symlink_tested}); missing root during an active "
            "session returns incomplete evidence for all 3 tools in both lifecycles; "
            f"outside-document aliases refused: {', '.join(aliases_exercised) or 'none'} "
            f"(untested on this platform: {', '.join(aliases_skipped) or 'none'}). "
            "Not a Claude Code/Codex host test."
        )


if __name__ == "__main__":
    asyncio.run(main())
