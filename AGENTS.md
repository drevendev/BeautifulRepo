# Working on BeautifulRepo as a coding agent

BeautifulRepo is a handbook for making repositories easy to understand, try and
contribute to: guides, tested starter examples, templates and small offline Python
checks. This file is the contract for agents that change it. People should read
[CONTRIBUTING.md](CONTRIBUTING.md), which says the same things at more length.

## Verify the checkout

From the repository root with Python 3.11 or newer, before every pull request:

```bash
python -I scripts/verify_checkout.py
```

This runs all nine Python steps of the Quality workflow's matrix job in order.
Use `--list` to inspect the inventory or `--keep-going` to collect independent
failures. It does **not** replace GitHub's cross-platform matrix, Action
self-test jobs or separate lint job. For targeted diagnosis, see
[CONTRIBUTING.md](CONTRIBUTING.md#verify-a-change-locally).
Report which checks actually ran and which did not.

Edit `catalog/resources.json`, never `catalog/README.md`. For catalog changes
only, regenerate the view with `python tools/catalog.py --write` before the
full verification command and review the generated diff.

## House rules

- **Public text is English**, specific and verified. Never invent a contact, badge,
  number, release, response time or test result. Say what you did not check.
- **The tools use the Python standard library only.** No runtime dependencies, no
  network requests, and nothing from the repository under audit is ever run.
- **Link issues without closing them by accident.** Write `Related: #N` for work that
  stays open, and `Closes #N` only when the pull request finishes the issue. Never
  write a negated closing phrase such as "does not fix #N".
- **Every change gets a changelog entry** under the matching `## [Unreleased]`
  section: Added, Changed, Deprecated, Removed, Fixed or Security.
- **Private targets stay private.** Before sharing findings, generated reports,
  screenshots or agent output, apply the
  [confidentiality checklist](checklists/confidentiality.md). Offline Python checks
  do not make an online agent session private.
- **Security problems are private.** Don't describe a vulnerability in a public
  issue, pull request or commit; follow [SECURITY.md](SECURITY.md).
- **One topic per pull request**, using the template's sections. `master` is
  protected: changes arrive by pull request, squash-merged after the five required
  checks pass on a branch that is up to date with `master`.

## Where things live

| Path | Contents |
| --- | --- |
| `guides/` | The handbook, one topic per page |
| `examples/` | Runnable starters, each with its own README and tests |
| `templates/`, `checklists/` | Reusable scaffolds and audit checklists |
| `tools/` | The offline checks, documented in `tools/README.md` |
| `tests/` | Unit and contract tests for all of the above |
| `skills/`, `plugin.json`, `.claude-plugin/` | The Claude Code and Codex plugin |
| `action.yml` | The GitHub Action other repositories pin |

The repository root is also the plugin root. A root `CLAUDE.md` would fail
`claude plugin validate --strict`, so Claude Code reads this file through
`.claude/CLAUDE.md` instead.
