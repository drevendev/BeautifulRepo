# Use BeautifulRepo from Claude Code or Codex

BeautifulRepo ships as **one plugin** for Claude Code and Codex. The
`audit-repo` skill audits a local repository the way this handbook does:

- It runs `repo_audit.py`, `docs_links.py` and `html_navigation.py` from the installed
  plugin against the target.
- It applies the [repository](../checklists/repository.md) and
  [first-success](../checklists/first-success.md) checklists.
- It reports prioritized findings, each with the smallest fix and a way to verify it.

The local Python checkers are read-only and make no network requests. An agent
session may still transfer repository context to the configured model provider.
Review approved data controls before inspecting private code. See the
[agent ground rules](agent-safety.md).

## Install

You need Python 3.11 or newer on `PATH`.

**Claude Code:**

```bash
claude plugin marketplace add drevendev/BeautifulRepo@v0.2.0
claude plugin install beautifulrepo@beautifulrepo
```

**Codex:**

```bash
codex plugin marketplace add drevendev/BeautifulRepo --ref v0.2.0
codex plugin add beautifulrepo@beautifulrepo
```

Restart the agent session afterwards so it loads the skill.

These commands pin release `v0.2.0`, the first release that contains the plugin.
Leave out `@v0.2.0` or `--ref v0.2.0` to follow `master` instead, for example
while working on the plugin.

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
`v0.2.0` release**. Install from a reviewed checkout or `master` to try it.
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
unpinned `master` or a local checkout rather than expecting it from
`v0.2.0`. Review the source and the agent's model-provider data controls first.

Ask "draft unreleased release notes from the local Git history", or use
`/beautifulrepo:draft-release-notes` in Claude Code and
`$draft-release-notes` in Codex. It calls the installed
`scripts/release_inventory.py` with an explicit target and isolated Python,
inspects local Git evidence and returns a **chat-only draft**. It does not
write a changelog, create tags or releases, contact remotes, run target
code or assert that commits shipped. Without tags it names the full
root-base SHA and says **Unreleased draft**. A version tag alone does
not verify a published release. See the [release-notes guide](release-notes.md).

Deterministic inventory tests run in CI; synthetic eval definitions check
intended triggers and no-tag language structurally. **No model-driven
release-note drafting or runtime skill activation has yet been verified.**

## Update or remove

| | Claude Code | Codex |
| --- | --- | --- |
| Update | `claude plugin marketplace update beautifulrepo`, then `claude plugin update beautifulrepo@beautifulrepo` | `codex plugin marketplace upgrade beautifulrepo` |
| Remove | `claude plugin uninstall beautifulrepo@beautifulrepo`, then `claude plugin marketplace remove beautifulrepo` | `codex plugin remove beautifulrepo@beautifulrepo`, then `codex plugin marketplace remove beautifulrepo` |

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

For a **manual Codex smoke check** after installing the plugin, try two positive
requests ("audit this repository's README" and "review onboarding for this
path") and one negative request ("review a Python code diff"), recording whether
the `audit-repo` skill triggered. Repeat with the injection-bait fixture and
confirm no file writes or invented reporting channel. Run against synthetic
repositories only unless the model provider is approved for the target data.
These are operator observations, not automated passing evals.

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
