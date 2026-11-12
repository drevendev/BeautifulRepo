# Experimental local MCP adapter (not a released integration)

**Development candidate, reviewed 2026-11-11 (UTC).** This optional adapter exposes
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
call. Root validation checks each directory ancestor for symlink/junction
redirects rather than comparing resolved and requested path spellings, which
can differ on ordinary Windows checkouts. Parent-traversal components remain
invalid. This is **not** a sandbox against concurrent filesystem replacement,
malicious OS-level mounts or secrets in ordinary repository documentation.
The child interpreter runs the fixed checked-in `audit_bundle.py` with
`-I -B`, a fixed argument vector, a 30-second timeout and a 512 KiB
per-stream response limit. Each MCP tool selects **only its own checker**
(`--only entry_points`, `markdown_links` or `html_navigation`), rather
than rerunning all three and potentially failing because an unrelated
checker's diagnostics exhaust the response budget. The public combined
CLI still runs all three by default. Child stdout/stderr are drained concurrently through bounded pipes; if
either stream exceeds 512 KiB the child is stopped rather than storing more
output in memory or on disk. Evidence is checked before parsing. This fixes
the former temporary-file disk-growth exposure; it does **not** turn the
trusted-root adapter into a general filesystem or process sandbox.
Before any of the three checkers starts, the adapter also makes a metadata-only,
fail-closed pass over the stable checkout: at most 50,000 directory entries,
5,000 Markdown sources, 2 MiB per Markdown source and 32 MiB total,
with a five-second preflight deadline. It skips `.git` and `node_modules`
like the link checkers and refuses Markdown-named devices, redirects outside
the repository, and hard-linked regular files (including extensionless
entry points and non-Markdown documents) whose in-root names could alias
files outside the checkout. Copy fixtures rather than using hard links. A limit or unreadable source returns **incomplete evidence**
(exit 2), not a clean audit. This is **not** a stable filesystem snapshot,
concurrent-write protection or a general limit on non-Markdown contents;
the standalone CLI has its own coverage boundaries.
The checkers do not execute target code or fetch external links. MCP clients
and model hosts **may transmit returned findings to their providers**.

## Local use versus directory distribution

**Submission requirements reviewed 2026-11-07; no submission made.**
Installing the experimental adapter with `claude mcp add` or
`codex mcp add` is a **manual local configuration**, not a packaged,
approved or published plugin. OpenAI's official
[desktop-only plugin submission rules](https://developers.openai.com/plugins/deploy/desktop-only)
currently limit **local stdio MCP submissions** to approved partners whose
organization is allowlisted. The
[plugin submission guide](https://developers.openai.com/plugins/deploy/submission)
also says an MCP server cannot later be added to an **already submitted
skills-only plugin** through a normal plugin update. These are **OpenAI
Plugin Directory rules**, not proof that local CLI registration works, nor
rules for an independent MCP Registry listing or Claude Code marketplace.

For now, test this adapter separately from BeautifulRepo's four-skill
development candidate. Do not promise a directory installation, a remote
ChatGPT connection or that any existing skills-only package will
automatically gain MCP tools. Publication, registration, eligibility checks
and external submissions remain outside this development trial and require
separate owner authorization.

## Install and connect (untested development instructions)

The official [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/) v2
provides `MCPServer` and the modern `2026-07-28` discovery flow while
supporting legacy `initialize` clients. Version `2.3.0` was published to
[PyPI](https://pypi.org/project/mcp/2.3.0/) on 2026-10-02. Pin the package
and the *BeautifulRepo Git commit* during an independent installation trial;
do not substitute a floating branch and claim the results are reproducible.

### Reproduce an immutable development checkout (POSIX)

This **source-checked procedure, refreshed 2026-11-11 (UTC), has not passed a fresh
Claude Code/Codex host installation**. Use a disposable environment. The
following full commit is a `master` snapshot containing both SDK protocol
smoke lifecycles, per-checker isolation, bounded child output, missing-root
and hard-link/symlink boundary cases, and source-level regressions for
unrecognized Windows reparse points (including attribute-only redirects).
It includes the [hard-link coverage fix](https://github.com/drevendev/BeautifulRepo/pull/324)
and [Windows reparse hardening](https://github.com/drevendev/BeautifulRepo/pull/345).
The Windows reparse tests use **mocked filesystem metadata**; no real NTFS
reparse-point host test or Claude Code/Codex installation PASS is claimed.
Older immutable trial commits such as `3c1040`, `331df37`, and
`8c1d1523` lack later boundary fixes. This commit is **not a released MCP version**:

[BeautifulRepo `ed1e70c0e41833fd2b60a8431e1e3134107bf3ac`](https://github.com/drevendev/BeautifulRepo/commit/ed1e70c0e41833fd2b60a8431e1e3134107bf3ac).

Run these commands from a writable **disposable parent directory** on
macOS/Linux with Git and Python 3.11+ installed:

```sh
git clone https://github.com/drevendev/BeautifulRepo.git
cd BeautifulRepo
git checkout --detach ed1e70c0e41833fd2b60a8431e1e3134107bf3ac
test "$(git rev-parse HEAD)" = "ed1e70c0e41833fd2b60a8431e1e3134107bf3ac" || exit 1
python3 -m venv ../beautifulrepo-mcp-venv
../beautifulrepo-mcp-venv/bin/python -m pip install "mcp==2.3.0"
../beautifulrepo-mcp-venv/bin/python -I -B integrations/mcp_protocol_smoke.py
BR_PYTHON="$(cd ../beautifulrepo-mcp-venv/bin && pwd -P)/python"
BR_SERVER="$(pwd -P)/integrations/mcp_server.py"
BR_ROOT="$(pwd -P)/tests/fixtures/agent-repos/healthy"
```

The `test` command stops this POSIX procedure if the checkout is not
**exactly** the 40-character commit above; do not silently substitute a
newer `master`. The smoke runs the real SDK **without a model** against
temporary synthetic repositories. It requires package download for installation; run it only if you accept the
environment/network implications. A smoke PASS validates protocol wiring,
**not** either model host. The sample `BR_ROOT` is a checked-in **synthetic**
fixture; replace it with the physical absolute path of a trusted, ordinary
repository only after reviewing data-sharing implications. The three
variables must be used in the same shell session, or replaced by their
absolute values later. Avoid private repository data during initial tests.

### Windows PowerShell: immutable source and SDK preflight (unverified host)

The POSIX `bin/python` path above is **not** a Windows path. For an
isolated PowerShell trial on Windows, use a Python **3.11+** launcher and
Git. This example selects Python 3.11; if only a newer supported version
is installed, change `py -3.11` to the installed launcher selection.
These commands have **not** been executed in a Windows host in this
project. The smoke is an SDK test, not Claude Code or Codex acceptance.

Run in a disposable parent directory; PowerShell command failures are
checked explicitly rather than assuming `$ErrorActionPreference` catches
external program exit codes:

```powershell
$pin = 'ed1e70c0e41833fd2b60a8431e1e3134107bf3ac'
git clone https://github.com/drevendev/BeautifulRepo.git
if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
Set-Location BeautifulRepo
git checkout --detach $pin
if ($LASTEXITCODE -ne 0) { throw 'Checkout failed' }
$actual = (git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actual -ne $pin) { throw 'Unexpected Git SHA' }
py -3.11 -m venv ..\beautifulrepo-mcp-venv
if ($LASTEXITCODE -ne 0) { throw 'Venv creation failed' }
$brPython = (Resolve-Path ..\beautifulrepo-mcp-venv\Scripts\python.exe).Path
& $brPython -m pip install 'mcp==2.3.0'
if ($LASTEXITCODE -ne 0) { throw 'SDK install failed' }
& $brPython -I -B .\integrations\mcp_protocol_smoke.py
if ($LASTEXITCODE -ne 0) { throw 'SDK smoke failed' }
$brServer = (Resolve-Path .\integrations\mcp_server.py).Path
$brRoot = (Resolve-Path .\tests\fixtures\agent-repos\healthy).Path
```

Keep the variables in the **same PowerShell session** for the host
registration examples below. `Resolve-Path` returns drive-qualified
absolute paths, including when the parent directory contains spaces.
An SDK smoke success is **not** a host connection or model-tool-call PASS.
Do not test on a confidential repository or assume a fresh install succeeds
just because these source-reviewed commands are provided.

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

For a **Windows PowerShell** host trial, use the variables from the Windows
preparation block instead of the POSIX environment variables:

```powershell
claude --version
claude mcp add --scope local --transport stdio beautifulrepo-audit -- $brPython -I -B $brServer --root $brRoot
claude mcp list
claude mcp get beautifulrepo-audit
```

These are unverified host commands, not an observed installation.
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

For a **Windows PowerShell** host trial, using the same `$brPython`,
`$brServer`, and `$brRoot` variables from the Windows preparation block:

```powershell
codex --version
codex mcp add beautifulrepo-audit -- $brPython -I -B $brServer --root $brRoot
codex mcp list
codex mcp get beautifulrepo-audit
```

Neither Windows host setup nor a real legacy model-host lifecycle has been
verified here. The separate SDK smoke exercises legacy `initialize` but is
**not** evidence that Claude Code or Codex uses that lifecycle.

### Report a real host result

Record host/CLI version, OS, Python and MCP SDK version, the **installed**
Git SHA, the configured absolute root, actual discovered tool names,
negotiated protocol version (if exposed), a healthy/broken synthetic call,
whether any target file changed, raw error if present, and a result of
`PASS`, `FAIL`, or `INCONCLUSIVE`. Review/redact paths and content before
sharing a trace. See [#255](https://github.com/drevendev/BeautifulRepo/issues/255)
for acceptance criteria. No claim of Claude Code or Codex host success is made here.

## Automated SDK protocol smoke (not host acceptance)

The optional [MCP workflow](../.github/workflows/mcp-protocol.yml) runs the
same pinned Python 3.11 / `mcp==2.3.0` protocol exercise independently on
`ubuntu-latest` and `windows-latest`. The jobs use GitHub's official
[OS matrix pattern](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
and `fail-fast: false` so a Windows failure cannot be hidden by a Linux
success, or vice versa. Inspect **each** job result and log: on Windows,
symlink creation may be reported as **untested**, which is not symlink
coverage. This smoke does not create a native Windows junction (that has a
separate Windows-only source-level regression), does not run an actual
Claude Code or Codex host, and does not establish model behavior or external
installation. Do not mark cross-platform protocol PASS until both jobs
actually complete successfully on the same commit.

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
directory is restored and its bytes rechecked. The current development smoke
also creates a synthetic file **outside** the repository, exposes it as a
hard-linked `LICENSE` and as an outside-pointing Markdown symlink, and demands
`incomplete` (exit 2) from **all three tools** through both SDK lifecycles.
Link creation that a platform does not permit is explicitly reported as
**untested**, not PASS. This is a protocol-level boundary regression, not proof
of resistance to concurrent filesystem replacement. The immutable host-trial checkout pinned above includes these smoke
cases, but the SDK's own clients are not independent Claude Code or Codex
hosts. Run locally
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
behavior, incomplete evidence and one actual broken-link fixture. On Windows,
the `test_real_windows_junction_ancestor_rejected_before_any_checker`
regression additionally attempts to create a **real directory junction** with
[`mklink /J`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mklink)
and checks that both a junction root and a nested root through it are refused
**before** a checker launches, without changing synthetic source bytes.
The test skips on non-Windows systems or when junction creation is unavailable:
inspect the named test's actual CI result rather than counting a skipped test
as native NTFS evidence. This does **not** test arbitrary reparse-point types,
host/model discovery, or a concurrent filesystem-swap attack. These are
**not** protocol tests.

For MCP acceptance, confirm the SDK smoke passes for both protocol eras,
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
