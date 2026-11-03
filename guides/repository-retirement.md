# Pause or archive a repository without misleading readers

A project can stop receiving maintenance while its code remains useful. The
reader's problem is not the absence of a badge: it is finding an apparently
active README, outdated installation steps, and a contribution link that no
longer leads to review. Publish a truthful landing page **before** changing the
repository's GitHub archive setting.

This is a **preparation recipe**, not an instruction to archive BeautifulRepo
or any other repository. Archival and unarchival are owner/admin decisions.
For a temporary absence or a possible successor, use the
[maintainer handoff recipe](maintainer-handoff.md) instead.

## Choose the actual state

| State | What the visitor can expect | What the owner should say |
| --- | --- | --- |
| **Active** | Maintenance route exists and is described accurately | Which contributions and support paths actually work |
| **Paused / unmaintained, not archived** | The repository is still writable by authorized users; response or review may not happen | That maintenance is paused, from when, and whether issues/PRs are being accepted |
| **GitHub-archived** | GitHub marks the repository read-only; existing issues, PRs, comments, code and releases cannot be changed until unarchived | That the archive action actually happened and there is no active support/merge promise |

**Do not write "archived" just because work stopped.** Check the live GitHub
repository status before using that word. GitHub's archive flag does not prove
the software is safe, current, or reproducible.

## Prepare the last truthful entrance

1. **Name the boundary.** Record the project's repository URL, full last
   maintained commit SHA, the date maintenance stopped, and the person or
   organization *actually authorized* to decide what happens next. Avoid a
   vague `latest` link. If no successor has accepted, say so.
2. **Keep one reproducible reading path.** Preserve the README's purpose,
   prerequisites, last-known working command and output **only where observed**.
   Give the tested environment and source revision. If untested, label it
   "Not verified since [date]" instead of claiming it still works. A GitHub
   archive does not certify builds or dependencies.
3. **Triage the public queue.** Review the actual open issues and PRs. GitHub
   recommends closing them before archiving; explain any intentionally
   unresolved work in a final public note. Do not silently close a valid
   security report or promise that a future fork will finish it.
4. **State the trust boundary.** Retire promises of response times and release
   schedules. Keep a confidential vulnerability channel only if it is
   genuinely active and someone can receive the report. Otherwise **do not**
   invite sensitive reports into public issues, or invent a private email.
   See [community safety](community-safety.md).
5. **Check retention, not just visibility.** Preserve licensing and
   third-party attributions. Consider whether any hosted demos, package
   registries, domains or download links will be switched off separately.
   Do not claim they remain available without checking. Follow your actual
   backup/retention requirements; archiving is not a substitute for backups.
6. **Prepare and review the notice.** Adapt the
   [archive/maintenance notice template](../templates/REPOSITORY_STATUS_NOTICE.template.md).
   Remove all bracketed placeholders, link it near the README top, and review
   the rendered narrow-screen view. Use the **paused** version until GitHub's
   actual archive status changes.

For a local checkout, these are **read-only Git identity/working-tree checks**,
not software tests:

```sh
git rev-parse --verify HEAD
git status --short
```

Record the results and date *when actually run*. A dirty working tree means
the displayed SHA does not describe every local file; do not claim it does.
If the last-known verification command runs project code, obtain the needed
permission and environment first. Do not treat an old CI badge as a fresh run.

## What the archive switch really does

GitHub says that an archived repository becomes read-only: issues, PRs,
comments, releases, labels, branches and repository content cannot be edited
until it is unarchived. Collaborators cannot be added or removed while
archived. Existing readers may still inspect/fork the public source, but this
is **not** a maintained support channel. GitHub recommends updating the
README and description and closing issues/PRs **before** archiving.

A repository **archive**, an individual **archived pull request** (a moderation
operation), and a **backup** are different things. Do not use one as evidence
for another. No admin action is part of this recipe.

## Worked example: an honest transition

_Fictional project and outputs; not a claim about BeautifulRepo._

**Before (misleading):**

> Harbor Notes — actively maintained. Open an issue for a quick fix. Run
> `python app.py` to get started.

This promises a response, omits prerequisites and does not show evidence.

**After (public notice prepared while the repo is still unarchived):**

> **Maintenance paused — 2026-11-03.** Harbor Notes is no longer accepting
> routine changes. Existing code can be inspected at commit
> `0123456789abcdef0123456789abcdef01234567` (illustrative SHA only).
> The former `python app.py` first-run path has **not** been rechecked,
> and may no longer work. No successor, support turnaround or private
> security intake is confirmed. Please do not post sensitive details in
> public issues. This repository has **not** been archived on GitHub.

**Before** an authorized archive, change the paused notice to truthful
future-facing language such as "This repository is being prepared for archival."
**After** the owner archives it, verify the GitHub archived flag. GitHub makes
the README read-only, so do not promise to change the notice afterward; that
would require a separate authorized unarchive. If a maintained fork exists,
link it only after checking the destination and the new maintainer's consent;
a fork is not automatically an endorsed successor.

## Acceptance receipt to leave behind

Record the actual revision and date, the final README/status wording, a
last-known command and its **observed** result or explicit unverified status,
what was done with open issues/PRs, whether a trusted security intake remains,
and the final **observed GitHub archived flag**. The notice and checked-out
source are reader evidence; an archive flag alone is not.

A revived maintainer should verify permissions and re-run the first-success
checks, link checks, and relevant CI on the **new** revision before removing
the notice. Unarchiving by itself does not restore maintenance.

## Sources and limits

Reviewed **2026-11-03**:

- [GitHub: Archiving repositories](https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories)
  documents the read-only surfaces, recommended issue/PR cleanup and
  unarchival requirement.
- [GitHub: Archiving a GitHub repository](https://docs.github.com/en/repositories/archiving-a-github-repository)
  distinguishes repository archival, citation and backups.
- [Open Source Guides: Best Practices for Maintainers](https://opensource.guide/best-practices/)
  discusses honest availability, documenting expectations and making space
  for a successor.

This is editorial guidance for GitHub repositories, not a legal preservation
policy, security audit, backup guarantee, or proof of current availability
of any external service. Verify current provider behavior before an admin
change.
