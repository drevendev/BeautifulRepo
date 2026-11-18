# Pull request review record (copy and adapt)

> **Template, not a required GitHub approval or a repository policy.** Keep the
> original PR as the source of live checks, reviews and merge state. Do not
> paste secrets, private repository contents or unredacted model transcripts.

## Proposal

- PR and linked issue: `<URL>`
- Base branch / reviewed head SHA: `<branch> / <40-character SHA>`
- Intended reader or user outcome: `<observable result>`
- Changed paths and excluded scope: `<paths / explicit exclusions>`

## Evidence observed

- Source/diff inspected: `<paths, specific concern>`
- Relevant commands actually run: `<exact command, OS/tool version, exit code>`
- Provider checks on **that head**: `<links and outcomes; name untested jobs>`
- Review findings and conversations: `<links, material / non-blocking / unknown>`
- Permissions, dependencies, privacy and documentation implications:
  `<observed or not applicable with reason>`

## Decision

Select exactly one:

- [ ] **ACCEPT** — bounded scope works, relevant evidence is current,
      no material finding remains and actual provider gates permit merge.
- [ ] **REPAIR** — specific material problem: `<finding and acceptance test>`
- [ ] **DEFER** — missing material evidence: `<unknown, why it matters, next check>`

Non-blocking follow-up, if any: `<separate issue or explicitly none>`

Reviewer / review date: `<identity, YYYY-MM-DD>`

**Before any authorized merge:** re-read exact head, current checks,
mergeability, required reviews and conversations. Do not treat this saved
card as a substitute for current provider state. **After a merge:** verify
the published target files; a merge is not a release.
