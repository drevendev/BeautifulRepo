# Dependency update review — editable card

> Replace every placeholder. This is a template, **not an approval, policy,
> vulnerability report or proof of execution**. Follow the
> [review recipe](../guides/dependency-review.md).

- Reviewed on (UTC): [YYYY-MM-DD]
- Repository and PR: [link]
- Exact base and head commits: [full SHA / full SHA]
- Package/Action, ecosystem and role: [name; runtime/dev/build/CI]
- Old identity → new identity: [version and source SHA/lockfile entry]
- Direct/transitive: [known relationship, or unknown]
- Upstream source diff and release notes: [reviewed links/date, or unknown]
- Licence and dependency changes: [evidence, or unknown]
- Added token, workflow, network or artifact privileges: [what changed/unknown]
- Reproduction commands and actual output: [source revision, platform and results]
- Required checks on the exact head: [names/results, or unobserved]
- Untested conditions: [explicit list]
- Decision: [ACCEPT / DEFER / REJECT]
- Reason and revisit trigger: [specific evidence or accepted trade-off]

Keep private source, tokens and credentials out of the card. A green CI badge,
bot suggestion, version tag or full SHA pin alone cannot make the decision.
