# Run all three offline checks together

BeautifulRepo includes three independent, zero-dependency checkers: the
[entry-point audit](../tools/repo_audit.py), the
[relative Markdown destination checker](../tools/docs_links.py), and the
[HTML/fragment navigation checker](../tools/html_navigation.py).

The [combined audit](../tools/audit_bundle.py) invokes **those actual scripts**
in sequence. It preserves their individual observations and failure states;
it does **not** invent a repository beauty score or replace the underlying tools.

## First run

Use Python **3.11+**, Git and a stable local target. From the **parent
directory** containing your target as `your-repository/`, clone the tools
beside it and check out a reviewed, immutable development snapshot:

```bash
git clone https://github.com/drevendev/BeautifulRepo.git
cd BeautifulRepo
git checkout --detach 28530c997bf6e0df4406c271f77dd21482e40781
python -I tools/audit_bundle.py ../your-repository --fail-on never
python -I tools/audit_bundle.py ../your-repository --format json
```

Replace `your-repository` with your real sibling folder. The detached pin
ensures the commands use the same source revision rather than a moving
`master` branch. It is **not** a new release: the released `v0.2.0`
Action does not include `audit_bundle.py`. `git clone` fetches from
GitHub; the Python checkers do not fetch external URLs or run target code.
Inspect the exit status of each Python command before treating its output
as complete. The local CI clone smoke exercises its tested branch HEAD,
not an independently observed remote clone of this pin.


## Windows PowerShell first run

From the **parent directory** containing `your-repository\` (rename that
placeholder to the folder you actually own), clone BeautifulRepo beside it.
Run the same **read-only**, dependency-free checker in PowerShell:

```powershell
git clone https://github.com/drevendev/BeautifulRepo.git
if ($LASTEXITCODE -ne 0) { throw "Git clone failed" }
Set-Location .\BeautifulRepo
git checkout --detach 28530c997bf6e0df4406c271f77dd21482e40781
if ($LASTEXITCODE -ne 0) { throw "Pinned checkout failed" }
python --version
if ($LASTEXITCODE -ne 0) { throw "Python not available" }
python -I .\tools\audit_bundle.py ..\your-repository --fail-on never
$LASTEXITCODE
```

Use Python **3.11 or later**. The final PowerShell expression prints the
Python process status: **0** when the selected threshold is clear, **1** for
broken local links or threshold-reaching findings, **2** for invalid roots or
incomplete evidence. The result also ends with `Exit N:`. PowerShell does
not automatically stop a session when a native command exits nonzero; do not
interpret that as a passing audit. `--fail-on never` only makes *entry-point*
findings advisory, not broken local links. If `python` is unavailable, install
Python 3.11+ and ensure its command is on PATH; do not substitute a different
unchecked interpreter or install packages into the target.

The pinned checkout is a reviewed development snapshot, not a new stable
release. This path is checked using a fresh **local** sibling Git clone of
the CI source revision on Windows; the remote pinned-revision checkout and
actual first-time end-user PowerShell session have not been independently
observed. The audit
does not edit either checkout. Do not run it on a sensitive private target
without first reviewing what source paths and diagnostics its output reveals.

For an optional **standalone HTML report** from the same three checks, redirect
stdout **outside** the target checkout:

```bash
python -I tools/audit_bundle.py ../your-repository --format html > audit-report.html
```

This retains exit codes 0/1/2 even when redirecting stdout. It creates one
local HTML document with semantic headings and lists, browser light/dark
system colors, no scripts, and no external assets or web requests. Path and
diagnostic strings (including terminal control characters) are escaped, but
**filenames and messages may still be sensitive**. This is a source-evidence
view, not a manual browser/accessibility certification. Invalid roots emit
stderr and exit 2 with no HTML; a shell redirect may still create an **empty**
report file. Check the exit status and content before sharing.

The default entry-point threshold is `error`. Use `--fail-on warning` to
include entry-point warnings in the exit status, or `--fail-on never` for an
advisory entry-point review. **Neither option suppresses broken local links**
reported by either link checker.

When a repository contains vendored or generated Markdown sources that should
not be audited, repeat `--exclude GLOB` to skip their sources in **both link
checkers**. The syntax follows the underlying local link checkers, matching
root-relative file or directory paths; excluded files remain valid destinations
from included documentation. This option does **not** change entry-point checks:

```bash
python -I tools/audit_bundle.py ../your-repository --exclude vendor --exclude "build/**"
```

Review exclusions carefully: they reduce link-check coverage, not findings
inside the entry-point audit. The JSON per-checker source counts show the scope.

- Exit **0**: all three checkers completed and the chosen threshold was clear.
  Warnings and information can still appear.
- Exit **1**: one or both link checkers found issues, or the entry-point
  threshold was reached. Inspect the actual rule and source location.
- Exit **2**: incomplete evidence (invalid root, failed checker, output
  overflow). Treat the entire combined result as **inconclusive**,
  even if another checker completed.

The JSON report is deterministic for the same stable checkout and tool
revision. It has `schema_version: 1`, an `exit_code`, a `coverage` warning,
and separate `checks`: `entry_points`, `markdown_links`, and
`html_navigation`. The entry-point result contains its unchanged nested
`repo_audit.py` report; link results retain their native diagnostics and inspected-source counts. A `state: incomplete` entry has a generic reason
instead of pretending an unrun or truncated check passed.

## Boundaries and privacy

The wrapper imports only the three fixed, checked-in Python checker modules,
never the target project. It launches **no subprocesses or network clients**.
Per-checker structured results are capped at 128 KiB; an excess is
**incomplete**, never silently truncated into a success. This is a returned
result cap, **not** a time, memory or filesystem-usage bound. The individual
checkers retain their own documented scan limits and syntax gaps. Use a stable,
ordinary local checkout, not an adversarial filesystem.

All three tools read repository-owned files locally. None intentionally
fetches remote links. This wrapper is **not** a security boundary against a
hostile or concurrently changing filesystem, an MCP server, an accessibility
certification, a Markdown renderer, or a hosted scanner. It cannot detect
whether external websites are reachable or whether an agent will transmit
tool results to a model provider.

In the human-readable report, unprintable Unicode control/format characters
from filenames or diagnostics are escaped on the same physical line (for
example, a newline becomes \u000a and an ANSI escape becomes \u001b).
Ordinary printable Unicode is preserved. JSON mode still uses its native
string encoding. This prevents a source filename from forging extra terminal
report lines; it does not make hostile filesystem traversal safe.

Reports can contain filenames, link targets and other project-sensitive
details. Review before sharing; avoid running on confidential material
without understanding that exposure. The wrapper does not create files
inside the checked repository or change repository settings.

For a single machine-readable entry-point report, continue to use
[repo_audit.py](../tools/repo_audit.py) directly. For detailed checker
contracts, see [the tools reference](../tools/README.md).
