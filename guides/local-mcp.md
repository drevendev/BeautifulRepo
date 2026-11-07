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

### Reproduce an immutable development checkout (POSIX)

This **source-checked procedure, reviewed 2026-11-07, has not passed a fresh
Claude Code/Codex host installation**. Use a disposable environment. The
following full commit was on `master` after the tested stdio changes; it is
**not a released MCP version**:

[BeautifulRepo `6c01779cce2ce7f63ceec15f762678c443086478`](https://github.com/drevendev/BeautifulRepo/commit/6c01779cce2ce7f63ceec15f762678c443086478).

Run these commands from a writable **disposable parent directory** on
macOS/Linux with Git and Python 3.11+ installed:

```sh
git clone https://github.com/drevendev/BeautifulRepo.git
cd BeautifulRepo
git checkout --detach 6c01779cce2ce7f63ceec15f762678c443086478
git rev-parse HEAD
python3 -m venv ../beautifulrepo-mcp-venv
../beautifulrepo-mcp-venv/bin/python -m pip install "mcp==2.3.0"
../beautifulrepo-mcp-venv/bin/python -I -B integrations/mcp_protocol_smoke.py
BR_PYTHON="$(cd ../beautifulrepo-mcp-venv/bin && pwd -P)/python"
BR_SERVER="$(pwd -P)/integrations/mcp_server.py"
BR_ROOT="$(pwd -P)/tests/fixtures/agent-repos/healthy"
```

Verify `git rev-parse HEAD` printed **exactly** the 40-character commit
above; do not silently substitute a newer `master`. The smoke runs the
real SDK **without a model** against temporary synthetic repositories. It
requires package download for installation; run it only if you accept the
environment/network implications. A smoke PASS validates protocol wiring,
**not** either model host. The sample `BR_ROOT` is a checked-in **synthetic**
fixture; replace it with the physical absolute path of a trusted, ordinary
repository only after reviewing data-sharing implications. The three
variables must be used in the same shell session, or replaced by their
absolute values later. Avoid private repository data during initial tests.

### Claude Code: local-scope stdio entry (host run unverified)

The [official Claude Code MCP guide](https://code.claude.com/docs/en/mcp)
documents `claude mcp add --transport stdio <name> -- <command> [args...]`
and local scope. With the shell variables from the preceding block:

```sh
claude --version
claude mcp add --scope local --transport stdio beautifulrepo-audit -- \
  "$BR_PYTHON" -I -B "$BR_SERVER" --root "$BR_ROOT"
claude mcp list
claude mcp get beautifulrepo-audit
```

Open **Claude Code** on that synthetic fixture and inspect `/mcp` for a
connected server and the three named tools. A successful `add` or `list`
alone is **only configuration evidence**. Actual acceptance still needs
an observed `tools/list` and `tools/call` via the host, with the version,
tool results, exact commit and file snapshot recorded. Model invocation may
consume subscription usage or paid tokens; obtain appropriate authorization.

Undo the **local** registration using
`claude mcp remove beautifulrepo-audit --scope local` and close the host
session. Do not commit a machine-specific `.mcp.json` to a public project
or use `--scope project` to bypass workspace approval.

### Codex CLI: stdio entry (host run unverified)

The [Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
documents `codex mcp add <name> -- <command>` and a shared
`~/.codex/config.toml` configuration for local Codex clients. With the
same shell variables, in a **separate host trial**:

```sh
codex --version
codex mcp add beautifulrepo-audit -- \
  "$BR_PYTHON" -I -B "$BR_SERVER" --root "$BR_ROOT"
codex mcp list
codex mcp get beautifulrepo-audit
```

Start a new local Codex session and inspect `/mcp` for the configured
server and tools. `codex mcp add` changes your user configuration:
do **not** confuse this with a repository-scoped or cloud plugin install.
Configuration visible in the CLI is not evidence of a host tool invocation.
Record actual calls and `PASS/FAIL/INCONCLUSIVE` separately from the Claude
Code run; do not use model calls without usage/cost authorization.
Remove the entry with `codex mcp remove beautifulrepo-audit`.

On **Windows**, use drive-qualified absolute `python.exe`, server and root
paths, and the host's Windows command quoting. POSIX `bin/python` paths
above do not apply. Neither Windows host setup nor a real legacy model-host lifecycle has been
proven by these instructions. The separate SDK smoke exercises a legacy
`initialize` connection, which is **not** evidence of Claude Code/Codex
using that lifecycle.

### Report a real host result

Record host/CLI version, OS, Python and MCP SDK version, the **installed**
Git SHA, the configured absolute root, actual discovered tool names,
negotiated protocol version (if exposed), a healthy/broken synthetic call,
whether any target file changed, raw error if present, and a result of
`PASS`, `FAIL`, or `INCONCLUSIVE`. Review/redact paths and content before
sharing a trace. See [#255](https://github.com/drevendev/BeautifulRepo/issues/255)
for acceptance criteria. No claim of Claude Code or Codex host success is made here.

## Automated SDK protocol smoke (not host acceptance)

An opt-in [real-protocol smoke script](../integrations/mcp_protocol_smoke.py)
and [focused GitHub Actions workflow](../.github/workflows/mcp-protocol.yml)
install the pinned `mcp==2.3.0` SDK in a disposable CI environment,
launch the actual server over stdio and check **both** protocol lifecycles:
modern `server/discover` (`2026-07-28`, SDK `mode="auto"`) and legacy
`initialize` (`2025-11-25`, SDK `mode="legacy"`). For each connection it
checks the negotiated version, `tools/list`, all three `tools/call` results
against direct offline checkers, and unchanged healthy/broken synthetic
fixture files. The smoke
also exercises real-process refusal of relative, missing, home and filesystem
roots, plus a symlink root where the platform permits creating one. While an
MCP client stays connected, the test temporarily renames its synthetic target
and requires **incomplete** results for all three tools in both lifecycles; the
directory is restored and its bytes rechecked. Run locally
with the optional SDK installed:

```sh
python -I -B integrations/mcp_protocol_smoke.py
```

The workflow runs on MCP/tool changes and is additional evidence, **not**
an invented repository protection gate. Record the actual CI output/version
before claiming a PASS. Denied-root checks do not prove defenses against
concurrent filesystem replacement or hostile mounts, and missing-root tests
do not measure a checker timeout. A successful smoke demonstrates only the **pinned Python SDK's own** modern
and legacy stdio client modes, not compatibility with independently implemented
older clients. It is not a clean install from an immutable public commit, a
Claude Code/Codex host session, model invocation, or external-user trial.
See [#255](https://github.com/drevendev/BeautifulRepo/issues/255) for
the remaining acceptance requirements.

## Check and grade before release

Run source-level adapter regressions with the ordinary repository test suite:

```sh
python -m unittest discover -s tests -v
python -I tools/audit_bundle.py /absolute/path/to/synthetic-fixture --format json
```

Source-level tests check path refusal, fixed subprocess arguments, timeout
behavior, incomplete evidence and one actual broken-link fixture. These are
**not** protocol tests. For MCP acceptance, confirm the SDK smoke passes for both protocol eras,
including negotiated versions, `tools/list` and `tools/call` on good and
broken synthetic repositories. This still does not verify a third-party
legacy client. Then connect actual
Claude Code and Codex hosts independently and record fresh install/discovery
and real tool invocations; follow [issue #255](https://github.com/drevendev/BeautifulRepo/issues/255).
Do not describe either client as supported until tested. Do not run paid model
sessions without separate authorization.

**Uninstall:** remove the MCP client entry/connection, stop the stdio child,
then delete the isolated environment. This does not delete or edit the target
repository. Treat tool results as potentially private local file-path
information; never publish host transcripts without review.
