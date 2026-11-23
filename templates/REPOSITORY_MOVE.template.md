# Repository relocation verification (editable)

> Planning and evidence only. **Not permission to rename or transfer a
> repository.** Replace placeholders and do not include confidential contacts,
> private configuration or secrets. Follow the
> [relocation recipe](../guides/repository-relocation.md).

## Identity and decision

- Change: [same-owner rename / ownership transfer / other]
- Old: [OLD-OWNER/OLD-REPO]
- Proposed new: [NEW-OWNER/NEW-REPO]
- Authorized decision-maker / evidence: [real reference, or UNCONFIRMED]
- Source branch and full pre-move SHA: [branch / SHA]
- Date and exact GitHub guidance reviewed: [YYYY-MM-DD / URLs]
- Move completed? [NO / YES on YYYY-MM-DD / UNKNOWN]
- Last observed clean-clone first success: [OS, revision, command, output / NOT RUN]

## Consumer inventory

| Surface | Old coordinate / discovery scope | Owner | Status |
| --- | --- | --- | --- |
| README, badges and local links | [tracked paths] | [role] | [NOT RUN] |
| Git remotes and installation instructions | [URL] | [role] | [NOT RUN] |
| Downstream GitHub Action `uses:` | [reference / UNKNOWN] | [role] | [NOT RUN] |
| Pages / custom website | [URL / NOT APPLICABLE] | [role] | [NOT RUN] |
| Packages, release artifacts and images | [coordinates / UNKNOWN] | [role] | [NOT RUN] |
| Security and contribution routes | [actual paths, no secrets] | [role] | [NOT RUN] |
| External consumers beyond our control | [known list / UNKNOWN] | [role] | [UNKNOWN] |

## Post-move results

Use **PASS**, **FAIL**, **NOT RUN** or **INCONCLUSIVE**. Do not count
redirects, a successful grep or passing local CI as tests of consumers.

| Check | Result | When / where | Evidence |
| --- | --- | --- | --- |
| New direct README and links | [NOT RUN] | [date / browser] | [URL, observation] |
| New remote resolves expected Git HEAD | [NOT RUN] | [date / environment] | [output] |
| Disposable clean clone and first success | [NOT RUN] | [OS / date] | [exact command and observed result] |
| Downstream Action use | [NOT RUN] | [workflow / date] | [run URL] |
| Website and package routes | [NOT RUN] | [environment / date] | [observed behavior] |
| Reporting and contribution routes | [NOT RUN] | [date] | [actual route, no sensitive text] |

## Unresolved work and truthful public notice

- Broken routes: [none observed / details]
- Unknown or untested consumers: [list]
- Migration notice location: [URL / NOT PUBLISHED]
- Follow-up ownership and review date: [real role + YYYY-MM-DD / UNASSIGNED]
- Honest reader-facing status: [one paragraph without unsupported promises]
