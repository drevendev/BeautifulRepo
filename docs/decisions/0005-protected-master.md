# 0005: `master` takes squash-merged pull requests after five required checks

- **Date:** 2026-10-22
- **Landed in:** the `Protect master` ruleset, with the checks from [#35](https://github.com/drevendev/BeautifulRepo/pull/35) and [#50](https://github.com/drevendev/BeautifulRepo/pull/50)
- **Status:** accepted

**Context.** One maintainer and many agent-authored pull requests share `master`.
Adopters pin its commits. A direct push or a merge that skipped Windows or Python
3.11 would ship untested code to them.

**Decision.** A ruleset requires a pull request, squash merge, linear history,
resolved review threads and an up-to-date branch. The five required checks are
`Python 3.11`, `Python 3.14`, `Python 3.14 (Windows)` and the Action self-test on
Ubuntu and Windows. Force pushes and deleting `master` are blocked for everyone.

**Consequences.** Each change is one commit on `master` that names its pull request.
Parallel pull requests rebase or merge `master` before they can merge, so
changelog conflicts are routine. No approving review is required, because a single
maintainer couldn't approve their own work.
