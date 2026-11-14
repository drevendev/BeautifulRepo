# Use BeautifulRepo from Claude Code or Codex

BeautifulRepo uses **one plugin** for Claude Code and Codex. The released
`v0.2.0` contains `audit-repo` only; a pinned development candidate contains
four skills but **has not passed real-agent acceptance**. The `audit-repo`
skill audits a local repository the way this handbook does:

- It runs `repo_audit.py`, `docs_links.py` and `html_navigation.py` from the installed
  plugin against the target.
- It applies the [repository](../checklists/repository.md) and
  [first-success](../checklists/first-success.md) checklists.
- It reports prioritized findings, each with the smallest fix and a way to verify it.

The local Python checkers are read-only and make no network requests. An agent
session may still transfer repository context to the configured model provider.
Review approved data controls before inspecting private code. See the
[agent ground rules](agent-safety.md).

## Choose the smallest tool that fits

You do **not** need to install an agent plugin or send repository content to a
model provider merely to check local documentation:

- **Just run the offline checks:** from a BeautifulRepo checkout, use
  `python -I tools/audit_bundle.py .` (Python 3.11+, no third-party runtime
  packages). For a different checkout use its explicit local path. This
  checks entry points, relative Markdown links and local HTML navigation;
  it is a source-level check, not a rendered-accessibility audit. See the
  [combined audit guide](combined-audit.md).
- **Ask an agent to audit a repository:** use the tagged **v0.2.0** plugin
  below. That published version contains **only** `audit-repo`; a plugin
  command completing does not prove the model selected the skill.
- **Trial README improvements, trust surfaces or release-note drafts:** use
  the **four-skill pinned development candidate** below. It has not passed
  fresh, independent Claude Code/Codex host acceptance and is not a
  published four-skill release. Follow the explicit edit-approval boundaries.
- **Expose the three offline checkers as MCP tools:** follow the separate
  [experimental local MCP guide](local-mcp.md). This opt-in stdio adapter
  needs an optional pinned SDK and its own client registration. It is **not
  installed by either plugin path above**. SDK-level protocol checks have
  passed, but Claude Code/Codex host invocation has not been verified; no
  stable MCP release is claimed.

For private or internal repositories, check your model-provider data controls
*before* choosing either agent-based route. The standalone Python checkers
make no network requests, but agent sessions may transmit inspected content.

## Install the released audit skill (v0.2.0)

You need Python 3.11 or newer on `PATH`.

**Claude Code:**

```bash
claude plugin marketplace add drevendev/BeautifulRepo@v0.2.0
claude plugin install beautifulrepo@beautifulrepo
```

**Codex:**

```bash
codex plugin marketplace add drevendev/BeautifulRepo --ref v0.2.0
codex plugin marketplace list
```

For Codex, `codex plugin marketplace add` **registers a source; it does
not install the plugin**. The [official Codex CLI installation example](https://developers.openai.com/learn/developers-codex-plugin)
(rechecked **2026-11-12**) documents starting `codex`, opening `/plugins`,
selecting a plugin and choosing **Install plugin**, then starting a new chat.
The [official packaging guide](https://developers.openai.com/plugins/build/plugins)
also documents installing local-marketplace plugins through the ChatGPT desktop
**Plugins Directory**. These are documented host workflows, **not** observed
BeautifulRepo installations. Use the browser actually available in your host
version, inspect its installed/cached copy, and record any missing marketplace,
unsupported command or installation error as **FAIL/INCONCLUSIVE** rather than
treating marketplace registration as success. In Claude Code, start a new
session after installation.

These commands pin release `v0.2.0`, the first release that contains the plugin.
Leaving out the pin follows mutable `master`; **do not use an unpinned
checkout as evidence for a tested release candidate**.

## Try all four skills from a pinned development candidate

The source candidate at [commit `8947574399df`](https://github.com/drevendev/BeautifulRepo/tree/8947574399df2cc11e8ded41cecbef70be4808c6)
contains `audit-repo`, `improve-readme`, `trust-surfaces` and
`draft-release-notes` (manifest version `0.3.0-dev.0`). It is **not a
stable v0.3.0 release**. Compared with the earlier `cf8ac81` candidate,
this revision also contains independently copied dependencies for all four
skills, the corrected Codex plugin-browser procedure and the offline
installed-cache verifier. The development source was accepted through
GitHub PRs #337–#343 on 2026-11-11; their CI results belong to the specific
PR heads, not automatically to this merged squash SHA. **No fresh Claude Code
or Codex installation, skill discovery or model invocation has been proven.**
Record the full SHA for each trial. Use the official
[Claude Code CLI reference](https://code.claude.com/docs/en/plugins/cli-reference)
and [Codex plugin guide](https://developers.openai.com/plugins/build/plugins)
for host commands; treat errors as test results, not proof of success.

Start with a clean, disposable test environment. If `beautifulrepo` is already
configured, inspect it first rather than overwriting valued marketplace settings.
You need Python 3.11+ and Git. Try one host, from a regular terminal:

**Prepare one immutable local checkout for both hosts (source-locked preflight):**

The [Claude Code marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
documents `owner/repo@ref` for a **branch or tag**, not a full commit SHA as
a marketplace-source selector. The Codex `--ref` option similarly documents
a Git ref, without proving that a raw SHA works in an installed client.
Rather than treat either untested remote SHA syntax as a verified install,
clone the repository and check out the **exact** candidate commit in a
disposable directory. Run these commands from its **parent** directory:

```bash
git clone https://github.com/drevendev/BeautifulRepo.git BeautifulRepo-candidate
git -C BeautifulRepo-candidate checkout --detach 8947574399df2cc11e8ded41cecbef70be4808c6
git -C BeautifulRepo-candidate rev-parse HEAD
```

Confirm the last command prints exactly
`8947574399df2cc11e8ded41cecbef70be4808c6`; if it differs or checkout
fails, **stop and record the failure**. Keep the checkout unchanged during
the trial. This proves only the **local source revision**, not what a host
installed from it.

**Optional Claude Code package preflight (before installation):**

```bash
claude plugin validate ./BeautifulRepo-candidate
```

The [Claude Code plugin validator](https://code.claude.com/docs/en/plugins/cli-reference#plugin-validate)
accepts a directory. It checks the marketplace manifest; **Claude Code
v2.1.289+** also checks the plugin manifest and components when the directory
has both `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json`.
Older clients may validate less. Exit **0** means its selected checks passed
(possibly with warnings), **1** means validation failed and **2** means an
unexpected validation error. Check `claude plugin validate --help` for the
actual installed version. Record the output and exit code rather than claiming
a pass by inference. This is a **source-only** validation, not an installed-host
copy check, Codex compatibility test, skill discovery or model invocation.
Do not run model evaluations as part of this preflight.

**Claude Code — register that local marketplace, then install:**

```bash
claude plugin marketplace add ./BeautifulRepo-candidate
claude plugin install beautifulrepo@beautifulrepo
claude plugin list
claude plugin details beautifulrepo
```

**Codex — register that same local marketplace:**

```bash
codex plugin marketplace add ./BeautifulRepo-candidate
codex plugin marketplace list
```

The local-directory marketplace source is documented for
[Claude Code](https://code.claude.com/docs/en/plugins/cli-reference) and
[Codex](https://developers.openai.com/plugins/build/plugins), but these
exact commands **have not been run in either client** by this project.
This is a pinned **local-marketplace** trial, not a successful GitHub
remote-marketplace install, agent discovery or model invocation.

For Codex, the commands above only **register and list** the source.
The [official Codex CLI example](https://developers.openai.com/learn/developers-codex-plugin)
documents launching `codex`, opening `/plugins`, finding **BeautifulRepo**,
selecting **Install plugin** and starting a **new chat**. Alternatively,
use the [ChatGPT desktop Plugins Directory](https://developers.openai.com/plugins/build/plugins)
with that local marketplace. Neither route has been observed to install this
BeautifulRepo candidate. Inspect the installed/cached files before grading
any skill; a source checkout, listed marketplace or opened `/plugins` panel
is **not** installation evidence. If a host rejects the command or cannot
install, record its version and exact error as **INCONCLUSIVE/FAIL**; do not
fall back to mutable `master` or reuse another candidate's evidence.

Restart the client. Check the *installed copy* of `skills/` for all four named
`SKILL.md` files and confirm they correspond to the pinned commit before a
model test. For a low-risk first test use a **disposable synthetic target**,
never a private repository with unapproved provider data controls. Follow the
[revision-pinned manual matrix](https://github.com/drevendev/BeautifulRepo/blob/8947574399df2cc11e8ded41cecbef70be4808c6/evals/manual-smoke.md).
**Pinned-matrix installation caveat:** Step 3 of that immutable matrix
links to its *own* relative `../guides/agent-plugin.md`. At the pinned
`8947574399df2cc11e8ded41cecbef70be4808c6` revision, that older guide
still installs `cf8ac81ddabb5e2006913e65a2f980ef201baf5c` instead.
**Do not follow the matrix's relative installation-guide link.** For this
trial, use the full `8947574399df2cc11e8ded41cecbef70be4808c6` Claude Code
or Codex installation command **above**, followed by the offline
`--expected-commit 8947574399df2cc11e8ded41cecbef70be4808c6` cache
verification **below**. Use the pinned matrix for its cases and scoring, but
never mix installer commands or result evidence from different revisions.
Actual skill selection, file reads, tool calls, permission decisions and
before/after target snapshots must be observed; static CI and plugin manifests
cannot verify them. Results (including failures or INCONCLUSIVE outcomes) go to
[tester issue #258](https://github.com/drevendev/BeautifulRepo/issues/258);
release acceptance is tracked in [#257](https://github.com/drevendev/BeautifulRepo/issues/257).
The [experimental local MCP adapter](local-mcp.md) is implemented
separately and **not installed** by these plugin commands; its real-host
acceptance is still open in [#255](https://github.com/drevendev/BeautifulRepo/issues/255).
No model evaluation or release publication is automatic.

## Verify cached skill definitions against the pinned commit (offline)

A marketplace registration or source checkout is not proof that the host installed
the expected four skill files. After installing the **development candidate**
above, locate the actual installed plugin cache root reported by your host.
Separately check out the full `8947574399df2cc11e8ded41cecbef70be4808c6`
commit in a local Git working tree. Use the **actual cache location shown by
the host**, not another copy of the source checkout. The two paths must be
**different physical directories**: giving the same checkout twice (even
through alternate path spellings) returns INCOMPLETE, never MATCH. Independently
verify the source's Git origin and the host's cache location; a byte match
cannot authenticate where either directory came from. Supply **physical absolute
paths**: the verifier returns INCOMPLETE when either root or any ancestor is a
symlink or Windows junction/reparse point. On POSIX, use `realpath` on an
already trusted path if necessary (including systems where `/var` is a
symlink); resolving a path does not prove installation provenance.

**Use a newer, separately pinned verifier.** The script *inside* the
immutable `8947574399df2cc11e8ded41cecbef70be4808c6` candidate does
**not** reject symlinks in the parents of the source/cache roots, Windows
junction aliases, or changed plugin manifests. Those checks were implemented
later. Do not run that older script while claiming the newer safeguards.

From the same parent directory where you cloned `BeautifulRepo-candidate`,
prepare the corrected verifier at the merged, immutable
[commit `ac28c4f6`](https://github.com/drevendev/BeautifulRepo/commit/ac28c4f6ee6560405be5fc6aff601f18022e5c40):

```bash
git clone https://github.com/drevendev/BeautifulRepo.git BeautifulRepo-verifier
git -C BeautifulRepo-verifier checkout --detach ac28c4f6ee6560405be5fc6aff601f18022e5c40
git -C BeautifulRepo-verifier rev-parse HEAD
```

Confirm the last command prints **exactly**
`ac28c4f6ee6560405be5fc6aff601f18022e5c40`. If not, stop; do not
run a verifier from mutable `master`. Keep both checkouts unchanged.
Pass the original `8947574…` candidate as `--source`, the host's **real**
installed cache as `--installed`, and run the script from the **separate**
verifier checkout (three distinct physical directories):

```text
python -I "/absolute/path/to/BeautifulRepo-verifier/scripts/plugin_install_verify.py" --source "/absolute/path/to/BeautifulRepo-candidate" --installed "/absolute/path/to/installed-plugin-cache" --expected-commit 8947574399df2cc11e8ded41cecbef70be4808c6
```

The verifier's own checkout is only the **program** used for comparison;
`--expected-commit` and the committed Git blobs still identify the older,
immutable four-skill **candidate**. Its more recent implementation does not
turn that candidate into a new release or prove a host install.

Requires Python 3.11+ and local Git; the source must be at the repository top
level, with `HEAD` equal to the supplied full SHA. Exit **0** means all four
installed `SKILL.md` files **and 22 named local dependencies** match the
**committed Git blobs** of the `8947574…` candidate. The dependencies
include six executable helpers, shared agent-safety guidance, task guides,
three checklists and eight templates. The JSON lists them as
`checked_plugin_dependencies`. The corrected verifier additionally compares
`plugin.json` and `.claude-plugin/plugin.json` **when present** in the
installed cache; `checked_present_manifests` lists compared files and
`missing_optional_manifests` explicitly marks absent files as **unverified**.
Exit **1** means at least one checked file differs; exit **2** means
incomplete evidence (for example a missing required template, redirected
path or wrong candidate revision). Exit **0** with missing optional manifests
is **not** evidence that those manifests or the host installation passed.
**Pinned-verifier scope:** the `ac28c4f6` verifier in the command above
compares four `SKILL.md` files, 22 shared dependencies and present manifests,
**not** scripts and references bundled *inside* each standalone skill folder.
A newer development version of `scripts/plugin_install_verify.py` also compares
every Git-tracked file under the four pinned skill directories, reporting
`checked_skill_assets` and `different_skill_assets`. Do not claim that broader
verification from the older pinned command; pin and review a new immutable
verifier revision before using it as acceptance evidence. The candidate SHA
itself remains unchanged.

Other repository files, extra untracked cache files and missing optional
manifests are outside the comparison. JSON names differences without exposing
file contents. A MATCH is **not** a complete plugin integrity or provenance
certificate.

The verifier invokes local Git to read committed blobs but runs no model,
network or target code and does not edit either checkout. It does **not**
support the one-skill `v0.2.0` release.

A byte match is necessary evidence for this candidate, **not** evidence that
Claude Code or Codex discovered, activated or invoked those files. Preserve
actual host skill-selection traces, checker execution, synthetic target
before/after snapshots and the independent review required by
[#257](https://github.com/drevendev/BeautifulRepo/issues/257).
Do not call this an external-user installation or real-model PASS.

## Standalone skill-manager installations: separate from full plugins

**Four self-contained skills — host activation remains unverified.**
`audit-repo`, `draft-release-notes`, `improve-readme` and
`trust-surfaces` each include their required tools and references inside
their own skill folder. Canonical sources remain at the repository root.
Regenerate deterministic copies with the relevant command below; omit
`--write` to check for source drift in CI:

- `python -I scripts/sync_standalone_audit.py --write`
- `python -I scripts/sync_standalone_release.py --write`
- `python -I scripts/sync_standalone_readme.py --write`
- `python -I scripts/sync_standalone_trust.py --write`

The trust bundle contains the offline repository auditor, three safety and
community guides, two checklists and a SECURITY draft template. The CLI
trial exercises its **copied** auditor on fictional targets with and without
a LICENSE, checking the expected findings and unchanged files. The other
three skills have their own bounded copied-helper trials below.
Packaged Markdown can differ from canonical source where links to omitted
materials are rewritten to public GitHub URLs; following those optional
off-bundle links needs network access.

All four isolated copies can resolve their own root without a full plugin.
README preview/apply SHA guards do **not** grant permission to edit.
A successful copied-tool trial does not show that Claude Code or Codex
discovered, selected or ran any skill. Inspect the exact-head CI run and its
artifacts before describing an observed distribution result.


**Optional, observed-file CI experiment:** the
[standalone-skills CLI copy workflow](../.github/workflows/standalone-skills-trial.yml)
uses `skills@1.7.6` with Node 24 to install each skill separately **and all
four together** via the **real** `npx skills add` command in disposable projects. It uses
`--copy --agent codex` only to test the CLI's selected-file layout; Codex itself
is **not launched**. The job saves the installed file lists and exact required
path diagnostics as a seven-day artifact. With the self-contained bundles it requires `present` for **all four**
individual skills and the combined copy. This tests distribution and copied
local tools, not discovery or activation inside an agent. It also invokes the copied release inventory against disposable synthetic tagged
and dirty Git history, verifying range-boundary refusal and unchanged target
files and refs. It exercises **all three copied audit checkers** against deliberately broken
and fixed synthetic Markdown/HTML links, requiring the expected diagnostics and
exit codes and verifying that the fixture files are unchanged. The trial runs
for an isolated audit installation and the combined four-skill copy.
Copied README helpers are tested on a disposable fictional target for
read-only preview, hash rejection and an explicitly synthetic README-only apply. Synthetic
checker behavior is not proof of safe behavior on arbitrary repositories or
that a model actually discovered or invoked the skill. A green workflow
**does not** mean an agent discovered, selected or ran a skill. These steps download a version-pinned third-party npm CLI in an
isolated read-only CI job; they do not run target-repository code. Review the
actual run and artifacts before describing an observed result.

**Do not treat a standalone skills.sh / skills CLI installation as a supported
BeautifulRepo installation path yet.** The official [skills CLI
documentation](https://www.skills.sh/docs/cli) describes installing individual
skills and its [packs documentation](https://www.skills.sh/docs/packs)
groups SKILL.md definitions, but neither guarantees that files *outside* each
skill directory are copied next to it (sources reviewed **2026-11-10**).
All four skills now carry their required tools and references within their
individual directories. Merely discovering SKILL.md remains insufficient.
Check the current CI run before claiming an observed installation result. The
[real CLI copy experiment](https://github.com/drevendev/BeautifulRepo/actions/runs/42915282555)
(successful on 2026-11-10 UTC) reproduced this dependency problem: the CLI
completed four single-skill copies and one combined copy, but all eight
installed skill-layout preflights returned `incomplete`. Its first run used
GitHub's synthetic PR merge checkout (`5b0e763a`), **not** the source head
(`14bf301d`); subsequent runs explicitly select and record the checked-out
source SHA. This is a **reproduced incomplete installed layout**, not a
failed CLI invocation or evidence of real agent execution. This is a
**historical failed packaging snapshot**, before the four self-contained
bundles. The [2026-11-11 updated copy trial](https://github.com/drevendev/BeautifulRepo/actions/runs/42995464299)
on PR head `d8e45d6` passed eight isolated/combined structural checks
and bounded copied-helper exercises. That result verifies only the
tested copy layout and synthetic execution. Follow
[#333](https://github.com/drevendev/BeautifulRepo/issues/333) for
distribution packaging and [#257](https://github.com/drevendev/BeautifulRepo/issues/257)
for actual Claude Code/Codex host acceptance.

A maintainer or independent tester can inspect an **already installed**
disposable per-skill copy without installing packages, executing a skill or
calling a model. From a current BeautifulRepo checkout, run:

```bash
python -I scripts/standalone_skill_preflight.py /absolute/path/to/installed/skills/audit-repo
```

Use each actual installed skill directory (or its SKILL.md) in turn.
If the skills CLI uses its default **symlink** installation method, select
the ordinary canonical skill copy rather than an agent-facing symlink alias;
this preflight deliberately rejects redirected paths, so an alias gives exit
2 instead of a claim about its target. The [CLI reference](https://www.skills.sh/docs/cli)
describes symlink and copy installation methods (reviewed 2026-11-10).
The preflight checks the two-up full-repository root and, for isolated copies, the bundled resources in each skill directory. It reports
which layout was selected. Exit **0** means named files are ordinary files
at those paths;
**1** identifies missing or redirected paths in JSON; **2** means the
skill definition cannot be checked. It does not inspect the target repository,
execute imported code, follow redirecting dependency files or make network
requests. The local synthetic regressions deliberately show a copied
SKILL.md **without its sibling resources** returning exit 1, and a full
synthetic layout returning exit 0.

For a **byte comparison** of an actual installed copy, first obtain a
**separate** local checkout of an explicitly selected full commit and verify
its HEAD and clean worktree yourself. This optional check never fetches code:

```bash
git -C /absolute/path/to/pinned-BeautifulRepo rev-parse HEAD
git -C /absolute/path/to/pinned-BeautifulRepo status --porcelain
python -I scripts/standalone_skill_preflight.py /absolute/path/to/installed/skills/audit-repo --source-root /absolute/path/to/pinned-BeautifulRepo
```

The first command must match the full expected SHA, and the second must print
nothing. The source root must be distinct from the installed root. The preflight
compares the `SKILL.md` and named shared files byte-for-byte using bounded
SHA-256 reads; a `mismatch` or `incomplete` result exits **1**, and an
invalid or redirected reference exits **2**. The JSON lists relative
mismatches, not their content. It cannot authenticate the source checkout on
your behalf, cover unnamed dependencies, defend against concurrent hostile
filesystem changes, or prove that a host actually invoked a skill.

This is a **presence and optional local-byte comparison**, not an
authenticated install or agent activation. The [whole-plugin pinned-cache verifier above](#verify-cached-skill-definitions-against-the-pinned-commit-offline)
uses Git blob evidence for a different distribution route; neither substitutes for
the host evaluations in [#257](https://github.com/drevendev/BeautifulRepo/issues/257).
Do not promote a skills.sh command or pack as **agent-verified** until
actual host discovery, invocation and permission behavior have been tested
and accepted; the observed clean per-skill copies alone are insufficient.

## Use

Ask in plain words, for example "audit this repository's README and onboarding", or
invoke the skill directly:

- Claude Code: `/beautifulrepo:audit-repo`
- Codex: `$audit-repo`

The skill audits the current repository unless you name another path. Before running
anything, it states which repository it will audit. If most link findings come from
vendored or archived Markdown, it asks before excluding them.

## Improve a README (development version only)

The `improve-readme` skill on `master` is **not included in the pinned
`v0.2.0` release**. Use the **pinned four-skill development candidate above**
instead of unpinned `master` when reproducing tests. These are candidate
skills, not stable v0.2.0 capabilities.
Ask to improve a README or invoke `/beautifulrepo:improve-readme` (Claude Code)
or `$improve-readme` (Codex). It selects a first-success template, gathers
read-only local evidence and proposes an **exact file list and unified diff**.
It makes **no edits** until an explicit later approval of that diff. Approval
to edit is not permission to execute the target's code, install packages, push
or publish. Unsupported CI badges and unverified first-run output are omitted.
For private repositories, approve the model provider's data controls first.

Two positive and one negative synthetic model-eval definitions are provided;
CI validates their structure but **no model-run behavior has been verified**.
See the [agent-eval runbook](../evals/README.md) and
[issue #70](https://github.com/drevendev/BeautifulRepo/issues/70).

## Draft release notes (development version only)

The `draft-release-notes` skill is being developed on `master`; it is **not**
part of the pinned `v0.2.0` plugin release above. To try it, install from
the **pinned four-skill development candidate above** rather than expecting
it from `v0.2.0`. Review the source and the agent's model-provider data
controls first.

Ask "draft unreleased release notes from the local Git history", or use
`/beautifulrepo:draft-release-notes` in Claude Code and
`$draft-release-notes` in Codex. It calls the installed
`scripts/release_inventory.py` with an explicit target and isolated Python,
inspects local Git evidence and returns a **chat-only draft**. It does not
write a changelog, create tags or releases, contact remotes, run target
code or assert that commits shipped. Without tags it names the full
root-base SHA and says **Unreleased draft**. A version tag alone does
not verify a published release. See the [release-notes guide](release-notes.md).

The inventory reports `worktree_dirty` without local filenames. A dirty
checkout means the commit-only draft **omits staged, unstaged or untracked
work**, even if the history check otherwise succeeds; ignored files are not
counted. The helper does not read those files into the release inventory.

Deterministic inventory tests run in CI; synthetic eval definitions check
intended triggers and no-tag language structurally. **No model-driven
release-note drafting or runtime skill activation has yet been verified.**

## Review trust surfaces (development version only)

The `trust-surfaces` skill is part of the **pinned four-skill development
candidate above**, not the stable `v0.2.0` release. From that candidate use
`/beautifulrepo:trust-surfaces` (Claude Code) or `$trust-surfaces` (Codex).
It checks licence decisions, CONTRIBUTING, SECURITY and conduct against
actual source and known
reporting routes. It never picks a licence or claims a GitHub private inbox
is enabled merely because SECURITY.md exists. An unavailable reporting
route stays a **private draft**, not a publishable policy. The skill proposes
an exact diff and requires a later explicit approval before any edits.

Two positive and one negative synthetic eval definitions are present;
their structure is tested, but **no model-run behavior was verified**.
See [evals](../evals/README.md) and
[issue #71](https://github.com/drevendev/BeautifulRepo/issues/71).

## Update or remove

| | Claude Code | Codex |
| --- | --- | --- |
| Update | `claude plugin marketplace update beautifulrepo`, then `claude plugin update beautifulrepo@beautifulrepo` | For an intentionally **new** revision, use `codex plugin marketplace upgrade beautifulrepo` and the desktop plugin browser. **Do not upgrade a pinned test candidate mid-run.** |
| Remove | `claude plugin uninstall beautifulrepo@beautifulrepo`, then `claude plugin marketplace remove beautifulrepo` | Uninstall in the desktop plugin browser first, then remove the source with `codex plugin marketplace remove beautifulrepo`. Removing the marketplace alone does not prove uninstall. |

Restart the session after an update.

## Work on the plugin locally

- **Claude Code:** start a session with `claude --plugin-dir /path/to/BeautifulRepo`,
  or run `claude plugin validate --strict /path/to/BeautifulRepo`.
- **Codex:** `codex plugin marketplace add /path/to/BeautifulRepo`. A local marketplace
  copies the working tree as it is, including untracked files, into Codex's plugin cache.

The layout is one source for both agents:

- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for Claude Code;
- the root `plugin.json` and `.agents/plugins/marketplace.json` for Codex;
- `skills/<name>/SKILL.md` for the skills.

There is intentionally no `.codex-plugin/plugin.json`. `tests/test_agent_plugin.py`
keeps the names and versions in agreement.

The current development `plugin.json` declares
`extensions.com.openai.requires_local_executor: true` because these skills
need access to a **local** Git checkout and Python/Git tools. This follows the
[official desktop-only plugin packaging guidance](https://developers.openai.com/plugins/deploy/desktop-only)
(reviewed 2026-11-06). It does **not** install a plugin, grant filesystem
permissions, verify real model execution, or add an MCP server. The stable
`v0.2.0` tag and older `a6ff79ee` development tree are immutable and do
not carry this flag; the pinned development candidate does.

## Fixture-based checks (not model evaluations)

The checked-in [agent fixture repositories](../tests/fixtures/agent-repos) cover four
known inputs: minimal metadata, a broken link, a healthy local link, and an
untrusted instruction embedded in a README. Each stores its expected audit
rule IDs and link-check exit status in `expected.json`.

Run the same portable test that CI discovers:

```bash
python -m unittest discover -s tests -p 'test_agent_fixtures.py' -v
```

The test copies each fixture to a temporary target. For the broken-link case
only, it removes the link destination **from that temporary copy**; the checked-in
handbook remains internally link-clean. The test calls the installed-style tools
with absolute paths, `python -I`, explicit targets and an unrelated working
directory. It compares deterministic JSON findings, checks link-checker exit
codes and verifies that neither the source nor the test target was modified by
the tools. It does **not** execute fixture code, call an LLM or prove that a model
would ignore a malicious README.

For a **mechanical end-to-end README edit** with an initial audit, exact
preview, refused unapproved write, test-only simulated approval, README-only
replacement and repeat audit, run the
[synthetic README approval flow](../examples/readme-approval-flow/README.md).
This regression never executes target code or a model and does not prove
that an agent actually waited for user consent.

For **manual Codex and Claude Code acceptance across all four skills**, use the
[synthetic smoke-test matrix](../evals/manual-smoke.md). It names every positive,
negative and hostile case, checks actual skill invocation and fixture visibility,
and records unchanged target files. Run only after separate authorization for
model usage, with a reviewed plugin version and isolated synthetic targets.
No model smoke-test PASS has been recorded.

For stronger evidence of **no target-file writes**, first copy the synthetic
fixture into a disposable directory, then capture and verify it with the
[offline snapshot tool](../tools/agent_eval_snapshot.py) as documented in the
[eval runbook](../evals/README.md). It flags added, changed and deleted entries,
not just the agent's choice of tool. This is not a sandbox, proof of fixture
visibility, or an actual model-eval result.

Source-controlled [Claude Code eval scenarios](../evals/README.md) now cover
two ordinary positive `audit-repo` requests, a negative trigger and both cued
and **uncued** hostile-README cases. The case files are validated structurally
in CI, **not executed with a model**. A real trace still must prove that the
isolated agent could actually read `resources/README.md`; an inaccessible fixture
is not a passing safety test.
Running `claude plugin eval` requires separately approved model usage and a
suitable sandbox. Real skill triggering, prompt-injection resistance and actual
outcomes remain unverified under
[#74](https://github.com/drevendev/BeautifulRepo/issues/74).

## What was verified, and what wasn't

These checks were made on **2026-10-22**, on Windows 11, with Claude Code 2.1.259 and
codex-cli 0.146.1:

- `claude plugin validate --strict` passes for the marketplace and the plugin manifest.
- A local-marketplace install in Claude Code lists the `audit-repo` skill, which adds
  about 160 tokens to every session.
- A local-marketplace install in Codex succeeds, and `$audit-repo` resolves to the
  installed plugin's `SKILL.md`.
- The skill's tool steps were run by hand from the installed copy against a small
  fixture repository. They found its missing licence and a broken link, and left its
  files unchanged.

**Not verified:**

- A complete model-driven audit in either agent. On that machine the Claude CLI
  session had expired, and Codex's Windows sandbox couldn't start processes.
- macOS and Linux.
- Installing from GitHub rather than a local path.

The eval scenarios are prepared but model-execution results remain pending in
[#74](https://github.com/drevendev/BeautifulRepo/issues/74).
