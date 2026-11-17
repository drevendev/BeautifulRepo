# Set a maintenance budget before promising support

A repository can be useful without being staffed like a product support desk.
The practical question is not “How many issues are open?” but **which
contributor expectations can this maintainer actually meet?** This recipe
helps a small or volunteer-run project publish an accurate, revisable
maintenance boundary. It is not BeautifulRepo's current support policy.

## 1. Inventory what readers can already reach

Open the repository's actual [README](../README.md),
[contribution guide](../CONTRIBUTING.md), issue forms, Discussions (if enabled),
[security policy](../SECURITY.md), release notes and open pull requests. For
your own project, note which routes work **today**, who is authorized to
answer, and whether any response interval has really been accepted.

Keep three kinds of request separate:

- **Reproducible defect:** version, steps, expected and observed output; run
  the smallest test before deciding on a fix.
- **Question or enhancement:** existing documentation or discussion route,
  with no implied entitlement to an implementation.
- **Security or private conduct report:** only an independently verified
  confidential intake route. Do **not** send sensitive details to a public
  issue or invent a private address to fill the gap.

GitHub supports a `SUPPORT.md` file in the repository root, `.github`, or
`docs`; its link is exposed on the issue creation page. A SUPPORT file
describes an **existing** route; it does not create a staffed support service.
See [GitHub's support resource documentation](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-support-resources-to-your-project).

## 2. Choose capacity, not an aspirational SLA

Use the [maintenance capacity card](../templates/MAINTAINER_CAPACITY.template.md)
to record a **realistic upper bound** for routine work and the category of work
you will prioritize. “Best effort; no guaranteed response time” is a valid
answer. Never publish a numerical response target merely because a template
has a field for it.

Keep a small reserve for regressions in your own tools and for documenting
decisions; do not allocate all available time to new requests. A security
incident needs a separately verified escalation and owner, not an imaginary
budget slot. If no authorized person can manage confidential reports, state
the limitation without inviting public disclosure.

## 3. Make trade-offs visible using one issue

Choose **one real, current** issue or PR. Record its link and do only what the
available evidence supports:

1. **Accept:** reproduce it, state the smallest valuable repair, then open a
   scoped PR with appropriate tests.
2. **Need evidence:** name the missing reproduction or environment fact and
   leave the result unverified.
3. **Decline:** explain the scope or maintenance cost and close when
   appropriate. A respectful “not planned” is better than a fictitious backlog
   commitment.
4. **Defer:** name a concrete revisit condition, such as a maintainer
   volunteering or a dependency changing; do not imply that it is scheduled.

Record the disposition on the **original GitHub issue**. Do not invent a
separate status spreadsheet. The [issue triage recipe](issue-triage.md) has
a copyable evidence card; the [governance guide](governance-decisions.md)
covers decision authority.

## Worked example — explicitly fictional

*Harbor Notes* is a hypothetical checkout-only CLI maintained by one volunteer.
The maintainer estimates **two hours per month**, not a response guarantee.
One month of work might look like this:

| Work | Illustrative allocation | Observable output |
| --- | ---: | --- |
| Verify one reported regression | 30 minutes | Exact input and observed failure, or “not reproduced” |
| Repair and test one bounded problem | 45 minutes | PR with before/after evidence |
| Review community changes | 30 minutes | A decision on an actual PR, not automatic acceptance |
| Update first-run instructions | 15 minutes | Tested command and dated limitations |

**These are example allocations, not measured workload or BeautifulRepo
commitments.** If the month contains no reproducible bug, the hours need not
be spent. If a security incident occurs or a maintainer becomes unavailable,
this plan is insufficient: the owner must make a fresh decision.

**Before — overpromising:** “We answer all issues in 48 hours and ship fixes
every Friday.” There is no staff, measurement or agreed release schedule
behind this claim.

**After — realistic, fictional public note:**

> Harbor Notes is maintained by one volunteer when time permits. Ordinary
> reproducible defects and small documentation PRs take priority. Please use
> the existing issue form for public, non-sensitive reports; response and
> release times are not guaranteed. The current maintainer alone decides
> what merges. A verified private security-report route has not been
> established; do not post sensitive details in a public issue.

Before adapting that paragraph, confirm your project's **real** issue route
and security intake. The example's security limitation is hypothetical,
not a claim about BeautifulRepo or any other existing project.

## 4. Revisit or pause without misleading users

Recheck the card when a maintainer's actual availability changes, a second
person explicitly accepts responsibility, or a sustained backlog changes
which requests can be handled. Date the public note **when updated**; do not
quietly extend an old review date.

If the project cannot be actively maintained, the
[handoff](maintainer-handoff.md) and
[pause/archive](repository-retirement.md) recipes distinguish a temporary
pause from GitHub's actual read-only archived state. Neither a card nor a
contribution automatically grants merge, release, admin or security authority.

## Primary sources and limits

Reviewed **2026-11-17**:

- [Open Source Guides — Best Practices for Maintainers](https://opensource.guide/best-practices/):
  document the project's real capacity, acceptance criteria and limits;
  respond constructively when declining work.
- [Open Source Guides — Leadership and Governance](https://opensource.guide/leadership-and-governance/):
  formalize responsibility as the project grows, without assuming that every
  contributor holds the same decision rights.
- [GitHub Docs — Adding support resources](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-support-resources-to-your-project):
  location and discovery behavior of `SUPPORT.md`.

The time-budget example and decision card are original BeautifulRepo
recommendations, **not** GitHub rules, a service-level agreement, legal
guidance, incident-response plan or evidence that any named project has
accepted a support obligation.
