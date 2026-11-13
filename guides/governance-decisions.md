# Decisions without a fictional committee

A newcomer should be able to tell **where to propose a change, who can
decide, what evidence matters and where the outcome will be recorded**.
A small open-source project does not need an elected board, a promised
response time or a voting process to explain these things.

This is a **copyable governance recipe**, not a new BeautifulRepo policy.
Our current public evidence is [CONTRIBUTING](../CONTRIBUTING.md) and
[actual decision records](../docs/decisions/README.md). Adapt the workflow
to roles and channels that really exist in your repository.

## Choose the right path

- **Small, reversible fix:** a bounded pull request (and an issue if the
  failure needs discussion); show before/after input and checks.
- **Feature or change to an existing guarantee:** gather opinions in an
  enabled discussion or issue; state alternatives and implications; only
  then scope an implementation PR.
- **Permissions, security, legal or release decision:** consult the real
  owner or authorized maintainer. A popular issue reaction cannot grant
  permissions or bypass protections. Send sensitive vulnerability and
  conduct details only through a **verified private route**, never into
  a public proposal. See [community safety](community-safety.md).

GitHub Discussions can host open-ended proposals **if an administrator has
enabled it**. If your repository does not have Discussions, use its
existing public issue route for ordinary questions; do not invent a new
forum, security inbox or governance board.

## Five-step decision loop

1. **Propose:** name the reader problem, evidence and one smallest useful
   outcome. Distinguish observed behavior from assumptions.
2. **Consult:** identify the actual decision maker and invite relevant
   feedback. Do not manufacture a review deadline or imply a vote.
3. **Decide:** record accepted, rejected or deferred, with reasoning and a
   measurable trigger for reconsideration. Unresolved is a valid status.
4. **Implement:** an accepted proposal becomes a scoped PR with relevant
   tests. Review and branch rules still apply.
5. **Link:** after the work really merges, connect the public decision,
   PR and verified result. Do not write `merged` before integration.

**Copyable decision card** — fill every bracketed field, do not publish
the example values as project facts:

```text
Proposal: [reader outcome]
Observed evidence: [revision, reproduction/output, or NOT RUN]
Options: [A / B / keep current behavior]
Decision owner: [real authorized person or role]
Status: proposed | accepted | rejected | deferred
Why: [trade-off, affected users, known unknowns]
Implementation: [actual PR URL, or NOT STARTED]
Revisit when: [observable event, not a fictitious date]
```

For a durable **accepted** architectural choice, adapt the
[short decision-record template](../docs/decisions/README.md#template).
Record `Landed in` only when the linked PR actually landed. A card is
not authority for spending, changing repository settings, or granting
access.

## Annotated real example: staying offline

BeautifulRepo [decision 0002](../docs/decisions/0002-offline-and-read-only.md)
describes why audit tools do not fetch live URLs or execute the repository
under inspection. The tools inspect untrusted source. Network access and
target-code execution introduce risks beyond a read-only document check.
The decision cites [PR #12](https://github.com/drevendev/BeautifulRepo/pull/12)
and later [PR #110](https://github.com/drevendev/BeautifulRepo/pull/110).

**Hypothetical follow-up:** “Scan every external URL automatically.”

- Observed boundary: today's offline tools do **not** check the live
  availability of external URLs. Do not label an unrun crawler as PASS.
- Real options: keep offline behavior; research a separately approved,
  opt-in network tool; or reject network inspection.
- Decision: **NOT MADE** for this imagined request. A real maintainer must
  weigh privacy, user expectation and failure modes before implementing it.
- Useful first artifact: a small issue containing the trade-off, a testable
  result and non-goals—not a hidden network call in an unrelated PR.

The example shows how an existing decision helps a new contributor understand
a constraint without making that choice permanent or unchallengeable.

## When to formalize more

Revisit your process when several people regularly merge changes, the same
dispute keeps blocking decisions, or the owner can no longer cover security
or maintenance. At that point define real roles, a route to responsibility,
conflict handling and a handoff path. Do not claim backup maintainers,
appeals or voting rights until those mechanisms exist. The
[maintainer-handoff guide](maintainer-handoff.md) covers practical gaps.

## Sources and boundaries

Reviewed **2026-11-13**:

- [Open Source Guides: Leadership and Governance](https://opensource.guide/leadership-and-governance/)
  describes governance structures, role distinctions and gradual formalization.
- [GitHub Docs: About discussions](https://docs.github.com/en/discussions/collaborating-with-your-community-using-discussions/about-discussions)
  documents optional discussions and administrator activation.

The decision loop and card are BeautifulRepo's suggested workflow, not a
provider rule, legal advice, moderation service or a claim that external
contributors can merge into this repository.
