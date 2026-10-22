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
      - uses: drevendev/BeautifulRepo@96e04e6a79027354c5e84a4a28f3ba5f5441d484 # v0.1.0
        with:
          exclude: |
            vendor
```

The example pins [`v0.1.0`](https://github.com/drevendev/BeautifulRepo/releases/tag/v0.1.0)
by its full commit SHA, with the tag kept as a comment. Pin a SHA rather than a
branch or a tag: a tag can be moved and a branch changes under you, while the
tools that check your pull requests should change only when you update the pin.
Each [release](https://github.com/drevendev/BeautifulRepo/releases) names its
commit. To confirm where a tag points before you copy it:

```bash
git ls-remote https://github.com/drevendev/BeautifulRepo refs/tags/v0.1.0
```

Each check also runs on Ubuntu and Windows runners in BeautifulRepo's own CI.
macOS runners are not tested.

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `path` | `.` | Directory to check, relative to the workspace. |
| `checks` | `audit docs-links html-navigation` | Space-separated subset to run. An unknown name fails the step instead of being skipped silently. |
| `audit-fail-on` | `error` | `error`, `warning` or `never`. Findings are printed either way. |
| `exclude` | empty | One glob per line, relative to `path`, for Markdown sources the link checks skip, such as `vendor`, `third_party` or `docs/archive/*.md`. |

`.git` and `node_modules` directories are always skipped. Their Markdown belongs
to Git and to installed packages, not to your repository. An excluded file is
not scanned, but a link **to** it from a scanned file is still checked.

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

Reviewed **2026-10-22**:

- [GitHub Docs — Metadata syntax for GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax):
  composite actions, `$GITHUB_ACTION_PATH`, and step `shell`/`if`/`env`/`continue-on-error`.
- [GitHub Docs — Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use):
  pinning actions to a full-length commit SHA, mutable tags, and Dependabot
  behavior for SHA-pinned actions.
