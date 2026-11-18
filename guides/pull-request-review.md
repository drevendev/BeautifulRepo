# Review a pull request without inventing a merge gate

A good review decides whether the **specific change** is safe, useful and
understandable. It does not treat a green badge, a large test count or a friendly
comment as a substitute for reading the diff. This procedure works for small
open-source projects where maintainers may also be the authors.

Use the [copyable review record](../templates/PULL_REQUEST_REVIEW.template.md)
for the important evidence. Keep the actual discussion and approval state in
the pull request rather than copying live GitHub status into a second tracker.

## 1. Confirm what is proposed

Read the PR description, linked issue, base and **exact current head commit**.
Identify the promised user-visible outcome and the files changed. Check for
unrelated edits, generated files, dependency changes, permissions, credentials,
licensing and behavior outside the advertised scope.

From a trusted checkout, after replacing the placeholders with real SHAs:

```bash
git diff --name-status BASE_SHA...HEAD_SHA
git diff --check BASE_SHA...HEAD_SHA
git diff BASE_SHA...HEAD_SHA -- README.md guides tools tests
```

The triple-dot comparison uses the merge base; it is appropriate for reviewing
a branch's proposed changes, but is **not** proof of what GitHub will ultimately
merge. Re-read the provider's PR diff and mergeability at decision time.
Do not run an untrusted contributor's build script simply to start a review.

## 2. Choose the smallest relevant evidence

Ask what would go wrong if the change were incorrect:

- **Documentation or navigation:** check new destinations and anchors, example
  commands, permissions implied by instructions, accessibility/text alternatives
  and whether an unfamiliar reader can reach a first result.
- **Tool or test code:** inspect the inputs and boundaries, reproduce the bug on
  disposable data, run the relevant regressions and verify that a negative test
  really fails before the fix. Treat skipped platforms as untested.
- **Dependency or workflow:** inspect exact upstream revisions, privileges,
  secrets, package/install hooks and review date. Use the separate
  [dependency-update procedure](dependency-review.md).
- **Policy, release, visibility or security-sensitive changes:** confirm the
  intended authority and actual provider settings. A proposed document does not
  establish a confidential reporting channel, SLA or published release.

Write down the commands **actually run**, their outcome and environment. A
previous green run, static inspection, example transcript or model-generated
summary is not a fresh PASS for the current head. CI confirms only the checks
it executed, not the entire intended behavior.

## 3. Classify findings and decide what blocks *this* change

**Material finding:** the promised behavior fails, data/permissions are at
risk, the evidence is misleading, an important path is untested, or a required
provider gate is unmet. Request a fix or defer the merge; rerun affected checks
on the changed head.

**Non-blocking follow-up:** a new idea, unrelated edge case or cosmetic
improvement that does not invalidate the bounded change. Record it in a
separate issue if useful; do not indefinitely expand an acceptable PR.

**Unknown:** evidence was unavailable or a test could not run. State exactly
which question remains open, the affected scope and whether it is material.
Do not translate an unavailable test into either PASS or FAIL automatically.

Review comments should be specific: file/line, observed behavior, why it
matters and a possible correction. Distinguish a personal suggestion from a
repository requirement. The author's response should show the fix or explain
why the proposed trade-off is acceptable.

GitHub's review actions have distinct meanings: **Comment** records feedback;
**Approve** approves the change; **Request changes** signals that work remains.
A same-author or same-account comment is not independent approval. Review
requirements, dismissal of stale approvals, resolved conversations and required
checks depend on the repository's **actual** branch rules; do not invent extra
policy or bypass configured protection.

## 4. Check the merge decision against the current head

Immediately before an authorized merge, verify the **same head** you reviewed,
the relevant current checks, the actual ruleset/protection requirements,
material review findings and provider mergeability. If the head changed,
repeat the affected review. A clean status from a previous commit does not
authorize merging new bytes.

Where the provider supports an expected-head parameter, use it to reject a
stale merge attempt. If a required check is pending or failed, do not call the
PR merge-ready; if an optional review comment cannot be written, do not invent
a gate that the repository does not require.

After integration, confirm the PR really merged and the intended file or
behavior appears in the target branch. Do not claim that a merge establishes a
release or an external-user installation.

## Worked example: a source-input guard, not a security certification

[BeautifulRepo PR #408](https://github.com/drevendev/BeautifulRepo/pull/408)
changed the offline GitHub Actions pin checker. The proposed defect was that a
hard-linked workflow or pin manifest could be read from outside the checkout
while appearing to be a regular file.

A bounded reviewer can follow its
[exact patch](https://github.com/drevendev/BeautifulRepo/pull/408/files)
through `tools/action_pins.py` and `tests/test_action_pins.py`:

1. Inspect the source path's pre-open `lstat`, link-count check, opened file
   descriptor identity and rejection of non-ordinary files.
2. Check the new synthetic regressions: workflow and manifest hard-link aliases
   must exit **2** and leave the outside fixture bytes unchanged.
3. Read the [PR's actual checks](https://github.com/drevendev/BeautifulRepo/pull/408/checks)
   on the reviewed head; do not substitute a newer `master` result.
4. Record the limitation: the tool assumes a stable checkout. It is **not** a
   race-free filesystem sandbox and does not certify arbitrary hostile targets.

This is a **worked review method based on a merged public PR**, not an
independent penetration test or a new security guarantee. The change was
merged on **2026-11-18**; current CI and review state remain on GitHub.

## Primary sources and scope

Reviewed **2026-11-18**:

- [GitHub: reviewing proposed changes](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request)
  — line comments, suggestions, file review and review decisions.
- [GitHub: quickstart for reviewing PRs](https://docs.github.com/en/pull-requests/get-started/reviewing-pull-requests-quickstart)
  — Comment / Approve / Request changes.
- [GitHub: protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
  — repository-specific required approvals, checks and conversation resolution.
- [GitHub: troubleshooting required checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
  — stale heads and expected checks.

This guide is a reusable judgement workflow, not an automated reviewer,
comprehensive security audit, authorization to change repository rules, or a
claim that any project's CI covers every risk.
