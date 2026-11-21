# Check contribution rights before merging

A repository-wide license does not establish who owns every submitted file.
Use this evidence-led intake for PRs that introduce code, documentation,
artwork, datasets, AI-assisted output or copied material. This is an
operational checklist, **not legal advice**, legal clearance, a new agreement
or automated verification of ownership.

**BeautifulRepo's actual policy:** its existing MIT `LICENSE` remains
unchanged. This guide adds **no CLA, DCO sign-off requirement or CI gate**.
Use [CONTRIBUTING](../CONTRIBUTING.md) for the current contribution route
and [third-party asset guidance](third-party-assets.md) for images and fonts.

## Separate three questions

1. **Outbound rights:** inspect the real `LICENSE` and any per-file
   license/attribution notices. Public source is not automatically open
   source. The [Open Source Guides legal chapter](https://opensource.guide/legal/)
   explains why an explicit license matters.
2. **Inbound permission:** can the author submit *these exact bytes*
   under the repository's terms? GitHub's
   [Terms of Service, section D.6](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#6-contributions-under-repository-license)
   establish a default for contributions to licensed repositories; they do
   not grant the author rights to material obtained from a third party.
3. **Extra attestation:** has the project actually chosen a Developer
   Certificate of Origin (DCO), a Contributor License Agreement (CLA),
   or an employment confirmation requirement? Never presume one exists
   because another project uses it.

## Inspect the PR, not the claim

Read the exact changed files and original notices. For each added/copy-pasted
item, record its creator, origin and redistribution conditions. A generic
sentence such as "from an open source repo" is not sufficient.

- **Original work:** look for inconsistent copyright notices; ask the
  contributor to confirm their right to submit it on the project's terms.
- **Copied or adapted code, prose or images:** record the upstream URL,
  revision, creator and actual license or permission. Keep required notices,
  attribution and relevant modifications. A search result is not permission.
- **AI-assisted content:** ask which inputs and third-party materials were
  used and whether any reuse limits are known. Do not treat an output as
  automatically cleared, or demand private prompts or model transcripts.
- **Employer/client work:** seek non-confidential clarification of authority
  when relevant; do not publish employment agreements or private records.
- **Dependencies or vendored code:** use the separate
  [dependency review](dependency-review.md), including license notices
  and the real distribution boundary.

Never request sensitive identity documents, internal contract text or secrets
through a public issue or PR. When the rights cannot be established without
such disclosure, stop and use an authorized private/legal process rather than
inventing a reporting address.

## Make one actionable decision

Copy the [rights-intake card](../templates/CONTRIBUTION_RIGHTS.template.md).
State the files, supporting evidence, unknowns and **one** outcome:

- **ACCEPT:** the evidence supports using the submitted material on the
  indicated terms; technical acceptance and required CI still apply.
- **REQUEST EVIDENCE:** specify the missing license, origin, notice or
  authority that can reasonably be documented.
- **REPLACE / OMIT:** substitute original, cleared material or remove the
  contested part, keeping the rest of a useful PR.
- **ESCALATE:** an actual legal, conflicting-license, employer-ownership or
  contributor-agreement question needs separate authorized judgment.
  Never silently relicense other authors' contributions.

**Worked example — fictional, not an actual PR:** a contributor adds
`assets/trophy.svg` to a README, saying it was "found on Google."
The publicly visible image has no identified owner or redistribution grant.
Record **REQUEST EVIDENCE**, with the specific request for the source page
and rights or a self-created replacement. The destination's MIT license
does not retroactively license the copied SVG. When replaced, review the
remainder normally; do not claim a release or an accessibility test.

## DCO is not a CLA, signature or license

The [Linux Foundation DCO guidance](https://bestpractices.linuxfoundation.org/ip/contribution-mechanisms-dco.html)
describes a contributor's rights **certification**. A commit sign-off
(`git commit -s`) is not cryptographic signing (e.g. `git commit -S`),
and the DCO itself grants no license. A CLA may contain additional grants
or obligations, requires an appropriate decision process and adds
administrative work. [Open Source Guides](https://opensource.guide/legal/)
does not recommend a CLA as the default for most projects.

Do not activate a DCO bot, add a signing check, change the MIT license, or
require a CLA as a side effect of this guide. Those would need a separate
owner-authorized decision with actual contributor communication.

Keep actual PR discussions, checks and merge evidence on GitHub. A worksheet
is a review aid, not a competing status tracker. Mark unperformed checks
`NOT RUN` and distinguish uncertainty from a verified failure.

**Sources reviewed 2026-11-21:** [Open Source Guides — legal](https://opensource.guide/legal/),
[GitHub — repository licensing](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository),
[GitHub — Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service),
[Linux Foundation — DCO](https://bestpractices.linuxfoundation.org/ip/contribution-mechanisms-dco.html).
Recheck the original sources and applicable project terms for consequential decisions.
