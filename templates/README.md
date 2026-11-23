# Choose a repository template by task

Start with the **reader's next action**, not a file name. These are editable
drafts, **not evidence** that your project has working setup, active maintainers,
security reporting, redistribution rights or a published release. Keep only
sections whose claims you can verify.

## Help someone use the project

- **General repository:** [general repository template](README.template.md) — promise, first result, proof and next steps.
- **Private/internal project:** [private/internal project template](INTERNAL_README.template.md) — access, data handling, ownership and support without presuming an open-source licence. See the [filled fictional example](../examples/internal-repository/README.md) and [private-repository adaptation guide](../guides/adopting-the-checks.md#private-and-enterprise-repositories).
- **Reusable library:** [reusable library template](LIBRARY_README.template.md) — tested installation, import and API.
- **Application or service:** [application or service template](APPLICATION_README.template.md) — a visible first run and data boundaries.
- **Game:** [game template](GAME_README.template.md) — play and build routes with separate asset rights; see the [runnable terminal example](../examples/game-starter/README.md).
- **Research or dataset:** [research or dataset template](RESEARCH_DATA_README.template.md) — source provenance and reproduction.
- **Curated references:** [curated references template](CURATED_README.template.md) — selection rules and stale-entry retirement.
- **Multi-page documentation:** [multi-page documentation template](DOCS_INDEX.template.md) — task-first first-run, how-to, reference and help routes; see the [navigation guide](../guides/documentation-navigation.md).

## Explain the presentation and permissions

- **Visual direction:** [visual direction template](DESIGN_INTENT.template.md) — audience, evidence and alternatives. See the [filled Rowcount case](../examples/readme-visuals/rowcount/DESIGN_INTENT.md).
- **Demo media:** [demo media template](DEMO_MEDIA.template.md) — poster, captions, text alternatives and untested playback.
- **Third-party assets:** [third-party assets template](ASSET_PROVENANCE.template.md) — author, licence, permitted use and rights evidence.

## Make maintenance decisions traceable

- **Release notes:** [release notes template](RELEASE_NOTES.template.md) — verified changes; a draft is not a published GitHub Release.
- **Rename or transfer:** [rename or transfer template](REPOSITORY_MOVE.template.md) — redirects, Actions, packages and first-run verification.
- **Pause or retire:** [pause or retire template](REPOSITORY_STATUS_NOTICE.template.md) — maintenance expectations without an invented response SLA.
- **CI investigation:** [ci investigation template](CI_FAILURE_RECORD.template.md) — observed job, attempted repair and retry decision.
- **Dependency update:** [dependency update template](DEPENDENCY_REVIEW.template.md) — privilege, compatibility, tests and accept/defer/reject.
- **Pull request review:** [pull request review template](PULL_REQUEST_REVIEW.template.md) — exact changes and findings, distinct from real GitHub merge gates.
- **Agent-assisted changes:** [agent-assisted changes template](AGENT_CONTRIBUTION_REVIEW.template.md) — authorised scope, tool actions and untested behavior.

## Invite contributions responsibly

- **First contribution:** [first contribution template](GOOD_FIRST_ISSUE.template.md) — reproducible problem and achievable acceptance.
- **Contribution rights:** [contribution rights template](CONTRIBUTION_RIGHTS.template.md) — licence checks and copied-material provenance.
- **Maintainer capacity:** [maintainer capacity template](MAINTAINER_CAPACITY.template.md) — non-binding availability and handoff.
- **Mentoring proposal:** [mentoring proposal template](GSOC_PROJECT_IDEA.template.md) — deliverable, real mentor capacity and current organizer rules; not an application. See the [dated programs guide](../guides/programs.md) and recheck organizer rules before publishing an ideas page.
- **File owners:** [file owners template](CODEOWNERS.template) — verified GitHub users and permissions; copying it does not enable required review.
- **Security policy:** [security policy template](SECURITY.template.md) — publish only after confirming an actual confidential reporting route.
- **Public-source case:** [public-source case template](SOURCE_ONLY_CASE.template.md) — pinned observations and an editorial proposal, not a completed upstream change.

## Adapt, then verify

1. Choose **one primary template** for the current task. Do not copy everything.
2. Replace placeholders and delete unsupported claims. Check commands, outputs,
   licence obligations, help routes, responsible owners and asset permissions.
3. Check relative links from the destination directory and rerun first-run
   commands in a clean checkout. Record what was **not tested**.
4. Inspect rendered task navigation and accessibility. A passing link check
   cannot prove a reader will find or understand a page.

For runnable starting points, see the [working examples](../examples/README.md).
For review criteria, use the [first-success checklist](../checklists/first-success.md).
