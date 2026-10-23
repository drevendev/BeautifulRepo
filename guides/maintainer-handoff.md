# A maintainer handoff that another person can actually use

A project can have a perfect README and still stall when its only maintainer
becomes unavailable. A handoff is **not** a promise that someone has agreed to
maintain it. It is a public, testable map of what works, who may decide, and
what is still unknown. This recipe is for a small, volunteer-maintained GitHub
repository; it is not a substitute for organization access or incident response.

## The next 30 minutes: reproduce the public baseline

Use BeautifulRepo itself as the concrete, checked-in example. In a checkout of
[`drevendev/BeautifulRepo`](https://github.com/drevendev/BeautifulRepo), from the
repository root, with Python 3.11 or newer:

```bash
python -m unittest discover -s tests -v
python tools/catalog.py
python tools/docs_links.py
python tools/html_navigation.py
```

The tests, catalog drift checker, repository-owned Markdown destination checker,
and bounded HTML navigation checker should exit **0** on a healthy checkout.
A future maintainer must record the **actual** output, Python version, commit,
and date rather than paste a historical green badge into a handoff. The
application tests use a short-lived loopback HTTP listener; no external Python
packages or hosted service are required. Do not claim that these commands test
screen readers, external links, all browsers, security, or a release deployment.

Before editing: inspect [README](../README.md), [contribution rules](../CONTRIBUTING.md),
[roadmap](../ROADMAP.md), [public changelog](../CHANGELOG.md), and current
[issues](https://github.com/drevendev/BeautifulRepo/issues) and
[pull requests](https://github.com/drevendev/BeautifulRepo/pulls). These are
public entry points; do not assume an old issue snapshot is current authority.

## Handoff card: a fictional one-maintainer project

**Example, not a real transfer:** _Harbor Notes_ is a hypothetical local Python
CLI repository. Its sole maintainer is taking an indefinite break. This card
is deliberately filled in rather than supplying an empty checklist.

| Question | Recorded answer |
| --- | --- |
| Reader's first success | From checkout, run `python -m unittest discover -s tests -v`; claim success only after a local run. |
| Public explanation | `README.md` for scope and invocation; `CONTRIBUTING.md` for small PRs and issue triage. |
| Current queue | Open GitHub issues/PRs, rechecked at handoff; no saved list is authoritative. |
| Tests and CI recovery | Reproduce the checkout command locally, inspect the failed job and compare it with the PR's exact head before changing code. |
| Releases | **Paused**. No one else has accepted responsibility for tags, publishing, or rollback. Do not invent a release schedule. |
| Decision owner | Existing repository owner retains merge and release decisions until explicitly delegated. |
| Contributors | May propose patches and explain reproduction; cannot assume write/admin access. |
| Security or conduct reports | **Unverified private intake.** Do not ask for secrets in a public issue; the owner must verify a safe route before publishing one. |
| Project status | Unmaintained during the break, with no response-time guarantee. |

This table describes decisions a maintainer should make **for their own repo**;
it does not assert that Harbor Notes exists or that any account has consented
to maintain it. For BeautifulRepo, its own community limitations remain in
[community safety guidance](community-safety.md).

## Before and after: make the missing authority visible

**Before — insufficient:**

> I'm away. Please keep the project going and publish fixes when needed.

This leaves write access, review criteria, release ownership and security
handling unstated. A good README does not grant permissions.

**After — fictional public notice:**

> Harbor Notes is paused as of 2026-10-21. Existing issues and pull requests
> remain public, but no response or merge time is promised. Contributors may
> propose changes using CONTRIBUTING.md; the existing owner still decides
> merges and releases. No replacement maintainer or verified confidential
> reporting route has been appointed. Do not post private security details in
> public issues. Release publishing is paused until responsibility and access
> are explicitly confirmed.

The revised note does not appoint a successor, imply a service-level agreement,
or claim a confidential address exists. Once someone actually accepts the role,
replace the pause notice with the verified person's **public GitHub role** and
which actions they are authorized to perform. Do not publish personal email,
credentials, internal runbooks, private queues, secrets, or backup codes.

## Access and decision checklist

- [ ] **Contributor:** can propose an issue or PR; this alone grants no push,
  merge, secrets or repository settings permissions.
- [ ] **Maintainer with write access:** confirm *actual* repository permissions
  and required review/check rules; decide who may triage and integrate work.
- [ ] **Owner/admin:** verify separately who can manage collaborators, secrets,
  protection and repo transfer. Write access is not the same as admin rights.
- [ ] **Review route:** identify the current PR, exact head, meaningful findings,
  checks, release impact and acceptance decision. Never inherit a past PASS.
- [ ] **Release decision:** identify version policy, tested build and rollback
  owner before tagging or publishing; mark releases paused if absent.
- [ ] **Issue triage:** preserve reproducible bugs, clarify out-of-scope requests,
  and label expected decisions as such without silently promising delivery.
- [ ] **Sensitive reports:** confirm a reporter-facing private route and an
  intake owner *before* advertising it; otherwise disclose the limitation.
- [ ] **Continuity:** post a dated public status only after the owner approves it;
  revisit it when someone accepts responsibility or access changes.
- [ ] **Decisions:** hand over the project's decision records with the access, so the
  next maintainer knows which constraints are deliberate. BeautifulRepo keeps its own
  in [`docs/decisions/`](../docs/decisions/README.md).

Repository **transfer**, **archiving**, adding collaborators, changing security
settings or using credentials are separate owner-authorized administrative acts,
not steps in this documentation recipe. Transferring a repository can preserve
issues and PRs while affecting URLs, settings and some account-dependent features;
read GitHub's current transfer prerequisites before any authorized operation.
Do not exercise admin operations merely to make a sample look complete.

## What stays public, and what stays private

**Public:** source at a named revision; maintained build/test commands; issue/PR
triage conventions; release criteria and stated pause; roadmap; contribution and
code-review expectations. These help a stranger verify the project independently.

**Private:** login or recovery material, personal addresses, private incident
details, internal job controls, unverified contact channels, or credentials.
A public handoff document is not an invitation to mirror operational telemetry.

## Sources and limits

Reviewed **2026-10-21**:

- [Open Source Guides — Best Practices for Maintainers](https://opensource.guide/best-practices/): document process and expectations, share responsibilities, and communicate a pause honestly.
- [GitHub — Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors): recognized `CONTRIBUTING.md` locations and contributor discovery.
- [GitHub — Transferring a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository): admin prerequisites, effects and transfer limitations. This is background, not permission to transfer.

This example is an original **fictional handoff card**, not evidence that a
real team accepted access, that project operations will continue, or that a
vulnerability-reporting channel has been verified.
