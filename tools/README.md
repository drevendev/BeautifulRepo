# Offline repository tools

`catalog.py` uses Python 3.11+ and the standard library. From the repository root:

```bash
python tools/catalog.py                 # validate and check the generated view
python tools/catalog.py --write         # explicitly regenerate catalog/README.md
python tools/docs_links.py               # check repository-owned Markdown destinations
python -I tools/media_budget.py --root .   # advisory local image size inventory
python tools/html_navigation.py          # verify local HTML/media and Markdown section anchors
python -I tools/action_pins.py --root .    # check reviewed GitHub Actions SHA annotations
python -m unittest discover -s tests -v
```

## Verify this BeautifulRepo checkout in one command

Before opening a PR, run the nine Python steps of the Quality CI matrix job
in their actual workflow order:

```sh
python -I scripts/verify_checkout.py
python -I scripts/verify_checkout.py --list         # list without running
python -I scripts/verify_checkout.py --keep-going   # collect all failures
```

The first command stops at the first failing step; `--keep-going` finishes
independent checks and returns failure if **any** step failed. It runs the
current Python interpreter and uses the root of the BeautifulRepo checkout
containing this script, even when invoked from another working directory.
The runner uses a fixed argument list (no shell, dynamic commands, or target
repository execution), reads the existing source, and does not install packages
or intentionally write outside the project. Some underlying tests or demos may
create temporary files or generated output inside their normal test boundaries.

This is **not** GitHub CI equivalence: a local run does not exercise the
cross-platform matrix, Action self-test jobs, separate Ruff lint job or
provider protection, and it is not an audit tool for untrusted repositories.
The tests explicitly compare its command inventory against
`.github/workflows/quality.yml` to expose future workflow drift. Use the live
GitHub checks for merge decisions.

The reviewed Actions pin check accepts ordinary and single- or double-quoted
`uses` mapping keys, as well as whole single- or double-quoted `uses:` YAML values. Quoting does not bypass SHA,
manifest or annotation validation. LF and CRLF workflow lines (even mixed in
one file) are inspected; Windows-style line endings must not hide an external
Action from the manifest check. This is a bounded line-oriented check,
not a complete YAML parser or a verification of remote action provenance.

For GitHub.com, the [commit-bound same-repository action syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#example-using-an-action-in-the-same-repository-as-the-workflow-at-the-running-commit)
(`uses: $/path/to/action`) is local, so no external SHA/manifest entry is required.
Malformed self-references (empty, parent-directory segments or an `@ref`) fail.
This syntax is **not available on GitHub Enterprise Server**. The pin
checker does not verify that local action paths or container tags exist.
Repositories using only recognized local/commit-bound/container `uses:` values
can omit `.github/action-pins.json`; if a manifest exists, unused entries
still fail. External `uses:` always require the reviewed manifest. A workflow
with no recognized action references still fails; this is intentionally a
bounded source check, not a YAML completeness guarantee.

To run `repo_audit.py`, `docs_links.py` and `html_navigation.py` in another
repository's CI, use the [GitHub Action](../guides/adopting-the-checks.md).

The Markdown and HTML/fragment scanners refuse hard-linked Markdown source files
and anchor targets rather than reading aliases to files outside the checkout.
The reviewed Actions pin checker likewise rejects hard-linked workflow files and
its pin manifest. It checks file identity again after opening each input and
refuses symlink targets; this is a stable-checkout preflight, not a sandbox
against concurrent filesystem replacement.

The HTML navigation checker reports explicit empty or whitespace-only `src` and
`srcset` attributes on active `img`, `source`, `video`, `audio` and `track`
markup, including valueless attributes. Omitting an optional `src` (for example
when an image has a valid `srcset`) is not treated as an empty value, nor is
an empty optional `poster`. This follows the [HTML Standard's non-empty image
source requirement](https://html.spec.whatwg.org/multipage/embedded-content.html)
but is a bounded static check, not playback or browser accessibility evidence.

The entry-point audit's `link.vague_text` informational rule now also checks
single-line full, collapsed and shortcut Markdown reference links (such as
`[here][guide]`, `[read more][]` or `[here]`) **only when the reference has a
defined, nonempty one-line destination**. It ignores reference definitions
themselves, images, literal code and unknown labels. This is a bounded source
heuristic, not a renderer, an exhaustive parser of nested/multiline references
or a judgment of link purpose in its full context.
No destination is echoed into the finding. See the
[GitHub Flavored Markdown reference-link specification](https://github.github.com/gfm/#reference-link)
for cases this intentionally limited checker does not parse.

The entry-point audit also masks fenced code blocks inside ordinary Markdown
blockquotes, so example commands and placeholders do not become prose findings.
An unfinished quoted fence stops masking when its containing quote ends.
This intentionally covers a bounded Markdown subset; nested list-container
parsing and rendered accessibility still require a human review. See the
[GitHub Flavored Markdown container rules](https://github.github.com/gfm/#container-blocks)
(reviewed 2026-11-21).

## Preflight a browser-game ZIP for itch.io

The dependency-free [`itch_html5_zip.py`](itch_html5_zip.py) checks an
exported **multi-file** HTML5 game ZIP's central-directory metadata before
a possible itch.io upload:

```sh
python -I tools/itch_html5_zip.py dist/game.zip
python -I tools/itch_html5_zip.py dist/game.zip --format json
```

Exit **0** means no reported metadata findings, **1** means an upload-shape
finding, **2** means an unreadable, invalid or unsupported archive. JSON
includes `status`, `files`, `uncompressed_bytes` and sorted `findings`.
The checker never extracts files, invokes game code or uses a network.

Rules cover a root-level, **nonempty** `index.html` **file** with exact case, published
itch.io file-count/path-length/uncompressed-size limits, and conservative
duplicate, file/directory path conflict, unsafe-path (including C0/C1 control
characters and Unicode bidirectional formatting controls in member names),
special-file, encryption and non-UTF-8-marked name preflights. Directory entries may end with one `/`; repeated trailing `//`
separators are reported as unsafe rather than silently normalized.
The Unicode guard covers the twelve invisible Bidi_Control characters defined by
[Unicode UAX #9](https://www.unicode.org/reports/tr9/) (reviewed **2026-11-21** UTC):
they may reorder a displayed member name. Ordinary Arabic/Hebrew filenames
remain allowed. This is a conservative archive review rule, **not** an itch.io
upload requirement or a claim that all Unicode filename tricks are detected.
It also reports Windows-nonportable member names (reserved
devices such as `NUL.txt` and `COM¹.json`, prohibited punctuation or trailing
dots/spaces) and case-distinct members that collide on common case-insensitive
filesystems. It also flags Unicode canonically equivalent member paths, such
as the NFC and NFD spellings of `café.png`, which may collide on
normalization-insensitive filesystems. A lone decomposed name is accepted.
The checker also flags aliases that appear **only when Unicode canonical
normalization and case folding are combined**, such as `CafÉ.png` and
`café.png`; it detects file-versus-parent-directory blockers too.
It uses Unicode canonical caseless matching (NFD/casefold/NFD), not
compatibility normalization (NFKC), and does not reject distinct names by
default. This is conservative portability guidance, **not** exact filesystem
emulation or a new itch.io rule; see [Unicode canonical caseless matching](https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-3/)
and [Apple's APFS filename guidance](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html)
(reviewed **2026-11-22** UTC). The Windows rules are based on
[Microsoft's filename rules](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file).
None are additional itch.io ZIP-upload requirements. Unix ZIP entries with
conflicting filename/directory type metadata are reported. For MS-DOS/FAT
creator metadata (host ID 0), an explicitly set directory bit also conflicts
with a filename lacking a trailing slash. A directory named `index.html`
without a trailing slash is **not** accepted as the game's entry point.
A trailing slash remains a directory marker even when the DOS bit is absent.
A directory declaring nonzero uncompressed data is a `directory_payload`
finding, not an ordinary file included in the size/file totals. Empty Deflate
streams remain accepted. This checks declared metadata, not actual payloads.
See [PKWARE APPNOTE 6.3.10](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)
(sections 4.3.8, 4.4.2 and 4.4.15) and [Microsoft file attribute constants](https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants),
reviewed **2026-11-28** UTC. This does not emulate every ZIP creator's attributes.
Non-ASCII names without the ZIP UTF-8 flag are reported as potentially
non-portable; malformed UTF-8 filenames return **incomplete** rather than
crashing. Store and Deflate ZIP member compression are accepted; BZIP2,
LZMA, Zstandard and unknown compression methods produce a `compression_method`
finding, because not every ZIP extractor supports them. This is a local
portability rule, **not** an itch.io requirement. If a member requires
an extractor version unsupported by the local Python `zipfile` reader, the
preflight returns **incomplete** (exit 2), not a traceback or a false
success; it does not try to extract the payload. This is distinct from a
recognized but nonportable compression method, which produces a finding
(exit 1). See the
[Python ZIP compatibility notes](https://docs.python.org/3/library/zipfile.html).
These are conservative metadata checks, not an asset URL or
browser compatibility test. It counts bytes from ZIP metadata, **not**
verified decompressed content; it does not verify
CRC, HTML/JS asset references, player controls, saves, platform behavior
or uploaded iframe execution. A single self-contained HTML upload is
outside its ZIP-only scope. For a verified first-play route, see the
[game repository guide](../guides/game-repositories.md#preflight-an-itchio-html5-zip-without-uploading-it)
and [itch.io's upload documentation](https://itch.io/docs/creators/html5)
(reviewed **2026-11-20**).

## Check a declared text-color pair offline

[WCAG 2.2, SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
defines a **4.5:1** minimum for ordinary text at level AA and **3:1** for
qualifying large text. Level AAA uses **7:1** and **4.5:1**, respectively.
Review date: **2026-11-19**. The small original
[color-pair calculator](color_contrast.py) uses the W3C sRGB relative-luminance
formula and deliberately **does not round before threshold comparison**:

```sh
python -I tools/color_contrast.py '#000000' '#ffffff'
# Contrast 21.0000:1; WCAG 2.2 AA normal text (minimum 4.5:1): PASS

python -I tools/color_contrast.py '#777777' '#ffffff' --format json
# Exit 1; ratio approximately 4.478 (below the unrounded 4.5 threshold).
```

Specify `--text large` only when the rendered text **actually qualifies**,
and `--level AAA` to evaluate the stricter level. Exit **0** = selected
numeric threshold met, **1** = contrast below it, **2** = invalid input.
Only opaque six-digit sRGB `#RRGGBB` foreground/background pairs are supported;
short hex, alpha, named colors, images, gradients, CSS variables and color
compositing are intentionally out of scope. JSON mode records the raw ratio.

A numeric PASS is **not WCAG conformance**: the tool cannot identify the
rendered colors, size/weight, antialiasing, interaction states, theme switching,
text over images, adjacent component colors, or the exceptions in SC 1.4.3.
Inspect the actual page at relevant widths and light/dark themes, then
perform manual accessibility checks. See
[visual README guidance](../guides/readme-visuals.md#accessibility-is-part-of-the-visual-design).

## Verify the revision pins in a source-only case

[`source_pins.py`](source_pins.py) checks that a Markdown source-only case
consistently links to its declared GitHub repository at one immutable,
40-character commit. It requires a pinned README blob link, checks other
tree/blob source links for moving branches or different revisions, ignores
fenced examples, paired single-line backtick spans and unrelated repositories,
and runs with no network access. Unclosed or multiline inline-code spans
are not fully parsed.

```sh
python -I tools/source_pins.py \
  --case case-studies/hungrycrab-first-command.md \
  --repository drevendev/HungryCrab \
  --commit d20850c4e71382c796c4b4dac554137ebcb7e937
```

Exit **0** means consistency only, **1** means a source-link problem and
**2** means invalid or unreadable input. This bounded scanner does not
parse all Markdown forms, check a license, verify actual content, prove the
repository is public or execute a tool from the target. Follow the
[separate anonymous verification guide](../guides/public-source-verification.md)
before treating any case study as publicly reproducible.

## All three checks in one local run

Run the [combined offline audit](../guides/combined-audit.md) to invoke the
entry-point, Markdown destination and HTML/fragment checkers together without
installing packages:

```bash
python -I tools/audit_bundle.py ../your-repository --format json
```

For an offline, browsable HTML view, run
`python -I tools/audit_bundle.py ../your-repository --format html > audit-report.html`.
The HTML contains no scripts or remote assets; review paths before sharing.

It preserves native findings and reports incomplete checks instead of silently
passing them. It imports fixed checked-in checker modules; no child processes are launched. This is a local CLI, **not** an MCP server or a beauty score.

## Verify an installed four-skill plugin cache

[plugin_install_verify.py](../scripts/plugin_install_verify.py) compares the installed
`audit-repo`, `improve-readme`, `trust-surfaces` and
`draft-release-notes` `SKILL.md` files, **all other Git-tracked files inside those four skill
folders** (including standalone scripts/references), and 22 named shared
dependencies against immutable committed Git blobs from a separately checked-out
pinned source. It is read-only, runs only
local Git commands (unlike the no-subprocess audit checkers in `tools/`), uses
Python 3.11+ and local Git, and reports JSON with exit 0 (match), 1
(mismatch) or 2 (incomplete). It rejects missing/extra skill directories
and redirecting skill file paths. It also rejects unexpected files and
redirected entries **inside the four installed skill folders** as INCOMPLETE
(exit 2; at most 1,024 inventory entries). Missing tracked assets are
INCOMPLETE; modified assets are MISMATCH. Extra files elsewhere in the plugin
cache and missing optional manifests remain unverified. A file match is not
proof of host installation, skill discovery or model execution.
This is for the **four-skill development candidate**, not the released
v0.2.0 single-skill bundle.

See the [Agent plugin verification procedure](../guides/agent-plugin.md#verify-cached-skill-definitions-against-the-pinned-commit-offline)
for the full command, expected revision, separate cache/source paths and
evidence limits. A matching cache does **not** verify that Claude Code or
Codex actually installed, discovered, selected or invoked the skills.

## Preview a proposed README without writing it

Given an **already prepared** candidate README file outside the target, inspect a
unified diff against the target's current `README.md`:

```sh
python -I tools/readme_preview.py --root /path/to/target --proposal /path/to/candidate.md
```

The [README improvement skill](../skills/improve-readme/SKILL.md) can use this
optional preview to show the exact candidate before requesting approval.
For a stale-content guard, repeat with `--expected-sha256` followed by the
64-character SHA-256 printed for the original README in an earlier preview.
The command fails with exit code 2 if that content has changed; it **does not**
apply a patch, obtain consent or prevent later concurrent edits. No file is
created or modified. The `--root` directory and **all lexical parents of both input files** must
be reached through non-redirected paths, not symlinked or junction-based
aliases. In particular, a proposal reached through a symlinked parent is
refused even when the proposal file itself is regular; ordinary `..`
components without redirection remain supported.
Both inputs must be ordinary, non-symlinked UTF-8 files
of at most 256 KiB; the tool rejects bare carriage returns, C0/C1
terminal controls (except tab and ordinary newlines), Unicode bidirectional
formatting marks, U+2028/U+2029 line/paragraph separators and
invisible U+200B (zero-width space), U+2060 (word joiner) or embedded
U+FEFF characters that could conceal a change in a terminal diff. This
intentionally rejects those characters even when their use was benign;
U+200C/U+200D script-shaping joiners remain supported. Ordinary CRLF
and non-ASCII scripts are supported. It reports line-ending differences.
Exit code 0 means a
comparison was produced, **not**
that the proposed README is correct or authorized. Review the diff for private
content before sharing it. The checker is not a sandbox against a concurrently
mutating or hostile filesystem.

## Apply a previously approved README proposal

After a human has **explicitly approved the exact displayed diff and file list**,
a separate helper can apply the already inspected candidate, with both SHA-256
values from that approval:

```sh
python -I tools/readme_apply.py --root /path/to/target \
  --proposal /path/to/candidate.md \
  --approved-current-sha256 ORIGINAL_HASH \
  --approved-proposed-sha256 PROPOSAL_HASH
```

The proposal must be outside the target checkout. The target root also rejects
symlinked or junction-backed parent paths, even if the final directory itself
is ordinary. Use the physical checkout path for preview and application.
The tool rechecks both byte hashes and refuses stale or unsafe input, missing
required hashes, symlinked files, non-UTF-8 text, display controls and
candidates over 256 KiB. On a normal
local filesystem it stages a temporary sibling, checks the current README again,
and replaces **only** `README.md`; it removes the staging file on ordinary
failures and retains the proposal file. It preserves POSIX mode bits. The tool
does not obtain, authenticate or infer consent: **hash arguments prove byte
identity, not approval.** Never invoke it unless a separate, specific human
approval of this exact diff has already been received. A general edit request
does not qualify.

After application run the handbook's read-only audit and link checks, compare
results with the recorded before-state, and keep unexecuted target commands
labelled unverified. The helper does not audit claims, run repository code,
commit, push or provide a sandbox against a concurrently hostile filesystem.
An abrupt crash can leave a staging file; atomic replacement is not a
durability guarantee. See the [improve-readme skill](../skills/improve-readme/SKILL.md).

For an evidence-based change comparison, save two JSON entry-point audits and
run `python -I tools/audit_delta.py before.json after.json`. For a copyable,
path-free PR summary, pass `--format markdown` and review it before sharing. The
[before/after comparison guide](../guides/audit-before-after.md) explains
coverage changes, immutable revisions, input limits and why fewer warnings
are not automatically fixes. This offline tool never executes the target.

`--data` and `--output` accept alternative paths for a separate collection.
`--write` prepares UTF-8 bytes and atomically replaces the selected output via a temporary sibling; review the path before using it. Failed encoding/replacement leaves the previous file unchanged (this is not an fsync/crash-durability guarantee).


## Check asset provenance record structure (optional)

Fill in the [asset record template](../templates/ASSET_PROVENANCE.template.md)
for each third-party image, icon, font, screenshot or borrowed excerpt, then:

```bash
python -I tools/asset_records.py asset-records.md --format json
```

This offline read-only check validates the template's **thirteen named fields**,
unique asset headings, review dates and declared `APPROVED`, `PENDING` or
`REMOVED` decisions. Exit 0 means structurally recorded without pending
decisions, 1 means pending, 2 means invalid/unreadable; neither 0 nor
`APPROVED` is legal permission. It does not fetch source URLs, authenticate
ownership, determine license compatibility or inspect actual assets. Read the
[provenance review workflow](../guides/third-party-assets.md#optional-offline-record-preflight)
before using it as a publication checklist.

## Saved Mermaid SVG structure check

[mermaid_svg_check.py](mermaid_svg_check.py) checks the **saved SVG element**
from a rendered Mermaid flowchart for nonempty `aria-labelledby` and
`aria-describedby` references resolving uniquely to `<title>` and `<desc>`
in the same SVG. It is an optional Python 3.11+ offline, dependency-free
reader aid for the [GitHub rendering acceptance checklist](../checklists/visual-accessibility-acceptance.md#mermaid-rendered-svg-acceptance):

```sh
python -I tools/mermaid_svg_check.py capture.svg --format json
```

Exit 0 reports `STRUCTURE_PASS`, the captured bytes' SHA-256 and resolved
texts; exit 1 reports an absent/ambiguous/empty reference or invalid SVG
structure; exit 2 reports an unreadable path. The file must be ordinary,
UTF-8 XML of at most 1 MiB; NUL bytes, DTD/entity declarations and symlinked
input files are rejected. The tool never fetches GitHub, runs SVG scripts,
modifies the capture or tests browser/screen-reader behaviour. Only a real
pinned GitHub page inspection plus separate manual observations can close
that evidence gap. Its regression suite uses synthetic SVG, not a browser.

## Contract

The JSON root has integer `schema_version: 1` and a nonempty `resources` array. Entries
have exactly the fields shown in `catalog/resources.json`. Categories are guide, checklist,
program, tool and example. Metadata currently records only `source-reviewed` evidence;
runtime verification belongs in separate, reproducible trial records before the schema
claims to represent it.

Errors include ambiguous repeated JSON object keys (including nested/escaped equivalents), missing or blank fields, malformed identifiers, duplicate IDs, duplicate
source URLs (ignoring fragment, trailing slash, host case and default HTTPS port), malformed
HTTPS URLs (including raw controls and malformed percent escapes), unsupported categories and invalid/future dates. Query strings remain meaningful; fragments are ignored for duplicate-source normalization rather than banned.
URL syntax validation does not establish destination safety or availability.

Exit code 0 means the metadata is structurally valid and its generated view is current.
Exit code 1 means validation, input/output or synchronization failed. Argument-parsing
errors use argparse's exit code 2. Warnings request rechecking programs after 30 days and
other entries after 180 days; they do not assert that a source actually changed.
Current UTC date affects freshness warnings and future-date validation, not rendering.
`--fail-on-warning` turns a due recheck into exit code 1. Only the scheduled
workflow uses it, because pull-request checks must not depend on the calendar.

The tool does not fetch links, follow redirects, execute repositories, judge editorial
quality, decide licenses, verify claims or score beauty. Source review dates must come
from real inspection, never from regenerating the view. Markdown output order is stable.


## Manual agent-eval file-integrity check

[agent_eval_snapshot.py](agent_eval_snapshot.py) is an optional **operator tool**
for verifying whether a disposable synthetic target changed during an authorized
agent smoke test. It uses only the standard library and does not execute target
code or fetch anything. See [the complete runbook](../evals/README.md) for
a capture/verify example, exit codes and important limits.

Snapshot **format 2** records file bytes (SHA-256), file and directory mode bits
(including the target root), directory entries and symlink target **text**.
A permission-only change to a file or directory now fails verification even
when its bytes are unchanged. Earlier format-1 baselines must be **recaptured**:
they did not record permission bits and cannot provide this evidence.

It does not traverse symlink directories or touch their destinations, and
refuses to write the JSON baseline inside the target. Windows mode bits are
not a complete ACL or ownership check; symlink permission metadata is not
compared. A match only establishes unchanged watched attributes at the two
snapshot instants, not absence of intervening writes, changes outside the
target, successful skill triggering, a sandbox, or resistance to prompt injection.

## Local release-history inventory

[release_inventory.py](../scripts/release_inventory.py) produces a **read-only JSON inventory** of
commits for drafting release notes from a local Git checkout:

```bash
python -I scripts/release_inventory.py .
python -I scripts/release_inventory.py ../another-checkout --base 0123456789abcdef
```

Replace the illustrative base SHA with an actual ancestor commit. By default the
tool compares HEAD against the nearest reachable `v[0-9]*` tag, or the unique
root commit if there is no matching tag. It names both exact commit SHAs, the
boundary kind and each commit SHA/subject. **Shallow checkouts are rejected**,
even with an explicit `--base`: Git can mistake a truncated boundary for a
history root. Use a complete local history (for GitHub Actions checkout, set
`fetch-depth: 0`) before running the inventory. The initial root commit itself is
excluded from a root-based comparison. More than 200 commits (configurable up
to 500) fails instead of silently truncating; the tool requires a unique root
or an explicit base on unusual histories.

Unlike BeautifulRepo's `tools/*.py` checkers, this separate script invokes the
installed `git` executable; it is therefore deliberately outside the tools
collection's no-subprocess contract. It only runs local history-read commands.

This inventory **is not a release and does not prove anything shipped**.
Tag presence does not establish a GitHub Release, downloadable asset or test pass.
Commit subjects are untrusted inputs, not verified user-visible behavior. Review
the underlying diffs and [release-note guidance](../guides/release-notes.md)
before writing public claims. The tool needs Python 3.11+ and Git, makes no
network requests, doesn't execute project code and writes no files. Exit 0
prints JSON; invalid inputs or Git read errors exit 2 without partial JSON.
## Synthetic local Git histories for agent-eval preflight

[agent_eval_release_fixture.py](../scripts/agent_eval_release_fixture.py)
creates a disposable **real Git checkout** to test the release inventory on
actual commits and an optional tag, instead of treating invented JSON output
as evidence that Git ran. It requires Python 3.11+ and the locally installed
Git executable. It is an **opt-in fixture generator**, not one of the
read-only repository checkers above.

```sh
WORK=$(mktemp -d)
python -I scripts/agent_eval_release_fixture.py no-tag "$WORK/no-tag"
python -I scripts/agent_eval_release_fixture.py tagged-history "$WORK/tagged"
python -I scripts/release_inventory.py "$WORK/no-tag"
python -I scripts/release_inventory.py "$WORK/tagged"
```

The output path must not exist and its parent must already exist; the script
refuses to overwrite existing content. It writes exactly three fictional
local commits, adds `v0.1.0` only in the tagged scenario, configures no
remotes, and prints the full root/head SHAs. It never invokes a model, runs
target code or publishes a release. The [agent-eval runbook](../evals/README.md#optional-real-git-release-note-preflight-no-model)
explains how to use these local histories and what they **do not** prove.

## GitHub Actions README badge file-presence check

`workflow_badges.py` checks **one narrow, verifiable part** of a CI badge:
whether a same-repository GitHub Actions status badge in the root `README.md`
points to an ordinary, checked-in `.github/workflows/*.yml` or `*.yaml` file.
It accepts inline Markdown images, single-line reference-style images
(`![CI][build]` with `[build]: URL`, collapsed `![CI][]`, and shortcut
`![CI]` using `[CI]: URL`), and HTML
`<img>` tags. Reference labels are case-insensitive; the first definition wins.

```bash
python -I tools/workflow_badges.py --root . --repo drevendev/BeautifulRepo --require-badge
```

The example opts into `--require-badge`: absence of a recognizable same-repository
badge then fails, so a missing README badge cannot silently pass BeautifulRepo CI.
Omit the flag for repositories that deliberately do not display a workflow badge.
Use your own GitHub `owner/repo` when checking another checkout. The tool is
offline, read-only, Python 3.11+ and standard-library-only. It does not run
workflows, target project code, `git` or network requests. Common fenced/inline
code samples and HTML comments are excluded, but this is not a complete GFM
renderer. It reads only a single-linked, ordinary root README (up to 256 KiB),
refusing hard-link aliases before and after opening. It checks literal local
workflow filenames without following symlinks or Windows junctions, and prints
file/line diagnostics when the workflow is missing. By default, exit 0 means the
checked references exist, **even if zero were found**. With `--require-badge`,
zero recognized same-repository workflow badges exit 1 instead. Missing or
unsupported targets also exit 1; malformed inputs exit 2. Neither mode verifies
whether a workflow was run or passed.

**Not verified:** whether the workflow triggers, passed, is enabled, has
permissions, belongs to a release, or honestly supports a badge label.
Shields.io, external badges, GitHub Enterprise domains,
multiline reference definitions, unusual filenames
and browser rendering remain outside this bounded check. Review those manually. GitHub's
[workflow-status badge documentation](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge)
defines the supported URL form and branch/event parameters (reviewed
2026-10-26). See the [evidence-first README review](../guides/ai-readme-review.md)
for the other claims a maintainer still needs to verify.

## Reviewed GitHub Actions commit pins

Run `python -I tools/action_pins.py --root .` to compare external `uses:`
references in `.github/workflows/*.yml` / `*.yaml` against the project's
reviewed `.github/action-pins.json`. The manifest names each action, its full
40-character lowercase commit SHA, upstream release label and actual manual
inspection date. A Dependabot bump that only changes a SHA now fails until a
maintainer verifies upstream and updates the manifest and workflow annotations.
Local `./`, commit-bound `$/` and `docker://` actions do not require
external SHA entries. The checker rejects `./` and `$/` references with
parent/current-directory components, repeated separators, backslashes,
whitespace or an `@ref` suffix; a bare `./` may point at an action in the
workspace root. It does not verify local action existence, whether the
workspace was checked out, or Docker image provenance. Duplicate manifest JSON keys,
unpinned tags, missing annotations, unknown actions and unused manifest records
fail closed. Files are bounded to 256 KiB (64 KiB manifest, 100 workflows);
symlinked files are rejected. Exit 0 means locally consistent references;
exit 1 means inconsistent pins; exit 2 means invalid input. It uses Python
3.11+, the standard library only, and never writes, runs repository code,
invokes Git, or makes a network request. It scans simple one-line `uses:`
forms, **not full YAML**, and cannot prove that a release tag maps to that SHA,
that remote code is safe, that a review date reflects a real inspection, or
that any workflow ran. Manual source review remains mandatory.

## Guide review dates

The scanner ignores date-like text inside single-line and multiline backtick
code spans within a paragraph, HTML comments and Markdown fenced examples,
including longer closing fences and unclosed blocks. Unmatched inline backticks
remain prose; blank paragraphs and interrupting Markdown blocks (headings,
quotes, bullets, ordered lists starting at 1, thematic breaks and line-starting
HTML comments) bound inline matching. Lines such as `2. ` and `3) ` can continue a prose paragraph. This follows bounded
[GitHub Flavored Markdown code-span rules](https://github.github.com/gfm/#code-spans)
(reviewed 2026-11-20) and
[fence rules](https://github.github.com/gfm/#fenced-code-blocks)
(reviewed 2026-10-27); it is not a complete Markdown renderer.

`review_dates.py` finds the dates on which someone re-read a guide's sources, such as
`Reviewed **2026-10-22**` or `Checked: 2026-10-03`, in `guides/`, `checklists/`,
`CONTRIBUTING.md`, `SECURITY.md` and this file. It warns when a date is older than
180 days (30 for `guides/programs.md`, whose rules change every season) and reports
impossible or future dates as errors. As with the catalog, `--fail-on-warning` is for
the scheduled run, and `--today YYYY-MM-DD` fixes the date for tests. A warning means
"re-read this source", not "this source changed". The scanner reads ordinary UTF-8
files only (up to 256 KiB per file and 4096 selected files). It rejects linked
or redirected source locations, invalid UTF-8 and NUL bytes with an input
error; these should be fixed rather than silently skipped.

## Relative documentation link checker

`docs_links.py` scans `.md` and `.markdown` files under the repository root.
It verifies that inline and bounded reference-style repository-owned links and
image destinations resolve to existing files or directories. It
supports paths relative to the current document, repository-root paths beginning with `/`,
URL-encoded path characters, and ordinary query/fragment suffixes on an otherwise local path.
It rejects destinations that escape the repository root. Like GitHub's renderer
(cmark-gfm), it stops reading a bare destination at its 33rd unclosed `(`, which also
keeps scanning time roughly linear in the size of a file.

A destination containing a backslash or a drive letter (`docs\guide.md`, `C:/x`,
or either one percent-encoded) is reported as non-portable without being opened. On
Windows such a path could name another drive, a UNC network share or a device. GitHub
doesn't treat a backslash as a folder separator either. A `:`, a trailing dot or space,
or a Windows device name (`NUL`, `CON`, `COM1.txt` and so on) is non-portable too.
Every name must match its directory entry exactly, letter case included, so
`docs/guide.md` for `docs/Guide.md` is reported on Windows and macOS as it is on
GitHub and Linux. Symbolic links and NTFS
junctions are never descended into while looking for Markdown files. When a source or
destination passes through one, its target is read as text first and followed only
if it stays inside the root. A link cycle is reported after 40 hops.

`.git` and `node_modules` directories are never scanned. Repeat `--exclude GLOB` to
skip other root-relative paths, such as `--exclude vendor`. A matching directory is
not descended into, and excluded files remain valid link destinations.
`html_navigation.py` accepts the same option.

Without `--root`, both link checkers scan the **current directory**, like
`repo_audit.py`, never the checkout the tools live in. All three also run under
`python -I` (isolated mode), the safer way to run them next to a repository you
don't control. For example, from inside another repository:

```bash
python -I /path/to/BeautifulRepo/tools/docs_links.py
python -I /path/to/BeautifulRepo/tools/html_navigation.py
python -I /path/to/BeautifulRepo/tools/repo_audit.py .
```

The checker deliberately does **not** fetch external URLs, validate redirect targets, certify
rendered HTML, or validate section fragments/heading anchors. It ignores links inside fenced
and single-backtick inline code because documentation examples should not become dependencies.
It also masks GFM raw HTML block types 1–7 (script/pre/style, comments, processing
instructions, uppercase declarations, CDATA, named block-level HTML tags and
standalone complete-tag blocks), including unclosed blocks, while preserving
source offsets and line numbers. Each type 3–5 block ends at its matching
`?>`, `>` or `]]>`; types 6–7 end at the next blank line even after a closing
tag. Type 7 starts only at a top-level block boundary: a standalone complete
opening/closing tag cannot interrupt a paragraph or lazy continuation. This
bounded check is not a full GFM parser for nested lists/quotes or inline HTML.
Real HTML destinations are still inspected separately by `html_navigation.py`. See the
[GFM HTML block rules](https://github.github.com/gfm/#html-blocks), reviewed 2026-11-02 (UTC).
Full (`[text][id]`), collapsed (`[text][]`) and shortcut (`[id]`)
reference-style links and images are checked when a valid definition begins
at a Markdown block boundary. The full-reference *visible text* may contain
balanced nested square brackets on one physical line, such as
`[a [nested] title][id]`; ordinary nested references follow inner-link
precedence while image references may remain inside a live link. A consumed
explicit `[id]` token is not double-counted as a shortcut. Collapsed and
shortcut reference labels remain flat (at most 999 characters) as required by
GFM; nested unescaped brackets do not create new labels. The scanner uses
bounded, nonrecursive delimiter matching, preserves source-character positions,
and does not parse every multiline/nested-container GFM construct. See the
[GFM link rules](https://github.github.com/gfm/#links), reviewed 2026-11-02. Definitions may follow their uses; labels use
case folding and collapsed whitespace, first definition wins, and unused
definitions are not checked. A bounded GFM subset permits the destination on
the next nonblank line after `[id]:` and/or a title on the next nonblank line
after the destination. Each continuation must be indented by at most three
columns; at most two additional physical lines and 4096 combined characters
are accepted. Invalid, over-limit and blank-line-separated candidates do not
consume subsequent Markdown. Definitions inside list/quote containers and
complex nested labels remain unsupported; this is not a complete GFM parser.
Raw HTML destinations are checked separately by `html_navigation.py`.
See the [GFM reference definition rules](https://github.github.com/gfm/#link-reference-definitions),
reviewed 2026-11-02.

### Optional link-use source anchors

For tooling that needs to distinguish two links on the same Markdown line, import
`iter_markdown_locations(path)` from `tools/docs_links.py`. It yields
`MarkdownLinkLocation(source_line, source_column, destination, diagnostic_line)`
records, in the **same order** as the existing iterator. Source coordinates are
one-based Unicode-character positions of the original link-use opener (the
opening `[` or an image `!`), not UTF-8 byte positions or decoded destination
offsets. Reference uses point to their actual use, not their definition. CRLF
does not add a column to the following line.

The older `iter_markdown_destinations(path)` still yields exactly
`(diagnostic_line, destination)` pairs. In a multiline inline link,
`diagnostic_line` identifies the destination line and can differ from
`source_line`; preserving it keeps the CLI's existing `file:line` output
unchanged. The inline scanner follows [GFM link nesting precedence](https://github.github.com/gfm/#links)
(reviewed 2026-11-02): a successfully parsed inner ordinary link prevents an
invalid enclosing ordinary link from being checked as a second destination.
Images inside links remain valid; link-like text inside a parsed image's alt
text or another link's destination is not counted as a separate link. Failed
inner parses leave a valid outer link available. The scanner is still a
bounded subset rather than a full Markdown renderer.

GitHub recommends relative links for repository-owned files because they follow the branch a
reader is viewing and remain useful in clones. Source reviewed 2026-10-04:
<https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#relative-links>.

## HTML navigation and fragment checker

`html_navigation.py` complements `docs_links.py`: it checks repository-local
`a href`, `img src/srcset`, `source src/srcset`, `video src/poster`,
`audio src` and `track src` destinations in active Markdown HTML, plus local
section fragments in HTML and inline Markdown links to `.md` and `.markdown`
targets. Media URL attributes follow the HTML resource semantics
([video and poster](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/video),
[source](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/source);
reviewed 2026-11-16). A missing local video poster, audio file or caption track
is a normal link failure; remote and data URLs remain outside offline checking.
This is **source inspection**, not proof GitHub renders the tag or that a browser
can decode the media format.
It ignores code examples using the same GFM literal-region masking as the
existing checker. It also flags live raw HTML `<img>` elements with no `alt`
attribute. An explicit `alt=""` is allowed for decorative images; the tool
cannot judge whether the alternative is appropriate or certify accessibility.
Markdown image syntax is not graded for descriptive quality.
Duplicate HTML `href`, `src`, `srcset`, `poster`, `alt`, `id`, `name`, `role` and
`aria-*` attributes are reported. The first occurrence is retained for the
checker’s destination and `alt` logic, as specified by the
[HTML Standard](https://html.spec.whatwg.org/multipage/parsing.html#parse-error-duplicate-attribute)
(reviewed 2026-10-31); later duplicates cannot silently replace a label or role.
This is a source-level duplicate check, not validation of computed accessible names
or screen-reader behavior.
Explicit HTML `id` and `a name` anchors and ordinary
Markdown ATX headings and simple top-level setext headings (including shared
duplicate suffixes) are supported. For setext, the underline uses `=` or at
least two `-` characters; the preceding lines must form a plain paragraph.

Heading anchors follow GitHub's rules. The rendered text is lowercased. Every
character other than a letter, mark, digit, connector punctuation, hyphen or space
is dropped, and each space becomes a hyphen, so `Terms & Conditions` becomes
`terms--conditions`. Code-span text counts. Images, tags, comments and emphasis
markers don't. The expected values in `tests/test_github_heading_slugs.py` were read
back from GitHub's Markdown API. Simple setext heading syntax follows the
[GitHub Flavored Markdown spec](https://github.github.io/gfm/#setext-headings)
(reviewed 2026-10-29). Known differences: setext paragraphs inside list/quote
containers, code-only headings, and HTML-block continuations are not fully
parsed; characters newer than the Unicode version GitHub uses may be kept or
dropped differently.

This offline source check is not a complete GitHub-flavored Markdown renderer.
It does not crawl external resources, support every Markdown extension or
reference-style link, or certify browser, keyboard or assistive-tech behavior.

## Repository entry-point audit

`repo_audit.py` inspects a local repository's selected README, license and contribution
documents without network requests, project execution or modifications. Findings carry
relative paths, source lines where applicable, explanations and suggested next steps.

```bash
python tools/repo_audit.py .
python tools/repo_audit.py ../your-repository --format json
python tools/repo_audit.py ../your-repository --fail-on warning
python examples/repository-audit/demo.py
```

The default failure threshold is errors only; warnings and informational findings remain
visible. Missing dedicated contribution guidance and empty image alternatives are not
unconditional failures. Exit 0 means the configured threshold was not reached, not that
all quality or accessibility questions were answered.

Read the [complete contract and limitations](../guides/repository-audit.md) and the
[tested before/after walkthrough](../examples/repository-audit/README.md). This bounded
source inspection is not a complete GitHub community-profile check, license classifier,
screen-reader audit or beauty score. Its tests join the existing default unittest suite;
no new required repository-protection rule is introduced.


## Inventory repository image weight before publishing

Run the [offline media inventory](media_budget.py) on an ordinary checkout:

```sh
python -I tools/media_budget.py --root . --max-file-kib 1024 --max-total-kib 8192
python -I tools/media_budget.py --root ../another-repo --format json
```

It scans nested regular PNG/JPEG/GIF/WebP/SVG/AVIF/APNG files by file size,
without decoding images, executing repository code or accessing the network.
Dependency folders are excluded; redirects and inventory limits produce
INCOMPLETE instead of a false PASS. Exit 0 = within chosen budgets;
1 = over budget; 2 = incomplete or invalid arguments. The 1 MiB per-file
and 8 MiB total defaults are configurable examples, **not** GitHub upload
limits or a substitute for checking the rendered README. The total counts
unreferenced assets and theme variants too. For a practical keep/re-export
decision, see [image weight and evidence](../guides/media-budget.md).

## Inventory old repository references before a move

The dependency-free [`repo_references.py`](repo_references.py) tool searches
selected local source/documentation text files for occurrences of an old
`OWNER/REPO` pair. It is useful *before* a GitHub rename/transfer, alongside
the [verification guide](../guides/repository-relocation.md).

```sh
python -I tools/repo_references.py --root ../target-checkout --old orchard-labs/maple-lint
python -I tools/repo_references.py --root ../target-checkout --old orchard-labs/maple-lint --format json
```

Both commands are **read-only** and require only Python 3.11+. The fictional
pair illustrates an exact case-insensitive substring search: hits in longer
names or example documentation are candidates for **manual review**, not
automatically broken references. The output records path/line/column, not
the source line, to avoid echoing adjacent secrets. Private filenames may
still be sensitive; do not publish unchecked reports.

**Exit status:** 0 = no matches in scanned text; 1 = references found;
2 = incomplete or invalid input. The inventory covers common Markdown,
plain text, YAML, JSON, TOML, HTML, shell/PowerShell, Python and Go
(`.go`, `.mod`, `.work`) suffixes, plus Makefile, Dockerfile and
.gitmodules. This includes Go module and workspace paths and Go source
imports, but excludes `go.sum` checksum data, dependency/build folders and
other unsupported files. It does **not** inspect binary formats, remote
consumers or redirect behavior. Paths with redirects/hard links, undecodable/oversized
eligible files, and scan ceilings produce incomplete results rather than
a misleading clean result. Bounds: 10,000 directory entries, 32 directory
levels, 1 MiB per text file, 24 MiB selected text and 2,000 matches.
This is a stable-checkout source inventory, not a sandbox against concurrent
filesystem changes or an exhaustive migration verifier. Run the separate
post-move checks in the guide before claiming continuity.
