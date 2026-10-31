# First contribution: from a useful issue to a verifiable pull request

A first contribution should have a visible reader benefit, a small enough change
to review, and a way to tell whether it worked. A `good first issue` label is
a discovery aid, **not** a promise that the work is unclaimed, easy on every
platform, or guaranteed to be merged.

This is a practical companion to [CONTRIBUTING](../CONTRIBUTING.md) and
[issue triage](issue-triage.md). It is not a recruitment campaign or a promise
of maintainer response time.

## Contributor route

1. **Choose current work, not an old label snapshot.** Check the live issue,
   linked PRs and latest comments before starting. Read the repository's
   `CONTRIBUTING.md` and license. In BeautifulRepo, look for
   [open issues](https://github.com/drevendev/BeautifulRepo/issues) and the
   `good first issue` label; there may be none at a given time. For a larger
   or unlabelled change, ask whether the approach fits before investing heavily.
2. **Name the outcome in one sentence.** A concrete example is “the README
   command works from a fresh checkout,” not “improve documentation.” Check
   whether someone is already fixing it. Do not assume an issue assigns you
   exclusive ownership.
3. **Reproduce safely.** First read the commands and their effects. Run target
   code only in an environment where you are authorized to do so. Record the
   starting revision, working directory, runtime and exact failed command.
   Never post secrets, private logs or sensitive reports in a public issue.
4. **Make the smallest coherent change.** Use a topic branch, keep unrelated
   improvements out, and preserve licensing and public behavior. A README
   update may need a matching test or fixture; a test result is evidence only
   for the environment and revision actually exercised.
5. **Show a before/after.** Repeat the same command with the same input.
   Include the observed exit code and output, or mark the verification
   **NOT RUN**. “Looks good” and a screenshot of an unrelated build are not
   substitutes for a reproduction.
6. **Open a reviewable PR.** Link the issue, explain the reader change, list
   changed files, checks actually run, and limitations. Use a closing keyword
   only when the complete acceptance conditions will be met on merge.
   Respond to material review findings or explain when you cannot continue.

For this repository, a contributor can inspect the
[working Rowcount example](../examples/cli-starter/README.md), then run the
[documented local checks](../CONTRIBUTING.md#add-a-resource) from a trusted
checkout with Python 3.11+. The Rowcount example's `Data rows: 3` expectation
has regression coverage; this page **does not claim to have rerun it**.
The full default test suite includes a loopback application test, so read the
[maintenance workflow](maintenance-workflow.md) before running unfamiliar code.

## A small issue with a complete handoff

The following **fictional** example illustrates a bounded documentation
repair; it is **not** a reported BeautifulRepo defect or an open task.

> **Outcome:** A newcomer can open the setup guide from the README.
>
> **Before:** At revision `<full-sha>`, README line 12 points to
> `docs/setup.md`, but the actual tracked path is `docs/Setup.md`.
> On case-sensitive filesystems, the link does not resolve.
>
> **Change:** Correct that one relative destination. Keep its visible link
> text meaningful; do not rename the guide or rework the README layout.
>
> **Acceptance:** `python -I /path/to/BeautifulRepo/tools/docs_links.py
> --root /path/to/target` reports the original broken destination, then
> passes after the fix. Check the link in the target's rendered README if
> possible. Report the actual output instead of inventing a PASS.
>
> **Not in scope:** External URL availability, screen-reader certification
> and unrelated documentation cleanup.

This example has a failure, one target file, a repair and a verification
method. It also exposes what the checker cannot prove. Replace every
illustrative path and placeholder with the real source and result before
creating an issue. The [copyable issue template](../templates/GOOD_FIRST_ISSUE.template.md)
uses the same structure.

## Maintainer route: earn the label

Only add `good first issue` after checking the issue is bounded enough for a
newcomer. Give the affected reader, exact location or reproduction, expected
result, safe verification command, likely files, known dependencies and a
clear “out of scope.” If evidence is missing, say so; do not pretend an
unreproduced idea is ready to implement. Avoid assigning an arbitrary deadline,
claiming a mentor is available, or promising a merge. Recheck for duplicate or
in-flight PRs before labelling.

Choose an issue the contributor can *finish*, not a seemingly small task
requiring hidden infrastructure, credentials, a release or admin access. A
documentation correction with an observed broken link may be better than a
“simple” feature touching several undocumented systems. Use the
[triage decision card](issue-triage.md#an-issue-card-worth-copying) when the
evidence is incomplete; leave a blocked issue blocked until its real condition
changes.

This template is deliberately a Markdown **copying aid**, not an installed
GitHub issue form. To install a native form later, separately validate the
form schema and place it under `.github/ISSUE_TEMPLATE/` on the default
branch. Doing so changes the issue chooser; this guide does not.

## What this does not certify

A first merged PR is not a quality metric or guarantee of sustained
participation. No tool can grade a task's social difficulty, review latency or
mentoring capacity from the label alone. A green local command is narrower
than all CI and all supported platforms. For security reports, follow the
[actual security policy](../SECURITY.md), not this public issue template.

## Primary references

Reviewed **2026-10-30 (UTC)** (source guidance, not a live contributor study):

- [GitHub: contributing to open source](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-open-source):
  read project rules, find current work, branch, test and submit reviewable PRs.
- [GitHub: setting contributor guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors):
  where the guidelines appear to contributors.
- [GitHub: issue and PR templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates):
  templates guide submissions; native forms require repository configuration.
- [Open Source Guides: how to contribute](https://opensource.guide/how-to-contribute/):
  ask before substantial work, follow project guidance, and handle review.
