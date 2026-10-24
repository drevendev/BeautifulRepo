# BeautifulRepo agent behavior evaluations

These are **unexecuted model-eval definitions** for the current `audit-repo` skill, prepared on **2026-10-24**. They are not CI results, proven prompt-injection protection, or a release gate.

The cases use the [Claude Code plugin-eval format](https://code.claude.com/docs/en/plugin-evals). Two ordinary requests should trigger the skill, one unrelated code request should not, and a separate hostile README case tests whether the skill treats repository text as untrusted data. Synthetic files are supplied under each case's `resources/` directory via `context.add_dirs`; no real repositories or private material are used.

## Running (requires separate model-usage authorization)

Claude Code **2.1.269+** is required. Evals make real model calls and may incur usage or cost. **Do not add them to ordinary CI or run them automatically.** First read and trust the plugin and test definitions. On a Linux or WSL2 host, from the plugin root:

```sh
claude plugin eval . --case 'audit-*' --runs 1 --ablation none --no-publish --max-cost-usd 1
```

The example deliberately grants only `Read`, `Glob`, `Grep`, and `Skill` (and no write/network/shell tools), so it measures skill selection and file-based reasoning, **not execution of the three Python checkers**. To test actual checker execution, a trusted operator must separately authorize `--allow-tools Bash` on a sandbox-capable Linux or WSL2 machine, review the target and cost limits, and verify that the skill calls only its own offline tools. Bash without a sandbox is not permitted. These source-controlled evals have **not** been executed in Claude.

The `tool_used: Skill` grader in a two-arm evaluation is an indicator, not automatically part of the score. The negative trigger uses `arm: both`, `min: 0`, `max: 0`. Do not treat a favorable summary score as proof the skill was called or that an injection failed: inspect the tool trace, generated files and final answer. Do not publish reports containing private context. Result artifacts under `evals/results/` are ignored.

The free and deterministic repo-fixture tests continue to run in CI: `python -m unittest discover -s tests -v`. The new `test_agent_eval_cases.py` checks that the case definitions cover each shipped skill without calling a model. The real-model evaluation work in [#74](https://github.com/drevendev/BeautifulRepo/issues/74) stays open until runs and outcomes are verified.
