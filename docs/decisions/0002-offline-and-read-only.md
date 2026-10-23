# 0002: The tools are offline and never run the repository they check

- **Date:** 2026-10-16
- **Landed in:** [#12](https://github.com/drevendev/BeautifulRepo/pull/12), hardened in [#110](https://github.com/drevendev/BeautifulRepo/pull/110)
- **Status:** accepted

**Context.** The audit and link checks read repositories written by other people:
in an adopter's CI, on a maintainer's laptop and through an agent. A check that
fetched URLs or imported the target's code would turn untrusted text into network
traffic or code execution.

**Decision.** The tools only read files, never import, build or execute the target,
and make no network requests. A destination or link target is checked as text
before anything is opened, so a path that names another drive, a UNC share or a
device is reported rather than followed.

**Consequences.** External links are out of scope, and the docs say so. The
promise is part of [SECURITY.md](../../SECURITY.md), so breaking it is a
vulnerability, not a missing feature.
