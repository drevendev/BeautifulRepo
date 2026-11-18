# Review a dependency update before trusting the green check

An update pull request is a **proposal**, not proof that the new dependency
is compatible or safe. This bounded recipe works for packages, build tools and
GitHub Actions without adding bots, secrets, repository settings or release gates.

## 1. Identify the actual change

Read the manifest, lockfile, workflow and reusable-workflow diff. Record the
dependency's role (runtime, development, build, CI), its old and new **exact**
versions/commits, and whether it is direct or transitive. Identify changed
permissions, network access, install hooks, generated artifacts and publishing
steps. Unknown source or test evidence is **UNKNOWN**, not PASS.

From a trusted local checkout, inspect tracked changes without running the
new dependency:

```bash
git diff --name-status BASE_SHA...HEAD_SHA
git diff BASE_SHA...HEAD_SHA -- .github/workflows .github/dependabot.yml
git diff BASE_SHA...HEAD_SHA -- pyproject.toml package.json package-lock.json
```

Replace both revision placeholders with full SHAs, and omit irrelevant paths.
These commands do not inspect downloaded package bytes or upstream publisher identity.

## 2. Check upstream and privileges

Read the upstream release notes and source diff **between the two exact
revisions**. Look for breaking changes, new transitive dependencies, licence
changes, workflow `permissions:`, secrets, publishing and outbound transfers.
Capture source links and a review date; if upstream evidence is inaccessible,
defer the update rather than converting a green badge into an authenticity claim.

For GitHub Actions, examine the `uses:` references, triggers and token scope.
GitHub recommends workflow dependency lockfiles where available; otherwise
pin third-party Actions to full-length commit SHAs rather than movable tags.
A full SHA is an identity pin, **not** a source audit or a runtime sandbox.
Dependabot may propose Actions updates, but it does not approve their behavior.
GitHub also documents that Dependabot **alerts for Actions apply to semantic
version references, not SHA references**; no alerts is not proof of safety.

## 3. Verify relevant behavior

First reproduce the affected workflow or API behavior on disposable inputs.
Then review the repository's exact-HEAD required CI, including unsupported
platforms, log/permission changes and material reviewer findings. Distinguish
what actually ran from what was merely source-inspected. Don't expose tokens in
a review card, and don't manufacture additional merge gates.

### A real repository workflow to adapt

In BeautifulRepo's source at
[commit `89b72b4`](https://github.com/drevendev/BeautifulRepo/tree/89b72b4a6fa0c7d8227eb33a96a2214343fac3fa),
the [Dependabot configuration](../.github/dependabot.yml) schedules weekly
grouped GitHub Actions updates with an open-PR limit of three. It does **not**
configure Python package updates. The
[reviewed pin manifest](../.github/action-pins.json) is maintained alongside
workflow SHA annotations. From the BeautifulRepo root, run:

```bash
python -I tools/action_pins.py --root .
```

The [pin checker source](../tools/action_pins.py) checks local consistency;
[the maintenance guide](maintenance-workflow.md) requires human upstream
revision review. **This is source inspection dated 2026-11-18**, not a claim
that an upstream Action update was installed, tested or accepted here.

## 4. Record a clear decision

- **ACCEPT:** upstream changes and privileges understood, relevant tests
  actually passed, required provider gates satisfied on the exact head.
- **DEFER:** a source diff, platform check, permission explanation or maintainer
  capacity is missing. Name the evidence needed to revisit.
- **REJECT:** unacceptable behavior, licence/privilege cost or no project value.

**Illustrative example, not a real PR:** a bot proposes an upload Action SHA.
CI is green but nobody reviewed changed artifact permissions or the upstream
source diff. Decision: **DEFER** until both are inspected. This is more useful
than either automatic merging or a generic "looks good".

Copy the [editable decision card](../templates/DEPENDENCY_REVIEW.template.md)
into your own review notes. The card documents judgement; it does not establish
a repository policy, private vulnerability route or new approval requirement.

## Primary references and limits

Reviewed **2026-11-18**:

- [Dependabot version updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates)
  and [Actions updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions).
- [Dependabot alert limitations](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts).
- [Secure use of third-party Actions](https://docs.github.com/en/actions/reference/security/secure-use).
- [Supply-chain code review](https://docs.github.com/en/code-security/tutorials/implement-supply-chain-best-practices/securing-code).

This is not a complete dependency inventory, vulnerability scan or package
provenance verification. Platform and subscription support for provider security
features can differ; confirm them before treating an automated check as a gate.
