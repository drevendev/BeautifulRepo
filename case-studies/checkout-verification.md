# One local verification command: from partial instructions to a checkable CI inventory

**Status (2026-11-23): implemented and merged; first-use case incomplete.**
The source, regression tests and exact-PR-head GitHub CI are inspectable.
A clean-clone run by a new contributor, a local full nine-step execution,
a manual rendered review and an actual user study were **NOT RUN**.
This documents a real source intervention, **not** measured onboarding gains
or a completed case under the [five-step procedure](README.md).

## Before: five documented checks, nine actual Python steps

- Target: [BeautifulRepo](https://github.com/drevendev/BeautifulRepo), MIT.
- Before: [README at `b25af1a339ac838ecb5eecc515aefe2a75630a1a`](https://github.com/drevendev/BeautifulRepo/blob/b25af1a339ac838ecb5eecc515aefe2a75630a1a/README.md).
- After: [README at `7d52c21f5b8de7bc93a946458045dd70f68ca0f1`](https://github.com/drevendev/BeautifulRepo/blob/7d52c21f5b8de7bc93a946458045dd70f68ca0f1/README.md).
- Change history: [PR #453](https://github.com/drevendev/BeautifulRepo/pull/453)
  built the checker; [PR #455](https://github.com/drevendev/BeautifulRepo/pull/455)
  made it the root README's primary local-check route. Both are merged.
  Inspected source and provider records on **2026-11-23**.

The earlier **This repository checks itself** section offered five separate
commands. In the same revision, the Quality workflow's Python matrix job also
executed the first-minute demo, combined audit, Action SHA-pin and README
badge checks. A contributor following the entire visible command block still
would not have run those four steps. This is a **source-level gap**; there
is no observed visitor failure, timing or support ticket.

## Intervention: one route, bounded scope

The [runner](https://github.com/drevendev/BeautifulRepo/blob/7d52c21f5b8de7bc93a946458045dd70f68ca0f1/scripts/verify_checkout.py)
executes the nine reviewed Python commands in order using the current
interpreter and **its own BeautifulRepo checkout**. The root README now shows:

```sh
python -I scripts/verify_checkout.py
```

`--list` prints commands without executing them; `--keep-going` continues
independent checks but still exits nonzero if any failed. The original five
commands are still documented for targeted diagnosis. The runner uses a
fixed argv inventory without a shell or user-supplied repository command.
It is **not** an auditor for arbitrary/untrusted checkouts.

The [regressions](https://github.com/drevendev/BeautifulRepo/blob/7d52c21f5b8de7bc93a946458045dd70f68ca0f1/tests/test_verify_checkout.py)
compare all nine argv lists to the [actual workflow](https://github.com/drevendev/BeautifulRepo/blob/7d52c21f5b8de7bc93a946458045dd70f68ca0f1/.github/workflows/quality.yml).
They also test list-only execution, failure propagation, keep-going behavior,
a process-launch error, complete success and the README promise. The parser
intentionally covers the existing workflow's structure; it is not a general
YAML interpreter. Changing the workflow requires reviewing its inventory
and the test rather than assuming this source contract stays true forever.

### The useful failed attempt

PR #453 initially placed the orchestration script under `tools/`.
The existing [offline contract](https://github.com/drevendev/BeautifulRepo/blob/7d52c21f5b8de7bc93a946458045dd70f68ca0f1/tests/test_offline_contract.py)
forbids a `tools/*.py` import of `subprocess`; an orchestrator must launch
processes. The implementation was therefore moved to `scripts/`, **not**
fixed by weakening the read-only tooling rule. The source and repair sequence
are visible in [PR #453](https://github.com/drevendev/BeautifulRepo/pull/453).
This was a real CI-discovered scope conflict, not a hypothetical test case.

**Trade-off:** an additional runner needs maintenance when workflow commands
change. In return, the documented local entry point can fail a regression
when it drifts from the workflow, and newcomers no longer need to compose
a longer command sequence by hand.

## Recorded verification, not imagined use

The repaired PR #453 head
[`0ca9df845bb899598880dfb2bcd4b2171f2aa7bb`](https://github.com/drevendev/BeautifulRepo/commit/0ca9df845bb899598880dfb2bcd4b2171f2aa7bb)
passed [Quality CI run 45060857580](https://github.com/drevendev/BeautifulRepo/actions/runs/45060857580),
**6/6 completed-success jobs**, including Windows Python 3.14.
The subsequent README PR #455 head
[`8eb0dc77dc55124a63fad0ca0a364537eb57b889`](https://github.com/drevendev/BeautifulRepo/commit/8eb0dc77dc55124a63fad0ca0a364537eb57b889)
passed [Quality CI run 45083095035](https://github.com/drevendev/BeautifulRepo/actions/runs/45083095035),
again **6/6**. Both run/job results were rechecked in GitHub on
**2026-11-23**. These results apply to those exact commits.

The new command covers **the Python steps on the current local checkout**.
It does **not** reproduce the separate GitHub Action self-test jobs, Ruff
lint job, Linux/Windows matrix, platform-specific failures, repository
protection or a real model host. No local full-run stdout or exit code
has been recorded for this case. Do not cite the green PR jobs as proof
that a fresh external user's command succeeded.

## Reuse and remaining work

**Reusable pattern:** expose a small, discoverable entry point for a real
subset of CI; bind its command inventory to maintained workflow source; keep
component commands for diagnosis; write negative-path tests and explain what
only the provider can verify. A local script is useful precisely when its
scope is explicit and its claims can fail a test.

**Needed for full case acceptance:** a clean-clone first success and one
failure path with actual outputs and environment; light/dark rendering at a
narrow viewport, with text alternatives; and explicitly recorded keyboard,
screen-reader or real-device tests if attempted. Newcomer comprehension,
time-to-first-success and adoption effects remain **UNKNOWN**.

**Primary guidance reviewed 2026-11-23:**
[GitHub's README guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
describes onboarding information;
[workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
separates jobs and steps;
[run-history guidance](https://docs.github.com/en/actions/how-tos/monitor-workflows/view-workflow-run-history)
describes the provider evidence used here. Those sources support the
method, not an unmeasured usability claim.
