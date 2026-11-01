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
