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

The source candidate at [commit `a6ff79ee137d2`](https://github.com/drevendev/BeautifulRepo/tree/a6ff79ee137d2eee8517792ba693c2854d51ed48)
contains `audit-repo`, `improve-readme`, `trust-surfaces` and
`draft-release-notes` (manifest version `0.3.0-dev.0`). It is **not a
stable v0.3.0 release**.
This candidate includes the four-skill manifest discovery correction (#261),
the bounded synthetic snapshot helper (#262) and the readable audit demo (#263).
Earlier candidate `9b3e43fd8502` remains inspectable, but its results must **not**
be treated as tests of this newer commit; record the exact SHA for every run. The following commands come from the current official
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
claude plugin marketplace add drevendev/BeautifulRepo@a6ff79ee137d2eee8517792ba693c2854d51ed48
claude plugin install beautifulrepo@beautifulrepo
claude plugin list
claude plugin details beautifulrepo
```

**Codex — test the same immutable commit:**

```bash
codex plugin marketplace add drevendev/BeautifulRepo --ref a6ff79ee137d2eee8517792ba693c2854d51ed48
codex plugin marketplace list
```

On Codex, the marketplace commands above only register and list the **pinned source**. Launch `codex`, open `/plugins`, choose **BeautifulRepo** from that marketplace and select **Install plugin**; start a new chat. The previously documented `codex plugin add ...` command is not part of the [current official marketplace CLI reference](https://developers.openai.com/plugins/build/plugins), so it is not a verified installation path. These UI steps are also a **test procedure**, not a claimed successful BeautifulRepo installation.

Restart the client. Check the *installed copy* of `skills/` for all four named
`SKILL.md` files and confirm they correspond to the pinned commit before a
model test. For a low-risk first test use a **disposable synthetic target**,
never a private repository with unapproved provider data controls. Follow the
[revision-pinned manual matrix](https://github.com/drevendev/BeautifulRepo/blob/a6ff79ee137d2eee8517792ba693c2854d51ed48/evals/manual-smoke.md).
Actual skill selection, file reads, tool calls, permission decisions and
before/after target snapshots must be observed; static CI and plugin manifests
cannot verify them. Results (including failures or INCONCLUSIVE outcomes) go to
[tester issue #258](https://github.com/drevendev/BeautifulRepo/issues/258);
release acceptance is tracked in [#257](https://github.com/drevendev/BeautifulRepo/issues/257).
The proposed [MCP server #255](https://github.com/drevendev/BeautifulRepo/issues/255)
is separate and **not installed** by these commands. No model evaluation or
release publication is automatic.

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
permissions, verify real model execution, or add an MCP server. The pinned
`v0.2.0` tag and `a6ff79ee` four-skill test candidate are immutable earlier
trees: do not attribute this new flag to either of them.

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
