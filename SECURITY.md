# Security policy

## Reporting a vulnerability

Use GitHub's private vulnerability reporting:
<https://github.com/drevendev/BeautifulRepo/security/advisories/new>.
Do not open a public issue, discussion or pull request for a security problem, and do
not post exploit details, secrets or personal data anywhere public.

A useful first report names the affected file or command, the version or commit, the
steps to reproduce, and what an attacker gains.

Reports are triaged by the maintainer, [@drevendev](https://github.com/drevendev), on a
best-effort basis. BeautifulRepo is maintained by one person, so no response time is
promised. Fixes are discussed in a private security advisory and disclosed once a fix is
available.

## What counts as a vulnerability here

BeautifulRepo's tools, its GitHub Action and its agent plugin read repositories that
other people wrote. They are designed so that a hostile target repository cannot:

1. **execute code.** `repo_audit.py`, `docs_links.py` and `html_navigation.py` only read
   files with the Python standard library. They never import, build or run the target,
   and they make no network requests.
2. **escape its root.** Markdown sources and link destinations that resolve outside the
   repository root, including through symlinks and NTFS junctions, are reported, not
   followed. Link targets are read as text and checked before they are followed, and a
   destination with a backslash or a drive letter is rejected unopened, so a path that
   names another drive, a UNC network share or a device is never opened. Fixed in
   v0.2.0 ([GHSA-9rpm-g83x-47w7](https://github.com/drevendev/BeautifulRepo/security/advisories/GHSA-9rpm-g83x-47w7)).
3. **inject shell commands through the Action.** `action.yml` passes every input to its
   scripts through environment variables, never through `${{ }}` inside a `run:` block,
   and rejects unknown check names.
4. **turn the agent skill against its user.** Skills treat target content as data and
   are read-only by default (see [agent ground rules](guides/agent-safety.md)). These are
   instructions to an agent, not a sandbox.

A way to break any of these promises is a vulnerability. So is `tools/catalog.py --write`
damaging a file it was not asked to write.

**Out of scope:**

- the example applications under `examples/`, which are teaching code (Pocket Board
  listens on loopback only and is not meant for production);
- the content and safety of third-party resources linked from the catalog or guides;
- resource exhaustion from deliberately enormous repositories. File reads are bounded
  in places but not everywhere, so reports that tighten this are still welcome as
  ordinary issues.

## Supported versions

BeautifulRepo is pre-1.0. Fixes land on `master` and in the next tagged release.
Pin a release by its commit SHA, as the [adoption guide](guides/adopting-the-checks.md)
recommends, and update the pin when a fix is released.
