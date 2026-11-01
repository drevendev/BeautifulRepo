# Reproduce a README edit without trusting its claims

This **synthetic, offline** example exercises the installed BeautifulRepo tools
as one workflow: diagnose a weak README, display an exact proposed change,
refuse an unapproved write, apply a deliberately **simulated** approval to a
disposable copy, and re-run the checks.

It is a regression test of **local tools**, not an evaluation of a language
model, a real maintainer's consent, user onboarding, visual accessibility or a
project's first-run code.

## Run the executable example

From a BeautifulRepo checkout with Python 3.11+:

```bash
python -m unittest discover -s tests -p 'test_readme_workflow.py' -v
```

The test constructs a temporary repository and a proposal **outside** it.
The original README contains a visible `{{PROJECT_NAME}}` placeholder and
a vague `[here](missing.md)` link. The replacement removes the placeholder
and points a descriptive `[usage notes](notes.md)` link to an existing file.
A synthetic target script that would write a marker is present but must **never
be executed**. No real project is edited.

The test checks the following observable outcomes:

1. The offline repository audit initially identifies
   `readme.placeholder` and `link.vague_text`; the relative-link check
   rejects the missing local destination.
2. `readme_preview.py` prints a unified diff and both original/proposed
   SHA-256 values without changing the temporary target.
3. `readme_apply.py` refuses an invocation **without** the two hashes.
   For the successful test only, the test harness supplies those hashes as a
   **simulation** of the separate consent decision.
4. The replacement keeps candidate bytes intact and changes only
   `README.md`; re-running the audit no longer reports the two findings,
   and both local link/navigation checkers exit successfully.
5. Separate regressions change the original or candidate **after** preview.
   Both stale inputs are rejected; unrelated files and the marker remain
   unchanged.

The test invokes BeautifulRepo's actual CLI tools with `python -I`, explicit
paths and a working directory outside the synthetic target. It does not load
or execute code from that target.

## What this deliberately cannot prove

**Hashes authenticate neither permission nor truth.** A caller who computes
both hashes can invoke the helper without anyone's consent. The actual
`improve-readme` skill must first show the exact file list and diff, obtain
an explicit later **yes to that specific change**, then perform the edit and
re-audit. An audit finding disappearing does not prove the README's factual
claims, output, badges or first-run instructions.

This example tests a narrow mechanical sequence. The model-level questions in
[issue #70](https://github.com/drevendev/BeautifulRepo/issues/70) and the
[agent evaluation plan](../../evals/README.md) remain open: actual agent
triggering, user permission handling, resistance to injected README content and
refusal to invent CI or first-success output require separate, authorized
model runs with retained transcripts and independent verification.

For real repositories use the
[improve-readme skill](../../skills/improve-readme/SKILL.md) and
[agent safety guidance](../../guides/agent-safety.md). Never treat this test's
simulated approval as permission to modify another repository.
