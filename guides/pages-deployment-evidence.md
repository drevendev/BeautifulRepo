# Verify what GitHub Pages actually published

A green build, a successful deployment, and a useful **public webpage** are
three different observations. A project can have passing tests while its Pages
site still serves an older commit, broken assets or an inaccessible first-run
link. This is a read-only evidence recipe for maintainers of a site that
already exists, not instructions to enable Pages or change repository settings.

Use the [editable deployment record](../templates/PAGES_DEPLOYMENT_RECORD.template.md)
to keep observations tied to a commit and a time. A repository without Pages
does not fail this checklist; mark it **NOT APPLICABLE**.

## Decide what you are verifying

Record these separately, rather than collapsing them into "deployed":

1. **Source:** exact repository and full commit SHA intended for publication.
2. **Build:** the workflow run, job and artifact (or branch publishing path)
   actually associated with that source.
3. **Deployment:** the GitHub Pages environment/deployment and its observed
   latest status. A build job alone is not a deployment.
4. **Serving:** the actual site URL, HTTP response and visible expected
   content observed at a specific time. A successful deployment record does
   not prove that links, assets or browser interaction work.
5. **Reader success:** one first task and a failed-route test on the rendered
   site. Reading raw Markdown in GitHub is not a substitute for visiting Pages.

GitHub supports publishing from a selected branch or through Actions. For an
Actions-published site, a workflow typically builds, uploads a Pages artifact
and deploys it to the `github-pages` environment. Do **not** infer which
mode a repository uses from the presence of a workflow file alone.

## Read the provider evidence (no settings changes)

Replace `OWNER`, `REPO`, `RUN_ID` and the target SHA below with observed
values. The CLI commands require a working GitHub CLI session and sufficient
read permission; public resources may also be readable without authentication.

```sh
# Record the exact source revision separately from moving branch names.
git -C /path/to/checkout rev-parse HEAD

# Find the publishing workflow and inspect its *specific* run/job steps.
gh run list --repo OWNER/REPO --limit 10
gh run view RUN_ID --repo OWNER/REPO --verbose

# Inspect the currently reported Pages configuration, when accessible.
gh api repos/OWNER/REPO/pages
```

In the workflow run, distinguish *build complete* from *deploy complete*.
Record the run URL, triggering event, head SHA and conclusion; read the
deployment job and identify the published URL rather than copying a guessed
username.github.io address. For an Actions workflow, check that the artifact
used by the deployment came from the intended build and source. A pull-request
build may pass without deploying anything.

A repository may expose deployment entries and status evidence separately:

```sh
gh api 'repos/OWNER/REPO/deployments?environment=github-pages'
# For an observed numeric deployment ID:
gh api repos/OWNER/REPO/deployments/DEPLOYMENT_ID/statuses
```

These are **read-only** requests. Check which commit, environment and latest
status belong to the actual publication. No matching entry, HTTP 404 or an API
permission error is **INCONCLUSIVE**, not proof that deployment failed.
The Pages-specific deployment-status endpoint is also available where the
deployment identifier or SHA is known; it is not a substitute for inspecting
the served site.

GitHub deployment statuses are time-varying; older status records have
retention limits. Save dated evidence, not a permanent claim that today's
provider response will remain available.

## Verify the site as a reader

Visit the URL reported by the Pages settings or deployment (not a URL inferred
from a repository's name), at both the root and the actual entry page. Capture:

- The requested URL, final URL after redirects, observation time and HTTP
  response. A redirect by itself is not a successful rendered page.
- One distinctive, **version-specific** visible content marker, then a link
  from the landing page to a meaningful task and back.
- One deep link and its relevant images/styles. If an asset path fails,
  record the exact URL and status instead of marking the site PASS.
- At least one narrower viewport and a keyboard-only navigation attempt.
  Distinguish self-observation from independently tested accessibility.

For an optional, repeatable *HTTP-only* probe on a public site:

```sh
curl --location --fail --show-error --silent \
  --output observed-page.html \
  'https://OWNER.github.io/REPO/'
```

Only run that command for the site's **confirmed** public URL, in an
authorized working directory. Review the saved HTML before sharing it.
Exit 0 means this HTTP fetch succeeded, **not** that the build SHA was served,
JavaScript ran, assets loaded, the page was accessible or the site is current.
A single `curl` response does not capture browser state or prove a site is
publicly reachable to everyone. Custom domains and enterprise Pages have
different URL shapes.

A full URL may serve a cached older revision after a deployment. If you
cannot bind the visible content to a specific source revision, record
**INCONCLUSIVE (served revision)** rather than attributing it to the latest
`master` commit.

## Worked example: fictional site, not a recorded deployment

Suppose a sample repository `acorn-docs` has a green build for commit
`1111111111111111111111111111111111111111`, a deploy job with status
`success`, but its rendered quickstart link returns 404. The build is
**PASS**, the provider's deployment record is **PASS as observed**, and the
reader's first route is **FAIL**. The overall publication must **not** be
called verified. A small fix would repair the deployed relative link, repeat
the first-task walkthrough and record new evidence at the new source commit.

This is a hypothetical decision example, not an actual GitHub Pages test.

## Acceptance and limitations

Mark a specific criterion **PASS**, **FAIL**, **INCONCLUSIVE**, **NOT RUN**
or **NOT APPLICABLE**. Require an exact SHA, dated URLs and observed outcomes
for any PASS. If the site is private, avoid putting served content, logs,
credentials or user data into a public issue.

This recipe deliberately does **not** install a site generator, modify
Settings → Pages, grant `pages: write`/`id-token: write`, create an
environment, publish a website, or certify accessibility, security, uptime,
cache freshness or DNS configuration. Those require separate authority
and tests. See [CI failure triage](ci-failure-triage.md) for failed workflow
jobs and [documentation navigation](documentation-navigation.md) for the
reader's first-task route.

## Primary sources

Reviewed **2026-11-23** (GitHub.com documentation; recheck before adopting):

- [Configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
  — branch vs Actions and the distinction between builds and deployments.
- [Custom GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
  — build artifact, deploy job, permissions and environment.
- [Workflow run history](https://docs.github.com/en/actions/how-tos/monitor-workflows/view-workflow-run-history)
  — exact run and job inspection.
- [Pages REST endpoints](https://docs.github.com/en/rest/pages/pages)
  — site information and Pages deployment status.
- [Deployment status REST endpoints](https://docs.github.com/en/rest/deployments/statuses)
  — latest status and history/retention boundaries.
