# Case studies

Real applications of the handbook to real repositories. Each case follows the same
procedure, so cases can be compared, and every claim can be traced to a revision, a
command or an observation.

| Case | Repository | Status |
| --- | --- | --- |
| [README before/after](readme-first-success-case.md) | BeautifulRepo | complete; written before this procedure, which it shaped |
| [First pattern studies](first-patterns.md) | Devostasis, Hungry Crab, Gum | source observations only, no changes made |

## The procedure

A case changes the target through that repository's normal pull request. It never edits
another repository without its owner's permission. The steps below are the minimum.

### 1. Snapshot "before"

- The full commit SHA and the date of observation.
- Metadata from `gh api repos/OWNER/REPO`: description, topics, homepage, licence.
- Releases and tags (`gh release list`, `git tag`).
- Whether private vulnerability reporting is enabled:
  `gh api repos/OWNER/REPO/private-vulnerability-reporting`.

### 2. Audit with pinned tools

Run BeautifulRepo's tools from a **pinned** release commit, never from a moving
branch, in isolated mode and with an explicit root. Save the output outside the target.

```bash
python -I tools/repo_audit.py ../target --format json --fail-on never
python -I tools/docs_links.py --root ../target
python -I tools/html_navigation.py --root ../target
```

Then go through the [repository checklist](../checklists/repository.md) and the
[first-success checklist](../checklists/first-success.md) by hand. Record each
finding as **obstacle → affected reader → smallest fix → verification**, with a
`file:line`.

### 3. Change the target through its own pull request

- Keep it to a few changes, each with a rationale and a trade-off.
- Follow the target's own contribution rules, checks and review.
- Don't add a contact route, badge or claim the target can't back.

### 4. Snapshot "after"

- The merge SHA and a re-run of the same pinned tools.
- The first-success command repeated in a **fresh clone**, with the **observed**
  output, including at least one failure path.
- Rendering at a narrow width (320 px) in light and dark themes, with a text
  equivalent of what was seen.
- The target's CI run URL for the merge commit.

### 5. Write up `case-studies/<repository>.md`

SHAs, a summary of the diff, the commands, observed versus expected results, and what
was **not** tested. Link it from the table above.

## Rights and quoting

- **Licensed targets** (for example MIT): short quotations with attribution are fine.
  Link to the target rather than copying files.
- **Unlicensed targets**: ideas only. Describe the obstacle and the change in your own
  words, and quote no text, code or images, unless the owner licenses the repository
  first. Being the owner of both repositories doesn't change what a public case may copy
  from an unlicensed one.

## Known tool caveats

- Use BeautifulRepo **v0.2.0 or later** on repositories you don't control. Earlier
  versions on Windows could open a UNC share named by the target
  ([GHSA-9rpm-g83x-47w7](https://github.com/drevendev/BeautifulRepo/security/advisories/GHSA-9rpm-g83x-47w7)).
- Before v0.2.0, `docs_links.py` and `html_navigation.py` without `--root` checked
  BeautifulRepo's own checkout, and `html_navigation.py` failed under `python -I`
  ([#68](https://github.com/drevendev/BeautifulRepo/issues/68)). Always pass `--root`.
- The link checkers don't fetch external URLs, parse reference-style links or scan
  setext headings. The audit's findings are heuristics with stated limits
  ([tools README](../tools/README.md)).
- Counts in tool output, such as destinations or tests, belong to one commit. Record
  them with the SHA, not as lasting facts.
- Rendering checks with viewport emulation are not real devices, and none of these
  steps tests a screen reader. Say so in the "not tested" list.

## Skeleton

```markdown
# <Repository>: <the reader obstacle, in one line>

**Case status, YYYY-MM-DD:** <complete | in progress>; <what is and isn't verified>.

## Target and revisions

- Repository: <link>, licence <SPDX id>.
- Before: `<full sha>` (observed YYYY-MM-DD). After: `<merge sha>`, via <PR link>.
- BeautifulRepo tools: `<pinned sha>` (vX.Y.Z).

## Before

<metadata, releases, private reporting; tool output summary; checklist findings as
obstacle → reader → smallest fix → verification>

## Changes and trade-offs

<each change, why, and what it costs>

## After

<tool re-run; fresh-clone first success with observed output and a failure path;
320 px light and dark with a text equivalent; CI run URL>

## Not tested

<explicit list>
```
