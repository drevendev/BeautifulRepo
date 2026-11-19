# Quillgrain: a first-run and reporting-route source baseline

**Status, 2026-11-01:** source-only, **not a completed before/after case**.
The two targets were read at immutable revisions. No target repository was edited,
no commands were executed in a clean checkout, and no accessibility, model or
human editorial-quality result was measured.

This is a practical intake for [the real-case workflow](README.md), not an
endorsement of untested instructions. The target PR, after-merge snapshot, actual
stdout/stderr, private-reporting verification and rendered evidence are still
missing. BeautifulRepo maintenance does **not** authorize changing either target.

## Target and pinned source

- **CLI engine:** [drevendev/Quillgrain](https://github.com/drevendev/Quillgrain),
  commit [`4e1cf298b3c5b0697c7a3912c10a833c67f9af6c`](https://github.com/drevendev/Quillgrain/commit/4e1cf298b3c5b0697c7a3912c10a833c67f9af6c).
  The [README](https://github.com/drevendev/Quillgrain/blob/4e1cf298b3c5b0697c7a3912c10a833c67f9af6c/README.md)
  describes a local, non-generative check; [`pyproject.toml`](https://github.com/drevendev/Quillgrain/blob/4e1cf298b3c5b0697c7a3912c10a833c67f9af6c/pyproject.toml)
  declares Python 3.11+, MIT and version `0.1.0rc4`.
- **Public data pack:** [drevendev/Quillgrain_Voice_Common](https://github.com/drevendev/Quillgrain_Voice_Common),
  commit [`892adbf4ba2cd29bac1c687d1a87bf103056c51b`](https://github.com/drevendev/Quillgrain_Voice_Common/commit/892adbf4ba2cd29bac1c687d1a87bf103056c51b).
  Its [README](https://github.com/drevendev/Quillgrain_Voice_Common/blob/892adbf4ba2cd29bac1c687d1a87bf103056c51b/README.md)
  calls version `0.5.0` a **candidate awaiting human review**, not a validated
  voice. It describes synthetic examples, not measured human authorship.
- **Inspection method:** GitHub source-file reads on 2026-11-01, without a
  fresh clone. The historical [case issue #83](https://github.com/drevendev/BeautifulRepo/issues/83)
  names `Quillgrain_Common` and `0.1.0rc1`; those names/version claims no longer
  describe the inspected default-branch files. No release/tag status was
  independently checked.

## Where a first-time reader gets stuck

1. **The engine's first command path assumes PowerShell.** The engine README
   gives a complete PowerShell sequence including `qg doctor`, pack validation,
   a public synthetic build, `qg check` and tests, but gives POSIX users only
   the executable substitutions. A POSIX newcomer has to translate the entire
   sequence. This is a *documentation-onboarding* finding, not a CLI defect.
2. **The engine does not show an observed result.** The README's synthetic
   `qg check` command writes `out/check.json`, but the landing path does not
   show the command's exit status or a small, redacted example of the resulting
   report. A prospective user cannot tell what a successful diagnostic looks
   like before installing it.
3. **The pack is a separate, versioned product.** The Common README includes
   `qg pack validate` and `qg pack build` examples, but does not give a
   complete pinned-engine install from a clean checkout. Its
   [public workflow](https://github.com/drevendev/Quillgrain_Voice_Common/blob/892adbf4ba2cd29bac1c687d1a87bf103056c51b/.github/workflows/validate.yml)
   does pin Quillgrain at
   [`fd15cc3f13ebfc86d5634e3d03e408886f3334a7`](https://github.com/drevendev/Quillgrain/commit/fd15cc3f13ebfc86d5634e3d03e408886f3334a7),
   installs it, validates the pack and compiles declared modes. The pin is
   deliberately distinct from the inspected engine head; do not silently
   upgrade it. The Common README and workflow **both use `--public`** for
   builds, so the older case issue's flag discrepancy is not reproduced here.
4. **A reporting route cannot be inferred from wording.** The engine's
   [SECURITY.md](https://github.com/drevendev/Quillgrain/blob/4e1cf298b3c5b0697c7a3912c10a833c67f9af6c/SECURITY.md)
   points to GitHub private security reporting *where available*. Issue #83
   recorded it disabled on 2026-10-22, but that is historical; the current API
   setting was **not** verified in this intake. Do not publish a guaranteed
   confidential route before checking that it exists.

## Reproduction plan — not executed

For the **engine**, a target-side documentation improvement could include a
full POSIX path equivalent to the current PowerShell instructions:

```sh
git clone https://github.com/drevendev/Quillgrain.git
cd Quillgrain
git checkout 4e1cf298b3c5b0697c7a3912c10a833c67f9af6c
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/qg doctor
.venv/bin/qg pack validate --pack examples/synthetic/common
.venv/bin/qg pack build --pack examples/synthetic/common --register essay --public --out out/demo
.venv/bin/qg check --draft examples/synthetic/draft.md --context out/demo/context.json --out out/check.json
.venv/bin/python -m json.tool out/check.json
```

**These commands are derived from source, not verified output.** Installation
needs network access and third-party packages. The path above is an
illustrative candidate to test in a throwaway clean clone, not a success
transcript or an endorsed dependency audit. A separate run should repeat the
check with a missing context file and record the actual nonzero exit,
stdout/stderr and whether it changes existing output.

For **Common**, use the workflow's exact engine pin when trying to reproduce
the pack validation, not whichever `master` happens to contain the latest
engine. Observe all four declared registers in both languages and the
`--public` behavior. Do not treat passing format checks as evidence of a
human-approved editorial voice.

## Smallest useful change and acceptance

The target maintainer could add one copyable POSIX command block and a
**real, minimal, non-sensitive `qg check` output excerpt** to the engine
README; Common could add a pinned clean-install route and explain why CI
pins the engine. Before changing SECURITY.md, read the live private-reporting
setting; enabling it is an administrative choice, not part of this case.
Releases, tags and consumer installs are likewise outside this baseline.

A complete before/after case requires an **authorized target PR**, an after
merge SHA, audits with one pinned BeautifulRepo tool revision, a fresh-clone
successful first run and failure path with observed output, target-native CI,
narrow light/dark observations with text alternatives, and explicit
accessibility and human-review limits. None is asserted here.

**Current decision:** preserve this as a traceable baseline for
[case #83](https://github.com/drevendev/BeautifulRepo/issues/83);
do not call the case complete or claim a target change.

## Follow-up: the first-success route changed (source review, 2026-11-16)

This is a **second source snapshot**, not an after-merge test. No target PR,
clean install, model-host invocation or CLI output was observed for this follow-up.
Keep the 2026-11-01 revisions above as the original intake, rather than
silently replacing them with newer source.

- The [engine at `6b022c2e51c688ee3639628551aa5a2d80e5568a`](https://github.com/drevendev/Quillgrain/tree/6b022c2e51c688ee3639628551aa5a2d80e5568a)
  now declares **0.1.0rc5** in `pyproject.toml`. Its README starts with an
  **agent-skill** route (`qg skill install` with `--agent codex` or `--agent claude`),
  **after** installing the engine. This is a different reader promise from
  running deterministic `qg check` alone. The detailed first-run command block
  is still PowerShell-first, with POSIX executable substitutions rather than
  a complete copyable POSIX sequence. Neither a `qg check` output example nor
  evidence of host skill discovery/invocation is present in the inspected
  landing page. These are source observations, **not** failed runtime tests.
- The [Common pack at `263a6bf82f7fb258828e3251d6c72f885deff907`](https://github.com/drevendev/Quillgrain_Voice_Common/tree/263a6bf82f7fb258828e3251d6c72f885deff907)
  now calls itself a **0.6.0 candidate, human review pending**. Its README
  reports targeted R03 checks through Codex as passed; BeautifulRepo did not
  reproduce or independently verify those checks, and the text does not claim
  broad editorial acceptance. The public workflow still pins engine
  `fd15cc3f13ebfc86d5634e3d03e408886f3334a7`, while the Common README
  calls that public-CI engine **0.1.0rc4**. Both README and CI retain
  `--public` for builds. Do not substitute the 0.1.0rc5 engine for the
  workflow's pin without an actual compatibility test.

**Case-design consequence:** there are now **two separate first-success claims**
that should not be conflated. First, demonstrate the *deterministic engine* in
an authorized fresh checkout with observed `doctor`, pack validation/build,
`qg check` output and a missing-input failure, including process exit codes.
Second, if an *agent-skill* route is advertised as working, independently record
Claude Code/Codex version, installed skill files, observed discovery/invocation,
model-provider data implications and any target-file changes. A source README
claim, a Codex check reported by the pack, or an ordinary schema test cannot
stand in for those host observations. Both tracks still require permission to
change the target repos and an actual target-side PR before this becomes a
completed before/after case.

## 2026-11-20: entry point availability in the first-minute path

The engine's [immutable 0.1.0rc5 README](https://github.com/drevendev/Quillgrain/blob/6b022c2e51c688ee3639628551aa5a2d80e5568a/README.md)
has a more precise source-level onboarding gap than the general
PowerShell/POSIX split above. Its very first agent setup block says
`qg skill install --agent codex` or `--agent claude`; the later source
installation creates `.venv` and invokes
`.\.venv\Scripts\qg.exe` on PowerShell, or `.venv/bin/qg` on POSIX,
with **no environment activation step**. A shell that has not added the new
environment's scripts directory to `PATH` cannot rely on bare `qg` finding
that newly installed entry point. A separately installed `qg` could hide
the mismatch rather than prove the new checkout works.

The minimal target-side documentation fix is to show a consistent direct
entry-point path after installation (proposed, **not executed**):

```sh
.venv/bin/qg skill install --agent codex --project PATH_TO_WRITING_PROJECT
```

```powershell
.\.venv\Scripts\qg.exe skill install --agent claude --project PATH_TO_WRITING_PROJECT
```

Alternatively, document activation first and then consistently use bare
`qg`. The paths above are platform examples, **not** evidence that either
host discovered or ran the skill. In a separately authorized, disposable
fresh clone, test both the direct CLI first success and the skill installation
route, recording the exact interpreter/entry-point paths, exit codes and
observed output. Verify actual host discovery/invocation separately. Do
not write the target repository or claim a runtime failure from this
source-only comparison.

This finding is backed by the pinned README and
[Python's venv behavior](https://docs.python.org/3/library/venv.html#how-venvs-work),
reviewed 2026-11-20. The same immutable engine and Common revisions from
2026-11-16 remain the inspected sources; no new target changes, releases,
fresh-clone runs or provider-setting checks are claimed.
