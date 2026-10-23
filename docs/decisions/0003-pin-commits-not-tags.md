# 0003: Adopters pin a commit SHA; release tags never move

- **Date:** 2026-10-22
- **Landed in:** [#51](https://github.com/drevendev/BeautifulRepo/pull/51), [#52](https://github.com/drevendev/BeautifulRepo/pull/52)
- **Status:** accepted

**Context.** The Action runs BeautifulRepo's code inside other repositories' CI. A
tag or branch reference can change under them, so a check that passed yesterday
could run different code today.

**Decision.** The adoption guide pins `drevendev/BeautifulRepo@<full sha> # vX.Y.Z`.
A tag ruleset blocks moving or deleting `v*` tags for everyone, admins included,
and the scheduled `pins.yml` check fails if a documented pin no longer matches its
tag.

**Consequences.** A wrong tag can't be fixed by moving it. Check the commit before
pushing a tag (maintenance workflow, "Cut a release"). Adopters update pins
deliberately, helped by Dependabot's `github-actions` updates.
