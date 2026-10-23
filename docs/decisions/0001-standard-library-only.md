# 0001: The tools use the Python standard library only

- **Date:** 2026-10-08
- **Landed in:** [#3](https://github.com/drevendev/BeautifulRepo/pull/3)
- **Status:** accepted

**Context.** The checks have to run in any maintainer's checkout, inside other
repositories' CI through the Action, and from an agent plugin's install folder. Each
third-party package would be one more install step, one more supply-chain risk and
one more thing to pin.

**Decision.** Everything under `tools/` and `examples/` imports only the Python
standard library. The minimum version is Python 3.11, which CI tests explicitly.

**Consequences.** `python tools/<tool>.py` works straight after a clone, with no
virtual environment. Markdown parsing is a bounded subset written here rather than
a full CommonMark library, and each tool's README states the limits. Developer-only
tools, such as a linter, may run in CI but are never imported by the tools.
