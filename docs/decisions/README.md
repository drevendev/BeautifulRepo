# Decision records

Short records of choices that keep coming up in reviews, so a new maintainer or
agent can see why BeautifulRepo works the way it does without digging through
pull requests. Each record states the context, the decision, its consequences, the
date and the pull request where it landed. Revisit one by writing a new record
that supersedes it; don't rewrite history.

| Record | Decision |
| --- | --- |
| [0001](0001-standard-library-only.md) | The tools use the Python standard library only |
| [0002](0002-offline-and-read-only.md) | The tools are offline and never run the repository they check |
| [0003](0003-pin-commits-not-tags.md) | Adopters pin a commit SHA; release tags never move |
| [0004](0004-composite-action.md) | Other repositories get a composite action, not a reusable workflow |
| [0005](0005-protected-master.md) | `master` takes squash-merged pull requests after five required checks |
| [0006](0006-no-unverified-channels.md) | No contact route, promise or policy is published before it works |
| [0007](0007-plugin-root-is-repository-root.md) | The repository root is also the agent plugin's root |

## Template

```markdown
# NNNN: <decision in one line>

- **Date:** YYYY-MM-DD
- **Landed in:** #<pull request>
- **Status:** accepted | superseded by NNNN

**Context.** The problem and the forces at play, in two or three sentences.

**Decision.** What we do, stated so it can be checked.

**Consequences.** What this makes easy, what it rules out, and what to watch.
```
