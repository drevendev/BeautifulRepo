# 0007: The repository root is also the agent plugin's root

- **Date:** 2026-10-22
- **Landed in:** [#90](https://github.com/drevendev/BeautifulRepo/pull/90), refined in [#120](https://github.com/drevendev/BeautifulRepo/pull/120)
- **Status:** accepted

**Context.** The Claude Code and Codex plugin needs the tools, guides and checklists
next to its skills. Copying them into a plugin folder would let the two drift apart,
and symlinks don't survive every install path.

**Decision.** The plugin root is the repository root. Claude Code reads
`.claude-plugin/`, Codex reads the root `plugin.json` and `.agents/plugins/`, and
both read `skills/<name>/SKILL.md`. Names and versions agree, which a test checks.
Agent instructions live in `AGENTS.md`, which Claude Code imports through
`.claude/CLAUDE.md`, because a root `CLAUDE.md` fails `claude plugin validate --strict`.

**Consequences.** Everything in the repository ships to plugin users, so new
top-level files are part of the plugin. Skills reach the tools by a path relative
to the installed copy and run them with `python -I` and an explicit `--root`.
