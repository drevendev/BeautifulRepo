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

- Exit **0**: all three checkers completed and the chosen threshold was clear.
  Warnings and information can still appear.
- Exit **1**: one or both link checkers found issues, or the entry-point
  threshold was reached. Inspect the actual rule and source location.
- Exit **2**: incomplete evidence (invalid root, failed checker, output
  overflow, or timeout). Treat the entire combined result as **inconclusive**,
  even if another checker completed.

The JSON report is deterministic for the same stable checkout and tool
revision. It has `schema_version: 1`, an `exit_code`, a `coverage` warning,
and separate `checks`: `entry_points`, `markdown_links`, and
`html_navigation`. The entry-point result contains its unchanged nested
`repo_audit.py` report; link results retain their native stdout and
stderr diagnostics. A `state: incomplete` entry has a generic reason
instead of pretending an unrun or truncated check passed.

## Boundaries and privacy

The wrapper starts only three fixed, checked-in Python scripts using
`python -I -X utf8`, without a shell and without running code from the
target. Each invocation has a 20-second timeout, with 128 KiB accepted
from each output stream; an excess is **incomplete**, never silently
truncated into a success. Output spools to operating-system temporary
files, so these limits are **not** a hard disk-usage quota. The individual
link checkers retain their own documented scan limits and syntax gaps.

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
