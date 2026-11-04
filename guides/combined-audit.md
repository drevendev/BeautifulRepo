# Run all three offline checks together

BeautifulRepo includes three independent, zero-dependency checkers: the
[entry-point audit](../tools/repo_audit.py), the
[relative Markdown destination checker](../tools/docs_links.py), and the
[HTML/fragment navigation checker](../tools/html_navigation.py).

The [combined audit](../tools/audit_bundle.py) invokes **those actual scripts**
in sequence. It preserves their individual observations and failure states;
it does **not** invent a repository beauty score or replace the underlying tools.

## First run

Python 3.11+ and a **stable local checkout** are required. From a clone of
BeautifulRepo, point the command at another local repository directory:

```bash
python -I tools/audit_bundle.py ../your-repository
python -I tools/audit_bundle.py ../your-repository --format json
```

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

Reports can contain filenames, link targets and other project-sensitive
details. Review before sharing; avoid running on confidential material
without understanding that exposure. The wrapper does not create files
inside the checked repository or change repository settings.

For a single machine-readable entry-point report, continue to use
[repo_audit.py](../tools/repo_audit.py) directly. For detailed checker
contracts, see [the tools reference](../tools/README.md).
