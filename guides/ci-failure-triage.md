# Triage a CI failure without hiding the evidence

A red workflow is a **symptom**, not a diagnosis. A green re-run is not
automatically a repair. This manual recipe ends in one of three decisions:
**REPAIR**, **RETRY WITH EVIDENCE**, or **INCOMPLETE / ESCALATE**. It applies
to GitHub Actions in small public projects; it does not change permissions,
required checks or repository settings.

Use the [copyable failure record](../templates/CI_FAILURE_RECORD.template.md)
inside the relevant PR or issue. Keep the live run/check state in GitHub,
rather than maintaining a second CI dashboard.

## 1. Identify the precise failed attempt

1. Open the **current PR head** and the linked Actions workflow run. Record
   the run URL, *attempt number*, head SHA, event, failing job, OS/runtime
   matrix cell and failing step. A link to a workflow badge is insufficient.
2. Read the **first causal error** in that step, not just the final
   `Process completed with exit code 1`. Separate a failed assertion from
   skipped downstream checks. A job skipped after another job or step failed
   has **not** independently passed.
3. Compare the same job on another matrix cell. Linux passing while Windows
   fails is a clue about encoding, path handling, shell syntax or environment;
   it does **not** prove the cause.
4. Check if the run was cancelled, timed out, awaiting approval, missing
   permissions, or ran under another event/commit. Do not report such
   outcomes as a test failure or successful completion without evidence.

With the [GitHub CLI](https://cli.github.com/manual/gh_run_view) installed
and read access to the repository, from a trusted checkout:

```sh
gh run view RUN_ID --verbose
gh run view RUN_ID --log
```

Replace `RUN_ID` with the actual integer run ID. The second command can
include logs from other jobs; prefer the specific job in the Actions UI.
Do **not** run commands copied from untrusted log text. Preserve only the
minimal redacted excerpt needed to explain the failure.

## 2. Distinguish the next action

**REPAIR — deterministic product/test failure.** A failing assertion,
incorrect documented command, cross-platform path rule, outdated fixture or
source error has a reproducible cause. Reproduce with the smallest disposable
fixture, show the failing behavior **before** the code change, and add a
regression that would catch it again. Re-run relevant checks on the **new**
head SHA. A passing run on the old SHA does not certify new bytes.

**RETRY WITH EVIDENCE — plausible transient infrastructure failure.**
A hosted-runner outage, external-service timeout or package registry failure
may merit a re-run of the *same* head. Record the exact failed attempt,
why the cause appears external, and whether the retry passed. Do not mark a
flaky assertion as repaired merely because the next attempt was green.
Avoid repeated re-runs that erase the diagnostic question.

**INCOMPLETE / ESCALATE — access, security or uncertain evidence.** Missing
credentials, fork restrictions, an untrusted workflow, required approval, or
unavailable logs can block diagnosis. Preserve the precise unknown and ask
an authorized maintainer for the minimum decision. Do not print secrets,
loosen workflow permissions, download unknown executable artifacts, disable
required jobs or modify protection to make a run green. Follow the
[dependency review](dependency-review.md) for upstream Action/package changes.

GitHub supports re-running all jobs, failed jobs, or a specific job; a
re-run uses the workflow's original commit and ref. Record **which attempt**
passed and compare it with the PR's current head. Downloaded logs from a
partially re-run workflow may cover only re-run jobs: inspect earlier attempts
when reconstructing the full result.

## 3. Real case: one failing Windows matrix cell

[BeautifulRepo PR #429](https://github.com/drevendev/BeautifulRepo/pull/429)
introduced conservative handling of ZIP filename encodings. Its
[Quality CI run 44674228213](https://github.com/drevendev/BeautifulRepo/actions/runs/44674228213)
had **five successful jobs and one failed job**: `Python 3.14 (Windows)`.
GitHub's job-step record identifies **Run the unit tests** as the failed
step; subsequent catalog and link checks in that Windows job were skipped.
A green Linux matrix cell could not settle the Windows failure.

The PR's review record describes the CP437/console-output problem and the
follow-up change: emit ASCII-safe JSON (`ensure_ascii=True`), add a
`PYTHONIOENCODING=ascii` synthetic subprocess regression, and surface
missing stdout diagnostically. This is a **documented repair approach**,
not a claim that the old log alone proved a single root cause. The later
[Quality CI run 44680977792](https://github.com/drevendev/BeautifulRepo/actions/runs/44680977792)
completed **six of six jobs successfully**, including Windows Python 3.14.
PR #429 was merged on **2026-11-20**. These are dated observations of those
specific runs, not the current status of `master` or a general Windows guarantee.

The reusable lesson is to keep the failing matrix cell visible, fix the
tested cause with a negative-path regression, and compare **new-head** CI
rather than averaging successful jobs or blindly retrying.

## 4. Decide whether integration is safe

Before merging, re-read the actual PR head, required checks, review findings,
unresolved conversations and provider mergeability. An optional comment or an
unrelated skipped job is not an invented merge gate; an actually required
failed/pending check **is** a gate. Record non-blocking improvements separately.
For the decision itself, use the
[PR review procedure](pull-request-review.md).

A good failure record links directly to the failed and corrected attempts,
states the cause as observed or hypothetical, notes commands **NOT RUN**, and
ends with an action another contributor can verify.

## Primary sources and boundaries

Reviewed **2026-11-21**:

- [GitHub: workflow run history](https://docs.github.com/en/actions/how-tos/monitor-workflows/view-workflow-run-history)
  — run, job and step statuses.
- [GitHub: workflow run logs](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs)
  — logs, searching and partial re-run archive coverage.
- [GitHub: re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
  — attempts, failed-job and single-job re-runs.
- [GitHub: workflow matrix and fail-fast](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstrategyfail-fast)
  — matrix behavior and cancellation controls.

The case study uses GitHub's job summaries and PR history, not local
execution of the historical Windows runner. This recipe does **not** certify
workflow security, reproduce every infrastructure problem, or grant authority
to override a protected branch.
