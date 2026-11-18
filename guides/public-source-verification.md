# Verify that a source-only case is publicly reproducible

Before publishing an open-source case study, prove that a reader **without
your repository permissions** can open the **specific source revision** used
to support its claims. An owner-authenticated checkout, connector read or
successful CI run does not establish anonymous access.

This is a read-only, manually evaluated preflight, **not** a guarantee that
the source will remain available or that the application runs. No target
code needs to be executed. Reviewed **2026-11-18**.

## A concrete example: HungryCrab

The current [source-only case](../case-studies/hungrycrab-first-command.md)
uses public repository `drevendev/HungryCrab` and the immutable revision
`d20850c4e71382c796c4b4dac554137ebcb7e937`.

In a session with **no GitHub authentication**, no GitHub-authorizing proxy
and no credentials in curl configuration, run these read-only requests.
The `-q` first option prevents curl from loading a per-user `.curlrc`.
The commands deliberately do not set an Authorization header, use `gh`,
run source code or store downloaded response bodies.

```sh
# Repository metadata: public anonymous access at the observation time.
curl -q --fail --silent --show-error --location --max-redirs 3 \
  --proto '=https' --proto-redir '=https' --max-time 20 \
  -H 'Accept: application/vnd.github+json' \
  -o /dev/null -w 'repository: HTTP %{http_code}; final: %{url_effective}\n' \
  'https://api.github.com/repos/drevendev/HungryCrab'

# Pinned README: the exact file, not a moving branch.
curl -q --fail --silent --show-error --location --max-redirs 3 \
  --proto '=https' --proto-redir '=https' --max-time 20 \
  -H 'Accept: application/vnd.github+json' \
  -o /dev/null -w 'README: HTTP %{http_code}; final: %{url_effective}\n' \
  'https://api.github.com/repos/drevendev/HungryCrab/contents/README.md?ref=d20850c4e71382c796c4b4dac554137ebcb7e937'

# Repeat for each file essential to your case; this example checks metadata.
curl -q --fail --silent --show-error --location --max-redirs 3 \
  --proto '=https' --proto-redir '=https' --max-time 20 \
  -H 'Accept: application/vnd.github+json' \
  -o /dev/null -w 'pyproject: HTTP %{http_code}; final: %{url_effective}\n' \
  'https://api.github.com/repos/drevendev/HungryCrab/contents/pyproject.toml?ref=d20850c4e71382c796c4b4dac554137ebcb7e937'
```

These are **example commands, not recorded execution results**. Substitute
your own owner/repository, exact 40-character commit and source paths. Check
the returned *final URL* remains on GitHub's expected API host and points to
the intended repository. Inspect the actual pinned files in a signed-out
browser too; an HTTP 200 for the API endpoint alone is insufficient to
verify that your prose accurately describes the file.

## Decide and record

- **Public source verified for this observation:** unsigned, non-privileged
  requests and the signed-out file page both return readable content from
  the intended exact revision. Record the UTC date, HTTP status, final URL,
  full SHA, inspected paths and **how** you verified the session had no
  privileged credentials. A public repository's current metadata is not
  frozen by that SHA.
- **Unknown / defer:** a 401, 403, 404, 429, DNS failure, transport error,
  redirect to another host, blocked browser, unavailable clean session or
  uninspected file. A 404 does **not** prove a repository is private.
  A rate limit or network block is not a license to use private data.
- **Not a runtime test:** a source GET does not prove installability,
  rendered layout, accessibility, CI on that revision, or any client/agent
  invocation. Label these **NOT RUN**, and do not claim an upstream patch
  when no upstream PR exists.

**Privacy:** do not paste an access token, API key, cookie, `gh auth`
output or private source into the case. Test from an actually separate
signed-out environment; proxies, browser profiles, credential injectors and
enterprise gateways can silently add access. If you cannot isolate
authentication, write **anonymous access unverified** and defer public
source assertions. Don't publish a privileged screenshot as a workaround.

**Reuse:** even anonymous source availability is not redistribution
permission. Inspect the repository license and any separately licensed
images, fonts or datasets; link to source rather than copying assets.

Use the [source-only case template](../templates/SOURCE_ONLY_CASE.template.md)
and [complete-case procedure](../case-studies/README.md#the-procedure)
to distinguish this preflight from a measured before/after.

## Sources and scope

GitHub's [repository contents endpoint](https://docs.github.com/en/rest/repos/contents)
can be read without authentication for public resources. Its [REST rate-limit
documentation](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
describes unauthenticated limits and error cases; do not assume a fixed
remaining quota. GitHub's [permalink guidance](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files)
explains why a commit SHA is preferable to a moving branch. Consulted
**2026-11-18**. These official references support the method, **not a claim
that the example requests succeeded during this development run**.
