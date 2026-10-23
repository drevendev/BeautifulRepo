# 0004: Other repositories get a composite action, not a reusable workflow

- **Date:** 2026-10-22
- **Landed in:** [#51](https://github.com/drevendev/BeautifulRepo/pull/51)
- **Status:** accepted

**Context.** Adopters want the audit and link checks as one step inside their own
job, next to their checkout and their choice of Python, without copying scripts.

**Decision.** `action.yml` is a composite action. It runs the tools from its own
checkout (`$GITHUB_ACTION_PATH`) with the caller's Python 3.11+, adds no nested
actions, and passes every input through environment variables rather than `${{ }}`
inside `run:`.

**Consequences.** Callers keep control of runners, permissions and Python setup.
A reusable workflow would have owned the whole job. The action can't install Python
itself, so it fails early with a message when none is on `PATH`. Its self-test in
`quality.yml` runs on Ubuntu and Windows, including cases that must fail.
