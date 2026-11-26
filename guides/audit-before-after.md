# Compare repository entry-point audits without claiming a beauty score

When you improve a README, license or contribution route, you can compare **two
saved BeautifulRepo audit reports**. The [audit](repository-audit.md) inspects
selected entry-point documents, not the whole repository or its rendered UI.
The comparison counts rule occurrences by **severity and rule ID**; it does
not claim to know whether a finding at a particular line was truly fixed.

## Run against two stable snapshots

From a BeautifulRepo checkout with Python 3.11+, create two ordinary local
checkout directories for the revisions under review. Choose the audit profile
(public, internal or private) explicitly and use **the same** profile for
both snapshots. These commands only read the snapshots and print JSON. The shell
redirects the reports to files outside the target repositories:

~~~sh
python -I tools/repo_audit.py /path/to/before --profile public --format json --fail-on never > before.json
python -I tools/repo_audit.py /path/to/after --profile public --format json --fail-on never > after.json
python -I tools/audit_delta.py before.json after.json
python -I tools/audit_delta.py before.json after.json --format json
python -I tools/audit_delta.py before.json after.json --format markdown > audit-delta.md
~~~

Replace the paths with real, immutable checkouts; record their **full Git commit
SHAs** alongside the report files in your case-study notes. The audit flag
--fail-on never lets you save complete evidence even when the input has audit
errors. It does **not** turn those findings into passes or change the report.
Check each command's exit code and stderr before treating its output as evidence.

For a tiny self-contained demonstration, the [repository-audit
walkthrough](../examples/repository-audit/README.md) has fictional before/after
sources and explicitly leaves unresolved warnings. Do not present those
examples as measurements of another project's deployed software.

For a pull request or case study, the Markdown format produces a copyable
severity table, changed-rule table and coverage notice. Review the result
before pasting it into a public discussion. No source filenames or finding
messages are copied into the generated Markdown, but the saved JSON reports
may contain private paths. Markdown uses the same input validation and exit
codes as the text/JSON views; it cannot certify that either report is genuine.
On rejection, known violations such as a redirected report, oversized evidence or
duplicate JSON keys retain a specific error category without printing the
input path. Unreadable files and generic JSON parsing errors still receive a
path-free generic message; no diagnostic authenticates the report.

## Optional: prepare both snapshots without switching your working branch

For a **trusted local Git repository** with both revisions already available,
use detached [Git worktrees](https://git-scm.com/docs/git-worktree)
(documentation reviewed 2026-11-25). This avoids switching your current branch
or stashing its edits. Git creates checkout files and updates its worktree
metadata: this preparation is not read-only. Checkout can invoke configured
hooks or filters; do not use this recipe for an untrusted Git environment.

Run from a clean, reviewed BeautifulRepo checkout. Replace all four example
values below. Choose a new evidence directory with an existing parent,
outside both repositories, in a location appropriate for private reports.
These POSIX shell commands stop on the first failure and preserve partial
evidence for inspection; do not continue using a failed preparation.

~~~sh
target='/absolute/path/to/target'
before='BEFORE_COMMIT'
after='AFTER_COMMIT'
evidence='/absolute/path/to/new-audit-evidence'

(
  set -eu
  before_sha=$(git -C "$target" rev-parse --verify --end-of-options "$before^{commit}")
  after_sha=$(git -C "$target" rev-parse --verify --end-of-options "$after^{commit}")
  mkdir "$evidence"
  printf 'before=%s\nafter=%s\n' "$before_sha" "$after_sha" > "$evidence/revisions.txt"
  git -C "$target" worktree add --detach "$evidence/before" "$before_sha"
  git -C "$target" worktree add --detach "$evidence/after" "$after_sha"
  test "$(git -C "$evidence/before" rev-parse HEAD)" = "$before_sha"
  test "$(git -C "$evidence/after" rev-parse HEAD)" = "$after_sha"
  git rev-parse HEAD > "$evidence/auditor-revision.txt"
  python -I tools/repo_audit.py "$evidence/before" --profile public --format json --fail-on never > "$evidence/before.json"
  python -I tools/repo_audit.py "$evidence/after" --profile public --format json --fail-on never > "$evidence/after.json"
  python -I tools/audit_delta.py "$evidence/before.json" "$evidence/after.json" --format markdown > "$evidence/delta.md"
)
~~~

Only use the generated delta if the block succeeds. Use the same profile in
both commands; select the internal or private profile for those targets.
Worktrees contain tracked checkout content, not uncommitted edits, ignored
local configuration or initialized submodule content. Review that limitation
before comparing results. Keep the reports and revision records together;
a recorded auditor SHA identifies the commit, not uncommitted auditor edits.

After reviewing the evidence, remove only the two linked worktrees:

~~~sh
git -C "$target" worktree remove "$evidence/before"
git -C "$target" worktree remove "$evidence/after"
~~~

Do not add `--force` if removal refuses a dirty worktree. Inspect and preserve
any local changes first. The reports and revision records remain in the
evidence directory; review their confidentiality before sharing.

## Interpreting the output

The tool prints the before and after totals for error, warning and info,
then only rules whose **occurrence counts changed**. For example, a line of
“WARNING [readme.placeholder]: 2 -> 1 (-1)” would say exactly that one fewer
placeholder warning was detected. It does **not** establish which placeholder
was repaired or whether the final README is better. If coverage_changed is
true, the tool reports which **entry-point roles** changed (README,
license or contribution document) and whether the set of inspected files
changed, including before/after file counts. It deliberately withholds the
actual filenames to avoid echoing private report paths. A switch between two
files can have identical counts; compare both saved reports privately to
understand the cause. Even unchanged coverage does not prove that two checkouts
have identical runtime behavior.

For reproducibility, use the same pinned BeautifulRepo audit implementation on
both snapshots. The comparison validates source schema v1 and equal audit
profiles, but cannot establish that two JSON files came from that same tool
version. Record its commit SHA independently. For a real case, accompany the
counts with a human-reviewed diff, actual checkout or browser observations,
remaining findings and known limits.

## Safety and limits

[audit_delta.py](../tools/audit_delta.py) uses Python's standard library,
reads at most **1 MiB per report** and 4,096 findings, rejects
symlinked lexical parent paths, detected Windows reparse points, nonregular
reports, duplicate JSON object keys, non-standard numeric literals (`NaN`,
`Infinity`, `-Infinity`), contradictory summary counts,
unsupported profiles and mismatched profiles. This path check is a preflight,
not a race-resistant sandbox or a guarantee for unusual filesystem features. It does not invoke Git,
run target code, contact a network, modify inputs, discover repositories or
include input document paths/messages in its output. Exit code **0** means
structurally comparable reports, not an improvement; **2** means invalid or
unreadable evidence. It is not a content or security scanner, visual test,
accessibility certification, release signal or ranking system. Reports
themselves may contain relative filenames and metadata: review them before
sharing, especially for private repositories.
