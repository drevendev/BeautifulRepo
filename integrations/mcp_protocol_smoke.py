#!/usr/bin/env python3
"""Optional real-SDK MCP stdio smoke test (no LLM calls or remote services).

Install mcp==2.3.0 in a disposable environment before running this script.
It launches the actual local adapter, negotiates MCP, lists and calls all
three tools on healthy/broken synthetic fixtures, and checks for target writes.
It does NOT test Claude Code, Codex, or external-user installation.
"""
from __future__ import annotations

import asyncio
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile

from mcp import Client, StdioServerParameters

SERVER = Path(__file__).resolve().with_name("mcp_server.py")
SPEC = importlib.util.spec_from_file_location("beautifulrepo_mcp_server", SERVER)
assert SPEC is not None and SPEC.loader is not None
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)
CHECKS = adapter.CHECKS
run_check = adapter.run_check


def snapshot(root: Path) -> dict[str, str]:
    """Detect additions/deletions as well as changed file contents."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


async def probe(root: Path, *, broken: bool) -> str:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-I", "-B", str(SERVER), "--root", str(root)],
    )
    before = snapshot(root)
    async with Client(params) as client:
        version = str(client.protocol_version)
        if not version or version == "None":
            raise AssertionError("no negotiated MCP version")
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
            expected = run_check(root, name)
            if response.structured_content != expected:
                raise AssertionError(
                    f"MCP result differs from CLI for {name}: "
                    f"{response.structured_content!r} != {expected!r}"
                )
            if expected["state"] != "complete":
                raise AssertionError(f"incomplete fixture: {name}: {expected!r}")
            if name == "check_documentation_links":
                if expected["exit_code"] != (1 if broken else 0):
                    raise AssertionError(f"incorrect broken-link result: {expected!r}")
    if before != snapshot(root):
        raise AssertionError("MCP checker created, removed, or modified fixture files")
    return version


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="beautifulrepo-mcp-") as tmp:
        root = Path(tmp).resolve()
        (root / "docs").mkdir()
        (root / "README.md").write_text(
            "# Fixture\n\n[Guide](docs/guide.md)\n", encoding="utf-8"
        )
        (root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        healthy_version = await probe(root, broken=False)
        (root / "README.md").write_text(
            "# Fixture\n\n[Broken](docs/missing.md)\n", encoding="utf-8"
        )
        broken_version = await probe(root, broken=True)
        if healthy_version != broken_version:
            raise AssertionError("protocol version changed across identical client settings")
        print(
            f"MCP stdio SDK smoke PASS; negotiated {healthy_version}; "
            "3 tools listed and matched direct checkers on healthy/broken synthetic roots; "
            "fixture files unchanged. Not a Claude Code/Codex host test."
        )


if __name__ == "__main__":
    asyncio.run(main())
