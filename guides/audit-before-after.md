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

## Optional: signal increasing rule counts in a local check

When comparing two reports with comparable coverage, opt in to a nonzero
exit code for increased rule counts:

~~~sh
python -I tools/audit_delta.py before.json after.json --format markdown --fail-on-increase warning
~~~

The command still prints the complete comparison. Exit 1 means at least one
individual rule count increased at the selected severity or above: `error`
checks errors; `warning` checks errors and warnings; `info` checks all three.
A decrease in another rule does not cancel an increase. The default `never`
preserves report-only behavior. Exit 2 still indicates invalid evidence or
arguments.

This is an optional count-based signal, not a new repository merge gate.
An unchanged count can hide different findings; changed coverage can distort
counts in either direction. Review coverage and source evidence separately,
even when the command exits 0. Do not use the exit code as proof of repaired
behavior or to block a contribution without an explicit local policy.

## Optional: require unchanged audited-document coverage

For a local regression check that should stop for review when the selected
documents change, combine the two opt-in signals:

~~~sh
python -I tools/audit_delta.py before.json after.json --format markdown --fail-on-increase warning --fail-on-coverage-change
~~~

The coverage flag alone exits 1 when an entry-point role or the inspected-file
selection changes, even if every rule count decreases or stays the same.
With both flags, **either** signal triggers exit 1; the complete comparison
is still printed. Check the coverage notice and changed-rule rows to
distinguish the reasons. Invalid evidence still exits 2 without a report.
Neither flag changes the default report-only mode.

For example, adding a missing LICENSE may be a deliberate improvement and
still trigger the coverage signal. Review the source diff and evidence
before accepting such a change; do not treat the signal as a defect or a
universal merge requirement. Unchanged coverage is only a comparison of
the recorded document roles and file selection, not proof of equivalent
content, an identical auditor revision or a valid measurement.

## Preserve the comparison and its exit status in CI

The two optional signals are available in **Unreleased** source, not the
v0.2.0 Action. Start with report-only runs; inspect typical changes before
choosing a regression policy. Use the same reviewed, pinned auditor for both
reports, separate from the target PR checkout. Do not execute a PR-controlled
copy of the auditor or use a privileged fork-PR workflow. See the
[adoption guide](adopting-the-checks.md) for the runner trust boundary.

When a team opts into both signals, a shell with `set -e` would normally
stop at the first nonzero status. Capture it explicitly so the job retains
the comparison for review without turning failures into passes. From the
trusted BeautifulRepo checkout, with fresh reports in a private, writable
evidence directory (replace the example path), this Bash step leaves the
Markdown on disk and propagates the original command status:

~~~bash
evidence='/absolute/path/to/audit-evidence'
status=0
python -I tools/audit_delta.py "$evidence/before.json" "$evidence/after.json" \
  --format markdown --fail-on-increase warning --fail-on-coverage-change \
  > "$evidence/delta.md" || status=$?
case "$status" in
  0) printf '%s\n' 'No opted-in signal; review the evidence.' ;;
  1) printf '%s\n' 'Review required: inspect report and stderr.' >&2 ;;
  2) printf '%s\n' 'Invalid evidence or arguments; regenerate or repair.' >&2 ;;
  *) printf '%s\n' 'Comparison did not complete normally.' >&2 ;;
esac
exit "$status"
~~~

Run this in its own CI step, not in an interactive shell you intend to keep
open. A shell redirection failure or an abnormal interpreter exit is not an
audit finding: check stderr and confirm the report is complete before
interpreting a status of 0 or 1. Status 2 or an unexpected exit must not be
treated as a valid comparison. Avoid `|| true`, which hides both signals
and invalid evidence.

For example, a new warning with unchanged document selection calls for
review of the source change. A newly added contribution guide may instead
trigger the coverage signal even though it helps readers. Inspect that
change and approve a new baseline deliberately rather than automatically
resetting it to silence the job. A profile mismatch is invalid evidence,
not a regression to waive. Keep the original reports and revision records
private; the Markdown can be reviewed for sharing, but this recipe does
not post or upload it. A separate later artifact step, if needed, must
respect the repository's data-retention and access policy.

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
structurally comparable reports with no triggered optional signal,
not an improvement; **1** means an opted-in rule-count increase or coverage
change signal was triggered; **2** means invalid or unreadable evidence or arguments. It is not a content or security scanner, visual test,
accessibility certification, release signal or ranking system. Reports
themselves may contain relative filenames and metadata: review them before
sharing, especially for private repositories.
