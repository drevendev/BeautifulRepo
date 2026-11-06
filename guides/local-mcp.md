# Experimental local MCP adapter (not a released integration)

**Development candidate, reviewed 2026-11-06.** This optional adapter exposes
BeautifulRepo's *existing* offline checkers as three read-only tools over MCP
stdio. No successful Claude Code, Codex, or external-user installation is
claimed. The normal CLI and GitHub Action do **not** require MCP.

## Scope and boundaries

The tools are `audit_repository` (entry-point findings),
`check_documentation_links` (local Markdown destinations), and
`check_html_navigation` (local HTML/media/heading anchors).
They return the original checker report/diagnostics, including incomplete
coverage and native link exit codes. No beauty score, remote link scanner,
rendered accessibility test, GitHub write, README editor or repository runner
is included. All three tools are **argument-free**: their root is fixed when
the server starts, so the model cannot select another directory.

Only use a trusted, stable local checkout containing synthetic or otherwise
approved documentation. The adapter rejects relative, missing, redirected,
home and filesystem root directories; it rechecks the bound path on each tool
call. This is **not** a sandbox against concurrent filesystem replacement,
malicious OS-level mounts or secrets in ordinary repository documentation.
The child interpreter runs the fixed checked-in `audit_bundle.py` with
`-I -B`, a fixed argument vector, a 30-second timeout and bounded output.
The checkers do not execute target code or fetch external links. MCP clients
and model hosts **may transmit returned findings to their providers**.

## Install and connect (untested development instructions)

The official [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/) v2
provides `MCPServer` and the modern `2026-07-28` discovery flow while
supporting legacy `initialize` clients. Version `2.3.0` was published to
[PyPI](https://pypi.org/project/mcp/2.3.0/) on 2026-10-02. Pin the package
and the *BeautifulRepo Git commit* during an independent installation trial;
do not substitute a floating branch and claim the results are reproducible.

From an **explicitly pinned** BeautifulRepo checkout and a freshly created
Python 3.11+ environment:

```sh
python -m pip install "mcp==2.3.0"
python -I -B tools/mcp_server.py --root /absolute/path/to/your-checkout
```

The command is a long-running **stdio** server: no output on stdout before
an MCP client connects is expected. A client should launch the Python
interpreter from its own environment and pass the absolute path to
`tools/mcp_server.py`, followed by `--root` and the *one allowed repository*.
No `cwd`, plugin auto-discovery or external installation is assumed.

A development-only example of the required process shape (not a verified
client-specific configuration):

```json
{
  "command": "/absolute/path/to/venv/bin/python",
  "args": [
    "-I", "-B", "/absolute/path/to/BeautifulRepo/tools/mcp_server.py",
    "--root", "/absolute/path/to/target-repository"
  ]
}
```

Windows uses its own absolute `python.exe` and drive-qualified paths.
Do not infer Windows acceptance from this example.

## Check and grade before release

Run source-level adapter regressions with the ordinary repository test suite:

```sh
python -m unittest discover -s tests -v
python -I tools/audit_bundle.py /absolute/path/to/synthetic-fixture --format json
```

Source-level tests check path refusal, fixed subprocess arguments, timeout
behavior, incomplete evidence and one actual broken-link fixture. These are
**not** protocol tests. For MCP acceptance, independently connect the SDK
client and verify the negotiated protocol version, `tools/list`, and
`tools/call` on a good and broken synthetic repository. Then connect actual
Claude Code and Codex hosts independently and record fresh install/discovery
and real tool invocations; follow [issue #255](https://github.com/drevendev/BeautifulRepo/issues/255).
Do not describe either client as supported until tested. Do not run paid model
sessions without separate authorization.

**Uninstall:** remove the MCP client entry/connection, stop the stdio child,
then delete the isolated environment. This does not delete or edit the target
repository. Treat tool results as potentially private local file-path
information; never publish host transcripts without review.
