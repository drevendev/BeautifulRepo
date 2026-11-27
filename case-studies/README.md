# Case studies

Real applications of the handbook to real repositories. Each case follows the same
procedure, so cases can be compared, and every claim can be traced to a revision, a
command or an observation. An **in-progress** case documents which parts of that
procedure have not been executed; a source comparison alone is not a finished case.

| Case | Repository | Status |
| --- | --- | --- |
| [README before/after](readme-first-success-case.md) | BeautifulRepo | complete; written before this procedure, which it shaped |
| [Offline first success](patchpitch.md) | PatchPitch | complete; change merged as PatchPitch#90 |
| [Milestone-claim drift](trade_simulation.md) | trade_simulation | in progress; pinned clone audits and live 320 px light/dark observations, broader accessibility/deployment proof pending |
| [First-run and reporting-route baseline](quillgrain.md) | Quillgrain + Quillgrain_Voice_Common | source-only baseline; no target PR or run evidence yet |
| [HungryCrab first command](hungrycrab-first-command.md) | HungryCrab (public) | source-only; pinned evidence and proposed first-screen copy, no target change or runtime test |
| [One local verification command](checkout-verification.md) | BeautifulRepo | merged source + CI evidence, first-use observation incomplete |
| [First pattern studies](first-patterns.md) | Devostasis, Hungry Crab, Gum | source observations only, no changes made |

## Source-only reviews: useful, but not a before/after

A **source-only** study can help a reader when no upstream patch or actual
first-run test exists. Use the [anonymous public-source verification recipe](../guides/public-source-verification.md)
for a copyable no-credential preflight, then the [source-only case template](../templates/SOURCE_ONLY_CASE.template.md)
to record an editorial proposal without claiming a completed intervention.
The [HungryCrab study](hungrycrab-first-command.md) demonstrates this evidence class.

**Check public reproducibility first:** inspect the exact target commit and
source-file permalinks without a privileged account, record the method and
date, and confirm an independent visitor can see them. Being able to fetch
a private repository with an authenticated connector does **not** make it a
public case study. A 404 is *inconclusive* (private, deleted, incorrect path,
permissions, rate limiting or transient errors). If public evidence cannot
be confirmed, **defer** rather than publish privileged source details. A
fictional example may be created independently, but must not leak private facts.

Use full commit SHAs for inspected files; separately date visibility, releases,
security settings and other metadata that Git does not freeze. Mark commands,
rendering, target changes and external-host checks **NOT RUN / NONE** when absent.
Even public, unlicensed source is not permission to reproduce its code or
images; see [rights and quoting](#rights-and-quoting).

This procedure is an editorial reproducibility gate, not a guarantee of
usability or public availability forever. Reference: [GitHub's README
guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
and [Open Source Guides' starting-a-project checklist](https://opensource.guide/starting-a-project/),
reviewed **2026-11-18**.

## The procedure

A case changes the target through that repository's normal pull request. It never edits
another repository without its owner's permission. The steps below are the minimum.

### 1. Snapshot "before"

- The full commit SHA and the date of observation.
- Repository metadata from `gh api repos/OWNER/REPO`: description, topics,
  homepage and licence. Record the observation date separately: provider
  metadata is **not pinned** by a Git commit.
- Releases and tags (`gh release list`, `git tag`), distinguishing a Git
  tag from an actual published GitHub Release.
- The pinned tree's `SECURITY.md`, if any, and its actual reporting
  instructions. A security policy does **not** establish that GitHub's
  separate private-vulnerability-reporting feature is enabled.
- For a dated, read-only check of that GitHub feature on a public repository,
  use the documented `GET` endpoint with a GitHub CLI session. The `-i`
  option prints the HTTP status line as well as the JSON response:

  ```sh
  gh api -i -H 'Accept: application/vnd.github+json' repos/OWNER/REPO/private-vulnerability-reporting
  ```

  Only an observed HTTP 200 response containing a boolean `enabled` value
  supports recording **enabled** or **disabled**, and only as of that check.
  Record the date and endpoint alongside the result. Authentication, API,
  network or access failures are **unknown**, not evidence of disabled
  reporting. Don't print tokens, probe with `PUT`/`DELETE`, invent an email
  address, or file a sensitive vulnerability in a public issue. A missing
  tracked policy also does not rule out an inherited security policy.
  See [GitHub's REST endpoint](https://docs.github.com/en/rest/repos/repos#check-if-private-vulnerability-reporting-is-enabled-for-a-repository),
  [private-reporting guidance](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately)
  and [GitHub CLI `--include` reference](https://cli.github.com/manual/gh_api)
  (all reviewed 2026-11-08).

### 2. Audit with pinned tools

Run BeautifulRepo's tools from a **pinned**, reviewed commit, never from a moving
branch, in isolated mode and with an explicit root. Use the same clean auditor
checkout, Python version and explicit audit profile for both target snapshots.
Record the full Git SHA of each target and the auditor, the interpreter version,
OS and observation date. A SHA alone does not establish a clean checkout.

For a POSIX shell, run this from the trusted auditor checkout. Replace both
paths: the target must be an already prepared snapshot, and the evidence directory
must be new, outside both checkouts, with an existing trusted private parent.
Repeat for the after snapshot with a different evidence directory.

```bash
target='/absolute/path/to/target-snapshot'
evidence='/absolute/path/to/new-case-evidence'
(
  set -eu
  umask 077
  mkdir "$evidence"
  capture() {
    name=$1; shift
    status=0
    "$@" > "$evidence/$name.out" 2> "$evidence/$name.err" || status=$?
    printf '%s\n' "$status" > "$evidence/$name.status"
  }
  capture audit python -I tools/repo_audit.py "$target" --profile public --format json --fail-on never
  capture markdown python -I tools/docs_links.py --root "$target"
  capture html python -I tools/html_navigation.py --root "$target"
)
```

Select the appropriate profile for non-public targets; do not publish their
evidence. The capture block continues after a nonzero checker exit so all three
independent results can be inspected. Its own success means only that the capture
steps completed, **not** that the checks passed. Inspect every status, stdout and
stderr file; a missing, incomplete or invalid report, launch failure or unexpected
diagnostic is not clean evidence. Never replace a failed output with an empty
report or treat `--fail-on never` as a passing audit. Keep raw reports private and
review the [confidentiality checklist](../checklists/confidentiality.md) before
publishing excerpts.

#### Portable capture (Windows or POSIX)

If a POSIX shell is unavailable, save the following Python 3.11+ block as
`capture_case.py` in a trusted private directory **outside both checkouts**.
Run it from the pinned auditor checkout with the same trusted Python interpreter
used for the audit. Pass two absolute paths (quote paths with spaces):

```powershell
python -I "C:\private\capture_case.py" "C:\snapshots\target" "C:\private\case-before"
```

```python
import subprocess
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: capture_case.py TARGET NEW_EVIDENCE_DIR")
auditor = Path.cwd().resolve()
target, evidence = map(Path, sys.argv[1:])
if not target.is_absolute() or not evidence.is_absolute():
    raise SystemExit("use absolute target and evidence paths")
target, evidence = target.resolve(), evidence.resolve()
if not target.is_dir() or not evidence.parent.is_dir():
    raise SystemExit("target and trusted evidence parent must exist")
if any(evidence.is_relative_to(root) for root in (auditor, target)):
    raise SystemExit("evidence must be outside both checkouts")

checks = (
    ("audit", "repo_audit.py", [str(target), "--profile", "public",
                             "--format", "json", "--fail-on", "never"]),
    ("markdown", "docs_links.py", ["--root", str(target)]),
    ("html", "html_navigation.py", ["--root", str(target)]),
)
evidence.mkdir(mode=0o700, exist_ok=False)
for name, tool, args in checks:
    command = [sys.executable, "-I", "-X", "utf8",
               str(auditor / "tools" / tool), *args]
    with (evidence / f"{name}.out").open("xb") as out, (
        evidence / f"{name}.err"
    ).open("xb") as err:
        result = subprocess.run(command, cwd=auditor, stdout=out,
                                stderr=err, check=False, timeout=120)
    with (evidence / f"{name}.status").open("x", encoding="ascii") as status:
        status.write(f"{result.returncode}\n")
```

The path example is illustrative; substitute your own existing directories.
On POSIX the new directory requests mode `0700`; on Windows, choose a parent
whose ACL already restricts access. The script does not configure ACLs. As in
the shell recipe, the output directory must not already exist, and all paths
and the auditor interpreter must be trusted. Ordinary nonzero checker exits
are recorded without stopping subsequent checks. A launch failure, timeout
or filesystem error stops capture and may leave partial files: inspect them
and use a different new directory for a retry. Never treat partial evidence
as a successful run. The standard-library script requires no additional
packages or model host.

For a current auditor checkout containing `audit_delta.py`, compare valid saved
`audit.out` JSON reports using the [before/after guide](../guides/audit-before-after.md).
Keep coverage changes separate from count changes. For example, the published
[PatchPitch case](patchpitch.md) recorded one fewer informational finding after
adding a contribution guide. That is also a reason to review changed document
selection, not to require identical coverage in every successful intervention.
This observation uses the case's historical counts; no new comparison of its
original JSON reports is claimed. The case's observed first run and remaining
contrast problems matter independently of those counts.

Then go through the [repository checklist](../checklists/repository.md) and the
[first-success checklist](../checklists/first-success.md) by hand. Record each
finding as **obstacle → affected reader → smallest fix → verification**, with a
`file:line`.

### 3. Change the target through its own pull request

- Keep it to a few changes, each with a rationale and a trade-off.
- Follow the target's own contribution rules, checks and review.
- Don't add a contact route, badge or claim the target can't back.

### 4. Snapshot "after"

- The merge SHA and a re-run of the same pinned tools.
- The first-success command repeated in a **fresh clone**, with the **observed**
  output, including at least one failure path.
- Rendering at a narrow width (320 px) in light and dark themes, with a text
  equivalent of what was seen.
- The target's CI run URL for the merge commit.

### 5. Write up `case-studies/<repository>.md`

SHAs, a summary of the diff, the commands, observed versus expected results, and what
was **not** tested. Link it from the table above.

## Rights and quoting

- **Licensed targets** (for example MIT): short quotations with attribution are fine.
  Link to the target rather than copying files.
- **Unlicensed targets**: ideas only. Describe the obstacle and the change in your own
  words, and quote no text, code or images, unless the owner licenses the repository
  first. Being the owner of both repositories doesn't change what a public case may copy
  from an unlicensed one.

## Known tool caveats

- Use BeautifulRepo **v0.2.0 or later** on repositories you don't control. Earlier
  versions on Windows could open a UNC share named by the target
  ([GHSA-9rpm-g83x-47w7](https://github.com/drevendev/BeautifulRepo/security/advisories/GHSA-9rpm-g83x-47w7)).
- Before v0.2.0, `docs_links.py` and `html_navigation.py` without `--root` checked
  BeautifulRepo's own checkout, and `html_navigation.py` failed under `python -I`
  ([#68](https://github.com/drevendev/BeautifulRepo/issues/68)). Always pass `--root`.
- The link checkers don't fetch external URLs. The HTML fragment checker handles
  simple top-level setext headings, but does not fully parse setext paragraphs in
  containers or reference-style links. The Markdown destination checker handles
  bounded one-line reference-style links without checking section anchors. The audit's findings
  are heuristics with stated limits
  ([tools README](../tools/README.md)).
- Counts in tool output, such as destinations or tests, belong to one commit. Record
  them with the SHA, not as lasting facts.
- Rendering checks with viewport emulation are not real devices, and none of these
  steps tests a screen reader. Say so in the "not tested" list.

## Skeleton

```markdown
# <Repository>: <the reader obstacle, in one line>

**Case status, YYYY-MM-DD:** <complete | in progress>; <what is and isn't verified>.

## Target and revisions

- Repository: <link>, licence <SPDX id>.
- Before: `<full sha>` (observed YYYY-MM-DD). After: `<merge sha>`, via <PR link>.
- BeautifulRepo tools: `<pinned sha>` (vX.Y.Z).

## Before

<dated metadata, tags and releases, pinned security policy and observed/unknown
private-reporting status; tool output summary; checklist findings as
obstacle → reader → smallest fix → verification>

## Changes and trade-offs

<each change, why, and what it costs>

## After

<tool re-run; fresh-clone first success with observed output and a failure path;
320 px light and dark with a text equivalent; CI run URL>

## Not tested

<explicit list>
```
