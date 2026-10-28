# Issue triage that ends in a decision

A useful issue queue is not the one with the fewest open issues. It is the one
where a reader can tell what was reproduced, what remains unknown, who can
decide, and what would make the next action worthwhile. This is a small,
manual workflow for a volunteer-maintained GitHub repository. It neither
automates closures nor promises a response time.

## Review one issue, not the entire backlog

1. **Open the current issue and related PRs.** Check its latest comments,
   linked work and existing closed issues before starting a duplicate
   investigation. A saved issue list is only a historical snapshot.
2. **Look for a reader-observable result.** For a bug, record the source
   revision, minimal steps, expected and actual behavior. For a docs request,
   name the missing first-success step or inaccurate claim. For a proposal,
   state the user benefit and explicit constraints. Mark commands and
   environments that were not exercised **NOT RUN**.
3. **Choose one disposition.** Accept a bounded task with a testable
   acceptance condition; request the single missing reproduction fact; link a
   real duplicate; close an out-of-scope request with a reason; or retain an
   explicitly blocked/time-gated issue with a concrete revisit condition.
   An open issue is not automatically abandoned, and a closed issue is not
   necessarily repaired.
4. **Leave one useful public decision.** Record the evidence link and next
   condition on the GitHub issue. Do not maintain a second, perpetually stale
   list of issue status in a README or spreadsheet. Do not promise a maintainer
   or release schedule that has not been agreed.

For sensitive reports, stop the public triage. Refer to a **verified**
confidential intake route, not an invented mailbox, and do not request secrets
or exploit details in a public comment. See the
[community safety guide](community-safety.md) and this repository's
[security policy](../SECURITY.md).

## Make the disposition specific

| Situation | Reader-facing response | What not to claim |
| --- | --- | --- |
| Reproduced defect | State revision, exact reproduction and a failing/expected result; define a fix's acceptance | That a proposed fix already works |
| Missing evidence | Ask for the smallest useful missing detail, or label the test **NOT RUN** | That the absence of a failing test proves correctness |
| Duplicate | Link the canonical issue; preserve any materially different reproduction | That two similar titles prove the same underlying defect |
| Outside scope | Explain the boundary and close as not planned when appropriate | That declining work is the same as resolving a defect |
| Blocked or date-gated | Name the real dependency/decision/date and keep it open if still actionable | That a future review or owner decision has already happened |
| Security or sensitive abuse | Use a verified private route and the applicable policy | That a public issue is a safe reporting channel |

GitHub provides native issue closure reasons and duplicate references. A
comment starting with `Duplicate of #123` can create the native duplicate
timeline relationship for someone with write access; use an **actual verified**
canonical issue number, not `#123` literally. Ordinary cross-references
alone do not establish equivalence. Only use a closing keyword in a PR when
its integration really completes the issue; see
[the contribution rules](../CONTRIBUTING.md).

## An issue card worth copying

Paste this into an issue comment or a maintainer's review note, replacing
every bracketed field. It is a decision aid, **not** another queue database.

```text
Reader problem: [one observable consequence]
Evidence (revision/date): [reproduction command, screenshot, or source link]
Verified: [what was actually observed]
NOT RUN / unknown: [specific remaining checks]
Decision: [accept / need evidence / duplicate / not planned / blocked]
Acceptance or revisit trigger: [testable result, owner decision, or date]
Next authorized action: [one bounded change; no invented owner or ETA]
```

A good card can say **DEFER**. If a target repository is outside your write
authority, identify that limit rather than quietly creating a PR there.

## Two live BeautifulRepo examples, dated 2026-10-29

- [Visual accessibility issue #16](https://github.com/drevendev/BeautifulRepo/issues/16)
  has published design briefs, first-screen alternatives and a read-only
  measurement probe. Actual GitHub-rendered 400% zoom, keyboard and
  screen-reader results are still missing. **Decision: keep open.** Source
  tests and local synthetic browser measurements must not be promoted to an
  accessibility acceptance result. Use the
  [manual evidence receipt](../checklists/visual-accessibility-acceptance.md)
  before claiming a pass.
- [Historical Hacktoberfest label issue #100](https://github.com/drevendev/BeautifulRepo/issues/100)
  separates corrected public text from a still-unmade decision about the
  native label. Its requested post-event review is **after 2026-11-01**.
  **Decision as of this review: keep open without changing the label.** A
  future review date is not permission to perform an administrative change.

These are dated examples, not a cached live issue dashboard. Reopen the linked
issues for their current state; do not reuse the disposition blindly.

## Sources and limits

Primary guidance reviewed **2026-10-29**:

- [Open Source Guides — Best Practices for Maintainers](https://opensource.guide/best-practices/):
  set honest expectations, communicate decisions, and say no to unsuitable
  contributions rather than accumulating silent work.
- [GitHub Docs — Marking issues or pull requests as a duplicate](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/marking-issues-or-pull-requests-as-a-duplicate):
  the native `Duplicate of` comment behavior and permission boundary.
- [GitHub Docs — Closing an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/closing-an-issue):
  closure reasons and authorized actors.
- [GitHub Docs — About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues):
  issue tracking, references, and discussions.

This recipe is editorial judgement, not an issue-classification model or a
guaranteed service level. It never changes labels, permissions, issues or
repository settings on its own.
