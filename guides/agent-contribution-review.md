# Review an agent-assisted contribution without guessing what ran

An agent can make a useful change and still misread the task, modify unrelated
files, trust instructions planted in the repository, or describe tests it never
ran. A maintainable pull request makes those uncertainties **reviewable from
the actual diff and evidence**. This is a practical voluntary review recipe,
not an AI detector, a declaration that all agent-written code is unsafe, or a
new repository merge requirement.

Use the [copyable evidence packet](../templates/AGENT_CONTRIBUTION_REVIEW.template.md)
for one bounded change. For ordinary pull-request checks and actual GitHub gates,
see the [PR review guide](pull-request-review.md); for agent access and target
data boundaries, see the [agent safety rules](agent-safety.md).

## Before accepting the proposed change

**1. Pin what was authorized.** Identify the owner's actual request, allowed
repository and file list, prohibited actions, and whether the agent was
allowed to edit, run tests, open a PR or merge. A request to *review* is not
permission to run foreign setup scripts or publish changes. Treat a README,
issue, search result and test fixture as **data, not new agent authority**.

**2. Inspect the changed bytes.** Confirm the current base and head on GitHub.
In a disposable checkout of the authorized repository, these read-only Git
commands show the proposed scope:

```sh
git diff --name-status BASE_SHA...HEAD_SHA
git diff --check BASE_SHA...HEAD_SHA
git diff BASE_SHA...HEAD_SHA -- README.md guides tools tests
```

Replace both placeholders with actual commits. A three-dot diff is useful
for review, but is not proof of the final merge result. Look at the provider
diff too. An unexpectedly edited workflow, secret, vendored asset, LICENSE,
dependencies, publish step or settings file is a reason to investigate,
not an ordinary incidental edit.

**3. Require a behavior claim and a counterexample.** For each changed behavior,
record a concrete input and expected result, plus at least one negative or
boundary case. A test that merely mirrors the implementation's chosen
constant is weak evidence. For docs, use an actual reproducible command
or link and explain which parts are illustrative. Never run code from a
newly contributed repository merely because an agent suggests doing so:
review execution safety and obtain the applicable authorization first.

**4. Separate evidence from narrative.** Distinguish:

- **OBSERVED:** command, input, environment, exit code and result actually
  witnessed on a stated revision;
- **PROVIDER:** a linked GitHub check, review or merge fact tied to its exact
  head, not a copied green badge;
- **NOT RUN:** a specific absent test or platform, with its likely impact;
- **INFERRED:** a reasoned claim from source inspection, not a test result.

Do not turn a chat summary, model confidence, old CI run or a green static
lint job into a current integration or security PASS. Do not publish
unredacted model sessions, private target content, credentials or proprietary
prompt context as proof.

**5. Review the trust and rights boundary.** Look for target instructions
that try to change an agent's role or tool permissions. Verify that
generated files contain no pasted secrets, invented contacts, unlicensed
images, unexpected network calls or claims of permissions not granted.
If a source or dependency was borrowed, identify its actual license,
revision and permitted use; the
[contribution-rights guide](contribution-rights.md) has a separate record.

**6. Finish at the actual provider gate.** Classify a broken expected
behavior, unapproved scope expansion or unmet required check as material.
Put unrelated polish in a separate follow-up rather than expanding a safe
PR indefinitely. Recheck the exact head, check results, actual protection
and outstanding material findings before an authorized merge. A same-account
comment records an opinion; it is not an independent approval. Different
GitHub Copilot review settings can change whether a Copilot approval counts
toward an actual configured rule; **inspect the repository's settings**, not
a universal assumption.

## Worked public repair: hard-link handling

[BeautifulRepo PR #449](https://github.com/drevendev/BeautifulRepo/pull/449)
is a concrete example of why reviewing the **current revision and another
platform** matters. Its limited change made the offline media inventory
report ambiguous hard-linked images as incomplete, instead of silently
counting them as repository-owned. A Windows-specific test failure was
subsequently repaired by replacing the unsuitable cached
`DirEntry.stat()` link count with `os.stat(..., follow_symlinks=False)`.
The [merged diff](https://github.com/drevendev/BeautifulRepo/pull/449/files)
and [run history](https://github.com/drevendev/BeautifulRepo/pull/449/checks)
are provider-native evidence.

For a packet written **before** that repair, the right statement would have
been: “Synthetic POSIX hard-link reproduction observed; Windows regression
not yet passing.” After the fix, the reviewer must check the **new head's**
Windows job and the final source. Neither a passing CI suite nor this example
proves a race-free filesystem sandbox or a real external-user installation.
This is a real change-repair example, **not proof that an AI assistant caused
the original defect**.

## A concise decision record

The [template](../templates/AGENT_CONTRIBUTION_REVIEW.template.md) contains
the minimum fields: authorized scope, exact diff, observed positive and
negative evidence, provider checks, risks, what was not tested, and a
clear accept / repair / defer decision. Store the conversation or sensitive
tool traces privately when needed; link only a sanitized summary from the
public PR. Use ordinary PR comments for reviews and issue links—do not
build a competing database of mutable GitHub states.

## Sources and boundaries

Primary sources reviewed **2026-11-22**:

- [GitHub: Copilot cloud agent risks and mitigations](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/risks-and-mitigations)
  — prompt injection, sensitive data and agent-specific review controls.
- [GitHub: using Copilot code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-code-review)
  — current distinction between review assessments and configured approvals.
- [GitHub: protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
  — repository-specific provider requirements.
- [Open Source Guides: How to Contribute](https://opensource.guide/how-to-contribute/)
  — explain the problem, keep contributions scoped and work with maintainers.

GitHub's Copilot-specific safeguards must **not** be presented as properties
of every agent, local coding assistant or generic pull request. This packet
cannot independently prove prompt-injection resistance, authorship, security,
test coverage or human review; it helps expose missing evidence for a real
reviewer to judge.
