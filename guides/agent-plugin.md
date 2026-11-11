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

For Codex, adding the pinned marketplace registers a **source**, not an installed plugin. Launch `codex`, open `/plugins`, find **BeautifulRepo** in that marketplace, select **Install plugin**, then start a new chat. This follows the [documented Codex plugin-browser flow](https://developers.openai.com/learn/developers-codex-plugin); actual installation of BeautifulRepo on a fresh Codex host remains unverified. In Claude Code, start a new session after installation.

These commands pin release `v0.2.0`, the first release that contains the plugin.
Leaving out the pin follows mutable `master`; **do not use an unpinned
checkout as evidence for a tested release candidate**.

## Try all four skills from a pinned development candidate

The source candidate at [commit `cf8ac81ddabb5`](https://github.com/drevendev/BeautifulRepo/tree/cf8ac81ddabb5e2006913e65a2f980ef201baf5c)
contains `audit-repo`, `improve-readme`, `trust-surfaces` and
`draft-release-notes` (manifest version `0.3.0-dev.0`). It is **not a
stable v0.3.0 release**. Unlike the earlier `a6ff79ee137d2` trial tree,
this revision includes the Codex desktop-only `requires_local_executor`
manifest declaration, the documented plugin-browser installation flow, and
the four-skill discovery, snapshot and synthetic-demo corrections.
The [six source CI checks](https://github.com/drevendev/BeautifulRepo/actions/runs/42210225927)
completed successfully on this exact commit on 2026-11-06; they are **not**
evidence of successful plugin installation, skill discovery or model behavior.
Earlier candidates `a6ff79ee137d2` and `9b3e43fd8502` remain inspectable,
but their results must **not** be transferred to this candidate. Record the
exact SHA for every run. The following commands come from the current official
[Claude Code CLI reference](https://code.claude.com/docs/en/plugins/cli-reference)
and [Codex plugin guide](https://developers.openai.com/plugins/build/plugins),
but **fresh GitHub-source installation and actual model invocation have not
been confirmed** at this revision. Treat installation errors as test results,
not as proof of success.

Start with a clean, disposable test environment. If `beautifulrepo` is already
configured, inspect it first rather than overwriting valued marketplace settings.
You need Python 3.11+ and Git. Try one host, from a regular terminal:

**Claude Code — test the immutable commit:**

```bash
claude plugin marketplace add drevendev/BeautifulRepo@cf8ac81ddabb5e2006913e65a2f980ef201baf5c
claude plugin install beautifulrepo@beautifulrepo
claude plugin list
claude plugin details beautifulrepo
```

**Codex — test the same immutable commit:**

```bash
codex plugin marketplace add drevendev/BeautifulRepo --ref cf8ac81ddabb5e2006913e65a2f980ef201baf5c
codex plugin marketplace list
```

On Codex, the marketplace commands above only register and list the **pinned source**. Launch `codex`, open `/plugins`, choose **BeautifulRepo** from that marketplace and select **Install plugin**; start a new chat. The previously documented `codex plugin add ...` command is not part of the [current official marketplace CLI reference](https://developers.openai.com/plugins/build/plugins), so it is not a verified installation path. These UI steps are also a **test procedure**, not a claimed successful BeautifulRepo installation.

Restart the client. Check the *installed copy* of `skills/` for all four named
`SKILL.md` files and confirm they correspond to the pinned commit before a
model test. For a low-risk first test use a **disposable synthetic target**,
never a private repository with unapproved provider data controls. Follow the
[revision-pinned manual matrix](https://github.com/drevendev/BeautifulRepo/blob/cf8ac81ddabb5e2006913e65a2f980ef201baf5c/evals/manual-smoke.md).
**Historical-link caveat:** that immutable matrix links relatively to the
plugin guide *as it existed in the pinned commit*, where the installer still
references the superseded `a6ff79ee` candidate. For a `cf8ac81` trial, use
the full-SHA installation commands **on this page** and verify the installed
copy against the `cf8ac81` source, not the old guide or mutable `master`.
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
Separately check out the full `cf8ac81ddabb5e2006913e65a2f980ef201baf5c`
commit in a local Git working tree. Use the **actual cache location shown by
the host**, not another copy of the source checkout. The two paths must be
**different physical directories**: giving the same checkout twice (even
through alternate path spellings) returns INCOMPLETE, never MATCH. Independently
verify the source's Git origin and the host's cache location; a byte match
cannot authenticate where either directory came from.

From a **current BeautifulRepo toolkit checkout** (the verifier was added
*after* the historical candidate and is not present at that SHA), run:

```text
python -I "/path/to/current-BeautifulRepo/scripts/plugin_install_verify.py" --source "/absolute/path/to/cf8ac81-source" --installed "/absolute/path/to/installed-plugin-cache" --expected-commit cf8ac81ddabb5e2006913e65a2f980ef201baf5c
```

Requires Python 3.11+ and local Git; the source must be at the repository top
level, with `HEAD` equal to the supplied full SHA. Exit **0** means all four
installed `SKILL.md` files **and 22 named local dependencies** match the
**committed Git blobs** of that revision. The dependencies include the six
executable helpers, shared agent-safety guidance, task guides, three checklists
and the eight templates selected or required by the skills. The exact paths
are reported in JSON as `checked_plugin_dependencies`. Exit **1** means at
least one checked file differs; exit **2** means verification is incomplete
(for example a missing template, redirected file or wrong source revision).
JSON names differences without publishing file contents. Other guides,
manifests, libraries and any extra files in the cache are **not covered**.
A MATCH is **not** a complete plugin integrity or provenance certificate.

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

**Audit pilot — not yet host-accepted:** `audit-repo` now ships a self-contained
copy of its offline Python tools, checklists and guidance inside the skill folder.
The canonical originals remain at the repository root. The maintainer uses
`python -I scripts/sync_standalone_audit.py --write` to regenerate deterministic
copies, rewriting Markdown links to omitted examples or guides as explicit
GitHub source URLs. These optional off-bundle readings require network access.
The same command without `--write` detects drift in CI. Packaged Markdown
is intentionally not byte-identical where off-bundle links were rewritten.
A copied audit skill can select this local root if the complete plugin root is
unavailable. This is not evidence that Claude Code or Codex discovered,
activated or invoked the skill, and does not change the other three skills.
Inspect the updated CLI trial artifacts for source SHA, copied paths and
synthetic checker execution before calling even the pilot installation verified.


**Optional, observed-file CI experiment:** the
[standalone-skills CLI copy workflow](../.github/workflows/standalone-skills-trial.yml)
uses `skills@1.7.6` with Node 24 to install each skill separately **and all
four together** via the **real** `npx skills add` command in disposable projects. It uses
`--copy --agent codex` only to test the CLI's selected-file layout; Codex itself
is **not launched**. The job saves the installed file lists and exact required
path diagnostics as a seven-day artifact. With the current layout it deliberately
expects `present` for the copied `audit-repo` pilot and `incomplete` for
the other three skills, both alone and in the combined copy. It also runs the
copied audit tool against a disposable synthetic README. A green workflow
**does not** mean an agent discovered, selected or ran a skill. These steps download a version-pinned third-party npm CLI in an
isolated read-only CI job; they do not run target-repository code. Review the
actual run and artifacts before describing an observed result.

**Do not treat a standalone skills.sh / skills CLI installation as a supported
BeautifulRepo installation path yet.** The official [skills CLI
documentation](https://www.skills.sh/docs/cli) describes installing individual
skills and its [packs documentation](https://www.skills.sh/docs/packs)
groups SKILL.md definitions, but neither guarantees that files *outside* each
skill directory are copied next to it (sources reviewed **2026-11-10**).
Three skills still depend on unbundled repository-root resources; the
`audit-repo` pilot now carries source-synchronized copies. Merely discovering
SKILL.md is insufficient. The
[real CLI copy experiment](https://github.com/drevendev/BeautifulRepo/actions/runs/42915282555)
(successful on 2026-11-10 UTC) reproduced this dependency problem: the CLI
completed four single-skill copies and one combined copy, but all eight
installed skill-layout preflights returned `incomplete`. Its first run used
GitHub's synthetic PR merge checkout (`5b0e763a`), **not** the source head
(`14bf301d`); subsequent runs explicitly select and record the checked-out
source SHA. This is a **reproduced incomplete installed layout**, not a
failed CLI invocation or evidence of real agent execution. Distribution
support remains blocked under [#333](https://github.com/drevendev/BeautifulRepo/issues/333).

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
The preflight checks the two-up full-repository root and, for an isolated
`audit-repo` copy, the bundled files inside its skill directory. It reports
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
Do not promote a skills.sh command or pack until a clean per-skill install has
been reproduced and its exact filesystem layout and actual tool execution
have been verified.

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
| Update | `claude plugin marketplace update beautifulrepo`, then `claude plugin update beautifulrepo@beautifulrepo` | Refresh the source with `codex plugin marketplace upgrade beautifulrepo`; manage the installed plugin separately in `/plugins` (availability varies by host/version) |
| Remove | `claude plugin uninstall beautifulrepo@beautifulrepo`, then `claude plugin marketplace remove beautifulrepo` | Manage the installed plugin in `/plugins`; when no longer needed, remove its source with `codex plugin marketplace remove beautifulrepo` |

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
not carry this flag; the pinned `cf8ac81` development candidate does.

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
