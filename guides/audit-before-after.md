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
symlinked/nonregular reports, duplicate JSON object keys, contradictory summary
counts, unsupported profiles and mismatched profiles. It does not invoke Git,
run target code, contact a network, modify inputs, discover repositories or
include input document paths/messages in its output. Exit code **0** means
structurally comparable reports, not an improvement; **2** means invalid or
unreadable evidence. It is not a content or security scanner, visual test,
accessibility certification, release signal or ranking system. Reports
themselves may contain relative filenames and metadata: review them before
sharing, especially for private repositories.
