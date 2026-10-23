# Run BeautifulRepo's checks in your repository

BeautifulRepo's offline checks are published as a GitHub Action
([`action.yml`](../action.yml)). A repository can run them on every pull request
without copying the tools. The action runs the same scripts this repository uses
on itself:

| Check | Tool | Fails when |
| --- | --- | --- |
| `audit` | [`repo_audit.py`](repository-audit.md) | A README, license or contribution finding reaches `audit-fail-on` (default: errors only, such as a missing README). |
| `docs-links` | [`docs_links.py`](../tools/README.md#relative-documentation-link-checker) | A relative Markdown link or image in a repository-owned file points to a missing path or escapes the repository. |
| `html-navigation` | [`html_navigation.py`](../tools/README.md#html-navigation-and-fragment-checker) | A local HTML `href`/`src`/`srcset` or a `#section` fragment does not resolve. |

None of them fetches external URLs, executes your project, renders GitHub
Markdown completely or certifies accessibility. A green run means these bounded
source checks found nothing, not that the documentation is good.

## Add it to a workflow

The action needs Python 3.11 or newer on `PATH` and makes no network requests of
its own. With your branch name in place of `main`:

```yaml
name: Documentation checks
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  beautifulrepo:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: '3.12'
      - uses: drevendev/BeautifulRepo@4f06f26ccef6e8b28d77c71633482b7a1a68518a # v0.2.0
        with:
          exclude: |
            vendor
```

The example pins [`v0.2.0`](https://github.com/drevendev/BeautifulRepo/releases/tag/v0.2.0)
by its full commit SHA, with the tag kept as a comment. Pin a SHA rather than a
branch or a tag: a tag can be moved and a branch changes under you, while the
tools that check your pull requests should change only when you update the pin.
Each [release](https://github.com/drevendev/BeautifulRepo/releases) names its
commit. To confirm where a tag points before you copy it:

```bash
git ls-remote https://github.com/drevendev/BeautifulRepo refs/tags/v0.2.0
```

Each check also runs on Ubuntu and Windows runners in BeautifulRepo's own CI.
macOS runners are not tested.

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `path` | `.` | Directory to check, relative to the workspace. |
| `checks` | `audit docs-links html-navigation` | Subset to run, separated by spaces or one name per line. An unknown name, or an empty list, fails the step instead of being skipped silently. |
| `audit-fail-on` | `error` | `error`, `warning` or `never`. Findings are printed either way. Any other value fails the step, even when `audit` is not selected. |
| `audit-profile` | `public` | Explicit `public`, `internal` or `private`. Alters missing-license guidance and owner/contact observations; invalid values fail even when audit is not selected. This input is **Unreleased**, not supported by the v0.2.0 pin above. |
| `exclude` | empty | One glob per line, relative to `path`, for Markdown sources the link checks skip, such as `vendor`, `third_party` or `docs/archive/*.md`. |

`.git` and `node_modules` directories are always skipped. Their Markdown belongs
to Git and to installed packages, not to your repository. An excluded file is
not scanned, but a link **to** it from a scanned file is still checked.

## Private and enterprise repositories

These source checks can inspect a private checkout without uploading its files.
The **Python check scripts** read local paths; they do not fetch external URLs
or call a model provider. The Actions runner, checkout step, action retrieval,
and any interpreter installation are separate infrastructure that **can**
require network access. Review those dependencies and any uploaded workflow
logs before calling a workflow air-gapped or confidential.

### Policy and cost on GitHub.com

- Ask an organization or enterprise owner to permit the public action if
  external actions are restricted. A narrow allow-list entry for this release
  is `drevendev/BeautifulRepo@4f06f26ccef6e8b28d77c71633482b7a1a68518a`.
  This is compatible with **Require actions to be pinned to a full-length
  commit SHA**. The workflow's checkout/setup-python actions also require
  permission and full SHAs when that policy is enabled.
- For private repositories, check the account's Actions billing and included
  minutes. The example above uses an Ubuntu runner and
  `timeout-minutes: 5` to bound each job's duration; it does not
  promise a free run or a five-minute total queue time. Windows and macOS
  hosted runners typically cost more than Linux. No paid runner is required by
  these Python scripts.
- Use minimum `contents: read` permissions. Avoid uploading private
  audit JSON, source snapshots or runner logs to public issues.

### Internal mirror or restricted runner

An organization can mirror this action while keeping the original Git commit
history. For the v0.2.0 commit, the following reference works **only if that
same commit object exists in the mirror**:

```yaml
- uses: YOUR-ORG/BeautifulRepo-mirror@4f06f26ccef6e8b28d77c71633482b7a1a68518a
```

Check the commit in **both** fetched checkouts before updating the workflow:

```bash
git -C BeautifulRepo rev-parse 4f06f26ccef6e8b28d77c71633482b7a1a68518a^{commit}
git -C BeautifulRepo-mirror rev-parse 4f06f26ccef6e8b28d77c71633482b7a1a68518a^{commit}
```

Both must print the same full SHA. A source-file copy or a new history is
**not** a byte-identical mirror and cannot honestly use that pin. Ensure the
commit is reachable to your runner under the mirror's access rules. Mirror
updates must be deliberate, reviewed changes, not silent tracking of master.

A self-hosted runner requires **Bash and Python 3.11+ on PATH** for this
composite action; the runner must also reach its configured GitHub Actions
service. The action does not install Python for you. Treat self-hosted
runners handling untrusted pull requests as a separate security risk.

### Enterprise Server and GHE.com (not tested)

- **GitHub Enterprise Server:** public GitHub.com actions are not directly
  available by default. Administrators can enable GitHub Connect with the
  requisite outbound access or use `actions-sync` to copy selected
  public actions, then follow the local instance's action policy. Server
  workflows use self-hosted runners. Check the installed GHES version and
  the administrator's policy; **BeautifulRepo has not been run on GHES**.
- **GitHub Enterprise Cloud with data residency (GHE.com):** GitHub Marketplace
  browsing/installation is unavailable, although actions may still be
  installed from source. Some GitHub.com-targeting actions do not work, and
  external-action namespace retirement can affect mirror names. Verify
  resolution, permissions and matching commits before adopting an action.
  **BeautifulRepo has not been run on GHE.com**.

### Without GitHub Actions

From a reviewed BeautifulRepo checkout with Python 3.11+, run all three
checks against a local target. No Action, Marketplace or hosted runner is
needed:

```bash
python -I tools/repo_audit.py ../private-repo --profile private
python -I tools/docs_links.py --root ../private-repo
python -I tools/html_navigation.py --root ../private-repo
```

The `--profile private` option is available in the **Unreleased** source after
issue #75; the pinned v0.2.0 Action example above predates the option. Do not
pass `audit-profile` to that pinned Action until you move deliberately to a
reviewed commit or a future release that includes it. Neither the option nor
the static checks inspect organization settings or discover visibility.

The repository's `tests/test_offline_contract.py` guards against direct
network/process-library imports in `tools/*.py` and direct
`curl`, `wget` or `gh` mentions inside the Action's shell
blocks. This is deliberately **static**: it is not a sandbox, firewall,
dependency audit or proof about dynamic imports, caller workflows or the
runner's network. Do not execute an untrusted repository's code as part of
this check.

## Roll it out without a red wall

1. **Run it locally first.** From a BeautifulRepo checkout:

   ```bash
   python tools/repo_audit.py ../your-repository
   python tools/docs_links.py --root ../your-repository --exclude vendor
   python tools/html_navigation.py --root ../your-repository --exclude vendor
   ```

2. **Decide what is repository-owned.** Exclude vendored, generated or archived
   documentation that you will not maintain. Fix the rest.
3. **Add the workflow** and let it pass on a pull request.
4. **Make it required.** Add the job's check name (`beautifulrepo` in the
   example) to the default branch's ruleset or branch protection, so a broken
   link cannot be merged.

A trial on seven unpublished local repositories (2026-10-22) shaped the defaults.
In two of them almost every link finding came from installed `node_modules`
packages, which is why those directories are now always skipped. Two other
findings were real: a missing screenshot, and a link written as
`github.com/...` without `https://`. Without a scheme, Markdown treats such a
link as a relative path, so the checker reports it as missing.

## Keep the pin current

Update the SHA deliberately, and read the release notes and the
[changelog](../CHANGELOG.md) when you do. Dependabot's `github-actions` version updates can propose new commits for
SHA-pinned actions. It does **not** raise vulnerability alerts for SHA-pinned
actions.

## Sources

Reviewed **2026-10-23**:

- [GitHub Docs — Metadata syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax):
  composite actions, `$GITHUB_ACTION_PATH`, and step `shell`/`if`/`env`/`continue-on-error`.
- [GitHub Docs — Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use):
  pinning actions to a full-length commit SHA, mutable tags, and Dependabot
  behavior for SHA-pinned actions.

- [GitHub Docs — Disabling or limiting actions for your organization](https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization):
  allow-list entries and full-length SHA requirements.
- [GitHub Docs — GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions):
  included minutes and operating-system cost differences.
- [GitHub Docs — Self-hosted runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners):
  runner connectivity and security requirements.
- [GitHub Enterprise Server — GitHub Connect](https://docs.github.com/en/enterprise-server@3.20/admin/managing-github-actions-for-your-enterprise/managing-access-to-actions-from-githubcom/enabling-automatic-access-to-githubcom-actions-using-github-connect):
  public action access and outbound connectivity.
- [GitHub Enterprise Server — actions-sync](https://docs.github.com/en/enterprise-server@3.21/admin/managing-github-actions-for-your-enterprise/managing-access-to-actions-from-githubcom/manually-syncing-actions-from-githubcom):
  syncing selected public actions.
- [GitHub Enterprise Cloud with data residency — feature overview](https://docs.github.com/en/enterprise-cloud@latest/admin/data-residency/feature-overview-for-github-enterprise-cloud-with-data-residency):
  Marketplace limits and namespace retirement.
