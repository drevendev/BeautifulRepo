# Use BeautifulRepo from Claude Code or Codex

BeautifulRepo ships as **one plugin** for Claude Code and Codex. Its first skill,
`audit-repo`, audits a local repository the way this handbook does:

- It runs `repo_audit.py`, `docs_links.py` and `html_navigation.py` from the installed
  plugin against the target.
- It applies the [repository](../checklists/repository.md) and
  [first-success](../checklists/first-success.md) checklists.
- It reports prioritized findings, each with the smallest fix and a way to verify it.

The skill is **read-only and offline**. It doesn't write files, run the target's code,
or send anything over the network. It follows the
[agent ground rules](agent-safety.md).

## Install

You need Python 3.11 or newer on `PATH`.

**Claude Code:**

```bash
claude plugin marketplace add drevendev/BeautifulRepo
claude plugin install beautifulrepo@beautifulrepo
```

**Codex:**

```bash
codex plugin marketplace add drevendev/BeautifulRepo
codex plugin add beautifulrepo@beautifulrepo
```

Restart the agent session afterwards so it loads the skill.

The plugin is **not yet in a tagged release**: `v0.1.0` contains only the GitHub
Action. Until the next release, these commands follow `master`. Once a release
includes the plugin, pin it instead. For Codex, use
`codex plugin marketplace add drevendev/BeautifulRepo --ref vX.Y.Z`. For Claude Code,
the marketplace documentation describes `drevendev/BeautifulRepo@vX.Y.Z`.

## Use

Ask in plain words, for example "audit this repository's README and onboarding", or
invoke the skill directly:

- Claude Code: `/beautifulrepo:audit-repo`
- Codex: `$audit-repo`

The skill audits the current repository unless you name another path. Before running
anything, it states which repository it will audit. If most link findings come from
vendored or archived Markdown, it asks before excluding them.

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

Automated agent evaluations are planned in
[#74](https://github.com/drevendev/BeautifulRepo/issues/74).
